"""Utility for converting `BaseMessageParam` to `ChatMessage`."""

from mistralai.models import (
    AssistantMessage,
    SystemMessage,
    ToolMessage,
    UserMessage,
)

from ...base import BaseMessageParam


def convert_message_params(
    message_params: list[
        BaseMessageParam | AssistantMessage | SystemMessage | ToolMessage | UserMessage
    ],
) -> list[BaseMessageParam]:
    converted_message_params = []
    for message_param in message_params:
        if not isinstance(
            message_param,
            BaseMessageParam,
        ):
            converted_message_params.append(message_param)
        elif isinstance(content := message_param.content, str):
            converted_message_params.append(
                BaseMessageParam(**message_param.model_dump())
            )
        else:
            if len(content) != 1 or content[0].type != "text":
                raise ValueError("Mistral currently only supports text parts.")
            converted_message_params.append(
                BaseMessageParam(role=message_param.role, content=content[0].text)
            )
    return converted_message_params
