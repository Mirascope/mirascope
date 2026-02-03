"""Tests for RetryPrompt and AsyncRetryPrompt property delegation."""

import pytest

from mirascope import llm

from .mock_provider import MockProvider

# --- Sync RetryPrompt tests ---


def test_fn_property(mock_provider: MockProvider) -> None:  # noqa: ARG001
    """Test that fn delegates to wrapped prompt."""

    @llm.prompt
    def greet() -> str:
        return "Hello"

    retry_prompt = llm.retry(greet, max_retries=2)

    assert retry_prompt.fn is greet.fn


def test_call_with_string_model_id(mock_provider: MockProvider) -> None:
    """Test that RetryPrompt.call accepts a string model ID."""

    @llm.prompt
    def greet() -> str:
        return "Hello"

    retry_prompt = llm.retry(greet, max_retries=2)

    # Pass model as string instead of Model object
    response = retry_prompt.call("mock/test-model")

    assert response.pretty() == "mock response"
    assert mock_provider.call_count == 1


# --- Async RetryPrompt tests ---


@pytest.mark.asyncio
async def test_async_fn_property(mock_provider: MockProvider) -> None:  # noqa: ARG001
    """Test that fn delegates to wrapped async prompt."""

    @llm.prompt
    async def greet() -> str:
        return "Hello"

    retry_prompt = llm.retry(greet, max_retries=2)

    assert retry_prompt.fn is greet.fn


@pytest.mark.asyncio
async def test_async_call_with_string_model_id(mock_provider: MockProvider) -> None:
    """Test that AsyncRetryPrompt.call accepts a string model ID."""

    @llm.prompt
    async def greet() -> str:
        return "Hello"

    retry_prompt = llm.retry(greet, max_retries=2)

    # Pass model as string instead of Model object
    response = await retry_prompt.call("mock/test-model")

    assert response.pretty() == "mock response"
    assert mock_provider.call_count == 1
