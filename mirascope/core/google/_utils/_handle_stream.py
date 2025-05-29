"""Handles streaming content and tools from the Google API."""

from collections.abc import AsyncGenerator, Generator

from google.genai.types import GenerateContentResponse

from ..call_response_chunk import GoogleCallResponseChunk
from ..tool import GoogleTool


def _handle_chunk(
    chunk: GenerateContentResponse, tool_types: list[type[GoogleTool]] | None = None
) -> Generator[tuple[GoogleCallResponseChunk, GoogleTool | None], None, None]:
    """Handles a chunk of the stream and yields any tools that are found.

    Note: google seems to only ever return full tool calls, so no partial possible here.
    """
    call_response_chunk = GoogleCallResponseChunk(chunk=chunk)
    has_tools = False
    if tool_types and (
        (candidates := chunk.candidates)
        and (content := candidates[0].content)
        and (parts := content.parts)
    ):
        for part in parts:
            if function_call := part.function_call:
                has_tools = True
                for tool_type in tool_types:
                    if tool_type._name() == function_call.name:
                        tool = tool_type.from_tool_call(function_call)
                        yield (call_response_chunk, tool)
    if not has_tools:
        yield call_response_chunk, None


def handle_stream(
    stream: Generator[GenerateContentResponse, None, None],
    tool_types: list[type[GoogleTool]] | None = None,
    partial_tools: bool = False,
) -> Generator[tuple[GoogleCallResponseChunk, GoogleTool | None], None, None]:
    """Iterator over the stream and constructs tools as they are streamed."""
    for chunk in stream:
        yield from _handle_chunk(chunk, tool_types)


async def handle_stream_async(
    stream: AsyncGenerator[GenerateContentResponse, None],
    tool_types: list[type[GoogleTool]] | None = None,
    partial_tools: bool = False,
) -> AsyncGenerator[tuple[GoogleCallResponseChunk, GoogleTool | None], None]:
    """
    Async iterator over the stream and constructs tools as they are streamed.

    Note: google does not currently support streaming tools.
    """
    async for chunk in stream:
        for call_response_chunk, tool in _handle_chunk(chunk, tool_types):
            yield call_response_chunk, tool
