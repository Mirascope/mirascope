from typing import TypeAlias

from .audio import Audio, AudioChunk, AudioUrl
from .chunk_boundary import ChunkEnd, ChunkStart
from .document import Document
from .image import Image, ImageChunk, ImageUrl
from .text import Text, TextChunk
from .thinking import Thinking, ThinkingChunk
from .tool_call import ToolCall, ToolCallChunk
from .tool_output import ToolOutput

UserContent: TypeAlias = (
    Text | Image | ImageUrl | Audio | AudioUrl | Document | ToolOutput
)
"""Content types that can be included in a UserMessage."""


AssistantContent: TypeAlias = Text | Image | Audio | ToolCall | Thinking
"""Content types that can be included in an AssistantMessage."""


SystemContent: TypeAlias = Text
"""Content types that can be included in a SystemMessage."""


ContentChunk: TypeAlias = (
    TextChunk
    | ImageChunk
    | AudioChunk
    | ToolCallChunk
    | ThinkingChunk
    | ChunkStart
    | ChunkEnd
)
"""Content chunk types that may be emitted by Streams."""
