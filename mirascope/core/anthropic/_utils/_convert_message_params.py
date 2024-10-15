"""Utility for converting `BaseMessageParam` to `MessageParam`"""

import base64

from anthropic.types import MessageParam

from ...base import BaseMessageParam


def convert_message_params(
    message_params: list[BaseMessageParam | MessageParam],
) -> list[MessageParam]:
    converted_message_params = []
    for message_param in message_params:
        if not isinstance(message_param, BaseMessageParam):
            converted_message_params.append(message_param)
        elif isinstance(content := message_param.content, str):
            converted_message_params.append(message_param.model_dump())
        else:
            converted_content = []
            for part in content:
                if part.type == "text":
                    converted_content.append(part.model_dump())
                elif part.type == "cache_control" and converted_content:
                    converted_content[-1]["cache_control"] = {"type": part.cache_type}
                elif part.type == "image":
                    if part.media_type not in [
                        "image/jpeg",
                        "image/png",
                        "image/gif",
                        "image/webp",
                    ]:
                        raise ValueError(
                            f"Unsupported image media type: {part.media_type}. "
                            "Anthropic currently only supports JPEG, PNG, GIF, and "
                            "WebP images."
                        )
                    converted_content.append(
                        {
                            "type": "image",
                            "source": {
                                "data": base64.b64encode(part.image).decode("utf-8"),
                                "media_type": part.media_type,
                                "type": "base64",
                            },
                        }
                    )
                else:
                    raise ValueError(
                        "Anthropic currently only supports text, image, and cache "
                        f"control parts. Part provided: {part.type}"
                    )
            converted_message_params.append(
                {"role": message_param.role, "content": converted_content}
            )
    return converted_message_params
