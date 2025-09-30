"""OpenAI Responses message types and conversion utilities."""

import logging
from collections.abc import Sequence
from typing import Literal, TypedDict

from openai import AsyncStream, NotGiven, Stream
from openai.types import responses as openai_types
from openai.types.responses import response_create_params
from openai.types.responses.easy_input_message_param import EasyInputMessageParam
from openai.types.responses.function_tool_param import FunctionToolParam
from openai.types.responses.response_format_text_json_schema_config_param import (
    ResponseFormatTextJSONSchemaConfigParam,
)
from openai.types.responses.response_stream_event import ResponseStreamEvent
from openai.types.responses.response_text_config_param import ResponseTextConfigParam
from openai.types.responses.tool_choice_allowed_param import ToolChoiceAllowedParam
from openai.types.responses.tool_choice_function_param import ToolChoiceFunctionParam
from openai.types.shared_params.response_format_json_object import (
    ResponseFormatJSONObject,
)
from openai.types.shared_params.responses_model import ResponsesModel

from ...content import (
    AssistantContentPart,
    Text,
    TextChunk,
    TextEndChunk,
    TextStartChunk,
    ToolCall,
    ToolCallChunk,
    ToolCallEndChunk,
    ToolCallStartChunk,
)
from ...formatting import (
    Format,
    FormattableT,
    _utils as _formatting_utils,
    resolve_format,
)
from ...messages import AssistantMessage, Message
from ...responses import (
    AsyncChunkIterator,
    ChunkIterator,
    RawChunk,
)
from ...tools import (
    FORMAT_TOOL_NAME,
    BaseToolkit,
    ToolSchema,
)
from ..base import Params, _utils as _base_utils
from ..openai._utils import (
    MODELS_WITHOUT_JSON_OBJECT_SUPPORT,
    MODELS_WITHOUT_JSON_SCHEMA_SUPPORT,
)
from .model_ids import OpenAIResponsesModelId

logger = logging.getLogger(__name__)


class ResponseCreateKwargs(TypedDict, total=False):
    """Kwargs to the OpenAI `client.responses.create` method."""

    model: ResponsesModel
    input: str | openai_types.ResponseInputParam
    instructions: str
    temperature: float
    max_output_tokens: int
    top_p: float
    tools: list[FunctionToolParam] | NotGiven
    tool_choice: response_create_params.ToolChoice | NotGiven
    text: ResponseTextConfigParam


def _encode_message(message: Message) -> EasyInputMessageParam:
    """Convert a Mirascope Message to OpenAI Responses EasyInputMessageParam."""

    if message.role == "system":
        # Responses API allows multiple "developer" messages, so rather than using the
        # instructions field, we convert system messages as we find them.
        # Unlike other LLM APIs, the system message does not need to be the first message.
        return EasyInputMessageParam(role="developer", content=message.content.text)

    text_content: list[str] = []
    for part in message.content:
        if part.type != "text":
            raise NotImplementedError()
        text_content.append(part.text)

    content: str | list[openai_types.ResponseInputContentParam]
    if len(text_content) == 1:
        content = text_content[0]
    else:
        content = [
            openai_types.ResponseInputTextParam(text=text, type="input_text")
            for text in text_content
        ]

    return EasyInputMessageParam(role=message.role, content=content)


def _ensure_additional_properties_false(obj: object) -> None:
    """Recursively adds additionalProperties = False to a schema, required by OpenAI API."""
    if isinstance(obj, dict):
        if obj.get("type") == "object" and "additionalProperties" not in obj:
            obj["additionalProperties"] = False
        for value in obj.values():
            _ensure_additional_properties_false(value)
    elif isinstance(obj, list):
        for item in obj:
            _ensure_additional_properties_false(item)


def _convert_tool_to_function_tool_param(tool: ToolSchema) -> FunctionToolParam:
    """Convert a Mirascope ToolSchema to OpenAI Responses FunctionToolParam."""
    schema_dict = tool.parameters.model_dump(by_alias=True, exclude_none=True)
    schema_dict["type"] = "object"
    _ensure_additional_properties_false(schema_dict)

    return FunctionToolParam(
        type="function",
        name=tool.name,
        description=tool.description,
        parameters=schema_dict,
        strict=tool.strict,
    )


def _create_strict_response_format(
    format: Format[FormattableT],
) -> ResponseFormatTextJSONSchemaConfigParam:
    """Create OpenAI Responses strict response format from a Mirascope Format.

    Args:
        format: The `Format` instance containing schema and metadata

    Returns:
        ResponseFormatTextJSONSchemaConfigParam for strict structured outputs
    """
    schema = format.schema.copy()
    _ensure_additional_properties_false(schema)

    response_format: ResponseFormatTextJSONSchemaConfigParam = {
        "type": "json_schema",
        "name": format.name,
        "schema": schema,
    }
    if format.description:
        response_format["description"] = format.description
    response_format["strict"] = True

    return response_format


PARAMS_TO_KWARGS: _base_utils.ParamsToKwargs = {
    "temperature": "temperature",
    "max_tokens": "max_output_tokens",
    "top_p": "top_p",
    "top_k": None,
    "seed": None,
    "stop_sequences": None,
}


