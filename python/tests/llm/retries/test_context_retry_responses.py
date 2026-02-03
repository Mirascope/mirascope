"""Tests for ContextRetryResponse and AsyncContextRetryResponse."""

import pytest

from mirascope import llm

from .conftest import CONNECTION_ERROR, RATE_LIMIT_ERROR
from .mock_provider import MockProvider

# --- Sync ContextRetryResponse tests ---


def test_context_retry_response_properties_delegate_to_wrapped(
    mock_provider: MockProvider,
) -> None:
    """Test that all response properties delegate to the wrapped response."""
    ctx = llm.Context(deps=None)
    retry_model = llm.retry_model("mock/test-model", max_retries=1)

    response = retry_model.context_call("Hello", ctx=ctx)

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


def test_context_retry_response_model_property(mock_provider: MockProvider) -> None:
    """Test that the model property returns a RetryModel."""
    ctx = llm.Context(deps=None)
    retry_model = llm.retry_model("mock/test-model", max_retries=1)

    response = retry_model.context_call("Hello", ctx=ctx)

    assert isinstance(response.model, llm.RetryModel)
    assert response.model.model_id == "mock/test-model"


def test_context_retry_response_retry_failures_empty_on_success(
    mock_provider: MockProvider,
) -> None:
    """Test that retry_failures is empty when the first attempt succeeds."""
    ctx = llm.Context(deps=None)
    retry_model = llm.retry_model("mock/test-model", max_retries=1)

    response = retry_model.context_call("Hello", ctx=ctx)

    assert response.retry_failures == []


def test_context_retry_response_retry_failures_populated_on_retry(
    mock_provider: MockProvider,
) -> None:
    """Test that retry_failures is populated when retries occur."""
    mock_provider.set_exceptions([CONNECTION_ERROR])
    ctx = llm.Context(deps=None)
    retry_model = llm.retry_model("mock/test-model", max_retries=1)

    response = retry_model.context_call("Hello", ctx=ctx)

    assert len(response.retry_failures) == 1
    assert response.retry_failures[0].model.model_id == "mock/test-model"
    assert response.retry_failures[0].exception is CONNECTION_ERROR


def test_context_retry_response_execute_tools(
    mock_provider: MockProvider,
) -> None:
    """Test that execute_tools works with context."""
    ctx = llm.Context(deps=None)
    retry_model = llm.retry_model("mock/test-model", max_retries=1)

    response = retry_model.context_call("Hello", ctx=ctx)
    result = response.execute_tools(ctx)
    assert result == []  # No tool calls in mock response


def test_context_retry_response_resume(mock_provider: MockProvider) -> None:
    """Test that resume delegates to model.context_resume with ctx."""
    ctx = llm.Context(deps=None)
    retry_model = llm.retry_model("mock/test-model", max_retries=1)

    response = retry_model.context_call("Hello", ctx=ctx)
    resumed = response.resume(ctx, "Follow up")

    assert isinstance(resumed, llm.ContextRetryResponse)
    assert resumed.model_id == "mock/test-model"


def test_context_retry_response_resume_uses_fallback_model(
    mock_provider: MockProvider,
) -> None:
    """Test that resume uses the fallback model when original succeeded on fallback."""
    # First call: primary fails, fallback succeeds
    mock_provider.set_exceptions([CONNECTION_ERROR])
    ctx = llm.Context(deps=None)
    retry_model = llm.retry_model(
        "mock/primary", max_retries=0, fallback_models=["mock/fallback"]
    )

    response = retry_model.context_call("Hello", ctx=ctx)

    # Response should have succeeded on fallback
    assert response.model_id == "mock/fallback"
    assert len(response.retry_failures) == 1

    # Resume should use the fallback model (which succeeded)
    resumed = response.resume(ctx, "Follow up")

    # Should succeed on fallback (no errors set)
    assert resumed.model_id == "mock/fallback"


def test_context_retry_response_resume_can_fall_back(
    mock_provider: MockProvider,
) -> None:
    """Test that resume can fall back to original model if fallback fails."""
    # First call: primary fails, fallback succeeds
    mock_provider.set_exceptions([CONNECTION_ERROR])
    ctx = llm.Context(deps=None)
    retry_model = llm.retry_model(
        "mock/primary", max_retries=0, fallback_models=["mock/fallback"]
    )

    response = retry_model.context_call("Hello", ctx=ctx)

    # Response should have succeeded on fallback
    assert response.model_id == "mock/fallback"

    # For resume: fallback fails, primary succeeds
    mock_provider.set_exceptions([RATE_LIMIT_ERROR])

    resumed = response.resume(ctx, "Follow up")

    # Should have fallen back to primary and succeeded
    assert resumed.model_id == "mock/primary"
    assert len(resumed.retry_failures) == 1
    assert resumed.retry_failures[0].model.model_id == "mock/fallback"


# --- Async AsyncContextRetryResponse tests ---


