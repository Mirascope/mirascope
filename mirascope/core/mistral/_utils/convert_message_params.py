"""Utility for converting `BaseMessageParam` to `ChatMessage`."""

from mistralai.models.chat_completion import ChatMessage

from ...base import BaseMessageParam


def convert_message_params(
    message_params: list[BaseMessageParam],
) -> list[ChatMessage]:
    converted_message_params = []
    for message_param in message_params:
        content = message_param["content"]
        if len(content) != 1 or content[0]["type"] != "text":
            raise ValueError("Mistral does not currently support multimodalities.")
        converted_message_params.append(
            ChatMessage(role=message_param["role"], content=content[0]["text"])
        )
    return converted_message_params
