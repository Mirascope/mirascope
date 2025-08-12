"""OpenAI message types and conversion utilities."""

from collections.abc import Sequence
from functools import lru_cache
from typing import Literal

from openai import NotGiven, Stream
from openai.types import chat as openai_types

from ...content import (
    AssistantContentPart,
    FinishReasonChunk,
    Text,
    TextChunk,
    TextEndChunk,
    TextStartChunk,
    ToolCall,
    ToolCallChunk,
    ToolCallEndChunk,
    ToolCallStartChunk,
)
from ...messages import AssistantMessage, Message, UserMessage
from ...responses import ChunkIterator, FinishReason
from ...tools import Tool

OPENAI_FINISH_REASON_MAP = {
    "stop": FinishReason.END_TURN,
    "length": FinishReason.MAX_TOKENS,
    "content_filter": FinishReason.REFUSAL,
    "tool_calls": FinishReason.TOOL_USE,
    "function_call": FinishReason.TOOL_USE,
}


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
    message: AssistantMessage,
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


def _encode_message(message: Message) -> list[openai_types.ChatCompletionMessageParam]:
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
        return [_encode_assistant_message(message)]
    else:
        raise ValueError(f"Unsupported role: {message.role}")  # pragma: no cover


def _decode_assistant_message(
    message: openai_types.ChatCompletionMessage,
) -> AssistantMessage:
    parts: list[AssistantContentPart] = []
    if message.content:
        parts.append(Text(text=message.content))
    if message.tool_calls:
        for tool_call in message.tool_calls:
            parts.append(
                ToolCall(
                    id=tool_call.id,
                    name=tool_call.function.name,
                    args=tool_call.function.arguments,
                )
            )

    return AssistantMessage(content=parts)


@lru_cache(maxsize=128)
def _convert_tool_to_tool_param(tool: Tool) -> openai_types.ChatCompletionToolParam:
    """Convert a single Mirascope `Tool` to OpenAI ChatCompletionToolParam with caching."""
    schema_dict = tool.parameters.model_dump(by_alias=True, exclude_none=True)
    schema_dict["type"] = "object"
    return openai_types.ChatCompletionToolParam(
        type="function",
        function={
            "name": tool.name,
            "description": tool.description,
            "parameters": schema_dict,
            "strict": tool.strict,
        },
    )


def prepare_openai_request(
    messages: Sequence[Message],
    tools: Sequence[Tool] | None = None,
) -> tuple[
    Sequence[openai_types.ChatCompletionMessageParam],
    Sequence[openai_types.ChatCompletionToolParam] | NotGiven,
]:
    """Prepare OpenAI API request parameters."""
    openai_tools = (
        [_convert_tool_to_tool_param(tool) for tool in tools] if tools else NotGiven()
    )

    encoded_messages: list[openai_types.ChatCompletionMessageParam] = []
    for message in messages:
        encoded_messages.extend(_encode_message(message))

    return (
        encoded_messages,
        openai_tools,
    )


def decode_response(
    response: openai_types.ChatCompletion,
) -> tuple[AssistantMessage, FinishReason]:
    """Convert OpenAI ChatCompletion to mirascope AssistantMessage."""
    choice = response.choices[0]
    assistant_message = _decode_assistant_message(choice.message)
    finish_reason = OPENAI_FINISH_REASON_MAP.get(
        choice.finish_reason, FinishReason.UNKNOWN
    )
    return assistant_message, finish_reason


def convert_openai_stream_to_chunk_iterator(
    openai_stream: Stream[openai_types.ChatCompletionChunk],
) -> ChunkIterator:
    """Returns a ChunkIterator converted from an OpenAI Stream[ChatCompletionChunk]"""
    current_content_type: Literal["text", "tool_call"] | None = None
    current_tool_index: int | None = None

    for chunk in openai_stream:
        choice = chunk.choices[0] if chunk.choices else None
        if not choice:
            continue  # pragma: no cover

        delta = choice.delta

        if delta.content is not None:
            if current_content_type is None:
                yield TextStartChunk(type="text_start_chunk"), chunk
                current_content_type = "text"
            elif current_content_type == "tool_call":
                raise RuntimeError(
                    "received text delta inside tool call"
                )  # pragma: no cover
            elif current_content_type != "text":
                raise NotImplementedError

            yield TextChunk(type="text_chunk", delta=delta.content), chunk

        if delta.tool_calls:
            if current_content_type == "text":
                # In testing, I can't get OpenAI to emit text and tool calls in the same chunk
                # But we handle this defensively.
                yield TextEndChunk(type="text_end_chunk"), chunk  # pragma: no cover
            elif current_content_type and current_content_type != "tool_call":
                raise RuntimeError(
                    f"Unexpected current_content_type: {current_content_type}"
                )  # pragma: no cover
            current_content_type = "tool_call"

            for tool_call_delta in delta.tool_calls:
                index = tool_call_delta.index

                if current_tool_index is None or current_tool_index < index:
                    if current_tool_index is not None:
                        yield (
                            ToolCallEndChunk(
                                type="tool_call_end_chunk",
                                content_type="tool_call",
                            ),
                            chunk,
                        )

                    if (
                        not tool_call_delta.function
                        or not tool_call_delta.function.name
                    ):
                        raise RuntimeError(
                            f"Missing name for tool call at index {index}"
                        )  # pragma: no cover

                    current_tool_index = index
                    name = tool_call_delta.function.name
                    tool_id = tool_call_delta.id or name

                    yield (
                        ToolCallStartChunk(
                            type="tool_call_start_chunk",
                            id=tool_id,
                            name=name,
                        ),
                        chunk,
                    )

                if current_tool_index > index:
                    raise RuntimeError(
                        f"Received tool data for already-finished tool at index {index}"
                    )  # pragma: no cover

                if tool_call_delta.function and tool_call_delta.function.arguments:
                    yield (
                        ToolCallChunk(
                            type="tool_call_chunk",
                            delta=tool_call_delta.function.arguments,
                        ),
                        chunk,
                    )

        if choice.finish_reason:
            if current_content_type == "text":
                yield TextEndChunk(type="text_end_chunk"), chunk
                current_content_type = None
            elif current_content_type == "tool_call":
                yield (
                    ToolCallEndChunk(
                        type="tool_call_end_chunk",
                        content_type="tool_call",
                    ),
                    chunk,
                )
            else:
                raise NotImplementedError

            finish_reason = OPENAI_FINISH_REASON_MAP.get(
                choice.finish_reason, FinishReason.UNKNOWN
            )
            yield FinishReasonChunk(finish_reason=finish_reason), chunk
