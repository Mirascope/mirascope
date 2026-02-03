"""Tests for model context manager interaction with retry semantics."""

import pytest

from mirascope import llm

from .conftest import CONNECTION_ERROR, RATE_LIMIT_ERROR
from .mock_provider import MockProvider

# --- RetryCall with regular Model context ---


def test_retry_call_with_model_context_gets_retry_semantics(
    mock_provider: MockProvider,
) -> None:
    """Test that RetryCall wraps a context Model in RetryModel to get retry semantics."""
    mock_provider.set_exceptions([CONNECTION_ERROR])

    @llm.retry(max_retries=1)
    @llm.call("mock/default-model")
    def greet() -> str:
        return "Hello"

    # Override with a plain Model via context
    with llm.model("mock/override-model"):
        response = greet()

    # Should have retried and succeeded
    assert response.model_id == "mock/override-model"
    assert len(response.retry_failures) == 1
    assert mock_provider.call_count == 2


def test_retry_call_with_retry_model_context_uses_context_config(
    mock_provider: MockProvider,
) -> None:
    """Test that RetryCall uses the context RetryModel's config, not the call's config."""
    # Set up 2 errors - context model has max_retries=1, call has max_retries=5
    mock_provider.set_exceptions([CONNECTION_ERROR, RATE_LIMIT_ERROR])

    @llm.retry(max_retries=5)
    @llm.call("mock/default-model")
    def greet() -> str:
        return "Hello"

    # Override with a RetryModel that has different retry config
    context_retry_model = llm.retry_model("mock/override-model", max_retries=1)

    with context_retry_model, pytest.raises(llm.RetriesExhausted) as exc_info:
        # Should fail because context model only has max_retries=1
        greet()

    assert len(exc_info.value.failures) == 2
    # 2 attempts: initial + 1 retry
    assert mock_provider.call_count == 2


@pytest.mark.asyncio
async def test_async_retry_call_with_model_context_gets_retry_semantics(
    mock_provider: MockProvider,
) -> None:
    """Test that async RetryCall wraps a context Model in RetryModel to get retry semantics."""
    mock_provider.set_exceptions([CONNECTION_ERROR])

    @llm.retry(max_retries=1)
    @llm.call("mock/default-model")
    async def greet() -> str:
        return "Hello"

    # Override with a plain Model via context
    with llm.model("mock/override-model"):
        response = await greet()

    # Should have retried and succeeded
    assert response.model_id == "mock/override-model"
    assert len(response.retry_failures) == 1
    assert mock_provider.call_count == 2


# --- Regular Call with RetryModel context ---


def test_regular_call_with_retry_model_context_gets_retry_semantics(
    mock_provider: MockProvider,
) -> None:
    """Test that a regular Call gets retry semantics when context is a RetryModel."""
    mock_provider.set_exceptions([CONNECTION_ERROR])

    @llm.call("mock/default-model")
    def greet() -> str:
        return "Hello"

    # Override with a RetryModel via context
    context_retry_model = llm.retry_model("mock/override-model", max_retries=1)

    with context_retry_model:
        response = greet()

    # Should have retried and succeeded via the RetryModel
    assert response.model_id == "mock/override-model"
    # Regular Response doesn't have retry_failures, but the call should have succeeded
    assert mock_provider.call_count == 2


def test_regular_call_with_retry_model_context_respects_retry_config(
    mock_provider: MockProvider,
) -> None:
    """Test that a regular Call respects the context RetryModel's retry config."""
    # Set up 2 errors - context model has max_retries=1
    mock_provider.set_exceptions([CONNECTION_ERROR, RATE_LIMIT_ERROR])

    @llm.call("mock/default-model")
    def greet() -> str:
        return "Hello"

    # Override with a RetryModel that has max_retries=1
    context_retry_model = llm.retry_model("mock/override-model", max_retries=1)

    with context_retry_model, pytest.raises(llm.RetriesExhausted) as exc_info:
        # Should fail because context model only has max_retries=1
        greet()

    assert len(exc_info.value.failures) == 2
    # 2 attempts: initial + 1 retry
    assert mock_provider.call_count == 2


@pytest.mark.asyncio
async def test_async_regular_call_with_retry_model_context_gets_retry_semantics(
    mock_provider: MockProvider,
) -> None:
    """Test that an async regular Call gets retry semantics when context is a RetryModel."""
    mock_provider.set_exceptions([CONNECTION_ERROR])

    @llm.call("mock/default-model")
    async def greet() -> str:
        return "Hello"

    # Override with a RetryModel via context
    context_retry_model = llm.retry_model("mock/override-model", max_retries=1)

    with context_retry_model:
        response = await greet()

    # Should have retried and succeeded via the RetryModel
    assert response.model_id == "mock/override-model"
    assert mock_provider.call_count == 2


# --- Streaming with model context ---


