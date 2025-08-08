"""Anthropic message types and conversion utilities."""

from collections.abc import Sequence

from anthropic import types as anthropic_types
from anthropic.lib.streaming import MessageStreamManager

from ...content import (
    AssistantContentPart,
    ContentPart,
    FinishReasonChunk,
    Text,
    TextChunk,
    TextEndChunk,
    TextStartChunk,
)
from ...messages import AssistantMessage, UserMessage, assistant
from ...responses import ChunkIterator, FinishReason

ANTHROPIC_FINISH_REASON_MAP = {
    "end_turn": FinishReason.END_TURN,
    "max_tokens": FinishReason.MAX_TOKENS,
    "stop_sequence": FinishReason.STOP,
    "tool_use": FinishReason.TOOL_USE,
    "refusal": FinishReason.REFUSAL,
}


def _encode_content(
    content: Sequence[ContentPart],
) -> str | Sequence[anthropic_types.ContentBlock]:
    """Convert mirascope content to Anthropic content format."""
    if len(content) == 1 and content[0].type == "text":
        return content[0].text
    raise NotImplementedError("Only single-content text responses are supported.")


def _decode_assistant_content(
    content: anthropic_types.ContentBlock,
) -> AssistantContentPart:
    """Convert Anthropic content block to mirascope AssistantContentPart."""
    if content.type == "text":
        return Text(text=content.text)
    else:
        raise NotImplementedError(
            f"Support for content type `{content.type}` is not yet implemented."
        )


def encode_messages(
    messages: Sequence[UserMessage | AssistantMessage],
) -> Sequence[anthropic_types.MessageParam]:
    """Convert user or assistant `Message`s to Anthropic `MessageParam` format.

    Args:
        messages: A Sequence containing `UserMessage`s or `AssistantMessage`s

    Returns:
        A Sequence of converted Anthropic `MessageParam`
    """

    return [
        {"role": message.role, "content": _encode_content(message.content)}
        for message in messages
    ]


def decode_response(
    response: anthropic_types.Message,
) -> tuple[AssistantMessage, FinishReason | None]:
    """Convert Anthropic message to mirascope AssistantMessage."""
    assistant_message = assistant(
        content=[_decode_assistant_content(part) for part in response.content]
    )
    finish_reason = (
        ANTHROPIC_FINISH_REASON_MAP.get(response.stop_reason, FinishReason.UNKNOWN)
        if response.stop_reason
        else None
    )
    return assistant_message, finish_reason


def convert_anthropic_stream_to_chunk_iterator(
    anthropic_stream_manager: MessageStreamManager,
) -> ChunkIterator:
    """Returns a ChunkIterator converted from an Anthropic MessageStreamManager"""
    current_block_type: str | None = None

    with anthropic_stream_manager as stream:
        for event in stream._raw_stream:
            if event.type == "content_block_start":
                content_block = event.content_block
                current_block_type = content_block.type

                if content_block.type == "text":
                    yield TextStartChunk(type="text_start_chunk"), event
                else:
                    raise NotImplementedError

            elif event.type == "content_block_delta":
                delta = event.delta
                if delta.type == "text_delta":
                    yield TextChunk(type="text_chunk", delta=delta.text), event
                else:
                    raise NotImplementedError

            elif event.type == "content_block_stop":
                if current_block_type == "text":
                    yield TextEndChunk(type="text_end_chunk"), event
                else:
                    raise NotImplementedError

                current_block_type = None

            elif event.type == "message_delta":
                if event.delta.stop_reason:
                    finish_reason = ANTHROPIC_FINISH_REASON_MAP.get(
                        event.delta.stop_reason, FinishReason.UNKNOWN
                    )
                    yield FinishReasonChunk(finish_reason=finish_reason), event
