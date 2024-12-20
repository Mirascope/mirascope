"""Utility for converting `BaseMessageParam` to `ChatCompletionMessageParam`"""

from cohere.types import ChatMessage

from ...base import BaseMessageParam


def convert_message_params(
    message_params: list[BaseMessageParam | ChatMessage],
) -> list[ChatMessage]:
    converted_message_params = []
    for message_param in message_params:
        if isinstance(message_param, ChatMessage):
            converted_message_params.append(message_param)
        elif isinstance(content := message_param.content, str):
            converted_message_params.append(
                ChatMessage(
                    role=message_param.role.upper(),  # pyright: ignore [reportCallIssue]
                    message=content,
                )
            )
        else:
            # TODO: Add support tool_result
            if len(content) != 1 or content[0].type != "text":
                raise ValueError("Cohere currently only supports text parts.")
            converted_message_params.append(
                ChatMessage(
                    role=message_param.role.upper(),  # pyright: ignore [reportCallIssue]
                    message=content[0].text,
                )
            )
    return converted_message_params
