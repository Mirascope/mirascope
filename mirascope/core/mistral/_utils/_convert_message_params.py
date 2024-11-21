"""Utility for converting `BaseMessageParam` to `ChatMessage`."""

import base64

from mistralai.models import (
    AssistantMessage,
    ImageURL,
    ImageURLChunk,
    SystemMessage,
    TextChunk,
    ToolMessage,
    UserMessage,
)

from ...base import BaseMessageParam


def _make_message(
    role: str,
    **kwargs,  # noqa: ANN003
) -> AssistantMessage | SystemMessage | ToolMessage | UserMessage:
    if role == "assistant":
        return AssistantMessage(**kwargs)
    elif role == "system":
        return SystemMessage(**kwargs)
    elif role == "tool":
        return ToolMessage(**kwargs)
    elif role == "user":
        return UserMessage(**kwargs)
    raise ValueError(f"Invalid role: {role}")


def convert_message_params(
    message_params: list[
        BaseMessageParam | AssistantMessage | SystemMessage | ToolMessage | UserMessage
    ],
) -> list[AssistantMessage | SystemMessage | ToolMessage | UserMessage]:
    converted_message_params = []
    for message_param in message_params:
        if not isinstance(message_param, BaseMessageParam):
            converted_message_params.append(message_param)
        elif isinstance(content := message_param.content, str):
            converted_message_params.append(_make_message(**message_param.model_dump()))
        else:
            converted_content = []
            for part in content:
                if part.type == "text":
                    converted_content.append(TextChunk(text=part.text))

                elif part.type == "image":
                    if part.media_type not in [
                        "image/jpeg",
                        "image/png",
                        "image/gif",
                        "image/webp",
                    ]:
                        raise ValueError(
                            f"Unsupported image media type: {part.media_type}. Mistral"
                            " currently only supports JPEG, PNG, GIF, and WebP images."
                        )
                    data = base64.b64encode(part.image).decode("utf-8")
                    converted_content.append(
                        ImageURLChunk(
                            image_url=ImageURL(
                                url=f"data:{part.media_type};base64,{data}",
                                detail=part.detail if part.detail else "auto",
                            )
                        )
                    )
                else:
                    raise ValueError(
                        "Mistral currently only supports text and image parts. "
                        f"Part provided: {part.type}"
                    )
            converted_message_params.append(
                _make_message(role=message_param.role, content=converted_content)
            )
    return converted_message_params
