from typing import TypeAlias

from .audio import Audio, AudioUrl
from .document import Document
from .image import Image, ImageUrl
from .thinking import Thinking
from .tool_call import ToolCall
from .tool_output import ToolOutput

UserContent: TypeAlias = (
    str | Image | ImageUrl | Audio | AudioUrl | Document | ToolOutput
)
"""Content types that can be included in a UserMessage."""

AssistantContent: TypeAlias = str | Image | Audio | ToolCall | Thinking
"""Content types that can be included in an AssistantMessage."""

SystemContent: TypeAlias = str
"""Content types that can be included in a SystemMessage."""
