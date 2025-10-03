"""The `Audio` content class."""

from dataclasses import dataclass
from typing import Literal

AudioMimeType = Literal[
    "audio/wav",
    "audio/mp3",
    "audio/aiff",
    "audio/aac",
    "audio/ogg",
    "audio/flac",
]


@dataclass(kw_only=True)
class Base64AudioSource:
    """Audio data represented as a base64 encoded string."""

    type: Literal["base64_audio_source"]

    data: str
    """The audio data, as a base64 encoded string."""

    mime_type: AudioMimeType
    """The mime type of the audio (e.g. audio/mp3)."""


@dataclass(kw_only=True)
class Audio:
    """Audio content for a message.

    Audio can be included in messages for voice or sound-based interactions.
    """

    type: Literal["audio"] = "audio"

    content_type: Literal["audio"] = "audio"
    """The type of content being represented."""

    source: Base64AudioSource

    @classmethod
    def from_url(
        cls,
        url: str,
    ) -> "Audio":
        """Create an `Audio` from a URL."""
        raise NotImplementedError

    @classmethod
    def from_file(
        cls,
        file_path: str,
        *,
        mime_type: AudioMimeType | None,
    ) -> "Audio":
        """Create an `Audio` from a file path."""
        raise NotImplementedError

    @classmethod
    def from_bytes(
        cls,
        data: bytes,
        *,
        mime_type: AudioMimeType | None,
    ) -> "Audio":
        """Create an `Audio` from raw bytes."""
        raise NotImplementedError
