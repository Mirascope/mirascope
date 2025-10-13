"""Thought streaming classes."""

from collections.abc import AsyncIterator, Iterator
from typing import Literal

from ..content import Thought, ThoughtChunk
from .base_stream import BaseAsyncStream, BaseStream


class ThoughtStream(BaseStream[ThoughtChunk, Thought]):
    """Synchronous thought stream implementation."""

    type: Literal["thought_stream"] = "thought_stream"

    content_type: Literal["thought"] = "thought"
    """The type of content this stream handles."""

    partial: Thought
    """The accumulated thought content as chunks are received."""

    def __iter__(self) -> Iterator[ThoughtChunk]:
        """Iterate over thought chunks as they are received.

        Yields:
            ThoughtChunk: Each chunk containing accumulated thoughts and delta.
        """
        raise NotImplementedError()

    def collect(self) -> Thought:
        """Collect all chunks and return the final Thought content.

        Returns:
            Thought: The complete thought content after consuming all chunks.
        """
        raise NotImplementedError()


class AsyncThoughtStream(BaseAsyncStream[ThoughtChunk, Thought]):
    """Asynchronous thought stream implementation."""

    type: Literal["async_thought_stream"] = "async_thought_stream"

    content_type: Literal["thought"] = "thought"
    """The type of content this stream handles."""

    partial: Thought
    """The accumulated thought content as chunks are received."""

    def __aiter__(self) -> AsyncIterator[ThoughtChunk]:
        """Asynchronously iterate over thought chunks as they are received.

        Yields:
            ThoughtChunk: Each chunk containing accumulated thoughts and delta.
        """
        raise NotImplementedError()

    async def collect(self) -> Thought:
        """Asynchronously collect all chunks and return the final Thought content.

        Returns:
            Thought: The complete thought content after consuming all chunks.
        """
        raise NotImplementedError()
