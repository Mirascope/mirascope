"""This module contains the base class for message parameters."""

from typing import Literal

from typing_extensions import TypedDict

_PartType = Literal["text", "image", "images"]
_Detail = Literal["auto", "low", "high"]


class ImagePart(TypedDict):
    type: Literal["image"]
    media_type: str
    image: bytes
    detail: _Detail | None


class TextPart(TypedDict):
    type: Literal["text"]
    text: str


class BaseMessageParam(TypedDict):
    """A base class for message parameters."""

    role: str
    content: list[TextPart | ImagePart]
