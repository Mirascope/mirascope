"""This module contains the base class for message parameters."""

from typing import Iterable, Literal

from typing_extensions import TypedDict


class _Image(TypedDict):
    type: Literal["image"]
    media_type: Literal["image/png", "image/jpeg", "image/gif", "image/webp"]
    base64_image: str
    detail: Literal["low", "high"] | None


class _Text(TypedDict):
    type: Literal["text"]
    content: str


class BaseMessageParam(TypedDict):
    """A base class for message parameters."""

    role: str
    content: str | Iterable[_Text | _Image]
