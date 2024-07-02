"""Handles streaming content and tools from the Gemini API."""

from collections.abc import AsyncGenerator, Generator
from typing import Iterable

from google.generativeai.types import GenerateContentResponse  # type: ignore

from ..call_response_chunk import GeminiCallResponseChunk


def handle_stream(
    stream: Generator[GenerateContentResponse, None, None]
    | AsyncGenerator[GenerateContentResponse, None],
    tool_types: None = None,
) -> (
    Generator[tuple[GeminiCallResponseChunk, None], None, None]
    | AsyncGenerator[tuple[GeminiCallResponseChunk, None], None]
):
    """Iterator over the stream and constructs tools as they are streamed.

    Note: gemini does not currently support streaming tools.
    """
    if isinstance(stream, Iterable):

        def generator():
            for chunk in stream:
                yield GeminiCallResponseChunk(chunk=chunk), None

        return generator()
    else:

        async def async_generator():
            async for chunk in stream:
                yield GeminiCallResponseChunk(chunk=chunk), None

        return async_generator()
