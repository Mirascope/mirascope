from typing import TypeAlias

from .audio_chunk import AudioChunk
from .image_chunk import ImageChunk
from .text_chunk import TextChunk
from .thinking_chunk import ThinkingChunk
from .tool_call_chunk import ToolCallChunk
from .video_chunk import VideoChunk

StreamedContent: TypeAlias = (
    TextChunk | ImageChunk | AudioChunk | VideoChunk | ToolCallChunk | ThinkingChunk
)
"""Content types that can be included in messages."""
