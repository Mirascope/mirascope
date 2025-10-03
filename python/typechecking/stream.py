from collections.abc import AsyncIterator, Iterator
from typing_extensions import assert_never, assert_type

from mirascope import llm


def stream_response() -> llm.StreamResponse:
    raise NotImplementedError()


def async_stream_response() -> llm.AsyncStreamResponse:
    raise NotImplementedError()


def stream_type_safety():
    for chunk in stream_response().pretty_stream():
        assert_type(chunk, str)

    streams: Iterator[llm.Stream] = stream_response().streams()
    for stream in streams:
        match stream.content_type:
            case "text":
                assert_type(stream, llm.streams.TextStream)
                for chunk in stream:
                    assert_type(chunk, llm.content.TextChunk)
            case "tool_call":
                assert_type(stream, llm.streams.ToolCallStream)
                for chunk in stream:
                    assert_type(chunk, llm.content.ToolCallChunk)
            case "thought":
                assert_type(stream, llm.streams.ThoughtStream)
                for chunk in stream:
                    assert_type(chunk, llm.content.ThoughtChunk)
            case _:
                assert_never(stream.content_type)


async def async_stream_type_safety():
    async for chunk in async_stream_response().pretty_stream():
        assert_type(chunk, str)

    streams: AsyncIterator[llm.AsyncStream] = await async_stream_response().streams()
    async for stream in streams:
        match stream.content_type:
            case "text":
                assert_type(stream, llm.streams.AsyncTextStream)
                async for chunk in stream:
                    assert_type(chunk, llm.content.TextChunk)
            case "tool_call":
                assert_type(stream, llm.streams.AsyncToolCallStream)
                async for chunk in stream:
                    assert_type(chunk, llm.content.ToolCallChunk)
            case "thought":
                assert_type(stream, llm.streams.AsyncThoughtStream)
                async for chunk in stream:
                    assert_type(chunk, llm.content.ThoughtChunk)
            case _:
                assert_never(stream.content_type)