@pytest.mark.asyncio
async def test_async_context_retry_response_properties_delegate_to_wrapped(
    mock_provider: MockProvider,
) -> None:
    """Test that all async response properties delegate to the wrapped response."""
    ctx = llm.Context(deps=None)
    retry_model = llm.retry_model("mock/test-model", max_retries=1)

    response = await retry_model.context_call_async("Hello", ctx=ctx)

    # Test all delegated properties
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
    _ = response.finish_reason
    _ = response.usage
    assert response.format is None
    assert response.parse() is None


@pytest.mark.asyncio
async def test_async_context_retry_response_model_property(
    mock_provider: MockProvider,
) -> None:
    """Test that the model property returns a RetryModel."""
    ctx = llm.Context(deps=None)
    retry_model = llm.retry_model("mock/test-model", max_retries=1)

    response = await retry_model.context_call_async("Hello", ctx=ctx)

    assert isinstance(response.model, llm.RetryModel)
    assert response.model.model_id == "mock/test-model"


@pytest.mark.asyncio
async def test_async_context_retry_response_retry_failures_empty_on_success(
    mock_provider: MockProvider,
) -> None:
    """Test that retry_failures is empty when the first attempt succeeds."""
    ctx = llm.Context(deps=None)
    retry_model = llm.retry_model("mock/test-model", max_retries=1)

    response = await retry_model.context_call_async("Hello", ctx=ctx)

    assert response.retry_failures == []


@pytest.mark.asyncio
async def test_async_context_retry_response_retry_failures_populated_on_retry(
    mock_provider: MockProvider,
) -> None:
    """Test that retry_failures is populated when retries occur."""
    mock_provider.set_exceptions([CONNECTION_ERROR])
    ctx = llm.Context(deps=None)
    retry_model = llm.retry_model("mock/test-model", max_retries=1)

    response = await retry_model.context_call_async("Hello", ctx=ctx)

    assert len(response.retry_failures) == 1
    assert response.retry_failures[0].model.model_id == "mock/test-model"
    assert response.retry_failures[0].exception is CONNECTION_ERROR


@pytest.mark.asyncio
async def test_async_context_retry_response_execute_tools(
    mock_provider: MockProvider,
) -> None:
    """Test that async execute_tools works with context."""
    ctx = llm.Context(deps=None)
    retry_model = llm.retry_model("mock/test-model", max_retries=1)

    response = await retry_model.context_call_async("Hello", ctx=ctx)
    result = await response.execute_tools(ctx)
    assert result == []  # No tool calls in mock response


@pytest.mark.asyncio
async def test_async_context_retry_response_resume(mock_provider: MockProvider) -> None:
    """Test that async resume delegates to model.context_resume_async with ctx."""
    ctx = llm.Context(deps=None)
    retry_model = llm.retry_model("mock/test-model", max_retries=1)

    response = await retry_model.context_call_async("Hello", ctx=ctx)
    resumed = await response.resume(ctx, "Follow up")

    assert isinstance(resumed, llm.AsyncContextRetryResponse)
    assert resumed.model_id == "mock/test-model"


@pytest.mark.asyncio
async def test_async_context_retry_response_resume_uses_fallback_model(
    mock_provider: MockProvider,
) -> None:
    """Test that async resume uses the fallback model when original succeeded on fallback."""
    # First call: primary fails, fallback succeeds
    mock_provider.set_exceptions([CONNECTION_ERROR])
    ctx = llm.Context(deps=None)
    retry_model = llm.retry_model(
        "mock/primary", max_retries=0, fallback_models=["mock/fallback"]
    )

    response = await retry_model.context_call_async("Hello", ctx=ctx)

    # Response should have succeeded on fallback
    assert response.model_id == "mock/fallback"
    assert len(response.retry_failures) == 1

    # Resume should use the fallback model (which succeeded)
    resumed = await response.resume(ctx, "Follow up")

    # Should succeed on fallback (no errors set)
    assert resumed.model_id == "mock/fallback"


@pytest.mark.asyncio
async def test_async_context_retry_response_resume_can_fall_back(
    mock_provider: MockProvider,
) -> None:
    """Test that async resume can fall back to original model if fallback fails."""
    # First call: primary fails, fallback succeeds
    mock_provider.set_exceptions([CONNECTION_ERROR])
    ctx = llm.Context(deps=None)
    retry_model = llm.retry_model(
        "mock/primary", max_retries=0, fallback_models=["mock/fallback"]
    )

    response = await retry_model.context_call_async("Hello", ctx=ctx)

    # Response should have succeeded on fallback
    assert response.model_id == "mock/fallback"

    # For resume: fallback fails, primary succeeds
    mock_provider.set_exceptions([RATE_LIMIT_ERROR])

    resumed = await response.resume(ctx, "Follow up")

    # Should have fallen back to primary and succeeded
    assert resumed.model_id == "mock/primary"
    assert len(resumed.retry_failures) == 1
    assert resumed.retry_failures[0].model.model_id == "mock/fallback"
