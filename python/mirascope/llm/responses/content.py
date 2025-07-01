from typing import TypeAlias

from ..content import Audio, Image, Video
from ..tools import ContextTool, Tool

BaseResponseContent: TypeAlias = str | Image | Audio | Video
"""Base content response types that do not vary based on context."""

SimpleResponseContent: TypeAlias = BaseResponseContent | Tool
"""Content types that can be returned in a SimpleResponse (non-context)."""

ContextResponseContent: TypeAlias = BaseResponseContent | ContextTool
"""Content types that can be returned in a ContextResponse."""

ResponseContent: TypeAlias = SimpleResponseContent | ContextResponseContent
"""Content types that can be returned in a Response."""
