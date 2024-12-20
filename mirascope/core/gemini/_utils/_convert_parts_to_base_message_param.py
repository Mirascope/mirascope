from typing import cast

from google.generativeai.types import (
    ContentDict,
    protos,
)
from google.generativeai.types.file_types import FileDataType as FileData

from mirascope.core import BaseMessageParam
from mirascope.core.base import DocumentPart, ImagePart, TextPart


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


def convert_message_param_to_base_message_param(
    message_param: ContentDict,
) -> BaseMessageParam:
    """Converts a Part to a BaseMessageParam."""
    role: str = "assistant"
    content_list = []
    for part in cast(list[protos.Part], message_param["parts"]):
        if part.text:
            content_list.append(TextPart(type="text", text=part.text))

        elif part.inline_data:
            blob = part.inline_data
            mime = blob.mime_type
            data = blob.data
            if _is_image_mime(mime):
                content_list.append(_to_image_part(mime, data))
            elif mime == "application/pdf":
                content_list.append(_to_document_part(mime, data))
            else:
                raise ValueError(
                    f"Unsupported inline_data mime type: {mime}. Cannot convert to BaseMessageParam."
                )

        elif part.file_data:
            file_data: FileData = part.file_data
            mime = file_data.mime_type
            data = file_data.data
            if _is_image_mime(mime):
                content_list.append(_to_image_part(mime, data))
            elif mime == "application/pdf":
                content_list.append(_to_document_part(mime, data))
            else:
                raise ValueError(
                    f"Unsupported file_data mime type: {mime}. Cannot convert to BaseMessageParam."
                )

        else:
            raise ValueError(
                "Part does not contain any supported content (text, image, or document)."
            )

    if len(content_list) == 1 and isinstance(content_list[0], TextPart):
        return BaseMessageParam(role=role, content=content_list)

    return BaseMessageParam(role=role, content=content_list)
