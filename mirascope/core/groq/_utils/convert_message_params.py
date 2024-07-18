"""Utility for converting `BaseMessageParam` to `ChatCompletionMessageParam`"""

from groq.types.chat import ChatCompletionMessageParam

from ...base import BaseMessageParam


def convert_message_params(
    message_params: list[BaseMessageParam],
) -> list[ChatCompletionMessageParam]:
    converted_message_params = []
    for message_param in message_params:
        content = message_param["content"]
        if len(content) != 1 or content[0]["type"] != "text":
            raise ValueError("Groq does not currently support multimodalities.")
        converted_message_params.append(
            {"role": message_param["role"], "content": content[0]["text"]}
        )
    return converted_message_params
