"""Tests for llm.providers.GoogleProvider."""

from collections.abc import AsyncIterator, Iterator
from unittest.mock import MagicMock, patch

import pytest
from google.genai.errors import ServerError as GoogleServerError
from google.genai.types import GenerateContentResponse

from mirascope import llm
from mirascope.llm.providers.google.provider import GoogleProvider


def test_custom_base_url() -> None:
    """Test that custom base URL is used for API requests."""
    example_url = "https://example.com"

    with patch("mirascope.llm.providers.google.provider.Client") as mock_client_class:
        mock_client_instance = MagicMock()
        mock_client_class.return_value = mock_client_instance

        google_client = llm.load_provider("google", base_url=example_url)

        mock_client_class.assert_called_once()
        call_args = mock_client_class.call_args
        assert call_args.kwargs["http_options"] is not None
        assert call_args.kwargs["http_options"].base_url == example_url

        assert google_client.client is mock_client_instance


def test_stream_rate_limit_error() -> None:
    """Test that Google ServerError with 429 is caught and re-wrapped during streaming calls."""
    model = llm.Model("google/gemini-2.0-flash")
    provider = model.provider
    assert isinstance(provider, GoogleProvider)

    # Create a mock stream that raises ServerError with 429
    def mock_stream() -> Iterator[GenerateContentResponse]:
        raise GoogleServerError(429, {"error": {"message": "Rate limit exceeded"}})
        yield  # pragma: no cover

    # Patch the client to return our mock stream
    with patch.object(
        provider.client.models,
        "generate_content_stream",
        return_value=mock_stream(),
    ):
        # Try to stream and expect RateLimitError
        response = model.stream(messages=[llm.messages.user("test")])

        with pytest.raises(llm.RateLimitError) as exc_info:
            response.finish()

        # Verify it's wrapped as mirascope RateLimitError and has proper chaining
        assert isinstance(exc_info.value, llm.RateLimitError)
        assert isinstance(exc_info.value.__cause__, GoogleServerError)


@pytest.mark.asyncio
async def test_async_stream_rate_limit_error() -> None:
    """Test that Google ServerError with 429 is caught and re-wrapped during async streaming calls."""
    model = llm.Model("google/gemini-2.0-flash")
    provider = model.provider
    assert isinstance(provider, GoogleProvider)

    # Create a mock async stream that raises ServerError with 429
    async def mock_async_stream() -> AsyncIterator[GenerateContentResponse]:
        raise GoogleServerError(429, {"error": {"message": "Rate limit exceeded"}})
        yield  # pragma: no cover

    # Patch the async client to return our mock stream
    with patch.object(
        provider.client.aio.models,
        "generate_content_stream",
        return_value=mock_async_stream(),
    ):
        # Try to stream and expect RateLimitError
        response = await model.stream_async(messages=[llm.messages.user("test")])

        with pytest.raises(llm.RateLimitError) as exc_info:
            await response.finish()

        # Verify it's wrapped as mirascope RateLimitError and has proper chaining
        assert isinstance(exc_info.value, llm.RateLimitError)
        assert isinstance(exc_info.value.__cause__, GoogleServerError)


def test_call_rate_limit_error() -> None:
    """Test that Google ServerError with 429 is caught and re-wrapped during non-streaming calls."""
    model = llm.Model("google/gemini-2.0-flash")
    provider = model.provider
    assert isinstance(provider, GoogleProvider)

    # Patch the client to raise ServerError with 429
    with patch.object(
        provider.client.models,
        "generate_content",
        side_effect=GoogleServerError(
            429, {"error": {"message": "Rate limit exceeded"}}
        ),
    ):
        # Try to call and expect RateLimitError
        with pytest.raises(llm.RateLimitError) as exc_info:
            model.call(messages=[llm.messages.user("test")])

        # Verify it's wrapped as mirascope RateLimitError and has proper chaining
        assert isinstance(exc_info.value, llm.RateLimitError)
        assert isinstance(exc_info.value.__cause__, GoogleServerError)


@pytest.mark.asyncio
async def test_async_call_rate_limit_error() -> None:
    """Test that Google ServerError with 429 is caught and re-wrapped during async non-streaming calls."""
    model = llm.Model("google/gemini-2.0-flash")
    provider = model.provider
    assert isinstance(provider, GoogleProvider)

    # Patch the async client to raise ServerError with 429
    with patch.object(
        provider.client.aio.models,
        "generate_content",
        side_effect=GoogleServerError(
            429, {"error": {"message": "Rate limit exceeded"}}
        ),
    ):
        # Try to call and expect RateLimitError
        with pytest.raises(llm.RateLimitError) as exc_info:
            await model.call_async(messages=[llm.messages.user("test")])

        # Verify it's wrapped as mirascope RateLimitError and has proper chaining
        assert isinstance(exc_info.value, llm.RateLimitError)
        assert isinstance(exc_info.value.__cause__, GoogleServerError)
