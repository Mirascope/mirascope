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
    Text | Image | Audio | Video | Document | ToolCall | ToolOutput | Thinking
)
"""Content types that can be included in messages."""
