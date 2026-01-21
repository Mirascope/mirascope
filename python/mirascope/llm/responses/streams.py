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

DeltaT = TypeVar("DeltaT")
"""Type variable for the deltas that the stream provides on iteration."""


class BaseStream(ABC, Generic[ContentT, DeltaT]):
    """Base class for synchronous streaming content."""

    @abstractmethod
    def __iter__(self) -> Iterator[DeltaT]:
        """Iterate over content deltas as they arrive."""
        ...

    @abstractmethod
    def collect(self) -> ContentT:
        """Collect all chunks and return the final content."""
        ...


class BaseAsyncStream(ABC, Generic[ContentT, DeltaT]):
    """Base class for asynchronous streaming content."""

    @abstractmethod
    def __aiter__(self) -> AsyncIterator[DeltaT]:
        """Asynchronously iterate over content deltas as they arrive."""
        ...

    @abstractmethod
    async def collect(self) -> ContentT:
        """Asynchronously collect all chunks and return the final content."""
        ...


class TextStream(BaseStream[Text, str]):
    """Synchronous text stream implementation."""

    type: Literal["text_stream"] = "text_stream"

    content_type: Literal["text"] = "text"
    """The type of content stored in this stream."""

    partial_text: str
    """The accumulated text content as chunks are received."""

    def __init__(
        self,
        chunk_iterator: Iterator[TextChunk],
    ) -> None:
        """Initialize TextStream with a start chunk and chunk iterator.

        Args:
            chunk_iterator: Iterator providing subsequent chunks.
        """
        self.partial_text = ""
        self._chunk_iterator = chunk_iterator

    def __iter__(self) -> Iterator[str]:
        """Iterate over text deltas as they are received.

        Yields:
            str: Each delta string containing text.
        """
        for chunk in self._chunk_iterator:
            delta = chunk.delta
            self.partial_text += delta
            yield delta

    def collect(self) -> Text:
        """Collect all chunks and return the final Text content.

        Returns:
            Text: The complete text content after consuming all chunks.
        """
        for _ in self:
            pass
        return Text(text=self.partial_text)


class AsyncTextStream(BaseAsyncStream[Text, str]):
    """Asynchronous text stream implementation."""

    type: Literal["async_text_stream"] = "async_text_stream"

    content_type: Literal["text"] = "text"
    """The type of content stored in this stream."""

    partial_text: str
    """The accumulated text content as chunks are received."""

    def __init__(
        self,
        chunk_iterator: AsyncIterator[TextChunk],
    ) -> None:
        """Initialize AsyncTextStream with a chunk iterator.

        Args:
            chunk_iterator: AsyncIterator providing subsequent chunks.
        """
        self.partial_text = ""
        self._chunk_iterator = chunk_iterator

    async def __aiter__(self) -> AsyncIterator[str]:
        """Asynchronously iterate over text deltas as they are received.

        Yields:
            str: Each delta string containing text.
        """
        async for chunk in self._chunk_iterator:
            delta = chunk.delta
            self.partial_text += delta
            yield delta

    async def collect(self) -> Text:
        """Asynchronously collect all chunks and return the final Text content.

        Returns:
            Text: The complete text content after consuming all chunks.
        """
        async for _ in self:
            pass
        return Text(text=self.partial_text)


class ThoughtStream(BaseStream[Thought, str]):
    """Synchronous thought stream implementation."""

    type: Literal["thought_stream"] = "thought_stream"

    content_type: Literal["thought"] = "thought"
    """The type of content stored in this stream."""

    partial_thought: str
    """The accumulated thought content as chunks are received."""

    def __init__(
        self,
        chunk_iterator: Iterator[ThoughtChunk],
    ) -> None:
        """Initialize ThoughtStream with a chunk iterator.

        Args:
            chunk_iterator: Iterator providing subsequent chunks.
        """
        self.partial_thought = ""
        self._chunk_iterator = chunk_iterator

    def __iter__(self) -> Iterator[str]:
        """Iterate over thought deltas as they are received.

        Yields:
            str: Each delta string containing thought text.
        """
        for chunk in self._chunk_iterator:
            delta = chunk.delta
            self.partial_thought += delta
            yield delta

    def collect(self) -> Thought:
        """Collect all chunks and return the final Thought content.

        Returns:
            Thought: The complete thought content after consuming all chunks.
        """
        for _ in self:
            pass
        return Thought(thought=self.partial_thought)


