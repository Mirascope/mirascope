"""Tests for llm.providers.GoogleProvider."""

from collections.abc import AsyncIterator, Iterator
from typing import get_args
from unittest.mock import MagicMock, patch

import pytest
from google.genai.errors import (
    ClientError as GoogleClientError,
    ServerError as GoogleServerError,
)
from google.genai.types import GenerateContentResponse, ThinkingLevel
from inline_snapshot import snapshot

from mirascope import llm
from mirascope.llm.providers.google._utils.encode import google_thinking_config
from mirascope.llm.providers.google._utils.errors import map_google_error
from mirascope.llm.providers.google.provider import GoogleProvider


def test_custom_base_url() -> None:
    """Test that custom base URL is used for API requests."""
    example_url = "https://example.com"

    with patch("mirascope.llm.providers.google.provider.Client") as mock_client_class:
        mock_client_instance = MagicMock()
        mock_client_class.return_value = mock_client_instance

        google_client = llm.register_provider("google", base_url=example_url)

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
        response = model.stream("test")

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
        response = await model.stream_async("test")

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
            model.call("test")

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
            await model.call_async("test")

        # Verify it's wrapped as mirascope RateLimitError and has proper chaining
        assert isinstance(exc_info.value, llm.RateLimitError)
        assert isinstance(exc_info.value.__cause__, GoogleServerError)


def test_map_google_error_not_google_error() -> None:
    """Test that non-Google errors return ProviderError."""
    result = map_google_error(Exception("test"))
    assert result == llm.ProviderError


def test_map_google_error_permission_denied() -> None:
    """Test that 403 errors map to PermissionError."""
    error = GoogleClientError(403, {"error": {"message": "Permission denied"}})
    result = map_google_error(error)
    assert result == llm.PermissionError


def test_map_google_error_not_found() -> None:
    """Test that 404 errors map to NotFoundError."""
    error = GoogleClientError(404, {"error": {"message": "Not found"}})
    result = map_google_error(error)
    assert result == llm.NotFoundError


def test_map_google_error_bad_request() -> None:
    """Test that 400/422 errors map to BadRequestError."""
    error_400 = GoogleClientError(400, {"error": {"message": "Bad request"}})
    result_400 = map_google_error(error_400)
    assert result_400 == llm.BadRequestError

    error_422 = GoogleClientError(422, {"error": {"message": "Unprocessable"}})
    result_422 = map_google_error(error_422)
    assert result_422 == llm.BadRequestError


def test_map_google_error_server_error() -> None:
    """Test that 5xx server errors map to ServerError."""
    error_500 = GoogleServerError(500, {"error": {"message": "Internal server error"}})
    result_500 = map_google_error(error_500)
    assert result_500 == llm.ServerError

    error_503 = GoogleServerError(503, {"error": {"message": "Service unavailable"}})
    result_503 = map_google_error(error_503)
    assert result_503 == llm.ServerError


def test_map_google_error_fallback() -> None:
    """Test that unknown error codes fall back to APIError."""
    # Test an unknown client error code
    error = GoogleClientError(418, {"error": {"message": "I'm a teapot"}})
    result = map_google_error(error)
    assert result == llm.APIError


def test_google_thinking_config_levels_2_5() -> None:
    """Test thinking config computation for Gemini 2.5 models."""

    results = {}
    for level in get_args(llm.ThinkingLevel):
        results[level] = google_thinking_config(
            {"level": level}, max_tokens=None, model_id="google/gemini-2.5-flash"
        )
    assert results == snapshot(
        {
            "none": {"thinking_budget": 0},
            "default": {"thinking_budget": -1},
            "minimal": {"thinking_budget": 1600},
            "low": {"thinking_budget": 3200},
            "medium": {"thinking_budget": 6400},
            "high": {"thinking_budget": 9600},
            "max": {"thinking_budget": 12800},
        }
    )


def test_google_thinking_config_levels_3_flash() -> None:
    """Test thinking config computation for Gemini 3 flash models."""

    results = {}
    for level in get_args(llm.ThinkingLevel):
        results[level] = google_thinking_config(
            {"level": level}, max_tokens=None, model_id="google/gemini-3-flash"
        )
    assert results == snapshot(
        {
            "none": {"thinking_level": ThinkingLevel.MINIMAL},
            "default": {"thinking_level": ThinkingLevel.THINKING_LEVEL_UNSPECIFIED},
            "minimal": {"thinking_level": ThinkingLevel.MINIMAL},
            "low": {"thinking_level": ThinkingLevel.LOW},
            "medium": {"thinking_level": ThinkingLevel.MEDIUM},
            "high": {"thinking_level": ThinkingLevel.HIGH},
            "max": {"thinking_level": ThinkingLevel.HIGH},
        }
    )


def test_google_thinking_config_levels_3_pro() -> None:
    """Test thinking config computation for Gemini 3 pro models."""

    results = {}
    for level in get_args(llm.ThinkingLevel):
        results[level] = google_thinking_config(
            {"level": level}, max_tokens=None, model_id="google/gemini-3-pro"
        )
    assert results == snapshot(
        {
            "none": {"thinking_level": ThinkingLevel.LOW},
            "default": {"thinking_level": ThinkingLevel.THINKING_LEVEL_UNSPECIFIED},
            "minimal": {"thinking_level": ThinkingLevel.LOW},
            "low": {"thinking_level": ThinkingLevel.LOW},
            "medium": {"thinking_level": ThinkingLevel.HIGH},
            "high": {"thinking_level": ThinkingLevel.HIGH},
            "max": {"thinking_level": ThinkingLevel.HIGH},
        }
    )


def test_google_thinking_config_include_thoughts() -> None:
    """Test include_thoughts flag is respected."""
    result = google_thinking_config(
        {"level": "low", "include_thoughts": False},
        max_tokens=1000,
        model_id="google/gemini-3.0-flash",
    )
    assert result.get("include_thoughts") is False

    result = google_thinking_config(
        {"level": "low", "include_thoughts": True},
        max_tokens=1000,
        model_id="google/gemini-2.5-flash",
    )
    assert result.get("include_thoughts") is True


def test_google_thinking_config_unknown_model() -> None:
    """Test unknown model defaults to 2.5 behavior."""
    result = google_thinking_config(
        {"level": "low"}, max_tokens=1000, model_id="google/gemini-unknown-model"
    )
    assert result.get("thinking_budget") == 200  # 20% of 1000
