"""Tests for model context manager interaction with retry semantics."""

import pytest

from mirascope import llm
from mirascope.llm.retries.utils import get_retry_model_from_context

from .conftest import CONNECTION_ERROR, RATE_LIMIT_ERROR
from .mock_provider import MockProvider

# --- Unit tests for get_retry_model_from_context ---


def test_get_retry_model_from_context_returns_stored_when_no_context() -> None:
    """Without context, returns the stored RetryModel."""
    stored = llm.retry_model("mock/stored", max_retries=3)
    result = get_retry_model_from_context(stored)
    assert result is stored


def test_get_retry_model_from_context_returns_context_retry_model() -> None:
    """With RetryModel in context, returns the context RetryModel directly."""
    stored = llm.retry_model("mock/stored", max_retries=3)
    context = llm.retry_model("mock/context", max_retries=5)

    with context:
        result = get_retry_model_from_context(stored)

    assert result is context


def test_get_retry_model_from_context_wraps_plain_model() -> None:
    """With plain Model in context, wraps it with stored RetryModel's config."""
    stored = llm.retry_model("mock/stored", max_retries=3, initial_delay=0.5)

    with llm.model("mock/context"):
        result = get_retry_model_from_context(stored)

    # Should be a new RetryModel wrapping the context model
    assert result.model_id == "mock/context"
    # Should inherit retry config from stored
    assert result.retry_config.max_retries == 3
    assert result.retry_config.initial_delay == 0.5


# --- Integration tests: RetryCall with model context ---


def test_retry_call_with_model_context_gets_retry_semantics(
    mock_provider: MockProvider,
) -> None:
    """RetryCall wraps a context Model in RetryModel to get retry semantics."""
    mock_provider.set_exceptions([CONNECTION_ERROR])

    @llm.retry(max_retries=1)
    @llm.call("mock/default-model")
    def greet() -> str:
        return "Hello"

    with llm.model("mock/override-model"):
        response = greet()

    assert response.model_id == "mock/override-model"
    assert len(response.retry_failures) == 1
    assert mock_provider.call_count == 2


def test_retry_call_with_retry_model_context_uses_context_config(
    mock_provider: MockProvider,
) -> None:
    """RetryCall uses the context RetryModel's config, not the call's config."""
    mock_provider.set_exceptions([CONNECTION_ERROR, RATE_LIMIT_ERROR])

    @llm.retry(max_retries=5)
    @llm.call("mock/default-model")
    def greet() -> str:
        return "Hello"

    context_retry_model = llm.retry_model("mock/override-model", max_retries=1)

    with context_retry_model, pytest.raises(llm.RetriesExhausted) as exc_info:
        greet()

    assert len(exc_info.value.failures) == 2
    assert mock_provider.call_count == 2


# --- Integration tests: Regular Call with RetryModel context ---


def test_regular_call_with_retry_model_context_gets_retry_semantics(
    mock_provider: MockProvider,
) -> None:
    """A regular Call gets retry semantics when context is a RetryModel."""
    mock_provider.set_exceptions([CONNECTION_ERROR])

    @llm.call("mock/default-model")
    def greet() -> str:
        return "Hello"

    context_retry_model = llm.retry_model("mock/override-model", max_retries=1)

    with context_retry_model:
        response = greet()

    assert response.model_id == "mock/override-model"
    assert mock_provider.call_count == 2


# --- Integration tests: Streaming with model context ---


def test_retry_call_stream_with_model_context_gets_retry_semantics(
    mock_provider: MockProvider,
) -> None:
    """RetryCall stream wraps a context Model in RetryModel to get retry semantics."""
    mock_provider.set_stream_exceptions([CONNECTION_ERROR])

    @llm.retry(max_retries=1)
    @llm.call("mock/default-model")
    def greet() -> str:
        return "Hello"

    with llm.model("mock/override-model"):
        response = greet.stream()

        with pytest.raises(llm.StreamRestarted):
            list(response.chunk_stream())

        chunks = list(response.chunk_stream())
        assert len(chunks) > 0

    assert response.model_id == "mock/override-model"
    assert len(response.retry_failures) == 1
    assert mock_provider.stream_count == 2


# --- Integration tests: Model context with fallback models ---


def test_retry_call_with_retry_model_context_uses_fallbacks(
    mock_provider: MockProvider,
) -> None:
    """RetryCall uses the context RetryModel's fallback models."""
    mock_provider.set_exceptions([CONNECTION_ERROR])

    @llm.retry(max_retries=5)
    @llm.call("mock/default-model")
    def greet() -> str:
        return "Hello"

    context_retry_model = llm.retry_model(
        "mock/primary", max_retries=0, fallback_models=["mock/fallback"]
    )

    with context_retry_model:
        response = greet()

    assert response.model_id == "mock/fallback"
    assert len(response.retry_failures) == 1
    assert mock_provider.call_count == 2


