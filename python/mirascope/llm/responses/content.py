"""The content types for specific response types."""

from typing import TypeAlias

from typing_extensions import TypeVar

from ..content import Audio, Image, Thinking, Video
from ..tools import ContextTool, Tool

ToolT = TypeVar("ToolT", bound=Tool | ContextTool)

BaseResponseContent: TypeAlias = str | Image | Audio | Video | Thinking | ToolT
"""Base content response types that do not vary based on context."""

ResponseContent: TypeAlias = BaseResponseContent[Tool]
"""Content types that can be returned in a SimpleResponse (non-context)."""

ContextResponseContent: TypeAlias = BaseResponseContent[ContextTool]
"""Content types that can be returned in a ContextResponse."""
