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
                assert_type(stream, llm.TextStream)
            case "tool_call":
                assert_type(stream, llm.ToolCallStream)
            case "thought":
                assert_type(stream, llm.ThoughtStream)
            case _:
                assert_never(stream.content_type)


async def async_stream_type_safety():
    async for chunk in async_stream_response().pretty_stream():
        assert_type(chunk, str)

    streams: AsyncIterator[llm.AsyncStream] = async_stream_response().streams()
    async for stream in streams:
        match stream.content_type:
            case "text":
                assert_type(stream, llm.AsyncTextStream)
            case "tool_call":
                assert_type(stream, llm.AsyncToolCallStream)
            case "thought":
                assert_type(stream, llm.AsyncThoughtStream)
            case _:
                assert_never(stream.content_type)
