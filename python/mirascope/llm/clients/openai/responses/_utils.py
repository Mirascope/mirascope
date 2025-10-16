"""OpenAI Responses message types and conversion utilities."""

import logging
from collections.abc import Sequence
from typing import Any, Literal, TypedDict, cast

from openai import AsyncStream, NotGiven, Stream
from openai.types import responses as openai_types
from openai.types.responses import response_create_params
from openai.types.responses.easy_input_message_param import EasyInputMessageParam
from openai.types.responses.function_tool_param import FunctionToolParam
from openai.types.responses.response_format_text_json_schema_config_param import (
    ResponseFormatTextJSONSchemaConfigParam,
)
from openai.types.responses.response_function_tool_call_param import (
    ResponseFunctionToolCallParam,
)
from openai.types.responses.response_input_param import (
    FunctionCallOutput,
    ResponseInputItemParam,
    ResponseInputParam,
)
from openai.types.responses.response_stream_event import ResponseStreamEvent
from openai.types.responses.response_text_config_param import ResponseTextConfigParam
from openai.types.responses.tool_choice_allowed_param import ToolChoiceAllowedParam
from openai.types.responses.tool_choice_function_param import ToolChoiceFunctionParam
from openai.types.shared_params import Reasoning
from openai.types.shared_params.response_format_json_object import (
    ResponseFormatJSONObject,
)
from openai.types.shared_params.responses_model import ResponsesModel

from ....content import (
    AssistantContentPart,
    Text,
    TextChunk,
    TextEndChunk,
    TextStartChunk,
    Thought,
    ThoughtChunk,
    ThoughtEndChunk,
    ThoughtStartChunk,
    ToolCall,
    ToolCallChunk,
    ToolCallEndChunk,
    ToolCallStartChunk,
)
from ....formatting import (
    Format,
    FormattableT,
    _utils as _formatting_utils,
    resolve_format,
)
from ....messages import AssistantMessage, Message
from ....responses import (
    AsyncChunkIterator,
    ChunkIterator,
    FinishReason,
    FinishReasonChunk,
    RawContentChunk,
    RawStreamEventChunk,
)
from ....tools import (
    FORMAT_TOOL_NAME,
    BaseToolkit,
    ToolSchema,
)
from ...base import Params, _utils as _base_utils
from ..shared import (
    _utils as _shared_utils,
)
from .model_ids import REASONING_MODELS, OpenAIResponsesModelId

logger = logging.getLogger(__name__)

INCOMPLETE_DETAILS_TO_FINISH_REASON = {
    "max_output_tokens": FinishReason.MAX_TOKENS,
    "content_filter": FinishReason.REFUSAL,
}


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
    reasoning: Reasoning | NotGiven


def _encode_message(
    message: Message, model_id: OpenAIResponsesModelId, encode_thoughts: bool
) -> ResponseInputParam:
    """Convert a Mirascope Message to OpenAI Responses input items.

    Returns a list because tool calls and tool outputs become separate input items
    in the Responses API, not part of message content.
    """

    if message.role == "system":
        # Responses API allows multiple "developer" messages, so rather than using the
        # instructions field, we convert system messages as we find them.
        # Unlike other LLM APIs, the system message does not need to be the first message.
        return [EasyInputMessageParam(role="developer", content=message.content.text)]

    if (
        message.role == "assistant"
        and message.provider == "openai:responses"
        and message.model_id == model_id
        and message.raw_content
    ):
        message_has_thoughts = any(
            content.type == "thought" for content in message.content
        )
        if not (encode_thoughts and message_has_thoughts):
            return cast(ResponseInputParam, message.raw_content)

    result: ResponseInputParam = []

    for part in message.content:
        if part.type == "text":
            result.append(EasyInputMessageParam(role=message.role, content=part.text))
        elif part.type == "tool_call":
            result.append(
                ResponseFunctionToolCallParam(
                    call_id=part.id,
                    name=part.name,
                    arguments=part.args,
                    type="function_call",
                )
            )
        elif part.type == "tool_output":
            result.append(
                FunctionCallOutput(
                    call_id=part.id,
                    output=str(part.value),
                    type="function_call_output",
                )
            )
        elif part.type == "thought" and encode_thoughts:
            result.append(
                EasyInputMessageParam(
                    role=message.role, content="**Thinking:** " + part.thought
                )
            )
        else:
            raise NotImplementedError(f"Unsupported content part type: {part.type}")

    return result


