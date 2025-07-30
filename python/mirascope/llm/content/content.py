from typing import TypeAlias

from .audio import Audio, AudioUrl
from .document import Document
from .image import Image, ImageUrl
from .text import Text, TextPartial
from .thinking import Thinking, ThinkingPartial
from .tool_call import ToolCall, ToolCallPartial
from .tool_output import ToolOutput

UserContent: TypeAlias = (
    Text | Image | ImageUrl | Audio | AudioUrl | Document | ToolOutput
)
"""Content types that can be included in a UserMessage."""


AssistantContent: TypeAlias = Text | Image | Audio | ToolCall | Thinking
"""Content types that can be included in an AssistantMessage."""


SystemContent: TypeAlias = Text
"""Content types that can be included in a SystemMessage."""


PartialContent: TypeAlias = TextPartial | ToolCallPartial | ThinkingPartial
"""Partial content that may be emitted by streams."""
