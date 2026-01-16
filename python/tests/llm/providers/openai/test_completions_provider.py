"""Tests for OpenAICompletionsProvider"""

from collections.abc import Iterator
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
