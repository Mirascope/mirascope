"""Anthropic message types and conversion utilities."""

import logging
from collections.abc import Sequence
from typing import TypeAlias

from anthropic import types as anthropic_types

from ...content import (
    AssistantContentPart,
    ContentPart,
    Text,
)
from ...messages import AssistantMessage, Message, assistant
from ...responses import FinishReason
from ..base.converter import BaseConverter

AnthropicMessageParam: TypeAlias = anthropic_types.MessageParam
AnthropicSystemMessage: TypeAlias = str | None

AnthropicMessage: TypeAlias = anthropic_types.Message

ANTHROPIC_FINISH_REASON_MAP = {
    "end_turn": FinishReason.END_TURN,
    "max_tokens": FinishReason.MAX_TOKENS,
    "stop_sequence": FinishReason.STOP,
    "tool_use": FinishReason.TOOL_USE,
    "refusal": FinishReason.REFUSAL,
}


class AnthropicConverter(
    BaseConverter[
        str | Sequence[anthropic_types.ContentBlock],  # ProviderContentT
        tuple[
            AnthropicSystemMessage, list[AnthropicMessageParam]
        ],  # ProviderMessagesInputT
        AnthropicMessage,  # ProviderMessageResponseT
        anthropic_types.ContentBlock,  # ProviderContentBlockT
        anthropic_types.StopReason,  # ProviderFinishReasonT
    ]
):
    """Converter for Anthropic message formats."""

    @classmethod
    def encode_content(
        cls, content: Sequence[ContentPart]
    ) -> str | Sequence[anthropic_types.ContentBlock]:
        """Convert mirascope content to Anthropic content format."""
        if len(content) == 1 and content[0].type == "text":
            return content[0].text
        result = []
        for item in content:
            if item.type == "text":
                result.append(anthropic_types.TextBlock(text=item.text, type="text"))
            else:
                raise NotImplementedError(
                    f"Have not implemented conversion for ${item.type}"
                )
        return result

    @classmethod
    def encode_messages(
        cls, messages: Sequence[Message]
    ) -> tuple[AnthropicSystemMessage, list[AnthropicMessageParam]]:
        """Convert messages to Anthropic MessageParam format.

        Args:
            messages: Sequence of messages to convert

        Returns:
            Tuple of (system_message, user_or_assistant_messages)
        """
        system_message: AnthropicSystemMessage = None
        converted_messages: list[AnthropicMessageParam] = []
        for i, message in enumerate(messages):
            if message.role != "system":
                converted_messages.append(
                    {
                        "role": message.role,
                        "content": cls.encode_content(message.content),
                    }
                )
            elif i == 0:
                system_message = message.content.text
            else:
                logging.warning(
                    "Non-first system message at index %d is being skipped", i
                )
        return system_message, converted_messages

    @classmethod
    def decode_assistant_message(cls, message: AnthropicMessage) -> AssistantMessage:
        """Convert Anthropic message to mirascope AssistantMessage."""
        return assistant(
            content=[cls.decode_assistant_content(part) for part in message.content]
        )

    @classmethod
    def decode_assistant_content(
        cls, content: anthropic_types.ContentBlock
    ) -> AssistantContentPart:
        """Convert Anthropic content block to mirascope AssistantContentPart."""
        if content.type == "text":
            return Text(text=content.text)
        else:
            raise NotImplementedError(
                f"Support for content type `{content.type}` is not yet implemented."
            )

    @classmethod
    def decode_finish_reason(
        cls, reason: anthropic_types.StopReason | None
    ) -> FinishReason:
        """Convert Anthropic stop reason to mirascope FinishReason."""
        if reason is None:
            return FinishReason.UNKNOWN
        return ANTHROPIC_FINISH_REASON_MAP.get(reason, FinishReason.UNKNOWN)
