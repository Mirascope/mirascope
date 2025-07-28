"""Text group classes for streaming text content."""

from typing import Literal

from ..content import Text, TextChunk
from .groups import BaseAsyncGroup, BaseGroup


class TextGroup(BaseGroup[TextChunk, Text]):
    """Group for streaming text content chunks."""

    @property
    def type(self) -> Literal["text"]:
        """The type identifier for text groups."""
        raise NotImplementedError()


class AsyncTextGroup(BaseAsyncGroup[TextChunk, Text]):
    """Async group for streaming text content chunks."""

    @property
    def type(self) -> Literal["text"]:
        """The type identifier for text groups."""
        raise NotImplementedError()
