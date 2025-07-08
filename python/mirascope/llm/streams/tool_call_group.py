"""Tool call group classes for streaming tool call content."""

from typing import Literal

from ..content import ToolCall, ToolCallChunk
from .groups import BaseAsyncGroup, BaseGroup


class ToolCallGroup(BaseGroup[ToolCallChunk, ToolCall]):
    """Group for streaming tool call content chunks."""

    @property
    def type(self) -> Literal["tool_call"]:
        """The type identifier for tool call groups."""
        raise NotImplementedError()



class AsyncToolCallGroup(BaseAsyncGroup[ToolCallChunk, ToolCall]):
    """Async group for streaming tool call content chunks."""

    @property
    def type(self) -> Literal["tool_call"]:
        """The type identifier for tool call groups."""
        raise NotImplementedError()