def prepare_openai_request(
    *,
    model_id: OpenAIResponsesModelId,
    messages: Sequence[Message],
    tools: Sequence[ToolSchema] | BaseToolkit | None = None,
    format: type[FormattableT] | Format[FormattableT] | None = None,
    params: Params | None = None,
) -> tuple[Sequence[Message], Format[FormattableT] | None, ResponseCreateKwargs]:
    """Prepare OpenAI Responses API request parameters.

    Args:
        model_id: The OpenAI model string.
        messages: A sequence of Mirascope `Message`s.
        tools: A sequence of Mirascope tools (or None).
        format: A format type (or None).
        params: Additional parameters.

    Returns:
        A tuple containing:
            - A sequence of Mirascope `Message`s, which may include modifications to the
              system message (e.g. with instructions for JSON mode formatting).
            - A Format instance (or None).
            - A ResponseCreateKwargs dict with parameters for OpenAI's Responses create method.
    """
    kwargs: ResponseCreateKwargs = {
        "model": model_id,
    }

    kwargs = _base_utils.map_params_to_kwargs(
        params,
        kwargs,
        PARAMS_TO_KWARGS,
        provider="OpenAI",
    )
    tools = tools.tools if isinstance(tools, BaseToolkit) else tools or []
    openai_tools = [_convert_tool_to_function_tool_param(tool) for tool in tools]

    model_supports_strict = model_id not in MODELS_WITHOUT_JSON_SCHEMA_SUPPORT
    default_mode = "strict" if model_supports_strict else "tool"

    format = resolve_format(format, default_mode=default_mode)
    if format is not None:
        if format.mode == "strict":
            kwargs["text"] = {"format": _create_strict_response_format(format)}
        elif format.mode == "tool":
            format_tool_schema = _formatting_utils.create_tool_schema(format)
            openai_tools.append(
                _convert_tool_to_function_tool_param(format_tool_schema)
            )
            if tools:
                kwargs["tool_choice"] = ToolChoiceAllowedParam(
                    type="allowed_tools",
                    mode="required",
                    tools=[
                        {"type": "function", "name": tool["name"]}
                        for tool in openai_tools
                    ],
                )
            else:
                kwargs["tool_choice"] = ToolChoiceFunctionParam(
                    type="function",
                    name=FORMAT_TOOL_NAME,
                )
        elif (
            format.mode == "json" and model_id not in MODELS_WITHOUT_JSON_OBJECT_SUPPORT
        ):
            kwargs["text"] = {"format": ResponseFormatJSONObject(type="json_object")}

        if format.formatting_instructions:
            messages = _base_utils.add_system_instructions(
                messages, format.formatting_instructions
            )

    kwargs["input"] = [_encode_message(msg) for msg in messages]

    if openai_tools:
        kwargs["tools"] = openai_tools

    return messages, format, kwargs


def decode_response(
    response: openai_types.Response,
) -> AssistantMessage:
    """Convert OpenAI Responses Response to mirascope AssistantMessage."""
    parts: list[AssistantContentPart] = []

    for output_item in response.output:
        if output_item.type == "message":
            for content in output_item.content:
                if content.type == "output_text":
                    parts.append(Text(text=content.text))
                elif content.type == "refusal":  # pragma: no cover
                    # TODO: Decide what to do here
                    raise NotImplementedError("Refusals not yet handled")
        elif output_item.type == "function_call":
            parts.append(
                ToolCall(
                    id=output_item.call_id,
                    name=output_item.name,
                    args=output_item.arguments,
                )
            )
        else:
            raise NotImplementedError(f"Unsupported output item: {output_item.type}")

    return AssistantMessage(content=parts)


class _OpenAIResponsesChunkProcessor:
    """Processes OpenAI Responses streaming events and maintains state across chunks."""

    def __init__(self) -> None:
        self.current_content_type: Literal["text", "tool_call"] | None = None

    def process_chunk(self, event: ResponseStreamEvent) -> ChunkIterator:
        """Process a single OpenAI Responses stream event and yield the appropriate content chunks."""
        yield RawChunk(raw=event)

        if hasattr(event, "type"):
            if event.type == "response.output_text.delta":
                if not self.current_content_type:
                    yield TextStartChunk()
                    self.current_content_type = "text"
                if self.current_content_type != "text":
                    raise RuntimeError(
                        "Received text delta when not processing text"
                    )  # pragma: no cover
                yield TextChunk(delta=event.delta)
            elif event.type == "response.output_text.done":
                if self.current_content_type != "text":
                    raise RuntimeError(
                        "Received text done while not processing text"
                    )  # pragma: no cover
                yield TextEndChunk()
                self.current_content_type = None
            elif event.type == "response.output_item.added":
                item = event.item
                if item.type == "function_call":
                    self.current_tool_call_id = item.call_id
                    self.current_tool_call_name = item.name
                    yield ToolCallStartChunk(
                        id=item.call_id,
                        name=item.name,
                    )
                    self.current_content_type = "tool_call"
            elif event.type == "response.function_call_arguments.delta":
                if self.current_content_type != "tool_call":
                    raise RuntimeError(
                        "Received tool args delta while not processing tool call"
                    )  # pragma: no cover
                yield ToolCallChunk(delta=event.delta)
            elif event.type == "response.function_call_arguments.done":
                if self.current_content_type != "tool_call":
                    raise RuntimeError(
                        "Received tool args done while not processing tool call"
                    )  # pragma: no cover
                yield ToolCallEndChunk()
                self.current_content_type = None


def convert_openai_responses_stream_to_chunk_iterator(
    openai_stream: Stream[ResponseStreamEvent],
) -> ChunkIterator:
    """Returns a ChunkIterator converted from an OpenAI Stream[ResponseStreamEvent]"""
    processor = _OpenAIResponsesChunkProcessor()
    for event in openai_stream:
        yield from processor.process_chunk(event)


async def convert_openai_responses_stream_to_async_chunk_iterator(
    openai_stream: AsyncStream[ResponseStreamEvent],
) -> AsyncChunkIterator:
    """Returns an AsyncChunkIterator converted from an OpenAI AsyncStream[ResponseStreamEvent]"""
    processor = _OpenAIResponsesChunkProcessor()
    async for event in openai_stream:
        for item in processor.process_chunk(event):
            yield item
