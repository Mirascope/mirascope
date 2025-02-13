from typing import cast

from vertexai.generative_models import Content

from mirascope.core import BaseMessageParam
from mirascope.core.base import DocumentPart, ImagePart, TextPart
from mirascope.core.base._utils._base_message_param_converter import (
    BaseMessageParamConverter,
)
from mirascope.core.base.message_param import ImageURLPart, ToolCallPart, ToolResultPart
from mirascope.core.vertex._utils import convert_message_params


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


class VertexMessageParamConverter(BaseMessageParamConverter):
    """Converts between Vertex `Content` and Mirascope `BaseMessageParam`."""

    @staticmethod
    def to_provider(message_params: list[BaseMessageParam]) -> list[Content]:
        """
        Convert from Mirascope `BaseMessageParam` to Vertex `Content`.
        """
        return convert_message_params(
            cast(list[BaseMessageParam | Content], message_params)
        )

    @staticmethod
    def from_provider(message_params: list[Content]) -> list[BaseMessageParam]:
        """
        Convert from Vertex's `Content` to Mirascope `BaseMessageParam`.
        """
        converted = []
        for message_param in message_params:
            role: str = (
                "assistant" if message_param.role == "model" else message_param.role
            )
            contents = []
            has_tool_call = False
            for part in message_param.parts:
                if part.function_response:
                    converted.append(
                        BaseMessageParam(
                            role=message_param.role,
                            content=[
                                ToolResultPart(
                                    type="tool_result",
                                    name=part.function_response.name,
                                    content=part.function_response.response["result"],  # pyright: ignore [reportReturnType, reportArgumentType]
                                    id=None,
                                    is_error=False,
                                )
                            ],
                        )
                    )
                elif part.inline_data:
                    blob = part.inline_data
                    mime = blob.mime_type
                    data = blob.data
                    if _is_image_mime(mime):
                        contents.append(_to_image_part(mime, data))
                    elif mime == "application/pdf":
                        contents.append(_to_document_part(mime, data))
                    else:
                        raise ValueError(
                            f"Unsupported inline_data mime type: {mime}. Cannot convert to BaseMessageParam."
                        )

                elif part.file_data:
                    if _is_image_mime(part.file_data.mime_type):
                        contents.append(
                            ImageURLPart(
                                type="image_url",
                                url=part.file_data.file_uri,
                                detail=None,
                            )
                        )
                    else:
                        raise ValueError(
                            f"FileData.file_uri is not support: {part.file_data}. Cannot convert to BaseMessageParam."
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
                elif part.text:
                    contents.append(TextPart(type="text", text=part.text))

                else:  # pragma: no cover
                    raise ValueError(
                        "Part does not contain any supported content (text, image, or document)."
                    )

            if len(contents) == 1 and isinstance(contents[0], TextPart):
                converted.append(BaseMessageParam(role=role, content=contents[0].text))
            else:
                if contents:
                    converted.append(
                        BaseMessageParam(
                            role="tool" if has_tool_call else role, content=contents
                        )
                    )

        return converted
