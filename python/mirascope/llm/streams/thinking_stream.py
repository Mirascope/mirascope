"""Thinking streaming classes."""

from collections.abc import AsyncIterator, Iterator
from typing import Literal

from ..content import Thinking, ThinkingChunk
from .base_stream import BaseAsyncStream, BaseStream


class ThinkingStream(BaseStream[ThinkingChunk, Thinking, Literal["thinking"]]):
    """Synchronous thinking stream implementation."""

    type: Literal["thinking_stream"] = "thinking_stream"

    @property
    def content_type(self) -> Literal["thinking"]:
        """The type of content this stream handles."""
        return "thinking"

    def __iter__(self) -> Iterator[ThinkingChunk]:
        """Iterate over thinking chunks as they are received.

        Yields:
            ThinkingChunk: Each chunk containing accumulated thoughts and delta.
        """
        raise NotImplementedError()

    def collect(self) -> Thinking:
        """Collect all chunks and return the final Thinking content.

        Returns:
            Thinking: The complete thinking content after consuming all chunks.
        """
        raise NotImplementedError()


class AsyncThinkingStream(
    BaseAsyncStream[ThinkingChunk, Thinking, Literal["thinking"]]
):
    """Asynchronous thinking stream implementation."""

    type: Literal["async_thinking_stream"] = "async_thinking_stream"

    @property
    def content_type(self) -> Literal["thinking"]:
        """The type of content this stream handles."""
        return "thinking"

    def __aiter__(self) -> AsyncIterator[ThinkingChunk]:
        """Asynchronously iterate over thinking chunks as they are received.

        Yields:
            ThinkingChunk: Each chunk containing accumulated thoughts and delta.
        """
        raise NotImplementedError()

    async def collect(self) -> Thinking:
        """Asynchronously collect all chunks and return the final Thinking content.

        Returns:
            Thinking: The complete thinking content after consuming all chunks.
        """
        raise NotImplementedError()