def _convert_tool_to_function_tool_param(tool: ToolSchema) -> FunctionToolParam:
    """Convert a Mirascope ToolSchema to OpenAI Responses FunctionToolParam."""
    schema_dict = tool.parameters.model_dump(by_alias=True, exclude_none=True)
    schema_dict["type"] = "object"
    _shared_utils._ensure_additional_properties_false(schema_dict)

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
    _shared_utils._ensure_additional_properties_false(schema)

    response_format: ResponseFormatTextJSONSchemaConfigParam = {
        "type": "json_schema",
        "name": format.name,
        "schema": schema,
    }
    if format.description:
        response_format["description"] = format.description
    response_format["strict"] = True

    return response_format


def _compute_reasoning(thinking: bool) -> Reasoning:
    """Compute the OpenAI `Reasoning` config based on thinking settings."""
    if thinking:
        return {"effort": "medium", "summary": "auto"}
    else:
        return {"effort": "minimal"}


def prepare_responses_request(
    *,
    model_id: OpenAIResponsesModelId,
    messages: Sequence[Message],
    tools: Sequence[ToolSchema] | BaseToolkit | None,
    format: type[FormattableT] | Format[FormattableT] | None,
    params: Params,
) -> tuple[Sequence[Message], Format[FormattableT] | None, ResponseCreateKwargs]:
    """Prepares a request for the `OpenAI.responses.create` method."""
    kwargs: ResponseCreateKwargs = {
        "model": model_id,
    }
    encode_thoughts = False

    with _base_utils.ensure_all_params_accessed(
        params=params,
        provider="openai:responses",
        unsupported_params=["top_k", "seed", "stop_sequences"],
    ) as param_accessor:
        if param_accessor.temperature is not None:
            kwargs["temperature"] = param_accessor.temperature
        if param_accessor.max_tokens is not None:
            kwargs["max_output_tokens"] = param_accessor.max_tokens
        if param_accessor.top_p is not None:
            kwargs["top_p"] = param_accessor.top_p
        if param_accessor.thinking is not None:
            thinking = param_accessor.thinking
            if model_id in REASONING_MODELS:
                # Only set reasoning if model supports it, otherwise we will get an API error
                # Note: If OpenAI adds a new reasoning model, then we need to update REASONING_MODELS
                # for mirascope users to configure it (not ideal)
                # TODO: Consider some way to future-proof this
                kwargs["reasoning"] = _compute_reasoning(thinking)
            else:
                param_accessor.emit_warning_for_unused_param(
                    "thinking", param_accessor.thinking, "openai:responses", model_id
                )
        if param_accessor.encode_thoughts_as_text:
            encode_thoughts = True

    tools = tools.tools if isinstance(tools, BaseToolkit) else tools or []
    openai_tools = [_convert_tool_to_function_tool_param(tool) for tool in tools]

    model_supports_strict = (
        model_id not in _shared_utils.MODELS_WITHOUT_JSON_SCHEMA_SUPPORT
    )
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
            format.mode == "json"
            and model_id not in _shared_utils.MODELS_WITHOUT_JSON_OBJECT_SUPPORT
        ):
            kwargs["text"] = {"format": ResponseFormatJSONObject(type="json_object")}

        if format.formatting_instructions:
            messages = _base_utils.add_system_instructions(
                messages, format.formatting_instructions
            )

    encoded_messages: list[ResponseInputItemParam] = []
    for message in messages:
        encoded_messages.extend(_encode_message(message, model_id, encode_thoughts))
    kwargs["input"] = encoded_messages

    if openai_tools:
        kwargs["tools"] = openai_tools

    return messages, format, kwargs


def _serialize_output_item(
    item: openai_types.ResponseOutputItem,
) -> dict[str, Any]:
    """Returns the item serialized as a dictionary."""
    return {key: value for key, value in item.model_dump().items() if value is not None}


