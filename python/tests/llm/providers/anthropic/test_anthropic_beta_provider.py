"""Tests for llm.providers.AnthropicProvider with beta features."""

from typing import NoReturn
from unittest.mock import MagicMock, patch

import pytest
from anthropic import RateLimitError as AnthropicRateLimitError

from mirascope import llm
from mirascope.llm.providers.anthropic.beta_provider import AnthropicBetaProvider


def test_beta_stream_rate_limit_error() -> None:
    """Test that Anthropic RateLimitError is caught and re-wrapped during beta streaming."""
    # Mock the beta stream manager to raise RateLimitError during iteration
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

    model = llm.Model("anthropic-beta/claude-sonnet-4-0")
    provider = model.provider
    assert isinstance(provider, AnthropicBetaProvider)

    # Patch the client on the already-registered provider
    with patch.object(
        provider.client.beta.messages, "stream", return_value=mock_stream_manager
    ):
        response = model.stream("test")

        # Try to finish the stream and expect RateLimitError
        with pytest.raises(llm.RateLimitError) as exc_info:
            response.finish()

        # Verify it's wrapped as mirascope RateLimitError and has proper chaining
        assert isinstance(exc_info.value, llm.RateLimitError)
        assert "Rate limit exceeded" in str(exc_info.value)
        assert isinstance(exc_info.value.__cause__, AnthropicRateLimitError)


@pytest.mark.asyncio
async def test_beta_async_stream_rate_limit_error() -> None:
    """Test that Anthropic RateLimitError is caught and re-wrapped during beta async streaming."""
    # Mock the async beta stream manager to raise RateLimitError during iteration
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

    model = llm.Model("anthropic-beta/claude-sonnet-4-0")
    provider = model.provider
    assert isinstance(provider, AnthropicBetaProvider)

    # Patch the async client on the already-registered provider
    with patch.object(
        provider.async_client.beta.messages, "stream", return_value=mock_stream_manager
    ):
        response = await model.stream_async("test")

        # Try to finish the stream and expect RateLimitError
        with pytest.raises(llm.RateLimitError) as exc_info:
            await response.finish()

        # Verify it's wrapped as mirascope RateLimitError and has proper chaining
        assert isinstance(exc_info.value, llm.RateLimitError)
        assert "Rate limit exceeded" in str(exc_info.value)
        assert isinstance(exc_info.value.__cause__, AnthropicRateLimitError)


def test_beta_call_rate_limit_error() -> None:
    """Test that Anthropic RateLimitError is caught and re-wrapped during beta non-streaming calls."""
    model = llm.Model("anthropic-beta/claude-sonnet-4-0")
    provider = model.provider
    assert isinstance(provider, AnthropicBetaProvider)

    # Patch the client to raise RateLimitError
    with patch.object(
        provider.client.beta.messages,
        "parse",
        side_effect=AnthropicRateLimitError(
            "Rate limit exceeded",
            response=MagicMock(status_code=429),
            body=None,
        ),
    ):
        # Try to call and expect RateLimitError
        with pytest.raises(llm.RateLimitError) as exc_info:
            model.call("test")

        # Verify it's wrapped as mirascope RateLimitError and has proper chaining
        assert isinstance(exc_info.value, llm.RateLimitError)
        assert "Rate limit exceeded" in str(exc_info.value)
        assert isinstance(exc_info.value.__cause__, AnthropicRateLimitError)


@pytest.mark.asyncio
async def test_beta_async_call_rate_limit_error() -> None:
    """Test that Anthropic RateLimitError is caught and re-wrapped during beta async non-streaming calls."""
    model = llm.Model("anthropic-beta/claude-sonnet-4-0")
    provider = model.provider
    assert isinstance(provider, AnthropicBetaProvider)

    # Patch the async client to raise RateLimitError
    with patch.object(
        provider.async_client.beta.messages,
        "parse",
        side_effect=AnthropicRateLimitError(
            "Rate limit exceeded",
            response=MagicMock(status_code=429),
            body=None,
        ),
    ):
        # Try to call and expect RateLimitError
        with pytest.raises(llm.RateLimitError) as exc_info:
            await model.call_async("test")

        # Verify it's wrapped as mirascope RateLimitError and has proper chaining
        assert isinstance(exc_info.value, llm.RateLimitError)
        assert "Rate limit exceeded" in str(exc_info.value)
        assert isinstance(exc_info.value.__cause__, AnthropicRateLimitError)
