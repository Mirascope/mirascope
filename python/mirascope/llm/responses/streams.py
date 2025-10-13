"""Stream classes for streaming assistant content parts."""

from abc import ABC, abstractmethod
from collections.abc import AsyncIterator, Iterator
from typing import Generic, Literal, TypeAlias, TypeVar

from ..content import (
    AssistantContentPart,
    Text,
    TextChunk,
    Thought,
    ThoughtChunk,
    ToolCall,
    ToolCallChunk,
)

ContentT = TypeVar("ContentT", bound=AssistantContentPart)
"""Type variable for content types (Text, Thought, ToolCall)."""

ChunkT = TypeVar("ChunkT", bound=TextChunk | ThoughtChunk | ToolCallChunk)
"""Type variable for chunk types."""


class BaseStream(ABC, Generic[ContentT, ChunkT]):
    """Base class for synchronous streaming content."""

    @abstractmethod
    def __iter__(self) -> Iterator[ChunkT]:
        """Iterate over delta chunks as they are received."""
        ...

    @abstractmethod
    def collect(self) -> ContentT:
        """Collect all chunks and return the final content."""
        ...


class BaseAsyncStream(ABC, Generic[ContentT, ChunkT]):
    """Base class for asynchronous streaming content."""

    @abstractmethod
    def __aiter__(self) -> AsyncIterator[ChunkT]:
        """Asynchronously iterate over delta chunks as they are received."""
        ...

    @abstractmethod
    async def collect(self) -> ContentT:
        """Asynchronously collect all chunks and return the final content."""
        ...


class TextStream(BaseStream[Text, TextChunk]):
    """Synchronous text stream implementation."""

    type: Literal["text_stream"] = "text_stream"

    content_type: Literal["text"] = "text"
    """The type of content stored in this stream."""

    partial_text: str
    """The accumulated text content as chunks are received."""

    def __iter__(self) -> Iterator[TextChunk]:
        """Iterate over text chunks as they are received.

        Yields:
            TextChunk: Each delta chunk containing text.
        """
        raise NotImplementedError()

    def collect(self) -> Text:
        """Collect all chunks and return the final Text content.

        Returns:
            Text: The complete text content after consuming all chunks.
        """
        raise NotImplementedError()


class AsyncTextStream(BaseAsyncStream[Text, TextChunk]):
    """Asynchronous text stream implementation."""

    type: Literal["async_text_stream"] = "async_text_stream"

    content_type: Literal["text"] = "text"
    """The type of content stored in this stream."""

    partial_text: str
    """The accumulated text content as chunks are received."""

    def __aiter__(self) -> AsyncIterator[TextChunk]:
        """Asynchronously iterate over text chunks as they are received.

        Yields:
            TextChunk: Each delta chunk containing text.
        """
        raise NotImplementedError()

    async def collect(self) -> Text:
        """Asynchronously collect all chunks and return the final Text content.

        Returns:
            Text: The complete text content after consuming all chunks.
        """
        raise NotImplementedError()


class ThoughtStream(BaseStream[Thought, ThoughtChunk]):
    """Synchronous thought stream implementation."""

    type: Literal["thought_stream"] = "thought_stream"

    content_type: Literal["thought"] = "thought"
    """The type of content stored in this stream."""

    partial_thought: str
    """The accumulated thought content as chunks are received."""

    def __iter__(self) -> Iterator[ThoughtChunk]:
        """Iterate over thought chunks as they are received.

        Yields:
            ThoughtChunk: Each delta chunk containing thought text.
        """
        raise NotImplementedError()

    def collect(self) -> Thought:
        """Collect all chunks and return the final Thought content.

        Returns:
            Thought: The complete thought content after consuming all chunks.
        """
        raise NotImplementedError()


class AsyncThoughtStream(BaseAsyncStream[Thought, ThoughtChunk]):
    """Asynchronous thought stream implementation."""

    type: Literal["async_thought_stream"] = "async_thought_stream"

    content_type: Literal["thought"] = "thought"
    """The type of content stored in this stream."""

    partial_thought: str
    """The accumulated thought content as chunks are received."""

    def __aiter__(self) -> AsyncIterator[ThoughtChunk]:
        """Asynchronously iterate over thought chunks as they are received.

        Yields:
            ThoughtChunk: Each delta chunk containing thought text.
        """
        raise NotImplementedError()

    async def collect(self) -> Thought:
        """Asynchronously collect all chunks and return the final Thought content.

        Returns:
            Thought: The complete thought content after consuming all chunks.
        """
        raise NotImplementedError()


class ToolCallStream(BaseStream[ToolCall, ToolCallChunk]):
    """Synchronous tool call stream implementation."""

    type: Literal["tool_call_stream"] = "tool_call_stream"

    content_type: Literal["tool_call"] = "tool_call"
    """The type of content stored in this stream."""

    tool_id: str
    """A unique identifier for this tool call."""

    tool_name: str
    """The name of the tool being called."""

    partial_args: str
    """The accumulated tool arguments as chunks are received."""

    def __iter__(self) -> Iterator[ToolCallChunk]:
        """Iterate over tool call chunks as they are received.

        Yields:
            ToolCallChunk: Each delta chunk containing tool arguments.
        """
        raise NotImplementedError()

    def collect(self) -> ToolCall:
        """Collect all chunks and return the final ToolCall content.

        Returns:
            ToolCall: The complete tool call after consuming all chunks.
        """
        raise NotImplementedError()


class AsyncToolCallStream(BaseAsyncStream[ToolCall, ToolCallChunk]):
    """Asynchronous tool call stream implementation."""

    type: Literal["async_tool_call_stream"] = "async_tool_call_stream"

    content_type: Literal["tool_call"] = "tool_call"
    """The type of content stored in this stream."""

    tool_id: str
    """A unique identifier for this tool call."""

    tool_name: str
    """The name of the tool being called."""

    partial_args: str
    """The accumulated tool arguments as chunks are received."""

    def __aiter__(self) -> AsyncIterator[ToolCallChunk]:
        """Asynchronously iterate over tool call chunks as they are received.

        Yields:
            ToolCallChunk: Each delta chunk containing tool arguments.
        """
        raise NotImplementedError()

    async def collect(self) -> ToolCall:
        """Asynchronously collect all chunks and return the final ToolCall content.

        Returns:
            ToolCall: The complete tool call after consuming all chunks.
        """
        raise NotImplementedError()


Stream: TypeAlias = TextStream | ToolCallStream | ThoughtStream
"""A synchronous assistant content stream."""

AsyncStream: TypeAlias = AsyncTextStream | AsyncToolCallStream | AsyncThoughtStream
"""An asynchronous assistant content stream."""

__all__ = [
    "AsyncStream",
    "AsyncTextStream",
    "AsyncThoughtStream",
    "AsyncToolCallStream",
    "BaseAsyncStream",
    "BaseStream",
    "Stream",
    "TextStream",
    "ThoughtStream",
    "ToolCallStream",
]
