"""OpenAI Responses message types and conversion utilities."""

import logging
from collections.abc import Sequence
from typing import Literal, TypedDict

from openai import AsyncStream, Stream
from openai.types import responses as openai_types
from openai.types.responses.easy_input_message_param import EasyInputMessageParam
from openai.types.responses.function_tool_param import FunctionToolParam
from openai.types.responses.response_stream_event import ResponseStreamEvent
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
    resolve_format,
)
from ...messages import AssistantMessage, Message
from ...responses import (
    AsyncChunkIterator,
    ChunkIterator,
    RawChunk,
)
from ...tools import (
    BaseToolkit,
    ToolSchema,
)
from ..base import Params
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
    tools: list[FunctionToolParam]


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
            obj["additionalProperties"] = False  # pragma: no cover (REMOVED IN NEXT PR)
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


def prepare_openai_request(
    *,
    model_id: OpenAIResponsesModelId,
    messages: Sequence[Message],
    tools: Sequence[ToolSchema] | BaseToolkit | None = None,
    format: type[FormattableT] | Format[FormattableT] | None = None,
    params: Params | None = None,
) -> tuple[Format[FormattableT] | None, ResponseCreateKwargs]:
    """Prepare OpenAI Responses API request parameters."""
    kwargs: ResponseCreateKwargs = {
        "model": model_id,
        "input": [_encode_message(msg) for msg in messages],
    }

    if params:
        if (temperature := params.get("temperature")) is not None:
            kwargs["temperature"] = temperature
        if (max_tokens := params.get("max_tokens")) is not None:
            kwargs["max_output_tokens"] = max_tokens
        if (top_p := params.get("top_p")) is not None:
            kwargs["top_p"] = top_p

    tools = tools.tools if isinstance(tools, BaseToolkit) else tools or []
    if tools:
        openai_tools = [_convert_tool_to_function_tool_param(tool) for tool in tools]
        kwargs["tools"] = openai_tools

    format = resolve_format(format, default_mode="strict")
    if format is not None:
        raise NotImplementedError("Structured output not yet supported")
    return format, kwargs


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
