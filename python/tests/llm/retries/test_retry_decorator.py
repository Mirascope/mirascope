"""Tests for the @llm.retry decorator."""

import pytest

from mirascope import llm

from .mock_provider import MockProvider

# --- Sync decorator tests ---


def test_retry_on_call_produces_retry_call(mock_provider: MockProvider) -> None:
    """Test that retry() on a Call produces a RetryCall."""

    @llm.call("mock/test-model")
    def greet() -> str:
        return "Hello"

    retry_call = llm.retry(greet, max_retries=2)

    assert isinstance(retry_call, llm.RetryCall)
    response = retry_call()
    assert response.model.retry_config.max_retries == 2


def test_retry_on_retry_call_updates_config(mock_provider: MockProvider) -> None:
    """Test that retry() on a RetryCall updates the config."""

    @llm.retry(max_retries=2)
    @llm.call("mock/test-model")
    def greet() -> str:
        return "Hello"

    updated = llm.retry(greet, max_retries=4)
    response = updated()
    assert response.model.retry_config.max_retries == 4


def test_retry_on_prompt(mock_provider: MockProvider) -> None:
    """Test that retry() works on a Prompt."""

    @llm.prompt
    def greet() -> str:
        return "Hello"

    retry_prompt = llm.retry(greet, max_retries=2)

    assert isinstance(retry_prompt, llm.RetryPrompt)
    model = llm.Model("mock/test-model")
    response = retry_prompt(model)
    assert response.model.retry_config.max_retries == 2


def test_retry_on_retry_prompt_updates_config(mock_provider: MockProvider) -> None:
    """Test that retry() on a RetryPrompt updates the config."""

    @llm.prompt
    def greet() -> str:
        return "Hello"

    retry_prompt = llm.retry(greet, max_retries=2)
    updated = llm.retry(retry_prompt, max_retries=4)

    model = llm.Model("mock/test-model")
    response = updated(model)
    assert response.model.retry_config.max_retries == 4


# --- Async decorator tests ---


@pytest.mark.asyncio
async def test_retry_on_async_call(mock_provider: MockProvider) -> None:
    """Test that retry() works on an AsyncCall."""

    @llm.call("mock/test-model")
    async def greet() -> str:
        return "Hello"

    retry_call = llm.retry(greet, max_retries=2)

    assert isinstance(retry_call, llm.AsyncRetryCall)
    response = await retry_call()
    assert response.model.retry_config.max_retries == 2


@pytest.mark.asyncio
async def test_retry_on_async_retry_call_updates_config(
    mock_provider: MockProvider,
) -> None:
    """Test that retry() on an AsyncRetryCall updates the config."""

    @llm.retry(max_retries=2)
    @llm.call("mock/test-model")
    async def greet() -> str:
        return "Hello"

    updated = llm.retry(greet, max_retries=4)
    response = await updated()
    assert response.model.retry_config.max_retries == 4


@pytest.mark.asyncio
async def test_retry_on_async_prompt(mock_provider: MockProvider) -> None:
    """Test that retry() works on an AsyncPrompt."""

    @llm.prompt
    async def greet() -> str:
        return "Hello"

    retry_prompt = llm.retry(greet, max_retries=2)

    assert isinstance(retry_prompt, llm.AsyncRetryPrompt)
    model = llm.Model("mock/test-model")
    response = await retry_prompt(model)
    assert response.model.retry_config.max_retries == 2


@pytest.mark.asyncio
async def test_retry_on_async_retry_prompt_updates_config(
    mock_provider: MockProvider,
) -> None:
    """Test that retry() on an AsyncRetryPrompt updates the config."""

    @llm.prompt
    async def greet() -> str:
        return "Hello"

    retry_prompt = llm.retry(greet, max_retries=2)
    updated = llm.retry(retry_prompt, max_retries=4)

    model = llm.Model("mock/test-model")
    response = await updated(model)
    assert response.model.retry_config.max_retries == 4


# --- Error handling tests ---


def test_retry_raises_value_error_for_unsupported_type() -> None:
    """Test that retry raises ValueError for unsupported target types."""
    with pytest.raises(ValueError, match="Unsupported target type for retry"):
        llm.retry("not a valid target", max_retries=2)  # type: ignore[arg-type]
