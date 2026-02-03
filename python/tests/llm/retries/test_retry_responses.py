"""Tests for RetryResponse and AsyncRetryResponse property delegation."""

import pytest

from mirascope import llm

from .conftest import CONNECTION_ERROR, RATE_LIMIT_ERROR
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


def test_retry_config_property(mock_provider: MockProvider) -> None:  # noqa: ARG001
    """Test that retry_config property returns the retry configuration."""

    @llm.retry(max_retries=3)
    @llm.call("mock/test-model")
    def greet() -> str:
        return "Hello"

    response = greet()

    assert response.retry_config.max_retries == 3


@pytest.mark.asyncio
async def test_async_retry_config_property(mock_provider: MockProvider) -> None:  # noqa: ARG001
    """Test that async retry_config property returns the retry configuration."""

    @llm.retry(max_retries=3)
    @llm.call("mock/test-model")
    async def greet() -> str:
        return "Hello"

    response = await greet()

    assert response.retry_config.max_retries == 3


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


# --- Resume with fallback tests ---


def test_resume_uses_fallback_model_when_original_succeeded_on_fallback(
    mock_provider: MockProvider,
) -> None:
    """Test that resume uses the fallback model when original response succeeded on fallback."""
    # First call: primary fails, fallback succeeds
    mock_provider.set_exceptions([CONNECTION_ERROR])

    retry_model = llm.retry_model(
        "mock/primary", max_retries=0, fallback_models=["mock/fallback"]
    )

    response = retry_model.call("Hello")

    # Response should have succeeded on fallback
    assert response.model_id == "mock/fallback"
    assert len(response.retry_failures) == 1

    # Resume should use the fallback model (which succeeded)
    resumed = response.resume("Follow up")

    # Should succeed on fallback (no errors set)
    assert resumed.model_id == "mock/fallback"


def test_resume_can_fall_back_to_original_if_fallback_fails(
    mock_provider: MockProvider,
) -> None:
    """Test that resume can fall back to original model if the fallback model fails."""
    # First call: primary fails, fallback succeeds
    mock_provider.set_exceptions([CONNECTION_ERROR])

    retry_model = llm.retry_model(
        "mock/primary", max_retries=0, fallback_models=["mock/fallback"]
    )

    response = retry_model.call("Hello")

    # Response should have succeeded on fallback
    assert response.model_id == "mock/fallback"

    # For resume: fallback fails, primary succeeds
    mock_provider.set_exceptions([RATE_LIMIT_ERROR])

    resumed = response.resume("Follow up")

    # Should have fallen back to primary and succeeded
    assert resumed.model_id == "mock/primary"
    assert len(resumed.retry_failures) == 1
    assert resumed.retry_failures[0].model.model_id == "mock/fallback"


@pytest.mark.asyncio
async def test_async_resume_uses_fallback_model_when_original_succeeded_on_fallback(
    mock_provider: MockProvider,
) -> None:
    """Test that async resume uses the fallback model when original response succeeded on fallback."""
    # First call: primary fails, fallback succeeds
    mock_provider.set_exceptions([CONNECTION_ERROR])

    retry_model = llm.retry_model(
        "mock/primary", max_retries=0, fallback_models=["mock/fallback"]
    )

    response = await retry_model.call_async("Hello")

    # Response should have succeeded on fallback
    assert response.model_id == "mock/fallback"
    assert len(response.retry_failures) == 1

    # Resume should use the fallback model (which succeeded)
    resumed = await response.resume("Follow up")

    # Should succeed on fallback (no errors set)
    assert resumed.model_id == "mock/fallback"


@pytest.mark.asyncio
async def test_async_resume_can_fall_back_to_original_if_fallback_fails(
    mock_provider: MockProvider,
) -> None:
    """Test that async resume can fall back to original model if the fallback model fails."""
    # First call: primary fails, fallback succeeds
    mock_provider.set_exceptions([CONNECTION_ERROR])

    retry_model = llm.retry_model(
        "mock/primary", max_retries=0, fallback_models=["mock/fallback"]
    )

    response = await retry_model.call_async("Hello")

    # Response should have succeeded on fallback
    assert response.model_id == "mock/fallback"

    # For resume: fallback fails, primary succeeds
    mock_provider.set_exceptions([RATE_LIMIT_ERROR])

    resumed = await response.resume("Follow up")

    # Should have fallen back to primary and succeeded
    assert resumed.model_id == "mock/primary"
    assert len(resumed.retry_failures) == 1
    assert resumed.retry_failures[0].model.model_id == "mock/fallback"


# --- Context retry response tests ---


def test_context_retry_config_property(mock_provider: MockProvider) -> None:  # noqa: ARG001
    """Test that ContextRetryResponse.retry_config property returns the retry configuration."""
    retry_model = llm.retry_model("mock/test-model", max_retries=3)
    ctx = llm.Context(deps=None)

    response = retry_model.context_call("Hello", ctx=ctx)

    assert response.retry_config.max_retries == 3


@pytest.mark.asyncio
async def test_async_context_retry_config_property(
    mock_provider: MockProvider,  # noqa: ARG001
) -> None:
    """Test that AsyncContextRetryResponse.retry_config property returns the retry configuration."""
    retry_model = llm.retry_model("mock/test-model", max_retries=3)
    ctx = llm.Context(deps=None)

    response = await retry_model.context_call_async("Hello", ctx=ctx)

    assert response.retry_config.max_retries == 3
