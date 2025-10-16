"""OpenAI message types and conversion utilities."""

import logging
from collections.abc import Sequence
from functools import lru_cache
from typing import Literal

from openai import AsyncStream, NotGiven, Stream
from openai.types import chat as openai_types, shared_params as shared_openai_types
from openai.types.shared_params.response_format_json_schema import JSONSchema

from ....content import (
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
from ....exceptions import FormattingModeNotSupportedError
from ....formatting import (
    Format,
    FormattableT,
    _utils as _formatting_utils,
    resolve_format,
)
from ....messages import AssistantMessage, Message, UserMessage
from ....responses import (
    AsyncChunkIterator,
    ChunkIterator,
    FinishReason,
    FinishReasonChunk,
    RawStreamEventChunk,
)
from ....tools import FORMAT_TOOL_NAME, BaseToolkit, ToolSchema
from ...base import BaseKwargs, Params, _utils as _base_utils
from ..shared import (
    _utils as _shared_utils,
)
from .model_ids import OpenAICompletionsModelId

logger = logging.getLogger(__name__)

OPENAI_FINISH_REASON_MAP = {
    "length": FinishReason.MAX_TOKENS,
    "content_filter": FinishReason.REFUSAL,
}


class ChatCompletionCreateKwargs(BaseKwargs, total=False):
    """Kwargs for OpenAI ChatCompletion.create method."""

    model: str
    messages: Sequence[openai_types.ChatCompletionMessageParam]
    tools: Sequence[openai_types.ChatCompletionToolParam] | NotGiven
    response_format: (
        shared_openai_types.ResponseFormatJSONObject
        | shared_openai_types.ResponseFormatJSONSchema
        | NotGiven
    )
    tool_choice: openai_types.ChatCompletionToolChoiceOptionParam | NotGiven
    parallel_tool_calls: bool | NotGiven
    temperature: float | NotGiven
    max_tokens: int | NotGiven
    top_p: float | NotGiven
    seed: int | NotGiven
    stop: str | list[str] | NotGiven
    reasoning_effort: shared_openai_types.ReasoningEffort | NotGiven


def _encode_user_message(
    message: UserMessage,
) -> list[openai_types.ChatCompletionMessageParam]:
    """Convert Mirascope `UserMessage` to a list of OpenAI `ChatCompletionMessageParam`."""

    message_params: list[openai_types.ChatCompletionMessageParam] = []
    for part in message.content:
        if part.type == "text":
            message_params.append(
                openai_types.ChatCompletionUserMessageParam(
                    role="user",
                    content=part.text,
                )
            )
        elif part.type == "tool_output":
            message_params.append(
                openai_types.ChatCompletionToolMessageParam(
                    role="tool",
                    content=str(part.value),
                    tool_call_id=part.id,
                )
            )
        else:
            raise NotImplementedError

    return message_params


def _encode_assistant_message(
    message: AssistantMessage, encode_thoughts: bool
) -> openai_types.ChatCompletionAssistantMessageParam:
    """Convert Mirascope `AssistantMessage` to OpenAI `ChatCompletionAssistantMessageParam`."""

    text_params: list[openai_types.ChatCompletionContentPartTextParam] = []
    tool_call_params: list[openai_types.ChatCompletionMessageToolCallParam] = []
    for part in message.content:
        if part.type == "text":
            text_params.append(
                openai_types.ChatCompletionContentPartTextParam(
                    text=part.text, type="text"
                )
            )
        elif part.type == "tool_call":
            tool_call_params.append(
                openai_types.ChatCompletionMessageToolCallParam(
                    id=part.id,
                    type="function",
                    function={"name": part.name, "arguments": part.args},
                )
            )
        elif part.type == "thought" and encode_thoughts:
            text_params.append(
                openai_types.ChatCompletionContentPartTextParam(
                    text="**Thinking:** " + part.thought, type="text"
                )
            )
        else:
            raise NotImplementedError

    content: str | list[openai_types.ChatCompletionContentPartTextParam] | None = None
    if len(text_params) == 1:
        content = text_params[0]["text"]
    elif text_params:
        content = text_params

    message_params = {
        "role": "assistant",
        "content": content,
    }
    if tool_call_params:
        message_params["tool_calls"] = tool_call_params

    return openai_types.ChatCompletionAssistantMessageParam(**message_params)


def _encode_message(
    message: Message, encode_thoughts: bool
) -> list[openai_types.ChatCompletionMessageParam]:
    """Convert a Mirascope `Message` to OpenAI `ChatCompletionMessageParam` format.

    Args:
        message: A Mirascope message (system, user, or assistant)

    Returns:
        A list of OpenAI `ChatCompletionMessageParam` (may be multiple for tool outputs)
    """
    if message.role == "system":
        return [
            openai_types.ChatCompletionSystemMessageParam(
                role="system", content=message.content.text
            )
        ]
    elif message.role == "user":
        return _encode_user_message(message)
    elif message.role == "assistant":
        return [_encode_assistant_message(message, encode_thoughts)]
    else:
        raise ValueError(f"Unsupported role: {message.role}")  # pragma: no cover


@lru_cache(maxsize=128)
def _convert_tool_to_tool_param(
    tool: ToolSchema,
) -> openai_types.ChatCompletionToolParam:
    """Convert a single Mirascope `Tool` to OpenAI ChatCompletionToolParam with caching."""
    schema_dict = tool.parameters.model_dump(by_alias=True, exclude_none=True)
    schema_dict["type"] = "object"
    _shared_utils._ensure_additional_properties_false(schema_dict)
    return openai_types.ChatCompletionToolParam(
        type="function",
        function={
            "name": tool.name,
            "description": tool.description,
            "parameters": schema_dict,
            "strict": tool.strict,
        },
    )


def _create_strict_response_format(
    format: Format[FormattableT],
) -> shared_openai_types.ResponseFormatJSONSchema:
    """Create OpenAI strict response format from a Mirascope Format.

    Args:
        format: The `Format` instance containing schema and metadata

    Returns:
        Dictionary containing OpenAI response_format specification
    """
    schema = format.schema.copy()

    _shared_utils._ensure_additional_properties_false(schema)

    json_schema = JSONSchema(
        name=format.name,
        schema=schema,
        strict=True,
    )
    if format.description:
        json_schema["description"] = format.description

    return shared_openai_types.ResponseFormatJSONSchema(
        type="json_schema", json_schema=json_schema
    )


def prepare_completions_request(
    *,
    model_id: OpenAICompletionsModelId,
    messages: Sequence[Message],
    tools: Sequence[ToolSchema] | BaseToolkit | None,
    format: type[FormattableT] | Format[FormattableT] | None,
    params: Params,
) -> tuple[Sequence[Message], Format[FormattableT] | None, ChatCompletionCreateKwargs]:
    """Prepares a request for the `OpenAI.chat.completions.create` method."""
    kwargs: ChatCompletionCreateKwargs = {
        "model": model_id,
    }
    encode_thoughts = False

    with _base_utils.ensure_all_params_accessed(
        params=params,
        provider="openai:completions",
        unsupported_params=["top_k", "thinking"],
    ) as param_accessor:
        if param_accessor.temperature is not None:
            kwargs["temperature"] = param_accessor.temperature
        if param_accessor.max_tokens is not None:
            kwargs["max_tokens"] = param_accessor.max_tokens
        if param_accessor.top_p is not None:
            kwargs["top_p"] = param_accessor.top_p

        if param_accessor.seed is not None:
            kwargs["seed"] = param_accessor.seed
        if param_accessor.stop_sequences is not None:
            kwargs["stop"] = param_accessor.stop_sequences
        if param_accessor.encode_thoughts_as_text is not None:
            encode_thoughts = True

    tools = tools.tools if isinstance(tools, BaseToolkit) else tools or []

    openai_tools = [_convert_tool_to_tool_param(tool) for tool in tools]

    model_supports_strict = (
        model_id not in _shared_utils.MODELS_WITHOUT_JSON_SCHEMA_SUPPORT
    )
    default_mode = "strict" if model_supports_strict else "tool"
    format = resolve_format(format, default_mode=default_mode)
    if format is not None:
        if format.mode == "strict":
            if not model_supports_strict:
                raise FormattingModeNotSupportedError(
                    formatting_mode="strict",
                    provider="openai:completions",
                    model_id=model_id,
                )
            kwargs["response_format"] = _create_strict_response_format(format)
        elif format.mode == "tool":
            if tools:
                kwargs["tool_choice"] = "required"
            else:
                kwargs["tool_choice"] = {
                    "type": "function",
                    "function": {"name": FORMAT_TOOL_NAME},
                }
                kwargs["parallel_tool_calls"] = False
            format_tool_schema = _formatting_utils.create_tool_schema(format)
            openai_tools.append(_convert_tool_to_tool_param(format_tool_schema))
        elif (
            format.mode == "json"
            and model_id not in _shared_utils.MODELS_WITHOUT_JSON_OBJECT_SUPPORT
        ):
            kwargs["response_format"] = {"type": "json_object"}

        if format.formatting_instructions:
            messages = _base_utils.add_system_instructions(
                messages, format.formatting_instructions
            )

    if openai_tools:
        kwargs["tools"] = openai_tools

    encoded_messages: list[openai_types.ChatCompletionMessageParam] = []
    for message in messages:
        encoded_messages.extend(_encode_message(message, encode_thoughts))
    kwargs["messages"] = encoded_messages

    return messages, format, kwargs


def decode_response(
    response: openai_types.ChatCompletion,
    model_id: OpenAICompletionsModelId,
) -> tuple[AssistantMessage, FinishReason | None]:
    """Convert OpenAI ChatCompletion to mirascope AssistantMessage."""
    choice = response.choices[0]
    message = choice.message
    refused = False

    parts: list[AssistantContentPart] = []
    if message.content:
        parts.append(Text(text=message.content))
    if message.refusal:
        parts.append(Text(text=message.refusal))
        refused = True
    if message.tool_calls:
        for tool_call in message.tool_calls:
            if tool_call.type == "custom":
                # This should never happen, because we never create "custom" tools
                # https://platform.openai.com/docs/guides/function-calling#custom-tools
                raise NotImplementedError("OpenAI custom tools are not supported.")
            parts.append(
                ToolCall(
                    id=tool_call.id,
                    name=tool_call.function.name,
                    args=tool_call.function.arguments,
                )
            )

    finish_reason = (
        FinishReason.REFUSAL
        if refused
        else OPENAI_FINISH_REASON_MAP.get(choice.finish_reason)
    )

    assistant_message = AssistantMessage(
        content=parts,
        provider="openai:completions",
        model_id=model_id,
        raw_content=[],
    )

    return assistant_message, finish_reason


class _OpenAIChunkProcessor:
    """Processes OpenAI chat completion chunks and maintains state across chunks."""

    def __init__(self) -> None:
        self.current_content_type: Literal["text", "tool_call"] | None = None
        self.current_tool_index: int | None = None
        self.refusal_encountered = False

    def process_chunk(self, chunk: openai_types.ChatCompletionChunk) -> ChunkIterator:
        """Process a single OpenAI chunk and yield the appropriate content chunks."""
        yield RawStreamEventChunk(raw_stream_event=chunk)

        choice = chunk.choices[0] if chunk.choices else None
        if not choice:
            return  # pragma: no cover

        delta = choice.delta

        content = delta.content or delta.refusal
        if delta.refusal:
            self.refusal_encountered = True
        if content is not None:
            if self.current_content_type is None:
                yield TextStartChunk()
                self.current_content_type = "text"
            yield TextChunk(delta=content)

        if delta.tool_calls:
            if self.current_content_type == "text":
                # In testing, I can't get OpenAI to emit text and tool calls in the same chunk
                # But we handle this defensively.
                yield TextEndChunk()  # pragma: no cover
            self.current_content_type = "tool_call"

            for tool_call_delta in delta.tool_calls:
                index = tool_call_delta.index

                if (
                    self.current_tool_index is not None
                    and self.current_tool_index > index
                ):
                    raise RuntimeError(
                        f"Received tool data for already-finished tool at index {index}"
                    )  # pragma: no cover

                if (
                    self.current_tool_index is not None
                    and self.current_tool_index < index
                ):
                    yield ToolCallEndChunk()
                    self.current_tool_index = None

                if self.current_tool_index is None:
                    if not tool_call_delta.function or not (
                        name := tool_call_delta.function.name
                    ):
                        raise RuntimeError(
                            f"Missing name for tool call at index {index}"
                        )  # pragma: no cover

                    self.current_tool_index = index
                    if not (tool_id := tool_call_delta.id):
                        raise RuntimeError(
                            f"Missing id for tool call at index {index}"
                        )  # pragma: no cover

                    yield ToolCallStartChunk(
                        id=tool_id,
                        name=name,
                    )

                if tool_call_delta.function and tool_call_delta.function.arguments:
                    yield ToolCallChunk(delta=tool_call_delta.function.arguments)

        if choice.finish_reason:
            if self.current_content_type == "text":
                yield TextEndChunk()
            elif self.current_content_type == "tool_call":
                yield ToolCallEndChunk()
            elif self.current_content_type is not None:  # pragma: no cover
                raise NotImplementedError()

            finish_reason = (
                FinishReason.REFUSAL
                if self.refusal_encountered
                else OPENAI_FINISH_REASON_MAP.get(choice.finish_reason)
            )
            if finish_reason is not None:
                yield FinishReasonChunk(finish_reason=finish_reason)


def convert_openai_stream_to_chunk_iterator(
    openai_stream: Stream[openai_types.ChatCompletionChunk],
) -> ChunkIterator:
    """Returns a ChunkIterator converted from an OpenAI Stream[ChatCompletionChunk]"""
    processor = _OpenAIChunkProcessor()
    for chunk in openai_stream:
        yield from processor.process_chunk(chunk)


async def convert_openai_stream_to_async_chunk_iterator(
    openai_stream: AsyncStream[openai_types.ChatCompletionChunk],
) -> AsyncChunkIterator:
    """Returns an AsyncChunkIterator converted from an OpenAI AsyncStream[ChatCompletionChunk]"""
    processor = _OpenAIChunkProcessor()
    async for chunk in openai_stream:
        for item in processor.process_chunk(chunk):
            yield item
