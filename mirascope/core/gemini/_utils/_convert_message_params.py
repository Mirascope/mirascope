"""Utility for converting `BaseMessageParam` to `ContentsType`"""

import io

import PIL.Image
from google.generativeai import protos
from google.generativeai.types import ContentDict

from ...base import BaseMessageParam
from ...base._utils import get_audio_type
from ...base._utils._parse_content_template import _load_media


def convert_message_params(
    message_params: list[BaseMessageParam | ContentDict],
) -> list[ContentDict]:
    converted_message_params = []
    for message_param in message_params:
        if not isinstance(message_param, BaseMessageParam):
            converted_message_params.append(message_param)
        elif (role := message_param.role) == "system":
            if not isinstance(message_param.content, str):
                raise ValueError(
                    "System message content must be a single text string."
                )  # pragma: no cover
            converted_message_params += [
                {
                    "role": "system",
                    "parts": [message_param.content],
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
                elif part.type == "image_url":
                    if part.url.startswith(("https://", "http://")):
                        image = PIL.Image.open(io.BytesIO(_load_media(part.url)))
                        media_type = (
                            PIL.Image.MIME[image.format]
                            if image.format
                            else "image/unknown"
                        )
                        if media_type not in [
                            "image/jpeg",
                            "image/png",
                            "image/webp",
                            "image/heic",
                            "image/heif",
                        ]:
                            raise ValueError(
                                f"Unsupported image media type: {media_type}. "
                                "Gemini currently only supports JPEG, PNG, WebP, HEIC, "
                                "and HEIF images."
                            )
                        converted_content.append(image)
                    else:
                        converted_content.append(protos.FileData(file_uri=part.url))
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
                elif part.type == "audio_url":
                    if part.url.startswith(("https://", "http://")):
                        audio = _load_media(part.url)
                        audio_type = f"audio/{get_audio_type(audio)}"
                        if audio_type not in [
                            "audio/wav",
                            "audio/mp3",
                            "audio/aiff",
                            "audio/aac",
                            "audio/ogg",
                            "audio/flac",
                        ]:
                            raise ValueError(
                                f"Unsupported audio media type: {audio_type}. "
                                "Gemini currently only supports WAV, MP3, AIFF, AAC, OGG, "
                                "and FLAC audio file types."
                            )
                        converted_content.append(
                            {"mime_type": audio_type, "data": audio}
                        )
                    else:
                        converted_content.append(protos.FileData(file_uri=part.url))
                elif part.type == "tool_call":
                    converted_content.append(
                        protos.FunctionCall(
                            name=part.name,
                            args=part.args,
                        )
                    )
                elif part.type == "tool_result":
                    if converted_content:
                        converted_message_params.append(
                            {
                                "role": role if role == "user" else "model",
                                "parts": converted_content,
                            }
                        )
                        converted_content = []
                    converted_message_params.append(
                        {
                            "role": "user",
                            "parts": [
                                protos.FunctionResponse(
                                    name=part.name, response={"result": part.content}
                                )
                            ],
                        }
                    )
                else:
                    raise ValueError(
                        "Gemini currently only supports text, image, and audio parts. "
                        f"Part provided: {part.type}"
                    )
            if converted_content:
                converted_message_params.append(
                    {
                        "role": role if role == "user" else "model",
                        "parts": converted_content,
                    }
                )
    return converted_message_params
