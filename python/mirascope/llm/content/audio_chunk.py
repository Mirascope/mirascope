"""The `AudioChunk` content class."""

from dataclasses import dataclass
from typing import Literal


@dataclass(kw_only=True)
class AudioChunk:
    """Streaming audio content chunk."""

    type: Literal["audio_chunk"] = "audio_chunk"

    mime_type: Literal[
        "audio/wav",
        "audio/mp3",
        "audio/aiff",
        "audio/aac",
        "audio/ogg",
        "audio/flac",
    ]
    """The MIME type of the audio, e.g., 'audio/mp3', 'audio/wav'."""

    id: str | None = None
    """A unique identifier for this series of chunks, if available."""

    delta: str
    """The incremental audio in this chunk as a base64 encoded string."""

    partial: str
    """The accumulated audio data in this series of chunks as a base64 encoded string."""
