"""Thinking group classes for streaming thinking content."""

from typing import Literal

from ..content import Thinking, ThinkingChunk
from .groups import BaseAsyncGroup, BaseGroup


class ThinkingGroup(BaseGroup[ThinkingChunk, Thinking]):
    """Group for streaming thinking content chunks."""

    @property
    def type(self) -> Literal["thinking"]:
        """The type identifier for thinking groups."""
        raise NotImplementedError()


class AsyncThinkingGroup(BaseAsyncGroup[ThinkingChunk, Thinking]):
    """Async group for streaming thinking content chunks."""

    @property
    def type(self) -> Literal["thinking"]:
        """The type identifier for thinking groups."""
        raise NotImplementedError()
