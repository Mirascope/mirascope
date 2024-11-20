"""Utility for converting `BaseMessageParam` to `ChatMessage`."""

from mistralai.models import (
    AssistantMessage,
    SystemMessage,
    ToolMessage,
    UserMessage,
)

from ...base import BaseMessageParam


def make_message(
    role: str,
    **kwargs,  # noqa: ANN003
) -> AssistantMessage | SystemMessage | ToolMessage | UserMessage:
    if role == "assistant":
        return AssistantMessage(**kwargs)
    elif role == "system":
        return SystemMessage(**kwargs)
    elif role == "tool":
        return ToolMessage(**kwargs)
    elif role == "user":
        return UserMessage(**kwargs)
    raise ValueError(f"Invalid role: {role}")


def convert_message_params(
    message_params: list[
        BaseMessageParam | AssistantMessage | SystemMessage | ToolMessage | UserMessage
    ],
) -> list[AssistantMessage | SystemMessage | ToolMessage | UserMessage]:
    converted_message_params = []
    for message_param in message_params:
        if not isinstance(message_param, BaseMessageParam):
            converted_message_params.append(message_param)
        elif isinstance(content := message_param.content, str):
            converted_message_params.append(make_message(**message_param.model_dump()))
        else:
            if len(content) != 1 or content[0].type != "text":
                raise ValueError("Mistral currently only supports text parts.")
            converted_message_params.append(
                make_message(role=message_param.role, content=content[0].text)
            )
    return converted_message_params
