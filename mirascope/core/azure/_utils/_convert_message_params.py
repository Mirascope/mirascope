"""Utility for converting `BaseMessageParam` to `ChatRequestMessage`."""

import base64
import json
from typing import cast

from azure.ai.inference.models import (
    AssistantMessage,
    ChatCompletionsToolCall,
    ChatRequestMessage,
    FunctionCall,
    ToolMessage,
    UserMessage,
)

from ...base import BaseMessageParam


def convert_message_params(
    message_params: list[BaseMessageParam | ChatRequestMessage],
) -> list[ChatRequestMessage]:
    converted_message_params: list[ChatRequestMessage | ToolMessage] = []
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
                elif part.type == "image_url":
                    converted_content.append(
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": part.url,
                                "detail": part.detail if part.detail else "auto",
                            },
                        }
                    )
                elif part.type == "tool_call":
                    converted_message_param = AssistantMessage(
                        tool_calls=[
                            ChatCompletionsToolCall(
                                id=part.id,  # pyright: ignore [reportArgumentType]
                                function=FunctionCall(
                                    name=part.name, arguments=json.dumps(part.args)
                                ),
                            )
                        ]
                    )

                    if converted_content:
                        if len(converted_content) == 1:
                            if converted_content[0]["type"] == "text":
                                converted_message_param["content"] = converted_content[
                                    0
                                ]["text"]
                        else:
                            converted_message_params.append(
                                ChatRequestMessage(
                                    {
                                        "role": message_param.role,
                                        "content": converted_content,
                                    }
                                )
                            )
                        converted_content = []
                    converted_message_params.append(converted_message_param)
                elif part.type == "tool_result":
                    if converted_content:
                        converted_message_params.append(
                            ChatRequestMessage(
                                {
                                    "role": message_param.role,
                                    "content": converted_content,
                                }
                            )
                        )
                        converted_content = []
                    converted_message_params.append(
                        ToolMessage(
                            content=part.content,
                            tool_call_id=cast(str, part.id),
                        )
                    )
                else:
                    raise ValueError(
                        "Azure currently only supports text and image parts. "
                        f"Part provided: {part.type}"
                    )
            if converted_content:
                converted_message_params.append(
                    ChatRequestMessage(
                        {"role": message_param.role, "content": converted_content}
                    )
                )
    return converted_message_params
