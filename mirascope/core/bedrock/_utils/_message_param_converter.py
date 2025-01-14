from mirascope.core import BaseMessageParam
from mirascope.core.base import DocumentPart, ImagePart, TextPart, ToolCallPart
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

    def to_provider(
        self, message_params: list[BaseMessageParam]
    ) -> list[InternalBedrockMessageParam]:
        """
        Convert from Mirascope `BaseMessageParam` to Bedrock's `InternalBedrockMessageParam`.
        """
        return convert_message_params(message_params)

    def from_provider(
        self, message_params: list[InternalBedrockMessageParam]
    ) -> list[BaseMessageParam]:
        """
        Convert from Bedrock's `InternalBedrockMessageParam` to Mirascope `BaseMessageParam`.
        """
        results = []
        for message_param in message_params:
            message_param["role"]
            content_blocks = message_param["content"]

            converted_content = []
            has_tool_call = False
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
                    converted_content.append(
                        ToolCallPart(
                            type="tool_call",
                            name=tool_use["name"],
                            id=tool_use["toolUseId"],
                            args=tool_use["input"],
                        )
                    )
                else:
                    raise ValueError(
                        "Content block does not contain supported content."
                    )
            if len(converted_content) == 1 and isinstance(
                converted_content[0], TextPart
            ):
                return BaseMessageParam(
                    role="assistant",
                    content=converted_content[0].text,
                )
            return BaseMessageParam(
                role="tool" if has_tool_call else "assistant", content=converted_content
            )

        return results
