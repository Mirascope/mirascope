"""This module contains the base class for message parameters."""

from typing import Literal

from pydantic import BaseModel


class TextPart(BaseModel):
    type: Literal["text"]
    text: str


class ImagePart(BaseModel):
    type: Literal["image"]
    media_type: str
    image: bytes
    detail: str | None


class AudioPart(BaseModel):
    type: Literal["audio"]
    media_type: str
    audio: bytes


class BaseMessageParam(BaseModel):
    """A base class for message parameters."""

    role: str
    content: str | list[TextPart | ImagePart | AudioPart]
