from typing import cast

from google.genai import Client
from google.genai.types import (
    Content,
    ContentDict,
    ContentOrDict,
)

from mirascope.core import BaseMessageParam
from mirascope.core.base import DocumentPart, ImagePart, TextPart
from mirascope.core.base._utils._base_message_param_converter import (
    BaseMessageParamConverter,
)
from mirascope.core.base.message_param import (
    AudioURLPart,
    ImageURLPart,
    ToolCallPart,
    ToolResultPart,
)
from mirascope.core.gemini._utils._message_param_converter import _is_audio_mime
from mirascope.core.google._utils import convert_message_params


def _is_image_mime(mime_type: str) -> bool:
    return mime_type in ["image/jpeg", "image/png", "image/gif", "image/webp"]


def _to_image_part(mime_type: str, data: bytes) -> ImagePart:
    if not _is_image_mime(mime_type):
        raise ValueError(
            f"Unsupported image media type: {mime_type}. "
            "Expected one of: image/jpeg, image/png, image/gif, image/webp."
        )
    return ImagePart(type="image", media_type=mime_type, image=data, detail=None)


def _to_document_part(mime_type: str, data: bytes) -> DocumentPart:
    if mime_type != "application/pdf":
        raise ValueError(
            f"Unsupported document media type: {mime_type}. "
            "Only application/pdf is supported."
        )
    return DocumentPart(type="document", media_type=mime_type, document=data)


class GoogleMessageParamConverter(BaseMessageParamConverter):
    """Converts between Google `ContentDict` and Mirascope `BaseMessageParam`."""

    @staticmethod
    def to_provider(
        message_params: list[BaseMessageParam], client: Client | None = None
    ) -> list[ContentDict]:
        """
        Convert from Mirascope `BaseMessageParam` to Google `ContentDict`.
        """
        return convert_message_params(
            cast(list[BaseMessageParam | ContentDict], message_params),
            client or Client(),
        )

    @staticmethod
    def from_provider(message_params: list[ContentOrDict]) -> list[BaseMessageParam]:
        """
        Convert from Google's `ContentDict` to Mirascope `BaseMessageParam`.
        """
        converted: list[BaseMessageParam] = []
        for message_param in message_params:
            if isinstance(message_param, dict):
                message_param = Content.model_validate(message_param)
            role: str = "assistant"
            content_list = []
            for part in message_param.parts or []:
                if part.text:
                    content_list.append(TextPart(type="text", text=part.text))

                elif part.inline_data:
                    blob = part.inline_data
                    mime = blob.mime_type or ""
                    data = blob.data or b""
                    if _is_image_mime(mime or ""):
                        content_list.append(_to_image_part(mime, data))
                    elif mime == "application/pdf":
                        content_list.append(_to_document_part(mime, data))
                    else:
                        raise ValueError(
                            f"Unsupported inline_data mime type: {mime}. Cannot convert to BaseMessageParam."
                        )

                elif part.file_data:
                    if _is_image_mime(cast(str, part.file_data.mime_type)):
                        content_list.append(
                            ImageURLPart(
                                type="image_url",
                                url=cast(str, part.file_data.file_uri),
                                detail=None,
                            )
                        )
                    elif _is_audio_mime(cast(str, part.file_data.mime_type)):
                        content_list.append(
                            AudioURLPart(
                                type="audio_url",
                                url=cast(str, part.file_data.file_uri),
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
                                    name=part.function_call.name,  # pyright: ignore [reportArgumentType]
                                    args=part.function_call.args,
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
                                    name=part.function_response.name,  # pyright: ignore [reportArgumentType]
                                    content=part.function_response.response[  # pyright: ignore [reportArgumentType, reportOptionalSubscript]
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

            if len(content_list) == 1 and isinstance(content_list[0], TextPart):
                converted.append(
                    BaseMessageParam(role=role, content=content_list[0].text)
                )
            else:
                if content_list:
                    converted.append(BaseMessageParam(role=role, content=content_list))

        return converted
