"""Handles the stream of completion chunks."""

from collections.abc import AsyncGenerator, Generator

from cohere.types import StreamedChatResponse

from ..call_response_chunk import CohereCallResponseChunk
from ..tool import CohereTool


def handle_stream(
    stream: Generator[StreamedChatResponse, None, None],
    tool_types: list[type[CohereTool]] | None = None,
    partial_tools: bool = False,
) -> Generator[tuple[CohereCallResponseChunk, None], None, None]:
    """Iterator over the stream and constructs tools as they are streamed.

    Note: cohere does not currently support streaming tools.
    """
    for chunk in stream:
        yield CohereCallResponseChunk(chunk=chunk), None


async def handle_stream_async(
    stream: AsyncGenerator[StreamedChatResponse, None],
    tool_types: list[type[CohereTool]] | None = None,
    partial_tools: bool = False,
) -> AsyncGenerator[tuple[CohereCallResponseChunk, None], None]:
    """
    Async iterator over the stream and constructs tools as they are streamed.

    Note: cohere does not currently support streaming tools.
    """
    async for chunk in stream:
        yield CohereCallResponseChunk(chunk=chunk), None
