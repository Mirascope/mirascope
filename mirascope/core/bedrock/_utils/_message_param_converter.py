from typing import cast

from mirascope.core import BaseMessageParam
from mirascope.core.base import (
    DocumentPart,
    ImagePart,
    TextPart,
    ToolCallPart,
    ToolResultPart,
)
from mirascope.core.base._utils._base_message_param_converter import (
    BaseMessageParamConverter,
)

from .._types import (
    InternalBedrockMessageParam,
)
from . import convert_message_params

IMAGE_FORMAT_MAP = {
    "JPEG": "image/jpeg",
    "PNG": "image/png",
    "GIF": "image/gif",
    "WEBP": "image/webp",
}


class BedrockMessageParamConverter(BaseMessageParamConverter):
    """Converts between Bedrock `InternalBedrockMessageParam` and Mirascope `BaseMessageParam`."""

    @staticmethod
    def to_provider(
        message_params: list[BaseMessageParam],
    ) -> list[InternalBedrockMessageParam]:
        """
        Convert from Mirascope `BaseMessageParam` to Bedrock's `InternalBedrockMessageParam`.
        """
        return convert_message_params(
            cast(list[BaseMessageParam | InternalBedrockMessageParam], message_params)
        )

    @staticmethod
    def from_provider(
        message_params: list[InternalBedrockMessageParam],
    ) -> list[BaseMessageParam]:
        """
        Convert from Bedrock's `InternalBedrockMessageParam` to Mirascope `BaseMessageParam`.
        """
        converted = []
        for message_param in message_params:
            message_param["role"]
            content_blocks = message_param["content"]

            converted_content = []
            for block in content_blocks:
                if "text" in block:
                    text = block["text"]
                    if not isinstance(text, str):
                        raise ValueError("Text content must be a string.")
                    converted_content.append(TextPart(type="text", text=text))

                elif "image" in block:
                    image_block = block["image"]
                    img_format = image_block["format"]  # e.g. "JPEG"
                    source = image_block["source"]
                    if "bytes" not in source or not isinstance(source["bytes"], bytes):
                        raise ValueError(
                            "Image block must have 'source.bytes' as bytes."
                        )
                    media_type = IMAGE_FORMAT_MAP.get(img_format.upper())
                    if not media_type:
                        raise ValueError(f"Unsupported image format: {img_format}")
                    converted_content.append(
                        ImagePart(
                            type="image",
                            media_type=media_type,
                            image=source["bytes"],
                            detail=None,
                        )
                    )

                elif "document" in block:
                    doc_block = block["document"]
                    doc_format = doc_block["format"]  # e.g. "PDF"
                    if doc_format.upper() != "PDF":
                        raise ValueError(
                            f"Unsupported document format: {doc_format}. Only PDF is supported."
                        )
                    source = doc_block["source"]
                    if "bytes" not in source or not isinstance(source["bytes"], bytes):
                        raise ValueError(
                            "Document block must have 'source.bytes' as bytes."
                        )
                    converted_content.append(
                        DocumentPart(
                            type="document",
                            media_type="application/pdf",
                            document=source["bytes"],
                        )
                    )
                elif "toolUse" in block:
                    tool_use = block["toolUse"]
                    if converted_content:
                        converted.append(
                            BaseMessageParam(
                                role=message_param["role"], content=converted_content
                            )
                        )
                        converted_content = []

                    converted.append(
                        BaseMessageParam(
                            role="assistant",
                            content=[
                                ToolCallPart(
                                    type="tool_call",
                                    name=tool_use["name"],
                                    id=tool_use["toolUseId"],
                                    args=tool_use["input"],
                                )
                            ],
                        )
                    )
                elif "toolResult" in block:
                    tool_result = block["toolResult"]
                    if converted_content:
                        converted.append(
                            BaseMessageParam(
                                role=message_param["role"], content=converted_content
                            )
                        )
                        converted_content = []
                    converted.append(
                        BaseMessageParam(
                            role="user",
                            content=[
                                ToolResultPart(
                                    type="tool_result",
                                    id=tool_result["toolUseId"],
                                    name=tool_result["name"],  # pyright: ignore [reportGeneralTypeIssues]
                                    content=tool_result["content"]
                                    if isinstance(tool_result["content"], str)
                                    else tool_result["content"][0]["text"],  # pyright: ignore [reportTypedDictNotRequiredAccess]
                                    is_error=tool_result.get("isError", False),
                                )
                            ],
                        )
                    )
                else:
                    raise ValueError(
                        "Content block does not contain supported content."
                    )
            if len(converted_content) == 1 and isinstance(
                converted_content[0], TextPart
            ):
                converted.append(
                    BaseMessageParam(
                        role=message_param["role"],
                        content=converted_content[0].text,
                    )
                )
            else:
                if converted_content:
                    converted.append(
                        BaseMessageParam(
                            role=message_param["role"],
                            content=converted_content,
                        )
                    )

        return converted
