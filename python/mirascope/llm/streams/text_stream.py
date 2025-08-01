"""Text streaming classes."""

from collections.abc import AsyncIterator, Iterator
from typing import Literal

from ..content import Text, TextChunk
from .base_stream import BaseAsyncStream, BaseStream


class TextStream(BaseStream[TextChunk, Text]):
    """Synchronous text stream implementation."""

    type: Literal["text_stream"] = "text_stream"

    content_type: Literal["text"] = "text"
    """The type of content this stream handles."""

    partial_text: str
    """The accumulated text content as chunks are received."""

    def __iter__(self) -> Iterator[TextChunk]:
        """Iterate over text chunks as they are received.

        Yields:
            TextChunk: Each chunk containing accumulated text and delta.
        """
        raise NotImplementedError()

    def collect(self) -> Text:
        """Collect all chunks and return the final Text content.

        Returns:
            Text: The complete text content after consuming all chunks.
        """
        raise NotImplementedError()


class AsyncTextStream(BaseAsyncStream[TextChunk, Text]):
    """Asynchronous text stream implementation."""

    type: Literal["async_text_stream"] = "async_text_stream"

    content_type: Literal["text"] = "text"
    """The type of content this stream handles."""

    partial_text: str
    """The accumulated text content as chunks are received."""

    def __aiter__(self) -> AsyncIterator[TextChunk]:
        """Asynchronously iterate over text chunks as they are received.

        Yields:
            TextChunk: Each chunk containing accumulated text and delta.
        """
        raise NotImplementedError()

    async def collect(self) -> Text:
        """Asynchronously collect all chunks and return the final Text content.

        Returns:
            Text: The complete text content after consuming all chunks.
        """
        raise NotImplementedError()
