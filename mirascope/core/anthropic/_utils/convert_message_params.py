"""Utility for converting `BaseMessageParam` to `MessageParam`"""

import base64

from anthropic.types import MessageParam

from ...base import BaseMessageParam


def convert_message_params(
    message_params: list[BaseMessageParam],
) -> list[MessageParam]:
    converted_message_params = []
    for message_param in message_params:
        content = message_param["content"]
        converted_content = []
        for part in content:
            if part["type"] == "text":
                converted_content.append(part)

            elif part["type"] == "image":
                if part["media_type"] not in [
                    "image/jpeg",
                    "image/png",
                    "image/gif",
                    "image/webp",
                ]:
                    raise ValueError(
                        f"Unsupported image media type: {part['media_type']}. Anthropic"
                        " currently only supports JPEG, PNG, GIF, and WebP images."
                    )
                converted_content.append(
                    {
                        "type": "image",
                        "source": {
                            "data": base64.b64encode(part["image"]).decode("utf-8"),
                            "media_type": part["media_type"],
                            "type": "base64",
                        },
                    }
                )
            else:
                raise ValueError(
                    "Anthropic currently only supports text and image modalities. "
                    f"Modality provided: {part['type']}"
                )
        converted_message_params.append(
            {"role": message_param["role"], "content": converted_content}
        )
    return converted_message_params
