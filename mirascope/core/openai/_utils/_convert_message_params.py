"""Utility for converting `BaseMessageParam` to `ChatCompletionMessageParam`."""

import base64
import json

from openai.types.chat import ChatCompletionMessageParam

from ...base import BaseMessageParam
from ...base._utils import get_audio_type
from ...base._utils._parse_content_template import _load_media


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

            tool_calls = []
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
                elif part.type == "audio":
                    if part.media_type not in [
                        "audio/wav",
                        "audio/mp3",
                    ]:
                        raise ValueError(
                            f"Unsupported audio media type: {part.media_type}. "
                            "OpenAI currently only supports WAV and MP3 audio file types."
                        )
                    data = (
                        part.audio
                        if isinstance(part.audio, str)
                        else base64.b64encode(part.audio).decode("utf-8")
                    )
                    converted_content.append(
                        {
                            "input_audio": {
                                "format": part.media_type.split("/")[-1],
                                "data": data,
                            },
                            "type": "input_audio",
                        }
                    )
                elif part.type == "audio_url":
                    audio = _load_media(part.url)
                    audio_type = get_audio_type(audio)
                    if audio_type not in [
                        "wav",
                        "mp3",
                    ]:
                        raise ValueError(
                            f"Unsupported audio media type: audio/{audio_type}. "
                            "OpenAI currently only supports WAV and MP3 audio file types."
                        )
                    converted_content.append(
                        {
                            "input_audio": {
                                "format": audio_type,
                                "data": base64.b64encode(audio).decode("utf-8"),
                            },
                            "type": "input_audio",
                        }
                    )
                elif part.type == "tool_call":
                    tool_calls.append(
                        {
                            "function": {
                                "name": part.name,
                                "arguments": json.dumps(part.args),
                            },
                            "type": "function",
                            "id": part.id,
                        }
                    )
                elif part.type == "tool_result":
                    if converted_content:
                        converted_message_params.append(
                            {"role": message_param.role, "content": converted_content}
                        )
                        converted_content = []

                    converted_message_params.append(
                        {
                            "role": "tool",
                            "tool_call_id": part.id,
                            "content": part.content,
                        }
                    )
                else:
                    raise ValueError(
                        "OpenAI currently only supports text, image and audio parts. "
                        f"Part provided: {part.type}"
                    )
            if tool_calls:
                converted_message_param = {
                    "role": "assistant",
                    "tool_calls": tool_calls,
                }
                converted_message_params.append(converted_message_param)
                if converted_content:
                    converted_message_param["content"] = converted_content
            elif converted_content:
                converted_message_params.append(
                    {
                        "role": message_param.role,
                        "content": converted_content,
                    }
                )
    return converted_message_params
