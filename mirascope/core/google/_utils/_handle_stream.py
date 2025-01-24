"""Handles streaming content and tools from the Google API."""

from collections.abc import AsyncGenerator, Generator

from google.genai.types import GenerateContentResponse

from ..call_response_chunk import GoogleCallResponseChunk
from ..tool import GoogleTool


def handle_stream(
    stream: Generator[GenerateContentResponse, None, None],
    tool_types: list[type[GoogleTool]] | None = None,
    partial_tools: bool = False,
) -> Generator[tuple[GoogleCallResponseChunk, None], None, None]:
    """Iterator over the stream and constructs tools as they are streamed.

    Note: google does not currently support streaming tools.
    """
    for chunk in stream:
        yield GoogleCallResponseChunk(chunk=chunk), None


async def handle_stream_async(
    stream: AsyncGenerator[GenerateContentResponse, None],
    tool_types: list[type[GoogleTool]] | None = None,
    partial_tools: bool = False,
) -> AsyncGenerator[tuple[GoogleCallResponseChunk, None], None]:
    """
    Async iterator over the stream and constructs tools as they are streamed.

    Note: google does not currently support streaming tools.
    """
    async for chunk in stream:
        yield GoogleCallResponseChunk(chunk=chunk), None
