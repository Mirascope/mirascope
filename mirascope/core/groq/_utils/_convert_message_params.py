"""Utility for converting `BaseMessageParam` to `ChatCompletionMessageParam`"""

import base64
import json

from groq.types.chat import (
    ChatCompletionMessageParam,
)

from ...base import BaseMessageParam


def convert_message_params(
    message_params: list[BaseMessageParam | ChatCompletionMessageParam],
) -> list[ChatCompletionMessageParam]:
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
                elif part.type == "image":
                    if part.media_type not in [
                        "image/jpeg",
                        "image/png",
                        "image/gif",
                        "image/webp",
                    ]:
                        raise ValueError(
                            f"Unsupported image media type: {part.media_type}. Groq"
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
                elif part.type == "image_url":
                    converted_content.append(
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": part.url,
                            },
                        }
                    )
                elif part.type == "tool_call":
                    converted_message_param = {
                        "role": "assistant",
                        "tool_calls": [
                            {
                                "type": "function",
                                "id": part.id,
                                "function": {
                                    "name": part.name,
                                    "arguments": json.dumps(part.args),
                                },
                            }
                        ],
                    }
                    if converted_content:
                        if len(converted_content) == 1:
                            if converted_content[0]["type"] == "text":
                                converted_message_param["content"] = converted_content[
                                    0
                                ]["text"]
                        else:
                            converted_message_params.append(
                                {
                                    "role": message_param.role,
                                    "content": converted_content,
                                }
                            )
                        converted_content = []
                    converted_message_params.append(converted_message_param)

                elif part.type == "tool_result":
                    if converted_content:
                        converted_message_params.append(
                            {
                                "role": message_param.role,
                                "content": converted_content,
                            }
                        )
                        converted_content = []
                    converted_message_params.append(
                        {
                            "role": "tool",
                            "content": part.content,
                            "tool_call_id": part.id,
                        }
                    )
                else:
                    raise ValueError(
                        "Groq currently only supports text and image parts. "
                        f"Part provided: {part.type}"
                    )
            if converted_content:
                converted_message_params.append(
                    {"role": message_param.role, "content": converted_content}
                )
    return converted_message_params
