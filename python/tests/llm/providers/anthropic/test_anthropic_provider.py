"""Tests for llm.providers.AnthropicProvider."""

from typing import NoReturn
from unittest.mock import MagicMock, patch

import pytest
from anthropic import RateLimitError as AnthropicRateLimitError

from mirascope import llm
from mirascope.llm.providers.anthropic.provider import AnthropicProvider


def test_stream_rate_limit_error() -> None:
    """Test that Anthropic RateLimitError is caught and re-wrapped during streaming."""
    # Mock the stream manager to raise RateLimitError during iteration
    mock_stream_manager = MagicMock()
    mock_stream = MagicMock()
    mock_stream_manager.__enter__.return_value = mock_stream

    # Simulate rate limit error during stream iteration
    def raise_rate_limit() -> NoReturn:
        raise AnthropicRateLimitError(
            "Rate limit exceeded",
            response=MagicMock(status_code=429),
            body=None,
        )

    mock_stream._raw_stream.__iter__ = lambda self: raise_rate_limit()

    model = llm.Model("anthropic/claude-sonnet-4-0")
    provider = model.provider
    assert isinstance(provider, AnthropicProvider)

    # Patch the client on the already-registered provider
    with patch.object(
        provider.client.messages, "stream", return_value=mock_stream_manager
    ):
        response = model.stream(messages=[llm.messages.user("test")])

        # Try to finish the stream and expect RateLimitError
        with pytest.raises(llm.RateLimitError) as exc_info:
            response.finish()

        # Verify it's wrapped as mirascope RateLimitError and has proper chaining
        assert isinstance(exc_info.value, llm.RateLimitError)
        assert "Rate limit exceeded" in str(exc_info.value)
        assert isinstance(exc_info.value.__cause__, AnthropicRateLimitError)


@pytest.mark.asyncio
async def test_async_stream_rate_limit_error() -> None:
    """Test that Anthropic RateLimitError is caught and re-wrapped during async streaming."""
    # Mock the async stream manager to raise RateLimitError during iteration
    mock_stream_manager = MagicMock()
    mock_stream = MagicMock()

    # Make async context manager methods actually async
    async def mock_aenter(self: object) -> MagicMock:
        return mock_stream

    async def mock_aexit(self: object, *args: object) -> None:
        return None

    mock_stream_manager.__aenter__ = mock_aenter
    mock_stream_manager.__aexit__ = mock_aexit

    # Create an async iterator that raises RateLimitError
    class MockAsyncIterator:
        def __aiter__(self) -> "MockAsyncIterator":
            return self

        async def __anext__(self) -> NoReturn:
            raise AnthropicRateLimitError(
                "Rate limit exceeded",
                response=MagicMock(status_code=429),
                body=None,
            )

    mock_stream._raw_stream = MockAsyncIterator()

    model = llm.Model("anthropic/claude-sonnet-4-0")
    provider = model.provider
    assert isinstance(provider, AnthropicProvider)

    # Patch the async client on the already-registered provider
    with patch.object(
        provider.async_client.messages, "stream", return_value=mock_stream_manager
    ):
        response = await model.stream_async(messages=[llm.messages.user("test")])

        # Try to finish the stream and expect RateLimitError
        with pytest.raises(llm.RateLimitError) as exc_info:
            await response.finish()

        # Verify it's wrapped as mirascope RateLimitError and has proper chaining
        assert isinstance(exc_info.value, llm.RateLimitError)
        assert "Rate limit exceeded" in str(exc_info.value)
        assert isinstance(exc_info.value.__cause__, AnthropicRateLimitError)


def test_call_rate_limit_error() -> None:
    """Test that Anthropic RateLimitError is caught and re-wrapped during non-streaming calls."""
    model = llm.Model("anthropic/claude-sonnet-4-0")
    provider = model.provider
    assert isinstance(provider, AnthropicProvider)

    # Patch the client to raise RateLimitError
    with patch.object(
        provider.client.messages,
        "create",
        side_effect=AnthropicRateLimitError(
            "Rate limit exceeded",
            response=MagicMock(status_code=429),
            body=None,
        ),
    ):
        # Try to call and expect RateLimitError
        with pytest.raises(llm.RateLimitError) as exc_info:
            model.call(messages=[llm.messages.user("test")])

        # Verify it's wrapped as mirascope RateLimitError and has proper chaining
        assert isinstance(exc_info.value, llm.RateLimitError)
        assert "Rate limit exceeded" in str(exc_info.value)
        assert isinstance(exc_info.value.__cause__, AnthropicRateLimitError)


@pytest.mark.asyncio
async def test_async_call_rate_limit_error() -> None:
    """Test that Anthropic RateLimitError is caught and re-wrapped during async non-streaming calls."""
    model = llm.Model("anthropic/claude-sonnet-4-0")
    provider = model.provider
    assert isinstance(provider, AnthropicProvider)

    # Patch the async client to raise RateLimitError
    with patch.object(
        provider.async_client.messages,
        "create",
        side_effect=AnthropicRateLimitError(
            "Rate limit exceeded",
            response=MagicMock(status_code=429),
            body=None,
        ),
    ):
        # Try to call and expect RateLimitError
        with pytest.raises(llm.RateLimitError) as exc_info:
            await model.call_async(messages=[llm.messages.user("test")])

        # Verify it's wrapped as mirascope RateLimitError and has proper chaining
        assert isinstance(exc_info.value, llm.RateLimitError)
        assert "Rate limit exceeded" in str(exc_info.value)
        assert isinstance(exc_info.value.__cause__, AnthropicRateLimitError)
