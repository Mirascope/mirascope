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
                raise ValueError(
                    "System message must have a single text part."
                )  # pragma: no cover
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
                if part["type"] == "text":
                    converted_content.append(part["text"])
                elif part["type"] == "image":
                    if part["media_type"] not in [
                        "image/jpeg",
                        "image/png",
                        "image/webp",
                        "image/heic",
                        "image/heif",
                    ]:
                        raise ValueError(
                            f"Unsupported image media type: {part['media_type']}. "
                            "Gemini currently only supports JPEG, PNG, WebP, HEIC, "
                            "and HEIF images."
                        )
                    image = PIL.Image.open(io.BytesIO(part["image"]))
                    converted_content.append(image)
                else:
                    if part["media_type"] not in [
                        "audio/wav",
                        "audio/mp3",
                        "audio/aiff",
                        "audio/aac",
                        "audio/ogg",
                        "audio/flac",
                    ]:
                        raise ValueError(
                            f"Unsupported audio media type: {part['media_type']}. "
                            "Gemini currently only supports WAV, MP3, AIFF, AAC, OGG, "
                            "and FLAC audio file types."
                        )
                    converted_content.append(
                        {"mime_type": part["media_type"], "data": part["audio"]}
                    )
            converted_message_params.append({"role": role, "parts": converted_content})
    return converted_message_params
