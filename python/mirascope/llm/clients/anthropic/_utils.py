"""Anthropic message types and conversion utilities."""

from collections.abc import Sequence

from anthropic import types as anthropic_types

from ...content import (
    AssistantContentPart,
    ContentPart,
    Text,
)
from ...messages import AssistantMessage, UserMessage, assistant
from ...responses import FinishReason

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
) -> tuple[AssistantMessage, FinishReason]:
    """Convert Anthropic message to mirascope AssistantMessage."""
    assistant_message = assistant(
        content=[_decode_assistant_content(part) for part in response.content]
    )
    if response.stop_reason:
        finish_reason = ANTHROPIC_FINISH_REASON_MAP.get(
            response.stop_reason, FinishReason.UNKNOWN
        )
    else:
        finish_reason = FinishReason.UNKNOWN  # pragma: no cover
    return assistant_message, finish_reason
