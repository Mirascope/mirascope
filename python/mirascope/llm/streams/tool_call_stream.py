"""Tool call streaming classes."""

from collections.abc import AsyncIterator, Iterator
from typing import Literal

from ..content import ToolCall, ToolCallChunk
from ..types import Jsonable
from .base_stream import BaseAsyncStream, BaseStream


class ToolCallStream(BaseStream[ToolCallChunk, ToolCall]):
    """Synchronous tool call stream implementation."""

    type: Literal["tool_call_stream"] = "tool_call_stream"
    """The type identifier for tool call stream."""

    content_type: Literal["tool_call"] = "tool_call"
    """The type of content this stream handles."""

    tool_id: str
    """A unique identifier for this tool call."""

    tool_name: str
    """The name of the tool being called."""

    partial_args: dict[str, Jsonable]
    """The accumulated tool arguments as chunks are received."""

    def __iter__(self) -> Iterator[ToolCallChunk]:
        """Iterate over tool call chunks as they are received.

        Yields:
            ToolCallChunk: Each chunk containing accumulated args and JSON delta.
        """
        raise NotImplementedError()

    def collect(self) -> ToolCall:
        """Collect all chunks and return the final ToolCall content.

        Returns:
            ToolCall: The complete tool call after consuming all chunks.
        """
        raise NotImplementedError()


class AsyncToolCallStream(BaseAsyncStream[ToolCallChunk, ToolCall]):
    """Asynchronous tool call stream implementation."""

    type: Literal["async_tool_call_stream"] = "async_tool_call_stream"
    """The type identifier for async tool call stream."""

    content_type: Literal["tool_call"] = "tool_call"
    """The type of content this stream handles."""

    tool_id: str
    """A unique identifier for this tool call."""

    tool_name: str
    """The name of the tool being called."""

    partial_args: dict[str, Jsonable]
    """The accumulated tool arguments as chunks are received."""

    def __aiter__(self) -> AsyncIterator[ToolCallChunk]:
        """Asynchronously iterate over tool call chunks as they are received.

        Yields:
            ToolCallChunk: Each chunk containing accumulated args and JSON delta.
        """
        raise NotImplementedError()

    async def collect(self) -> ToolCall:
        """Asynchronously collect all chunks and return the final ToolCall content.

        Returns:
            ToolCall: The complete tool call after consuming all chunks.
        """
        raise NotImplementedError()
