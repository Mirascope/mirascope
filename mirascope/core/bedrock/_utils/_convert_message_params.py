"""Utility for converting `BaseMessageParam` to `BedrockMessageParam`."""

from typing import cast

from ...base import BaseMessageParam
from .._types import ConversationRoleType, InternalBedrockMessageParam


def convert_message_params(
    message_params: list[BaseMessageParam | InternalBedrockMessageParam],
) -> list[InternalBedrockMessageParam]:
    converted_message_params = []
    for message_param in message_params:
        if not isinstance(message_param, BaseMessageParam):
            converted_message_params.append(message_param)
        elif isinstance((content := message_param.content), str):
            converted_message_params.append(
                {
                    "role": cast(ConversationRoleType, message_param.role),
                    "content": [{"text": content}],
                }
            )
        else:
            converted_content = []
            for part in content:
                if part.type == "text":
                    converted_content.append({"text": part.text})
                elif part.type == "image":
                    if part.media_type not in [
                        "image/jpeg",
                        "image/png",
                        "image/gif",
                        "image/webp",
                    ]:
                        raise ValueError(
                            f"Unsupported image media type: {part.media_type}. Bedrock"
                            " currently only supports JPEG, PNG, GIF, and WebP images."
                        )
                    converted_content.append(
                        {"format": part.media_type, "bytes": part.image}
                    )
                else:
                    raise ValueError(
                        "Bedrock currently only supports text and image parts. "
                        f"Part provided: {part.type}"
                    )
            converted_message_params.append(
                {"role": message_param.role, "content": converted_content}
            )
    return converted_message_params
