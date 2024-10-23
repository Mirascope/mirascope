from __future__ import annotations

from collections.abc import Sequence
from io import FileIO
from typing import cast
from wave import Wave_read

from pydantic import BaseModel
from typing_extensions import TypeIs

from .._utils._get_image_type import get_image_type
from ..message_param import (
    AudioPart,
    BaseMessageParam,
    CacheControlPart,
    ImagePart,
    TextPart,
)
from ..types import AudioSegment, Image, has_pil_module, has_pydub_module

SAMPLE_WIDTH = 2
FRAME_RATE = 24000
CHANNELS = 1


def _convert_message_sequence_part_to_content_part(
    message_sequence_part: str
    | Image.Image
    | TextPart
    | ImagePart
    | AudioPart
    | AudioSegment
    | Wave_read,
) -> TextPart | ImagePart | AudioPart | CacheControlPart:
    if isinstance(message_sequence_part, str):
        return TextPart(text=message_sequence_part, type="text")
    elif isinstance(
        message_sequence_part, TextPart | ImagePart | AudioPart | CacheControlPart
    ):
        return message_sequence_part
    elif has_pil_module and isinstance(message_sequence_part, Image.Image):
        image = message_sequence_part.tobytes()
        return ImagePart(
            type="image",
            media_type=f"image/{get_image_type(image)}",
            image=image,
            detail=None,
        )
    elif has_pydub_module and isinstance(message_sequence_part, AudioSegment):
        return AudioPart(
            type="audio",
            media_type="audio/wav",
            audio=cast(
                FileIO,
                message_sequence_part.set_frame_rate(FRAME_RATE)
                .set_channels(CHANNELS)
                .set_sample_width(SAMPLE_WIDTH)
                .export(format="wav"),
            ).read(),
        )
    elif isinstance(message_sequence_part, Wave_read):
        return AudioPart(
            type="audio",
            media_type="audio/wav",
            audio=message_sequence_part.readframes(-1),
        )
    else:
        raise ValueError(f"Invalid message sequence type: {message_sequence_part}")


def convert_message_content_to_message_param_content(
    message_sequence: Sequence[
        str | TextPart | ImagePart | Image.Image | AudioPart | AudioSegment | Wave_read
    ],
) -> list[TextPart | ImagePart | AudioPart | CacheControlPart] | str:
    if isinstance(message_sequence, str):
        return message_sequence
    return [
        _convert_message_sequence_part_to_content_part(message)
        for message in message_sequence
    ]


def _is_base_message_params(
    value: object,
) -> TypeIs[list[BaseMessageParam]]:
    # Note: we also need to catch the original provider message parameters here
    return isinstance(value, list) and all(
        isinstance(v, BaseMessageParam | dict | BaseModel) for v in value
    )


def convert_messages_to_message_params(
    messages: str
    | Sequence[
        str | TextPart | ImagePart | Image.Image | AudioPart | AudioSegment | Wave_read
    ]
    | list[BaseMessageParam]
    | BaseMessageParam,
    role: str = "user",
) -> list[BaseMessageParam]:
    if isinstance(messages, BaseMessageParam):
        return [messages]
    elif _is_base_message_params(messages):
        return messages
    elif isinstance(messages, str | Sequence):
        return [
            BaseMessageParam(
                content=convert_message_content_to_message_param_content(messages),
                role=role,
            )
        ]
    else:
        raise ValueError(f"Invalid messages type: {messages}")