def decode_response(
    response: openai_types.Response,
    model_id: OpenAIResponsesModelId,
) -> tuple[AssistantMessage, FinishReason | None]:
    """Convert OpenAI Responses Response to mirascope AssistantMessage."""
    parts: list[AssistantContentPart] = []
    finish_reason: FinishReason | None = None
    refused = False

    for output_item in response.output:
        if output_item.type == "message":
            for content in output_item.content:
                if content.type == "output_text":
                    parts.append(Text(text=content.text))
                elif content.type == "refusal":
                    parts.append(Text(text=content.refusal))
                    refused = True
        elif output_item.type == "function_call":
            parts.append(
                ToolCall(
                    id=output_item.call_id,
                    name=output_item.name,
                    args=output_item.arguments,
                )
            )
        elif output_item.type == "reasoning":
            for summary_part in output_item.summary:
                if summary_part.type == "summary_text":
                    parts.append(Thought(thought=summary_part.text))
            if output_item.content:  # pragma: no cover
                # TODO: Add test case covering this
                # (Likely their open-source models output reasoning_text rather than summaries)
                for reasoning_content in output_item.content:
                    if reasoning_content.type == "reasoning_text":
                        parts.append(Thought(thought=reasoning_content.text))

        else:
            raise NotImplementedError(f"Unsupported output item: {output_item.type}")

    if refused:
        finish_reason = FinishReason.REFUSAL
    elif details := response.incomplete_details:
        finish_reason = INCOMPLETE_DETAILS_TO_FINISH_REASON.get(details.reason or "")

    assistant_message = AssistantMessage(
        content=parts,
        provider="openai:responses",
        model_id=model_id,
        raw_content=[
            _serialize_output_item(output_item) for output_item in response.output
        ],
    )

    return assistant_message, finish_reason


class _OpenAIResponsesChunkProcessor:
    """Processes OpenAI Responses streaming events and maintains state across chunks."""

    def __init__(self) -> None:
        self.current_content_type: Literal["text", "tool_call", "thought"] | None = None
        self.refusal_encountered = False

    def process_chunk(self, event: ResponseStreamEvent) -> ChunkIterator:
        """Process a single OpenAI Responses stream event and yield the appropriate content chunks."""
        yield RawStreamEventChunk(raw_stream_event=event)

        if hasattr(event, "type"):
            if event.type == "response.output_text.delta":
                if not self.current_content_type:
                    yield TextStartChunk()
                    self.current_content_type = "text"
                yield TextChunk(delta=event.delta)
            elif event.type == "response.output_text.done":
                yield TextEndChunk()
                self.current_content_type = None
            if event.type == "response.refusal.delta":
                if not self.current_content_type:
                    yield TextStartChunk()
                    self.current_content_type = "text"
                yield TextChunk(delta=event.delta)
            elif event.type == "response.refusal.done":
                yield TextEndChunk()
                self.refusal_encountered = True
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
                yield ToolCallChunk(delta=event.delta)
            elif event.type == "response.function_call_arguments.done":
                yield ToolCallEndChunk()
                self.current_content_type = None
            elif (
                event.type == "response.reasoning_text.delta"
                or event.type == "response.reasoning_summary_text.delta"
            ):
                if not self.current_content_type:
                    yield ThoughtStartChunk()
                    self.current_content_type = "thought"
                yield ThoughtChunk(delta=event.delta)
            elif (
                event.type == "response.reasoning_summary_text.done"
                or event.type == "response.reasoning_text.done"
            ):
                yield ThoughtEndChunk()
                self.current_content_type = None
            elif event.type == "response.incomplete":
                details = event.response.incomplete_details
                reason = (details and details.reason) or ""
                finish_reason = INCOMPLETE_DETAILS_TO_FINISH_REASON.get(reason)
                if finish_reason:
                    yield FinishReasonChunk(finish_reason=finish_reason)
            elif event.type == "response.completed":
                for output_item in event.response.output:
                    yield RawContentChunk(content=_serialize_output_item(output_item))
                if self.refusal_encountered:
                    yield FinishReasonChunk(finish_reason=FinishReason.REFUSAL)


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
