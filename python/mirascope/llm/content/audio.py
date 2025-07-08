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
class Audio:
    """Audio content for a message.

    Audio can be included in messages for voice or sound-based interactions.
    """

    type: Literal["audio"] = "audio"

    id: str | None = None
    """A unique identifier for this audio content. This is useful for tracking and referencing generated audio."""

    data: str
    """The audio data, as a base64 encoded string."""

    transcript: str | None = None
    """The transcript of the audio, if available. This is useful for accessibility and search."""

    mime_type: AudioMimeType
    """The MIME type of the audio, e.g., 'audio/mp3', 'audio/wav'."""

    @classmethod
    def from_file(
        cls,
        file_path: str,
        *,
        mime_type: AudioMimeType | None,
        transcript: str | None = None,
        id: str | None = None,
    ) -> "Audio":
        """Create an Audio from a file path."""
        raise NotImplementedError

    @classmethod
    def from_bytes(
        cls,
        data: bytes,
        *,
        mime_type: AudioMimeType | None,
        transcript: str | None = None,
        id: str | None = None,
    ) -> "Audio":
        """Create an Audio from raw bytes."""
        raise NotImplementedError


@dataclass(kw_only=True)
class AudioUrl:
    """Audio content for a message, referenced by url.

    Use AudioUrl when you want to provide audio content, but have the LLM load it
    via http. This can be specified as input, but LLM generated audios will use standard
    audio content.
    """

    type: Literal["audio_url"] = "audio_url"

    url: str
    """The audio url."""

    mime_type: AudioMimeType | None
    """The MIME type of the audio, e.g., 'audio/png', 'audio/jpeg'."""
