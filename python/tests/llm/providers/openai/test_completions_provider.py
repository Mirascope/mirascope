"""Tests for OpenAICompletionsProvider"""

from collections.abc import AsyncIterator, Iterator, Sequence
from typing import Literal
from unittest.mock import MagicMock, patch

import pytest
from openai import RateLimitError as OpenAIRateLimitError
from openai.types.chat import ChatCompletionChunk

from mirascope import llm
from mirascope.llm.providers.openai.provider import OpenAIProvider


def test_stream_rate_limit_error() -> None:
    """Test that OpenAI RateLimitError is caught and re-wrapped during streaming calls."""
    model = llm.Model("openai/gpt-4o:completions")
    provider = model.provider
    assert isinstance(provider, OpenAIProvider)
    completions_provider = provider._completions_provider  # pyright: ignore[reportPrivateUsage]

    # Create a mock stream that raises RateLimitError
    def mock_stream() -> Iterator[ChatCompletionChunk]:
        raise OpenAIRateLimitError(
            "Rate limit exceeded", response=MagicMock(status_code=429), body=None
        )
        yield  # pragma: no cover

    # Patch the client to return our mock stream
    with patch.object(
        completions_provider.client.chat.completions,
        "create",
        return_value=mock_stream(),
    ):
        # Try to stream and expect RateLimitError
        response = model.stream("test")

        with pytest.raises(llm.RateLimitError) as exc_info:
            response.finish()

        # Verify it's wrapped as mirascope RateLimitError and has proper chaining
        assert isinstance(exc_info.value, llm.RateLimitError)
        assert isinstance(exc_info.value.__cause__, OpenAIRateLimitError)


@pytest.mark.asyncio
async def test_async_stream_rate_limit_error() -> None:
    """Test that OpenAI RateLimitError is caught and re-wrapped during async streaming calls."""
    model = llm.Model("openai/gpt-4o:completions")
    provider = model.provider
    assert isinstance(provider, OpenAIProvider)
    completions_provider = provider._completions_provider  # pyright: ignore[reportPrivateUsage]

    # Create a mock async stream that raises RateLimitError
    class MockAsyncStream:
        def __aiter__(self) -> "MockAsyncStream":
            return self

        async def __anext__(self) -> ChatCompletionChunk:
            raise OpenAIRateLimitError(
                "Rate limit exceeded", response=MagicMock(status_code=429), body=None
            )

    # Create an async function that returns the mock stream
    async def create_mock_stream(**kwargs: object) -> MockAsyncStream:
        return MockAsyncStream()

    # Patch the async client to return our mock stream
    with patch.object(
        completions_provider.async_client.chat.completions,
        "create",
        side_effect=create_mock_stream,
    ):
        # Try to stream and expect RateLimitError
        response = await model.stream_async("test")

        with pytest.raises(llm.RateLimitError) as exc_info:
            await response.finish()

        # Verify it's wrapped as mirascope RateLimitError and has proper chaining
        assert isinstance(exc_info.value, llm.RateLimitError)
        assert isinstance(exc_info.value.__cause__, OpenAIRateLimitError)


def test_call_rate_limit_error() -> None:
    """Test that OpenAI RateLimitError is caught and re-wrapped during non-streaming calls."""
    model = llm.Model("openai/gpt-4o:completions")
    provider = model.provider
    assert isinstance(provider, OpenAIProvider)
    completions_provider = provider._completions_provider  # pyright: ignore[reportPrivateUsage]

    # Patch the client to raise RateLimitError
    with patch.object(
        completions_provider.client.chat.completions,
        "create",
        side_effect=OpenAIRateLimitError(
            "Rate limit exceeded", response=MagicMock(status_code=429), body=None
        ),
    ):
        # Try to call and expect RateLimitError
        with pytest.raises(llm.RateLimitError) as exc_info:
            model.call("test")

        # Verify it's wrapped as mirascope RateLimitError and has proper chaining
        assert isinstance(exc_info.value, llm.RateLimitError)
        assert isinstance(exc_info.value.__cause__, OpenAIRateLimitError)


@pytest.mark.asyncio
async def test_async_call_rate_limit_error() -> None:
    """Test that OpenAI RateLimitError is caught and re-wrapped during async non-streaming calls."""
    model = llm.Model("openai/gpt-4o:completions")
    provider = model.provider
    assert isinstance(provider, OpenAIProvider)
    completions_provider = provider._completions_provider  # pyright: ignore[reportPrivateUsage]

    # Patch the async client to raise RateLimitError
    with patch.object(
        completions_provider.async_client.chat.completions,
        "create",
        side_effect=OpenAIRateLimitError(
            "Rate limit exceeded", response=MagicMock(status_code=429), body=None
        ),
    ):
        # Try to call and expect RateLimitError
        with pytest.raises(llm.RateLimitError) as exc_info:
            await model.call_async("test")

        # Verify it's wrapped as mirascope RateLimitError and has proper chaining
        assert isinstance(exc_info.value, llm.RateLimitError)
        assert isinstance(exc_info.value.__cause__, OpenAIRateLimitError)


@llm.tool
def function_one(value: int) -> str:
    """Return the integer fixture value as text."""
    return str(value)


@llm.tool
def function_two(value: str) -> str:
    """Return the string fixture value."""
    return value


