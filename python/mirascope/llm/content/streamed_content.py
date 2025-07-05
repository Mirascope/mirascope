from typing import TypeAlias

from .audio_chunk import AudioChunk
from .image_partial import ImagePartial
from .text_chunk import TextChunk
from .thinking_chunk import ThinkingChunk
from .tool_call_chunk import ToolCallChunk

StreamedContent: TypeAlias = (
    TextChunk | ImagePartial | AudioChunk | ToolCallChunk | ThinkingChunk
)
"""Content types that can be included in streamed responses."""
