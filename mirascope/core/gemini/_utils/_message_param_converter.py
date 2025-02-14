# file: gemini_message_param_converter.py

from typing import cast

from google.generativeai.types import (
    ContentDict,
    protos,
)

from mirascope.core import BaseMessageParam
from mirascope.core.base import (
    AudioPart,
    AudioURLPart,
    DocumentPart,
    ImagePart,
    ImageURLPart,
    TextPart,
)
from mirascope.core.base._utils._base_message_param_converter import (
    BaseMessageParamConverter,
)
from mirascope.core.base.message_param import ToolCallPart, ToolResultPart
from mirascope.core.gemini._utils import convert_message_params


def _is_image_mime(mime_type: str) -> bool:
    return mime_type in ["image/jpeg", "image/png", "image/gif", "image/webp"]


def _to_image_part(mime_type: str, data: bytes) -> ImagePart:
    if not _is_image_mime(mime_type):
        raise ValueError(
            f"Unsupported image media type: {mime_type}. "
            "Expected one of: image/jpeg, image/png, image/gif, image/webp."
        )
    return ImagePart(type="image", media_type=mime_type, image=data, detail=None)


def _is_audio_mime(mime_type: str) -> bool:
    return mime_type in [
        "audio/wav",
        "audio/mp3",
        "audio/wav",
        "audio/mp3",
        "audio/aiff",
        "audio/aac",
        "audio/ogg",
        "audio/flac",
    ]


def _to_audio_part(mime_type: str, data: bytes) -> AudioPart:
    if not _is_audio_mime(mime_type):
        raise ValueError(
            f"Unsupported audio media type: {mime_type}. "
            "Expected one of: audio/wav, audio/mp3, audio/aiff, audio/aac, audio/ogg, audio/flac."
        )
    return AudioPart(type="audio", media_type=mime_type, audio=data)


def _to_document_part(mime_type: str, data: bytes) -> DocumentPart:
    if mime_type != "application/pdf":
        raise ValueError(
            f"Unsupported document media type: {mime_type}. "
            "Only application/pdf is supported."
        )
    return DocumentPart(type="document", media_type=mime_type, document=data)


class GeminiMessageParamConverter(BaseMessageParamConverter):
    """Converts between Gemini `ContentDict` and Mirascope `BaseMessageParam`."""

    @staticmethod
    def to_provider(message_params: list[BaseMessageParam]) -> list[ContentDict]:
        """
        Convert from Mirascope `BaseMessageParam` to Gemini `ContentDict`.
        """
        return convert_message_params(
            cast(list[BaseMessageParam | ContentDict], message_params)
        )

    @staticmethod
    def from_provider(message_params: list[ContentDict]) -> list[BaseMessageParam]:
        """
        Convert from Gemini's `ContentDict` to Mirascope `BaseMessageParam`.
        """
        converted: list[BaseMessageParam] = []
        for message_param in message_params:
            role: str = (
                "assistant"
                if message_param["role"] == "model"
                else message_param["role"]
            )
            content_list = []
            for part in cast(
                list[protos.Part | protos.FunctionCall | protos.FunctionResponse],
                message_param["parts"],
            ):
                if isinstance(part, protos.Part):
                    if part.text:
                        content_list.append(TextPart(type="text", text=part.text))

                    elif part.inline_data:
                        blob = part.inline_data
                        mime = blob.mime_type
                        data = blob.data
                        if _is_image_mime(mime):
                            content_list.append(_to_image_part(mime, data))
                        elif _is_audio_mime(mime):
                            content_list.append(_to_audio_part(mime, data))
                        elif mime == "application/pdf":
                            content_list.append(_to_document_part(mime, data))
                        else:
                            raise ValueError(
                                f"Unsupported inline_data mime type: {mime}. Cannot convert to BaseMessageParam."
                            )

                    elif part.file_data:
                        if _is_image_mime(part.file_data.mime_type):
                            content_list.append(
                                ImageURLPart(
                                    type="image_url",
                                    url=part.file_data.file_uri,
                                    detail=None,
                                )
                            )
                        elif _is_audio_mime(part.file_data.mime_type):
                            content_list.append(
                                AudioURLPart(
                                    type="audio_url",
                                    url=part.file_data.file_uri,
                                )
                            )
                        else:
                            raise ValueError(
                                f"Unsupported file_data mime type: {part.file_data.mime_type}. Cannot convert to BaseMessageParam."
                            )
                    elif part.function_call:
                        converted.append(
                            BaseMessageParam(
                                role=role,
                                content=[
                                    ToolCallPart(
                                        type="tool_call",
                                        name=part.function_call.name,
                                        args=dict(part.function_call.args),
                                    )
                                ],
                            )
                        )
                    elif part.function_response:
                        converted.append(
                            BaseMessageParam(
                                role=role,
                                content=[
                                    ToolResultPart(
                                        type="tool_result",
                                        name=part.function_response.name,
                                        content=part.function_response.response[  # pyright: ignore [reportArgumentType]
                                            "result"
                                        ],
                                        id=None,
                                        is_error=False,
                                    )
                                ],
                            )
                        )
                    else:
                        raise ValueError(
                            "Part does not contain any supported content (text, image, or document)."
                        )
                elif isinstance(part, protos.FunctionCall):
                    converted.append(
                        BaseMessageParam(
                            role=role,
                            content=[
                                ToolCallPart(
                                    type="tool_call",
                                    name=part.name,
                                    args=dict(part.args),
                                )
                            ],
                        )
                    )
                elif isinstance(part, protos.FunctionResponse):
                    converted.append(
                        BaseMessageParam(
                            role=role,
                            content=[
                                ToolResultPart(
                                    type="tool_result",
                                    name=part.name,
                                    content=part.response["result"],  # pyright: ignore [reportArgumentType]
                                    id=None,
                                    is_error=False,
                                )
                            ],
                        )
                    )

            if len(content_list) == 1 and isinstance(content_list[0], TextPart):
                converted.append(
                    BaseMessageParam(role=role, content=content_list[0].text)
                )
            else:
                if content_list:
                    converted.append(BaseMessageParam(role=role, content=content_list))

        return converted
