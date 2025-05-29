from typing import TypeAlias

from ..content import Audio, Image, Video
from ..tools import ContextTool, Tool

ResponseContent: TypeAlias = str | Image | Audio | Video | Tool
"""Content types that can be returned in a model response."""

ContextResponseContent: TypeAlias = str | Image | Audio | Video | ContextTool
"""Content types that can be returned in a model response with context."""
