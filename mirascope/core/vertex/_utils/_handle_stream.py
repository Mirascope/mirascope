"""Handles streaming content and tools from the Vertex API."""

from collections.abc import AsyncGenerator, Generator

from vertexai.generative_models import GenerationResponse

from ..call_response_chunk import VertexCallResponseChunk
from ..tool import VertexTool


def handle_stream(
    stream: Generator[GenerationResponse, None, None],
    tool_types: list[type[VertexTool]] | None = None,
) -> Generator[tuple[VertexCallResponseChunk, None], None, None]:
    """Iterator over the stream and constructs tools as they are streamed.

    Note: vertex does not currently support streaming tools.
    """
    for chunk in stream:
        yield VertexCallResponseChunk(chunk=chunk), None


async def handle_stream_async(
    stream: AsyncGenerator[GenerationResponse, None],
    tool_types: list[type[VertexTool]] | None = None,
) -> AsyncGenerator[tuple[VertexCallResponseChunk, None], None]:
    """
    Async iterator over the stream and constructs tools as they are streamed.

    Note: vertex does not currently support streaming tools.
    """
    async for chunk in stream:
        yield VertexCallResponseChunk(chunk=chunk), None
