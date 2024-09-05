"""Utility for converting `BaseMessageParam` to `ChatRequestMessage`."""

import base64

from azure.ai.inference.models import ChatRequestMessage, UserMessage

from ...base import BaseMessageParam


def convert_message_params(
    message_params: list[BaseMessageParam | ChatRequestMessage],
) -> list[ChatRequestMessage]:
    converted_message_params: list[ChatRequestMessage] = []
    for message_param in message_params:
        if not isinstance(message_param, BaseMessageParam):
            converted_message_params.append(message_param)
        elif isinstance((content := message_param.content), str):
            converted_message_params.append(UserMessage(content=content))
        else:
            converted_content = []
            for part in content:
                if part.type == "text":
                    converted_content.append(part.model_dump())
                elif part.type == "image":
                    if part.media_type not in [
                        "image/jpeg",
                        "image/png",
                        "image/gif",
                        "image/webp",
                    ]:
                        raise ValueError(
                            f"Unsupported image media type: {part.media_type}. Azure"
                            " currently only supports JPEG, PNG, GIF, and WebP images."
                        )
                    data = base64.b64encode(part.image).decode("utf-8")
                    converted_content.append(
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:{part.media_type};base64,{data}",
                                "detail": part.detail if part.detail else "auto",
                            },
                        }
                    )
                else:
                    raise ValueError(
                        "Azure currently only supports text and image parts. "
                        f"Part provided: {part.type}"
                    )
            converted_message_params.append(
                ChatRequestMessage(
                    {"role": message_param.role, "content": converted_content}
                )
            )
    return converted_message_params
