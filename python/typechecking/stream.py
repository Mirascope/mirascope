from collections.abc import AsyncIterator, Iterator

from typing_extensions import assert_never, assert_type

from mirascope import llm


def stream_response() -> llm.StreamResponse:
    raise NotImplementedError()


def async_stream_response() -> llm.StreamResponse[llm.AsyncStream]:
    raise NotImplementedError()


def stream_type_safety():
    text_stream: llm.streams.TextStream = stream_response().text_stream()
    for chunk in text_stream:
        assert_type(chunk, llm.content.TextChunk)

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
            case "thinking":
                assert_type(stream, llm.streams.ThinkingStream)
                for chunk in stream:
                    assert_type(chunk, llm.content.ThinkingChunk)
            case _:
                assert_never(stream.content_type)


async def async_stream_type_safety():
    text_stream: llm.streams.AsyncTextStream = (
        await async_stream_response().text_stream()
    )
    async for chunk in text_stream:
        assert_type(chunk, llm.content.TextChunk)

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
            case "thinking":
                assert_type(stream, llm.streams.AsyncThinkingStream)
                async for chunk in stream:
                    assert_type(chunk, llm.content.ThinkingChunk)
            case _:
                assert_never(stream.content_type)
