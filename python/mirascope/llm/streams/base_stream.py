"""Base stream classes for sync and async streaming."""

from abc import ABC, abstractmethod
from collections.abc import AsyncIterator, Iterator
from typing import Generic, TypeVar

from ..content import AssistantContentPart, Chunk, StreamableContentType

ChunkT = TypeVar("ChunkT", bound=Chunk)
"""Type variable for chunk types (e.g., TextChunk, ThinkingChunk, ToolCallChunk)."""

ContentT = TypeVar("ContentT", bound=AssistantContentPart)
"""Type variable for final content types (e.g., Text, Thinking, ToolCall)."""

ContentTypeT = TypeVar("ContentTypeT", bound=StreamableContentType)
"""Type variable for streamable content types, constrained to StreamableContentType."""


class BaseStream(ABC, Generic[ChunkT, ContentT, ContentTypeT]):
    """Base class for synchronous streaming content."""

    @property
    @abstractmethod
    def content_type(self) -> ContentTypeT:
        """The type of content this stream handles."""
        ...

    @abstractmethod
    def __iter__(self) -> Iterator[ChunkT]:
        """Iterate over chunks as they are received."""
        ...

    @abstractmethod
    def collect(self) -> ContentT:
        """Collect all chunks and return the final content."""
        ...


class BaseAsyncStream(ABC, Generic[ChunkT, ContentT, ContentTypeT]):
    """Base class for asynchronous streaming content."""

    @property
    @abstractmethod
    def content_type(self) -> ContentTypeT:
        """The type of content this stream handles."""
        ...

    @abstractmethod
    def __aiter__(self) -> AsyncIterator[ChunkT]:
        """Asynchronously iterate over chunks as they are received."""
        ...

    @abstractmethod
    async def collect(self) -> ContentT:
        """Asynchronously collect all chunks and return the final content."""
        ...
