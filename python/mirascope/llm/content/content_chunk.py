from typing import TypeAlias

from .audios.audio_chunk import AudioChunk
from .images.image_chunk import ImageChunk
from .texts.text_chunk import TextChunk
from .thinking.thinking_chunk import ThinkingChunk
from .tools.tool_call_chunk import ToolCallChunk

ContentChunk: TypeAlias = (
    TextChunk | ImageChunk | AudioChunk | ToolCallChunk | ThinkingChunk
)
"""Content chunk types that may be emitted by Streams."""
