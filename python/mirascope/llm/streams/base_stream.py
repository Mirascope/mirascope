"""Base stream classes for sync and async streaming."""

from abc import ABC, abstractmethod
from collections.abc import AsyncIterator, Iterator
from typing import Generic, TypeVar

from ..content import AssistantContentChunk, AssistantContentPart

ChunkT = TypeVar("ChunkT", bound=AssistantContentChunk)
"""Type variable for chunk types (e.g., TextChunk, ThinkingChunk, ToolCallChunk)."""

ContentT = TypeVar("ContentT", bound=AssistantContentPart)
"""Type variable for final content types (e.g., Text, Thinking, ToolCall)."""


class BaseStream(ABC, Generic[ChunkT, ContentT]):
    """Base class for synchronous streaming content."""

    partial: ContentT
    """The accumulated content as chunks are received."""

    @abstractmethod
    def __iter__(self) -> Iterator[ChunkT]:
        """Iterate over chunks as they are received."""
        ...

    @abstractmethod
    def collect(self) -> ContentT:
        """Collect all chunks and return the final content."""
        ...


class BaseAsyncStream(ABC, Generic[ChunkT, ContentT]):
    """Base class for asynchronous streaming content."""

    partial: ContentT
    """The accumulated content as chunks are received."""

    @abstractmethod
    def __aiter__(self) -> AsyncIterator[ChunkT]:
        """Asynchronously iterate over chunks as they are received."""
        ...

    @abstractmethod
    async def collect(self) -> ContentT:
        """Asynchronously collect all chunks and return the final content."""
        ...
