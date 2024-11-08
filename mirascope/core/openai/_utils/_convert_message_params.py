"""Utility for converting `BaseMessageParam` to `ChatCompletionMessageParam`."""

import base64

from openai.types.chat import ChatCompletionMessageParam

from ...base import BaseMessageParam


def convert_message_params(
    message_params: list[BaseMessageParam | ChatCompletionMessageParam],
) -> list[ChatCompletionMessageParam]:
    converted_message_params = []
    for message_param in message_params:
        if not isinstance(message_param, BaseMessageParam):
            converted_message_params.append(message_param)
        elif isinstance((content := message_param.content), str):
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
                            f"Unsupported image media type: {part.media_type}. OpenAI"
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
                elif part.type == "audio":
                    if part.media_type not in [
                        "audio/wav",
                        "audio/mp3",
                    ]:
                        raise ValueError(
                            f"Unsupported audio media type: {part.media_type}. "
                            "OpenAI currently only supports WAV and MP3 audio file types."
                        )
                    converted_content.append(
                        {
                            "input_audio": {
                                "format": part.media_type.split("/")[-1],
                                "data": base64.b64encode(part.audio).decode("utf-8"),
                            },
                            "type": "input_audio",
                        }
                    )
                else:
                    raise ValueError(
                        "OpenAI currently only supports text, image and audio parts. "
                        f"Part provided: {part.type}"
                    )
            converted_message_params.append(
                {"role": message_param.role, "content": converted_content}
            )
    return converted_message_params