def test_retry_call_stream_with_model_context_gets_retry_semantics(
    mock_provider: MockProvider,
) -> None:
    """Test that RetryCall stream wraps a context Model in RetryModel to get retry semantics."""
    mock_provider.set_stream_exceptions([CONNECTION_ERROR])

    @llm.retry(max_retries=1)
    @llm.call("mock/default-model")
    def greet() -> str:
        return "Hello"

    # Override with a plain Model via context
    with llm.model("mock/override-model"):
        response = greet.stream()

        # First iteration fails
        with pytest.raises(llm.StreamRestarted):
            list(response.chunk_stream())

        # Second iteration succeeds
        chunks = list(response.chunk_stream())
        assert len(chunks) > 0

    # Should have retried
    assert response.model_id == "mock/override-model"
    assert len(response.retry_failures) == 1
    assert mock_provider.stream_count == 2


def test_regular_call_stream_with_retry_model_context_gets_retry_semantics(
    mock_provider: MockProvider,
) -> None:
    """Test that a regular Call stream gets retry semantics when context is a RetryModel."""
    mock_provider.set_stream_exceptions([CONNECTION_ERROR])

    @llm.call("mock/default-model")
    def greet() -> str:
        return "Hello"

    # Override with a RetryModel via context
    context_retry_model = llm.retry_model("mock/override-model", max_retries=1)

    with context_retry_model:
        response = greet.stream()

        # First iteration fails
        with pytest.raises(llm.StreamRestarted):
            list(response.chunk_stream())

        # Second iteration succeeds
        chunks = list(response.chunk_stream())
        assert len(chunks) > 0

    # Should have retried via the RetryModel
    assert response.model_id == "mock/override-model"
    assert mock_provider.stream_count == 2


@pytest.mark.asyncio
async def test_async_retry_call_stream_with_model_context_gets_retry_semantics(
    mock_provider: MockProvider,
) -> None:
    """Test that async RetryCall stream wraps a context Model in RetryModel."""
    mock_provider.set_stream_exceptions([CONNECTION_ERROR])

    @llm.retry(max_retries=1)
    @llm.call("mock/default-model")
    async def greet() -> str:
        return "Hello"

    # Override with a plain Model via context
    with llm.model("mock/override-model"):
        response = await greet.stream()

        # First iteration fails
        with pytest.raises(llm.StreamRestarted):
            _ = [chunk async for chunk in response.chunk_stream()]

        # Second iteration succeeds
        chunks = [chunk async for chunk in response.chunk_stream()]
        assert len(chunks) > 0

    # Should have retried
    assert response.model_id == "mock/override-model"
    assert len(response.retry_failures) == 1
    assert mock_provider.stream_count == 2


@pytest.mark.asyncio
async def test_async_regular_call_stream_with_retry_model_context_gets_retry_semantics(
    mock_provider: MockProvider,
) -> None:
    """Test that async regular Call stream gets retry semantics when context is a RetryModel."""
    mock_provider.set_stream_exceptions([CONNECTION_ERROR])

    @llm.call("mock/default-model")
    async def greet() -> str:
        return "Hello"

    # Override with a RetryModel via context
    context_retry_model = llm.retry_model("mock/override-model", max_retries=1)

    with context_retry_model:
        response = await greet.stream()

        # First iteration fails
        with pytest.raises(llm.StreamRestarted):
            _ = [chunk async for chunk in response.chunk_stream()]

        # Second iteration succeeds
        chunks = [chunk async for chunk in response.chunk_stream()]
        assert len(chunks) > 0

    # Should have retried via the RetryModel
    assert response.model_id == "mock/override-model"
    assert mock_provider.stream_count == 2


# --- Model context with fallback models ---


def test_retry_call_with_retry_model_context_uses_fallbacks(
    mock_provider: MockProvider,
) -> None:
    """Test that RetryCall uses the context RetryModel's fallback models."""
    # Primary model fails, fallback succeeds
    mock_provider.set_exceptions([CONNECTION_ERROR])

    @llm.retry(max_retries=5)  # Call's config won't be used
    @llm.call("mock/default-model")
    def greet() -> str:
        return "Hello"

    # Override with a RetryModel that has fallback models
    context_retry_model = llm.retry_model(
        "mock/primary", max_retries=0, fallback_models=["mock/fallback"]
    )

    with context_retry_model:
        response = greet()

    # Should have used the fallback model
    assert response.model_id == "mock/fallback"
    assert len(response.retry_failures) == 1
    assert mock_provider.call_count == 2


@pytest.mark.asyncio
async def test_async_retry_call_with_retry_model_context_uses_fallbacks(
    mock_provider: MockProvider,
) -> None:
    """Test that async RetryCall uses the context RetryModel's fallback models."""
    # Primary model fails, fallback succeeds
    mock_provider.set_exceptions([CONNECTION_ERROR])

    @llm.retry(max_retries=5)  # Call's config won't be used
    @llm.call("mock/default-model")
    async def greet() -> str:
        return "Hello"

    # Override with a RetryModel that has fallback models
    context_retry_model = llm.retry_model(
        "mock/primary", max_retries=0, fallback_models=["mock/fallback"]
    )

    with context_retry_model:
        response = await greet()

    # Should have used the fallback model
    assert response.model_id == "mock/fallback"
    assert len(response.retry_failures) == 1
    assert mock_provider.call_count == 2
