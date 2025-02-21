"""Utility for converting `BaseMessageParam` to `Content`"""

import base64
import io

import PIL.Image
from google.cloud.aiplatform_v1beta1.types import content as gapic_content_types
from google.cloud.aiplatform_v1beta1.types import tool as gapic_tool_types
from vertexai.generative_models import Content, Image, Part

from ...base import BaseMessageParam
from ...base._utils import get_audio_type
from ...base._utils._parse_content_template import _load_media


def convert_message_params(
    message_params: list[BaseMessageParam | Content],
) -> list[Content]:
    converted_message_params = []
    for message_param in message_params:
        if isinstance(message_param, Content):
            converted_message_params.append(message_param)
        elif (role := message_param.role) == "system":
            content = message_param.content
            if not isinstance(content, str):
                raise ValueError(
                    "System message content must be a single text string."
                )  # pragma: no cover
            converted_message_params += [
                Content(
                    role="system",
                    parts=[
                        Part.from_text(content) if isinstance(content, str) else content
                    ],
                ),
            ]
        elif isinstance((content := message_param.content), str):
            converted_message_params.append(
                Content(role="user", parts=[Part.from_text(content)])
            )
        else:
            converted_content: list[Part] = []
            for part in content:
                if part.type == "text":
                    converted_content.append(Part.from_text(part.text))
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
                            "Vertex currently only supports JPEG, PNG, WebP, HEIC, "
                            "and HEIF images."
                        )
                    image = Image.from_bytes(part.image)
                    converted_content.append(Part.from_image(image))
                elif part.type == "image_url":
                    # Should download the image to determine the media type
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
                    converted_content.append(
                        Part.from_uri(part.url, mime_type=media_type)
                    )
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
                            "Vertex currently only supports WAV, MP3, AIFF, AAC, OGG, "
                            "and FLAC audio file types."
                        )
                    converted_content.append(
                        Part.from_data(
                            mime_type=part.media_type,
                            data=part.audio
                            if isinstance(part.audio, bytes)
                            else base64.b64decode(part.audio),
                        )
                    )
                elif part.type == "audio_url":
                    # Should download the audio to determine the media type
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
                        Part.from_uri(part.url, mime_type=audio_type)
                    )
                elif part.type == "tool_call":
                    if converted_content:
                        converted_message_params.append(
                            Content(role=role, parts=converted_content)
                        )
                        converted_content = []
                    raw_gapic_part = gapic_content_types.Part(
                        function_call=gapic_tool_types.FunctionCall(
                            name=part.name, args=part.args
                        )
                    )
                    converted_message_params.append(
                        Content(
                            role=role,
                            parts=[Part._from_gapic(raw_gapic_part)],
                        )
                    )
                elif part.type == "tool_result":
                    if converted_content:
                        converted_message_params.append(
                            Content(role=role, parts=converted_content)
                        )
                        converted_content = []
                    converted_message_params.append(
                        Content(
                            role=role,
                            parts=[
                                Part.from_function_response(
                                    name=part.name,
                                    response={
                                        "content": {"result": part.content},
                                    },
                                )
                            ],
                        )
                    )
                else:
                    raise ValueError(
                        "Vertex currently only supports text, image, and audio parts. "
                        f"Part provided: {part.type}"
                    )
            if converted_content:
                converted_message_params.append(
                    Content(role=role, parts=converted_content)
                )
    return converted_message_params
