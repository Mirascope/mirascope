"""Tests for RetryResponse and AsyncRetryResponse property delegation."""

import pytest

from mirascope import llm

from .mock_provider import MockProvider

# --- Sync RetryResponse tests ---


def test_response_properties_delegate_to_wrapped(mock_provider: MockProvider) -> None:
    """Test that all response properties delegate to the wrapped response."""

    @llm.retry(max_retries=1)
    @llm.call("mock/test-model")
    def greet() -> str:
        return "Hello"

    response = greet()

    # Test all delegated properties - these delegate to wrapped_response
    assert response.raw is not None
    assert response.provider_id == "mock"
    assert response.provider_model_name == "test-model"
    assert response.params is not None
    assert response.toolkit is not None
    assert response.messages is not None
    assert response.content is not None
    assert response.texts is not None
    assert response.tool_calls is not None
    assert response.thoughts is not None
    # These may be None depending on mock implementation
    _ = response.finish_reason
    _ = response.usage
    assert response.format is None  # No format specified
    assert response.parse() is None  # No format specified


def test_execute_tools(mock_provider: MockProvider) -> None:  # noqa: ARG001
    """Test that execute_tools delegates to wrapped response."""

    @llm.retry(max_retries=1)
    @llm.call("mock/test-model")
    def greet() -> str:
        return "Hello"

    response = greet()
    result = response.execute_tools()
    assert result == []  # No tool calls in mock response


# --- Async RetryResponse tests ---


@pytest.mark.asyncio
async def test_async_execute_tools(mock_provider: MockProvider) -> None:  # noqa: ARG001
    """Test that async execute_tools delegates to wrapped response."""

    @llm.retry(max_retries=1)
    @llm.call("mock/test-model")
    async def greet() -> str:
        return "Hello"

    response = await greet()
    result = await response.execute_tools()
    assert result == []  # No tool calls in mock response
