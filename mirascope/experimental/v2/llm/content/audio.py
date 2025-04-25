"""The `Audio` content class."""

from dataclasses import dataclass
from typing import Literal


@dataclass(kw_only=True)
class Audio:
    """Audio content for a message.

    Audio can be included in messages for voice or sound-based interactions.
    """

    type: Literal["audio"] = "audio"

    id: str | None
    """A unique identifier for this audio content. This is useful for tracking and referencing generated audio."""

    data: str | bytes
    """The audio data, which can be a URL, file path, base64-encoded string, or binary data."""

    transcript: str | None
    """The transcript of the audio, if available. This is useful for accessibility and search."""

    mime_type: Literal[
        "audio/wav",
        "audio/mp3",
        "audio/aiff",
        "audio/aac",
        "audio/ogg",
        "audio/flac",
    ]
    """The MIME type of the audio, e.g., 'audio/mp3', 'audio/wav'."""
