"""OpenAI message types and conversion utilities."""

import json
from collections.abc import Sequence
from typing import Literal

from openai import NotGiven, Stream
from openai.types.chat import (
    ChatCompletion,
    ChatCompletionAssistantMessageParam,
    ChatCompletionChunk,
    ChatCompletionContentPartTextParam,
    ChatCompletionMessageParam,
    ChatCompletionMessageToolCallParam,
    ChatCompletionSystemMessageParam,
    ChatCompletionToolMessageParam,
    ChatCompletionToolParam,
    ChatCompletionUserMessageParam,
)

from ...content import (
    AssistantContentPart,
    FinishReasonChunk,
    Text,
    TextChunk,
    TextEndChunk,
    TextStartChunk,
    ToolCall,
    UserContentPart,
)
from ...messages import AssistantMessage, Message, assistant
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
    content: Sequence[UserContentPart],
) -> list[ChatCompletionMessageParam]:
    """Convert mirascope user message content to OpenAI message format."""
    messages: list[ChatCompletionMessageParam] = []

    for part in content:
        if part.type == "tool_output":
            messages.append(
                ChatCompletionToolMessageParam(
                    role="tool",
                    content=str(part.value),
                    tool_call_id=part.id,
                )
            )
        elif part.type == "text":
            messages.append(
                ChatCompletionUserMessageParam(
                    role="user",
                    content=[
                        ChatCompletionContentPartTextParam(type="text", text=part.text)
                    ],
                )
            )
        else:
            raise NotImplementedError

    return messages


def _encode_assistant_message(
    content: Sequence[AssistantContentPart],
) -> ChatCompletionAssistantMessageParam:
    """Convert mirascope assistant message content to OpenAI message format."""
    text_parts = [part for part in content if part.type == "text"]
    tool_calls: list[ChatCompletionMessageToolCallParam] = []

    for part in content:
        if part.type == "tool_call":
            tool_calls.append(
                ChatCompletionMessageToolCallParam(
                    id=part.id,
                    type="function",
                    function={
                        "name": part.name,
                        "arguments": json.dumps(part.args),
                    },
                )
            )

    content_parts = [
        ChatCompletionContentPartTextParam(type="text", text=part.text)
        for part in text_parts
    ]

    message_params = {
        "role": "assistant",
        "content": content_parts if content_parts else None,
    }
    if tool_calls:
        message_params["tool_calls"] = tool_calls

    return ChatCompletionAssistantMessageParam(**message_params)


def _decode_assistant_content(
    content: str | None,
    tool_calls: list | None = None,
) -> list[AssistantContentPart]:
    """Convert OpenAI content to mirascope AssistantContentPart list."""
    parts = []

    if content:
        parts.append(Text(text=content))

    if tool_calls:
        for tool_call in tool_calls:
            parts.append(
                ToolCall(
                    id=tool_call.id,
                    name=tool_call.function.name,
                    # TODO: Consider whether we want to do any validation here
                    args=json.loads(tool_call.function.arguments),
                )
            )

    return parts or [Text(text="")]


def _encode_message(message: Message) -> list[ChatCompletionMessageParam]:
    """Convert a Mirascope `Message` to OpenAI `ChatCompletionMessageParam` format.

    Args:
        message: A Mirascope message (system, user, or assistant)

    Returns:
        A list of OpenAI `ChatCompletionMessageParam` (may be multiple for tool outputs)
    """
    if message.role == "system":
        return [
            ChatCompletionSystemMessageParam(
                role="system", content=message.content.text
            )
        ]
    elif message.role == "user":
        return _encode_user_message(message.content)
    elif message.role == "assistant":
        return [_encode_assistant_message(message.content)]
    else:
        raise ValueError(f"Unsupported role: {message.role}")  # pragma: no cover


def _convert_tools_to_openai(
    tools: Sequence[Tool],
) -> Sequence[ChatCompletionToolParam]:
    """Convert Mirascope tools to OpenAI tool format."""
    openai_tools: list[ChatCompletionToolParam] = []

    for tool in tools:
        # TODO: Add caching for performance
        schema_dict = tool.parameters.model_dump(by_alias=True, exclude_none=True)

        openai_tool = ChatCompletionToolParam(
            type="function",
            function={
                "name": tool.name,
                "description": tool.description,
                "parameters": schema_dict,
                "strict": tool.strict,
            },
        )
        openai_tools.append(openai_tool)

    return openai_tools


def prepare_openai_request(
    messages: Sequence[Message],
    tools: Sequence[Tool] | None = None,
) -> tuple[
    Sequence[ChatCompletionMessageParam],
    Sequence[ChatCompletionToolParam] | NotGiven,
]:
    """Prepare OpenAI API request parameters."""
    openai_tools = _convert_tools_to_openai(tools) if tools else NotGiven()

    # Flatten the message list since _encode_message can return multiple messages
    encoded_messages: list[ChatCompletionMessageParam] = []
    for message in messages:
        encoded_messages.extend(_encode_message(message))

    return (
        encoded_messages,
        openai_tools,
    )


def decode_response(response: ChatCompletion) -> tuple[AssistantMessage, FinishReason]:
    """Convert OpenAI ChatCompletion to mirascope AssistantMessage."""
    choice = response.choices[0]
    assistant_message = assistant(
        content=_decode_assistant_content(
            choice.message.content,
            choice.message.tool_calls,
        )
    )
    finish_reason = OPENAI_FINISH_REASON_MAP.get(
        choice.finish_reason, FinishReason.UNKNOWN
    )
    return assistant_message, finish_reason


def convert_openai_stream_to_chunk_iterator(
    openai_stream: Stream[ChatCompletionChunk],
) -> ChunkIterator:
    """Returns a ChunkIterator converted from an OpenAI Stream[ChatCompletionChunk]"""
    current_content_type: Literal["text"] | None = None

    for chunk in openai_stream:
        choice = chunk.choices[0] if chunk.choices else None
        if not choice:
            continue  # pragma: no cover

        delta = choice.delta

        if delta.content is not None:
            if current_content_type is None:
                yield TextStartChunk(type="text_start_chunk"), chunk
                current_content_type = "text"
            elif current_content_type != "text":
                raise NotImplementedError

            yield TextChunk(type="text_chunk", delta=delta.content), chunk

        if choice.finish_reason:
            if current_content_type == "text":
                yield TextEndChunk(type="text_end_chunk"), chunk
                current_content_type = None
            else:
                raise NotImplementedError

            finish_reason = OPENAI_FINISH_REASON_MAP.get(
                choice.finish_reason, FinishReason.UNKNOWN
            )
            yield FinishReasonChunk(finish_reason=finish_reason), chunk
