"""The `llm.messages.content` module."""

from typing import TypeAlias

from .audio import Audio
from .document import Document
from .image import Image
from .text import Text
from .thinking import Thinking
from .tool_call import ToolCall
from .tool_output import ToolOutput
from .video import Video

Content: TypeAlias = (
    str | Text | Image | Audio | Video | Document | ToolCall | ToolOutput | Thinking
)
"""Content types that can be included in messages."""


__all__ = [
    "Audio",
    "Content",
    "Document",
    "Image",
    "Text",
    "Thinking",
    "ToolCall",
    "ToolOutput",
    "Video",
]
