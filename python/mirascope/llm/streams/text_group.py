"""Text group classes for streaming text content."""

from typing import Literal

from .groups import BaseAsyncGroup, BaseGroup


class TextGroup(BaseGroup[str, str]):
    """Group for streaming text content chunks."""

    @property
    def type(self) -> Literal["text"]:
        """The type identifier for text groups."""
        raise NotImplementedError()


class AsyncTextGroup(BaseAsyncGroup[str, str]):
    """Async group for streaming text content chunks."""

    @property
    def type(self) -> Literal["text"]:
        """The type identifier for text groups."""
        raise NotImplementedError()
