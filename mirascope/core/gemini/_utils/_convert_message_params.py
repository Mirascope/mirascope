"""Utility for converting `BaseMessageParam` to `ContentsType`"""

import io

import PIL.Image
from google.generativeai.types import ContentDict

from ...base import BaseMessageParam


def convert_message_params(
    message_params: list[BaseMessageParam | ContentDict],
) -> list[ContentDict]:
    converted_message_params = []
    for message_param in message_params:
        if not isinstance(message_param, BaseMessageParam):
            converted_message_params.append(message_param)
        elif (role := message_param.role) == "system":
            content = message_param.content
            if not isinstance(message_param.content, str):
                raise ValueError(
                    "System message content must be a single text string."
                )  # pragma: no cover
            converted_message_params += [
                {
                    "role": "user",
                    "parts": [message_param.content],
                },
                {
                    "role": "model",
                    "parts": ["Ok! I will adhere to this system message."],
                },
            ]
        elif isinstance((content := message_param.content), str):
            converted_message_params.append(
                {"role": role if role == "user" else "model", "parts": [content]}
            )
        else:
            converted_content = []
            for part in content:
                if part.type == "text":
                    converted_content.append(part.text)
                elif part.type == "image":
                    if part.media_type not in [
                        "image/jpeg",
                        "image/png",
                        "image/webp",
                        "image/heic",
                        "image/heif",
                    ]:
                        raise ValueError(
                            f"Unsupported image media type: {part.media_type}. "
                            "Gemini currently only supports JPEG, PNG, WebP, HEIC, "
                            "and HEIF images."
                        )
                    image = PIL.Image.open(io.BytesIO(part.image))
                    converted_content.append(image)
                elif part.type == "audio":
                    if part.media_type not in [
                        "audio/wav",
                        "audio/mp3",
                        "audio/aiff",
                        "audio/aac",
                        "audio/ogg",
                        "audio/flac",
                    ]:
                        raise ValueError(
                            f"Unsupported audio media type: {part.media_type}. "
                            "Gemini currently only supports WAV, MP3, AIFF, AAC, OGG, "
                            "and FLAC audio file types."
                        )
                    converted_content.append(
                        {"mime_type": part.media_type, "data": part.audio}
                    )
                else:
                    raise ValueError(
                        "Gemini currently only supports text, image, and audio parts. "
                        f"Part provided: {part.type}"
                    )
            converted_message_params.append(
                {
                    "role": role if role == "user" else "model",
                    "parts": converted_content,
                }
            )
    return converted_message_params
