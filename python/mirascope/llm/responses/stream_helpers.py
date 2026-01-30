"""Helper functions for streaming responses."""

from collections.abc import AsyncIterator, Iterator

from ..content import (
    AssistantContentChunk,
    TextChunk,
    ThoughtChunk,
    ToolCallChunk,
)
from .streams import (
    AsyncStream,
    AsyncTextStream,
    AsyncThoughtStream,
    AsyncToolCallStream,
    Stream,
    TextStream,
    ThoughtStream,
    ToolCallStream,
)


def pretty_chunk(chunk: AssistantContentChunk, spacer: str) -> str:
    """Format a chunk for human-readable output.

    Args:
        chunk: The content chunk to format.
        spacer: String to prepend (typically "" or "\\n\\n" between content parts).

    Returns:
        A formatted string representation of the chunk.
    """
    match chunk.type:
        case "text_start_chunk":
            return spacer
        case "text_chunk":
            return chunk.delta
        case "tool_call_start_chunk":
            return spacer + f"**ToolCall ({chunk.name}):** "
        case "tool_call_chunk":
            return chunk.delta
        case "thought_start_chunk":
            return spacer + "**Thinking:**\n  "
        case "thought_chunk":
            return chunk.delta.replace("\n", "\n  ")  # Indent every line
        case _:
            return ""


def sync_streams(
    chunk_iter: Iterator[AssistantContentChunk],
) -> Iterator[Stream]:
    """Yield Stream objects from a chunk iterator.

    Args:
        chunk_iter: Iterator yielding content chunks.

    Yields:
        Stream objects for each content part (text, thought, tool_call).
    """
    for start_chunk in chunk_iter:
        match start_chunk.type:
            case "text_start_chunk":

                def text_stream_iterator() -> Iterator[TextChunk]:
                    for chunk in chunk_iter:
                        if chunk.type == "text_chunk":
                            yield chunk
                        else:
                            return

                stream = TextStream(chunk_iterator=text_stream_iterator())
                yield stream

            case "thought_start_chunk":

                def thought_stream_iterator() -> Iterator[ThoughtChunk]:
                    for chunk in chunk_iter:
                        if chunk.type == "thought_chunk":
                            yield chunk
                        else:
                            return

                stream = ThoughtStream(chunk_iterator=thought_stream_iterator())
                yield stream

            case "tool_call_start_chunk":
                tool_id = start_chunk.id
                tool_name = start_chunk.name

                def tool_call_stream_iterator() -> Iterator[ToolCallChunk]:
                    for chunk in chunk_iter:
                        if chunk.type == "tool_call_chunk":
                            yield chunk
                        else:
                            return

                stream = ToolCallStream(
                    tool_id=tool_id,
                    tool_name=tool_name,
                    chunk_iterator=tool_call_stream_iterator(),
                )
                yield stream

            case _:  # pragma: no cover
                raise RuntimeError(f"Expected start chunk, got: {start_chunk.type}")

        stream.collect()


async def async_streams(
    chunk_iter: AsyncIterator[AssistantContentChunk],
) -> AsyncIterator[AsyncStream]:
    """Yield AsyncStream objects from an async chunk iterator.

    Args:
        chunk_iter: Async iterator yielding content chunks.

    Yields:
        AsyncStream objects for each content part (text, thought, tool_call).
    """
    async for start_chunk in chunk_iter:
        match start_chunk.type:
            case "text_start_chunk":

                async def text_stream_iterator() -> AsyncIterator[TextChunk]:
                    async for chunk in chunk_iter:
                        if chunk.type == "text_chunk":
                            yield chunk
                        else:
                            return

                stream = AsyncTextStream(chunk_iterator=text_stream_iterator())
                yield stream

            case "thought_start_chunk":

                async def thought_stream_iterator() -> AsyncIterator[ThoughtChunk]:
                    async for chunk in chunk_iter:
                        if chunk.type == "thought_chunk":
                            yield chunk
                        else:
                            return

                stream = AsyncThoughtStream(chunk_iterator=thought_stream_iterator())
                yield stream

            case "tool_call_start_chunk":
                tool_id = start_chunk.id
                tool_name = start_chunk.name

                async def tool_call_stream_iterator() -> AsyncIterator[ToolCallChunk]:
                    async for chunk in chunk_iter:
                        if chunk.type == "tool_call_chunk":
                            yield chunk
                        else:
                            return

                stream = AsyncToolCallStream(
                    tool_id=tool_id,
                    tool_name=tool_name,
                    chunk_iterator=tool_call_stream_iterator(),
                )
                yield stream

            case _:  # pragma: no cover
                raise RuntimeError(f"Expected start chunk, got: {start_chunk.type}")

        await stream.collect()
