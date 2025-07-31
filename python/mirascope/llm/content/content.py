from typing import TypeAlias

from .audio import Audio, AudioUrl
from .document import Document
from .image import Image, ImageUrl
from .text import Text, TextChunk
from .thinking import Thinking, ThinkingChunk
from .tool_call import ToolCall, ToolCallChunk
from .tool_output import ToolOutput

UserContentPart: TypeAlias = (
    Text | Image | ImageUrl | Audio | AudioUrl | Document | ToolOutput
)
"""Content parts that can be included in a UserMessage."""

AssistantContentPart: TypeAlias = Text | ToolCall | Thinking
"""Content parts that can be included in an AssistantMessage."""

Chunk: TypeAlias = TextChunk | ToolCallChunk | ThinkingChunk
"""Chunk of AssistantContent for inclusion in Streams."""