def make_stream_chunk(
    tools: Sequence[tuple[int, str, bool]] = (),
    *,
    content: str | None = None,
    finish_reason: Literal["tool_calls"] | None = None,
    usage_only: bool = False,
) -> ChatCompletionChunk:
    tool_deltas = [
        {
            "index": index,
            "id": f"tool_{index + 1}" if initial else None,
            "type": "function" if initial else None,
            "function": {
                "name": ("function_one", "function_two")[index] if initial else None,
                "arguments": arguments,
            },
        }
        for index, arguments, initial in tools
    ]
    return ChatCompletionChunk.model_validate(
        {
            "id": "fixture-stream",
            "created": 1,
            "model": "gpt-4o",
            "object": "chat.completion.chunk",
            "choices": []
            if usage_only
            else [
                {
                    "index": 0,
                    "delta": {"content": content, "tool_calls": tool_deltas or None},
                    "finish_reason": finish_reason,
                }
            ],
            "usage": {
                "prompt_tokens": 7,
                "completion_tokens": 5,
                "total_tokens": 12,
                "prompt_tokens_details": {"cached_tokens": 2},
                "completion_tokens_details": {"reasoning_tokens": 1},
            }
            if usage_only
            else None,
        }
    )


@pytest.fixture(
    params=["single", "serial", "interleaved", "same_chunk", "text_to_tools"]
)
def tool_stream_fixture(
    request: pytest.FixtureRequest,
) -> tuple[list[ChatCompletionChunk], list[str], str]:
    first_start = make_stream_chunk([(0, '{"value": ', True)])
    first_end = make_stream_chunk([(0, "10}", False)])
    second_start = make_stream_chunk([(1, '{"value": ', True)])
    second_end = make_stream_chunk([(1, '"hello"}', False)])
    cases = {
        "single": [first_start, first_end],
        "serial": [first_start, first_end, second_start, second_end],
        "interleaved": [first_start, second_start, first_end, second_end],
        "same_chunk": [
            make_stream_chunk([(0, '{"value": ', True), (1, '{"value": ', True)]),
            make_stream_chunk([(0, "10}", False), (1, '"hello"}', False)]),
        ],
        "text_to_tools": [
            make_stream_chunk(content="Checking values."),
            first_start,
            second_start,
            first_end,
            second_end,
        ],
    }
    chunks = [
        *cases[request.param],
        make_stream_chunk(finish_reason="tool_calls"),
        make_stream_chunk(usage_only=True),
    ]
    expected_ids = ["tool_1"] if request.param == "single" else ["tool_1", "tool_2"]
    expected_text = "Checking values." if request.param == "text_to_tools" else ""
    return chunks, expected_ids, expected_text


def assert_streamed_tools(
    chunks: list[llm.AssistantContentChunk],
    tool_calls: Sequence[llm.ToolCall],
    usage: llm.Usage | None,
    expected_ids: list[str],
    expected_text: str,
) -> None:
    assert [tool.id for tool in tool_calls] == expected_ids
    expected_calls = [
        ("tool_1", "function_one", '{"value": 10}'),
        ("tool_2", "function_two", '{"value": "hello"}'),
    ]
    assert [(tool.id, tool.name, tool.args) for tool in tool_calls] == expected_calls[
        : len(expected_ids)
    ]
    assert [
        chunk.id for chunk in chunks if chunk.type == "tool_call_start_chunk"
    ] == expected_ids
    assert [
        chunk.id for chunk in chunks if chunk.type == "tool_call_end_chunk"
    ] == expected_ids
    assert "".join(chunk.delta for chunk in chunks if chunk.type == "text_chunk") == (
        expected_text
    )
    if expected_text:
        assert [chunk.type for chunk in chunks[:3]] == [
            "text_start_chunk",
            "text_chunk",
            "text_end_chunk",
        ]
    assert usage is not None
    assert usage.input_tokens == 7
    assert usage.output_tokens == 5
    assert usage.cache_read_tokens == 2
    assert usage.reasoning_tokens == 1


def test_stream_tool_calls(
    tool_stream_fixture: tuple[list[ChatCompletionChunk], list[str], str],
) -> None:
    sdk_chunks, expected_ids, expected_text = tool_stream_fixture
    model = llm.Model("openai/gpt-4o:completions")
    with patch(
        "openai.resources.chat.completions.Completions.create",
        return_value=iter(sdk_chunks),
    ):
        response = model.stream(
            "Check fixture values.", tools=[function_one, function_two]
        )
        chunks = list(response.chunk_stream())
        response.finish()
        assert_streamed_tools(
            chunks, response.tool_calls, response.usage, expected_ids, expected_text
        )
        assert list(response.chunk_stream()) == chunks


@pytest.mark.asyncio
async def test_async_stream_tool_calls(
    tool_stream_fixture: tuple[list[ChatCompletionChunk], list[str], str],
) -> None:
    sdk_chunks, expected_ids, expected_text = tool_stream_fixture

    @llm.tool
    async def function_one(value: int) -> str:
        """Return the integer fixture value as text."""
        return str(value)

    @llm.tool
    async def function_two(value: str) -> str:
        """Return the string fixture value."""
        return value

    async def mock_stream() -> AsyncIterator[ChatCompletionChunk]:
        for chunk in sdk_chunks:
            yield chunk

    async def create_mock_stream(
        **_kwargs: object,
    ) -> AsyncIterator[ChatCompletionChunk]:
        return mock_stream()

    model = llm.Model("openai/gpt-4o:completions")
    with patch(
        "openai.resources.chat.completions.AsyncCompletions.create",
        side_effect=create_mock_stream,
    ):
        response = await model.stream_async(
            "Check fixture values.", tools=[function_one, function_two]
        )
        chunks = [chunk async for chunk in response.chunk_stream()]
        await response.finish()
        assert_streamed_tools(
            chunks, response.tool_calls, response.usage, expected_ids, expected_text
        )
        assert [chunk async for chunk in response.chunk_stream()] == chunks
