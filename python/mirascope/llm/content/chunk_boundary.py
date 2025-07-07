"""Chunk boundary classes for grouping related chunks."""

from dataclasses import dataclass
from typing import Literal


@dataclass(kw_only=True)
class ChunkStart:
    """Marks the beginning of a group of related chunks."""

    type: Literal["chunk_start"] = "chunk_start"

    subtype: Literal[
        "text_chunk", "image_chunk", "audio_chunk", "tool_call_chunk", "thinking_chunk"
    ]

    def __repr__(self) -> str:
        """Strategic representation for clean default printing."""
        if self.subtype == "text_chunk":
            return ""
        elif self.subtype == "image_chunk":
            return "{image:start}"
        elif self.subtype == "audio_chunk":
            return "{audio:start}"
        elif self.subtype == "tool_call_chunk":
            return "{tool:start}"
        elif self.subtype == "thinking_chunk":
            return "{thinking:start}"
        return f"{{chunk:start:{self.subtype}}}"


@dataclass(kw_only=True)
class ChunkEnd:
    """Marks the end of a group of related chunks."""

    type: Literal["chunk_end"] = "chunk_end"

    subtype: Literal[
        "text_chunk", "image_chunk", "audio_chunk", "tool_call_chunk", "thinking_chunk"
    ]

    def __repr__(self) -> str:
        """Strategic representation for clean default printing."""
        if self.subtype == "text_chunk":
            return "\n"
        elif self.subtype == "image_chunk":
            return "{image:done}"
        elif self.subtype == "audio_chunk":
            return "{audio:done}"
        elif self.subtype == "tool_call_chunk":
            return "{tool:done}"
        elif self.subtype == "thinking_chunk":
            return "{thinking:done}"
        return f"{{chunk:end:{self.subtype}}}"