class AsyncThoughtStream(BaseAsyncStream[Thought, str]):
    """Asynchronous thought stream implementation."""

    type: Literal["async_thought_stream"] = "async_thought_stream"

    content_type: Literal["thought"] = "thought"
    """The type of content stored in this stream."""

    partial_thought: str
    """The accumulated thought content as chunks are received."""

    def __init__(
        self,
        chunk_iterator: AsyncIterator[ThoughtChunk],
    ) -> None:
        """Initialize AsyncThoughtStream with a chunk iterator.

        Args:
            chunk_iterator: AsyncIterator providing subsequent chunks.
        """
        self.partial_thought = ""
        self._chunk_iterator = chunk_iterator

    async def __aiter__(self) -> AsyncIterator[str]:
        """Asynchronously iterate over thought deltas as they are received.

        Yields:
            str: Each delta string containing thought text.
        """
        async for chunk in self._chunk_iterator:
            delta = chunk.delta
            self.partial_thought += delta
            yield delta

    async def collect(self) -> Thought:
        """Asynchronously collect all chunks and return the final Thought content.

        Returns:
            Thought: The complete thought content after consuming all chunks.
        """
        async for _ in self:
            pass
        return Thought(thought=self.partial_thought)


class ToolCallStream(BaseStream[ToolCall, str]):
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

    def __init__(
        self,
        tool_id: str,
        tool_name: str,
        chunk_iterator: Iterator[ToolCallChunk],
    ) -> None:
        """Initialize ToolCallStream with tool metadata and chunk iterator.

        Args:
            tool_id: A unique identifier for this tool call.
            tool_name: The name of the tool being called.
            chunk_iterator: Iterator providing subsequent chunks.
        """
        self.tool_id = tool_id
        self.tool_name = tool_name
        self.partial_args = ""
        self._chunk_iterator = chunk_iterator

    def __iter__(self) -> Iterator[str]:
        """Iterate over tool call argument deltas as they are received.

        Yields:
            str: Each delta string containing JSON argument fragments.
        """
        for chunk in self._chunk_iterator:
            delta = chunk.delta
            self.partial_args += delta
            yield delta

    def collect(self) -> ToolCall:
        """Collect all chunks and return the final ToolCall content.

        Returns:
            ToolCall: The complete tool call after consuming all chunks.
        """
        for _ in self:
            pass
        return ToolCall(id=self.tool_id, name=self.tool_name, args=self.partial_args)


class AsyncToolCallStream(BaseAsyncStream[ToolCall, str]):
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

    def __init__(
        self,
        tool_id: str,
        tool_name: str,
        chunk_iterator: AsyncIterator[ToolCallChunk],
    ) -> None:
        """Initialize AsyncToolCallStream with tool metadata and chunk iterator.

        Args:
            tool_id: A unique identifier for this tool call.
            tool_name: The name of the tool being called.
            chunk_iterator: AsyncIterator providing subsequent chunks.
        """
        self.tool_id = tool_id
        self.tool_name = tool_name
        self.partial_args = ""
        self._chunk_iterator = chunk_iterator

    async def __aiter__(self) -> AsyncIterator[str]:
        """Asynchronously iterate over tool call argument deltas as they are received.

        Yields:
            str: Each delta string containing JSON argument fragments.
        """
        async for chunk in self._chunk_iterator:
            delta = chunk.delta
            self.partial_args += delta
            yield delta

    async def collect(self) -> ToolCall:
        """Asynchronously collect all chunks and return the final ToolCall content.

        Returns:
            ToolCall: The complete tool call after consuming all chunks.
        """
        async for _ in self:
            pass
        return ToolCall(id=self.tool_id, name=self.tool_name, args=self.partial_args)


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
