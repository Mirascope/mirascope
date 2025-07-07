"""The `TextChunk` content class."""

from dataclasses import dataclass
from typing import Literal


@dataclass(kw_only=True)
class ChunkBoundary:
    """Demarcates the start or end of a group of related chunks."""

    type: Literal["chunk_start", "chunk_end"]

    subtype: Literal[
        "text_chunk", "image_chunk", "audio_chunk", "tool_call_chunk", "thinking_chunk"
    ]