# --- Integration tests: RetryResponse.resume() with model context ---


def test_retry_response_resume_with_model_context_uses_context_model(
    mock_provider: MockProvider,
) -> None:
    """retry_response.resume() respects model context override."""
    retry_model = llm.retry_model("mock/original-model", max_retries=2)
    response = retry_model.call("Hello")

    assert response.model_id == "mock/original-model"
    assert mock_provider.call_count == 1

    with llm.model("mock/override-model"):
        continued = response.resume("Continue please")

    assert continued.model_id == "mock/override-model"
    assert mock_provider.call_count == 2


def test_retry_response_resume_with_model_context_preserves_retry_config(
    mock_provider: MockProvider,
) -> None:
    """retry_response.resume() with model context preserves retry config."""
    retry_model = llm.retry_model("mock/original-model", max_retries=2)
    response = retry_model.call("Hello")
    assert mock_provider.call_count == 1

    mock_provider.set_exceptions([CONNECTION_ERROR])

    with llm.model("mock/override-model"):
        continued = response.resume("Continue please")

    assert continued.model_id == "mock/override-model"
    assert len(continued.retry_failures) == 1
    assert mock_provider.call_count == 3


def test_retry_response_resume_with_retry_model_context_uses_context_config(
    mock_provider: MockProvider,
) -> None:
    """retry_response.resume() with RetryModel context uses context's config."""
    original_retry_model = llm.retry_model("mock/original-model", max_retries=5)
    response = original_retry_model.call("Hello")
    assert mock_provider.call_count == 1

    mock_provider.set_exceptions([CONNECTION_ERROR, RATE_LIMIT_ERROR])

    context_retry_model = llm.retry_model("mock/override-model", max_retries=1)

    with context_retry_model, pytest.raises(llm.RetriesExhausted) as exc_info:
        response.resume("Continue please")

    assert len(exc_info.value.failures) == 2
    assert mock_provider.call_count == 3


def test_retry_response_resume_without_context_uses_cached_model(
    mock_provider: MockProvider,
) -> None:
    """retry_response.resume() without context uses the cached model."""
    retry_model = llm.retry_model("mock/original-model", max_retries=2)
    response = retry_model.call("Hello")

    assert response.model_id == "mock/original-model"
    assert mock_provider.call_count == 1

    continued = response.resume("Continue please")

    assert continued.model_id == "mock/original-model"
    assert mock_provider.call_count == 2


# --- Integration tests: RetryStreamResponse.resume() with model context ---


def test_retry_stream_response_resume_with_model_context_uses_context_model(
    mock_provider: MockProvider,
) -> None:
    """retry_stream_response.resume() respects model context override."""
    retry_model = llm.retry_model("mock/original-model", max_retries=2)
    response = retry_model.stream("Hello")

    list(response.chunk_stream())
    assert response.model_id == "mock/original-model"
    assert mock_provider.stream_count == 1

    with llm.model("mock/override-model"):
        continued = response.resume("Continue please")
        list(continued.chunk_stream())

    assert continued.model_id == "mock/override-model"
    assert mock_provider.stream_count == 2


def test_retry_stream_response_resume_with_model_context_preserves_retry_config(
    mock_provider: MockProvider,
) -> None:
    """retry_stream_response.resume() with model context preserves retry config."""
    retry_model = llm.retry_model("mock/original-model", max_retries=2)
    response = retry_model.stream("Hello")

    list(response.chunk_stream())
    assert mock_provider.stream_count == 1

    mock_provider.set_stream_exceptions([CONNECTION_ERROR])

    with llm.model("mock/override-model"):
        continued = response.resume("Continue please")

        with pytest.raises(llm.StreamRestarted):
            list(continued.chunk_stream())

        list(continued.chunk_stream())

    assert continued.model_id == "mock/override-model"
    assert len(continued.retry_failures) == 1
    assert mock_provider.stream_count == 3


def test_retry_stream_response_resume_without_context_uses_cached_model(
    mock_provider: MockProvider,
) -> None:
    """retry_stream_response.resume() without context uses the cached model."""
    retry_model = llm.retry_model("mock/original-model", max_retries=2)
    response = retry_model.stream("Hello")

    list(response.chunk_stream())
    assert response.model_id == "mock/original-model"
    assert mock_provider.stream_count == 1

    continued = response.resume("Continue please")
    list(continued.chunk_stream())

    assert continued.model_id == "mock/original-model"
    assert mock_provider.stream_count == 2
