"""This module contains the base class for message parameters."""

from typing import Literal

from typing_extensions import TypedDict

_Detail = Literal["auto", "low", "high"]


class TextPart(TypedDict):
    type: Literal["text"]
    text: str


class ImagePart(TypedDict):
    type: Literal["image"]
    media_type: str
    image: bytes
    detail: _Detail | None


class AudioPart(TypedDict):
    type: Literal["audio"]
    media_type: str
    audio: bytes


class BaseMessageParam(TypedDict):
    """A base class for message parameters."""

    role: str
    content: list[TextPart | ImagePart | AudioPart]
