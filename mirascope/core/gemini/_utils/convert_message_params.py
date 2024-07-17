"""Utility for converting `BaseMessageParam` to `ContentsType`"""

import io

import PIL.Image
from google.generativeai.types import ContentsType

from ...base import BaseMessageParam


def convert_message_params(
    message_params: list[BaseMessageParam],
) -> list[ContentsType]:
    converted_message_params = []
    for message_param in message_params:
        if (role := message_param["role"]) == "system":
            content = message_param["content"]
            if len(content) != 1 or content[0]["type"] != "text":
                raise ValueError("System message must have a single text part.")
            converted_message_params += [
                {
                    "role": "user",
                    "parts": [content[0]["text"]],
                },
                {
                    "role": "model",
                    "parts": ["Ok! I will adhere to this system message."],
                },
            ]
        else:
            content = message_param["content"]
            converted_content = []
            for part in content:
                if part["type"] == "image":
                    image = PIL.Image.open(io.BytesIO(part["image"]))
                    converted_content.append(image)
                else:
                    converted_content.append(part["text"])
            converted_message_params.append({"role": role, "parts": converted_content})
            converted_message_params.append(
                {"role": message_param["role"], "parts": converted_content}
            )
    return converted_message_params
