"""This module contains the base class for message parameters."""

from collections.abc import Sequence
from typing import Literal

from pydantic import BaseModel


class TextPart(BaseModel):
    """A content part for text.

    Attributes:
        type: Always "text"
        text: The text content
    """

    type: Literal["text"]
    text: str


class CacheControlPart(BaseModel):
    """A part for marking cache control.

    This part is currently only available with Anthropic. For more details, see:
    https://docs.anthropic.com/en/docs/build-with-claude/prompt-caching

    Attributes:
        type: Always "cache_control"
        cache_type: Currently only "ephemeral" is available.
    """

    type: Literal["cache_control"]
    cache_type: str


class ImagePart(BaseModel):
    """A content part for images.

    Attributes:
        type: Always "image"
        media_type: The media type (e.g. image/jpeg)
        image: The raw image bytes
        detail: (Optional) The detail to use for the image (supported by OpenAI)
    """

    type: Literal["image"]
    media_type: str
    image: bytes
    detail: str | None


class ImageURLPart(BaseModel):
    """A content part for images with a URL or base64 encoded image data.

    Attributes:
        type: Always "image_url"
        url: The URL to the image
        detail: (Optional) The detail to use for the image (supported by OpenAI)
    """

    type: Literal["image_url"]
    url: str
    detail: str | None


class AudioPart(BaseModel):
    """A content part for audio.

    Attributes:
        type: Always "audio"
        media_type: The media type (e.g. audio/wav)
        audio: The raw audio bytes or base64 encoded audio data
    """

    type: Literal["audio"]
    media_type: str
    audio: bytes | str


class AudioURLPart(BaseModel):
    """A content part for audio with a URL or base64 encoded audio data.

    Attributes:
        type: Always "audio_url"
        url: The URL to the audio
    """

    type: Literal["audio_url"]
    url: str


class DocumentPart(BaseModel):
    """A content part for pdf.

    Attributes:
        type: Always "document"
        media_type: The media type (e.g. application/pdf)
        document: document data
    """

    type: Literal["document"]
    media_type: str
    document: bytes


class ToolCallPart(BaseModel):
    """A content part for tool.

    Attributes:
        type: Always "tool"
        name: The name of the tool
        id: The id of the tool
    """

    type: Literal["tool_call"]
    name: str
    args: dict | None = None
    id: str | None = None


class ToolResultPart(BaseModel):
    """A content part for tool.

    Attributes:
        type: Always "tool"
        name: The name of the tool
        id: The id of the tool
    """

    type: Literal["tool_result"]
    name: str = ""
    content: str
    id: str | None = None
    is_error: bool = False


class BaseMessageParam(BaseModel):
    """A base class for message parameters.

    usage docs: learn/prompts.md#prompt-templates-messages

    Attributes:
        role: The role of the message (e.g. "system", "user", "assistant", "tool")
        content: The content of the message
        tool_name: The name of the tool, if any
    """

    role: str
    content: (
        str
        | Sequence[
            TextPart
            | ImagePart
            | ImageURLPart
            | AudioPart
            | AudioURLPart
            | CacheControlPart
            | DocumentPart
            | ToolCallPart
            | ToolResultPart
        ]
    )
