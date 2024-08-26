"""Utility for converting `BaseMessageParam` to `ChatMessage`."""

from mistralai.models.chat_completion import ChatMessage

from ...base import BaseMessageParam


def convert_message_params(
    message_params: list[BaseMessageParam | ChatMessage],
) -> list[ChatMessage]:
    converted_message_params = []
    for message_param in message_params:
        if isinstance(message_param, ChatMessage):
            converted_message_params.append(message_param)
        elif isinstance(content := message_param.content, str):
            converted_message_params.append(ChatMessage(**message_param.model_dump()))
        else:
            if len(content) != 1 or content[0].type != "text":
                raise ValueError("Mistral currently only supports text parts.")
            converted_message_params.append(
                ChatMessage(role=message_param.role, content=content[0].text)
            )
    return converted_message_params
