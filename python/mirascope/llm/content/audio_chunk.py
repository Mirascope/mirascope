"""The `AudioChunk` content class."""

from dataclasses import dataclass
from typing import Literal

from .audio import AudioMimeType


@dataclass(kw_only=True)
class AudioChunk:
    """Streaming audio content chunk."""

    type: Literal["audio_chunk"] = "audio_chunk"

    mime_type: AudioMimeType
    """The MIME type of the audio, e.g., 'audio/mp3', 'audio/wav'."""

    id: str | None = None
    """A unique identifier for this series of chunks, if available."""

    delta: str
    """The incremental audio in this chunk as a base64 encoded string."""

    delta_transcript: str | None = None
    """The incremental transcript text in this chunk, if available."""

    final: bool
    """Whether this is the final piece of content in its sequence. If true, this content's partial is finished generating."""

    def __repr__(self) -> str:
        """Strategic representation for clean default printing."""
        return self.delta_transcript or "."
