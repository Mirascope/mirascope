from collections.abc import AsyncIterator, Iterator
from typing import Generic, Literal, TypeAlias, TypeVar

from .content import (
    AssistantContent,
    PartialContent,
    Text,
    TextPartial,
    Thinking,
    ThinkingPartial,
    ToolCall,
    ToolCallPartial,
)

StreamPartialT = TypeVar("StreamPartialT", bound=PartialContent)
StreamContentT = TypeVar("StreamContentT", bound=AssistantContent)


class BaseStream(Generic[StreamPartialT, StreamContentT]):
    @property
    def type(
        self,
    ) -> Literal["text"] | Literal["thinking"] | Literal["tool_call"]:
        """The type identifier for this stream."""
        raise NotImplementedError()

    def collect(self) -> StreamContentT:
        """Collects the final combined content part in this stream.

        Calling this will iterate through the stream if it is not already exhausted."""
        raise NotImplementedError()

    def __iter__(self) -> Iterator[StreamPartialT]:
        """Iterates through the partial content in the stream."""
        raise NotImplementedError()


class BaseAsyncStream(Generic[StreamPartialT, StreamContentT]):
    @property
    def type(
        self,
    ) -> Literal["text"] | Literal["thinking"] | Literal["tool_call"]:
        """The type identifier for this stream."""
        raise NotImplementedError()

    async def collect(self) -> StreamContentT:
        """Collects the final combined content part in this stream.

        Calling this will iterate through the stream if it is not already exhausted."""
        raise NotImplementedError()

    def __aiter__(self) -> AsyncIterator[StreamPartialT]:
        """Iterates through the partial content in the stream."""
        raise NotImplementedError()


class TextStream(BaseStream[TextPartial, Text]):
    @property
    def type(self) -> Literal["text"]:
        """The type identifier for text groups."""
        return "text"


class AsyncTextStream(BaseAsyncStream[TextPartial, Text]):
    @property
    def type(self) -> Literal["text"]:
        """The type identifier for text groups."""
        return "text"


class ToolCallStream(BaseStream[ToolCallPartial, ToolCall]):
    @property
    def type(self) -> Literal["tool_call"]:
        """The type identifier for tool call streams."""
        return "tool_call"


class AsyncToolCallStream(BaseAsyncStream[ToolCallPartial, ToolCall]):
    @property
    def type(self) -> Literal["tool_call"]:
        """The type identifier for tool call streams."""
        return "tool_call"


class ThinkingStream(BaseStream[ThinkingPartial, Thinking]):
    @property
    def type(self) -> Literal["thinking"]:
        """The type identifier for thinking streams."""
        return "thinking"


class AsyncThinkingStream(BaseAsyncStream[ThinkingPartial, Thinking]):
    @property
    def type(self) -> Literal["thinking"]:
        """The type identifier for thinking streams."""
        return "thinking"


Stream: TypeAlias = TextStream | ToolCallStream | ThinkingStream
AsyncStream: TypeAlias = AsyncTextStream | AsyncToolCallStream | AsyncThinkingStream
