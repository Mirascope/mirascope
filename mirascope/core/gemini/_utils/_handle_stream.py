"""Handles streaming content and tools from the Gemini API."""

from collections.abc import AsyncGenerator, Generator

from google.generativeai.types import GenerateContentResponse

from ..call_response_chunk import GeminiCallResponseChunk
from ..tool import GeminiTool


def handle_stream(
    stream: Generator[GenerateContentResponse, None, None],
    tool_types: list[type[GeminiTool]] | None = None,
) -> Generator[tuple[GeminiCallResponseChunk, None], None, None]:
    """Iterator over the stream and constructs tools as they are streamed.

    Note: gemini does not currently support streaming tools.
    """
    for chunk in stream:
        yield GeminiCallResponseChunk(chunk=chunk), None


async def handle_stream_async(
    stream: AsyncGenerator[GenerateContentResponse, None],
    tool_types: list[type[GeminiTool]] | None = None,
) -> AsyncGenerator[tuple[GeminiCallResponseChunk, None], None]:
    """
    Async iterator over the stream and constructs tools as they are streamed.

    Note: gemini does not currently support streaming tools.
    """
    async for chunk in stream:
        yield GeminiCallResponseChunk(chunk=chunk), None
