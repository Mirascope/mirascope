"""Utility for converting `BaseMessageParam` to `ChatCompletionMessageParam`"""

from groq.types.chat import ChatCompletionMessageParam

from ...base import BaseMessageParam


def convert_message_params(
    message_params: list[BaseMessageParam | ChatCompletionMessageParam],
) -> list[ChatCompletionMessageParam]:
    converted_message_params = []
    for message_param in message_params:
        if not isinstance(message_param, BaseMessageParam):
            converted_message_params.append(message_param)
        elif isinstance(content := message_param.content, str):
            converted_message_params.append(message_param.model_dump())
        else:
            if len(content) != 1 or content[0].type != "text":
                raise ValueError("Groq does not currently support multimodalities.")
            converted_message_params.append(
                {"role": message_param.role, "content": content[0].text}
            )
    return converted_message_params
