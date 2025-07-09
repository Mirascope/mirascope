from typing import TypeAlias

from .audio_chunk import AudioChunk
from .chunk_boundary import ChunkEnd, ChunkStart
from .image_chunk import ImageChunk
from .thinking_chunk import ThinkingChunk
from .tool_call_chunk import ToolCallChunk

ContentChunk: TypeAlias = (
    str
    | ImageChunk
    | AudioChunk
    | ToolCallChunk
    | ThinkingChunk
    | ChunkStart
    | ChunkEnd
)
"""Content chunk types that may be emitted by Streams."""
