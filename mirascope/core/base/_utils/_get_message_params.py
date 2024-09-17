from __future__ import annotations

from collections.abc import Sequence
from typing import TYPE_CHECKING

from typing_extensions import TypeIs

from .. import AudioPart, BaseMessageParam, CacheControlPart, ImagePart, TextPart
from .._utils import get_image_type

if TYPE_CHECKING:
    from PIL import Image

    has_pil_module: bool
else:
    try:
        from PIL import Image  # pyright: ignore [reportAssignmentType]

        has_pil_module = True
    except ImportError:
        has_pil_module = False

        class Image:
            class Image:
                def tobytes(self) -> bytes: ...


def _get_content_part_from_message(
    message_sequence_part: str | Image.Image | TextPart | ImagePart | AudioPart,
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
    else:
        raise ValueError(f"Invalid message sequence type: {message_sequence_part}")


def get_content_from_message_sequence(
    message_sequence: Sequence[str | Image.Image | TextPart | ImagePart | AudioPart],
) -> list[TextPart | ImagePart | AudioPart | CacheControlPart]:
    return [_get_content_part_from_message(message) for message in message_sequence]


def _is_base_message_params(
    value: Sequence[str | Image.Image | TextPart | ImagePart | AudioPart]
    | list[BaseMessageParam],
) -> TypeIs[list[BaseMessageParam]]:
    return isinstance(value[0], BaseMessageParam)


def get_message_params(
    messages: str
    | Sequence[str | Image.Image | TextPart | ImagePart | AudioPart]
    | list[BaseMessageParam]
    | BaseMessageParam,
    role: str = "user",
) -> list[BaseMessageParam]:
    if isinstance(messages, str):
        return [BaseMessageParam(content=messages, role=role)]
    elif isinstance(messages, BaseMessageParam):
        return [messages]
    elif _is_base_message_params(messages):
        return messages
    elif isinstance(messages, Sequence):
        return [
            BaseMessageParam(
                content=get_content_from_message_sequence(messages), role=role
            )
        ]
    else:
        raise ValueError(f"Invalid messages type: {messages}")
