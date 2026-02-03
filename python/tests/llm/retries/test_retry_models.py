"""Tests for RetryModel properties."""

import pytest

from mirascope import llm

from .conftest import CONNECTION_ERROR
from .mock_provider import MockProvider


def test_model_id_property(mock_provider: MockProvider) -> None:  # noqa: ARG001
    """Test that model_id delegates to wrapped model."""
    retry_model = llm.retry_model("mock/test-model", max_retries=2)

    assert retry_model.model_id == "mock/test-model"


def test_params_property(mock_provider: MockProvider) -> None:  # noqa: ARG001
    """Test that params delegates to wrapped model."""
    retry_model = llm.retry_model("mock/test-model", max_retries=2)

    assert retry_model.params is not None


# --- Context call method tests ---


def test_context_call_returns_context_retry_response(
    mock_provider: MockProvider,
) -> None:
    """Test that context_call returns a ContextRetryResponse."""
    ctx = llm.Context(deps=None)
    retry_model = llm.retry_model("mock/test-model", max_retries=1)

    response = retry_model.context_call("Hello", ctx=ctx)

    assert isinstance(response, llm.ContextRetryResponse)
    assert response.model_id == "mock/test-model"


def test_context_call_with_retry(mock_provider: MockProvider) -> None:
    """Test that context_call retries on failure and returns ContextRetryResponse."""
    mock_provider.set_exceptions([CONNECTION_ERROR])
    ctx = llm.Context(deps=None)
    retry_model = llm.retry_model("mock/test-model", max_retries=1)

    response = retry_model.context_call("Hello", ctx=ctx)

    assert isinstance(response, llm.ContextRetryResponse)
    assert len(response.retry_failures) == 1
    assert mock_provider.call_count == 2


def test_context_call_exhausts_retries(mock_provider: MockProvider) -> None:
    """Test that context_call raises RetriesExhausted when retries are exhausted."""
    mock_provider.set_exceptions([CONNECTION_ERROR, CONNECTION_ERROR])
    ctx = llm.Context(deps=None)
    retry_model = llm.retry_model("mock/test-model", max_retries=1)

    with pytest.raises(llm.RetriesExhausted) as exc_info:
        retry_model.context_call("Hello", ctx=ctx)

    assert len(exc_info.value.failures) == 2


@pytest.mark.asyncio
async def test_context_call_async_returns_async_context_retry_response(
    mock_provider: MockProvider,
) -> None:
    """Test that context_call_async returns an AsyncContextRetryResponse."""
    ctx = llm.Context(deps=None)
    retry_model = llm.retry_model("mock/test-model", max_retries=1)

    response = await retry_model.context_call_async("Hello", ctx=ctx)

    assert isinstance(response, llm.AsyncContextRetryResponse)
    assert response.model_id == "mock/test-model"


@pytest.mark.asyncio
async def test_context_call_async_with_retry(mock_provider: MockProvider) -> None:
    """Test that context_call_async retries on failure."""
    mock_provider.set_exceptions([CONNECTION_ERROR])
    ctx = llm.Context(deps=None)
    retry_model = llm.retry_model("mock/test-model", max_retries=1)

    response = await retry_model.context_call_async("Hello", ctx=ctx)

    assert isinstance(response, llm.AsyncContextRetryResponse)
    assert len(response.retry_failures) == 1
    assert mock_provider.call_count == 2


@pytest.mark.asyncio
async def test_context_call_async_exhausts_retries(mock_provider: MockProvider) -> None:
    """Test that context_call_async raises RetriesExhausted when retries are exhausted."""
    mock_provider.set_exceptions([CONNECTION_ERROR, CONNECTION_ERROR])
    ctx = llm.Context(deps=None)
    retry_model = llm.retry_model("mock/test-model", max_retries=1)

    with pytest.raises(llm.RetriesExhausted) as exc_info:
        await retry_model.context_call_async("Hello", ctx=ctx)

    assert len(exc_info.value.failures) == 2


# --- Context resume method tests ---


def test_context_resume_returns_context_retry_response(
    mock_provider: MockProvider,
) -> None:
    """Test that context_resume returns a ContextRetryResponse."""
    ctx = llm.Context(deps=None)
    retry_model = llm.retry_model("mock/test-model", max_retries=1)

    initial_response = retry_model.context_call("Hello", ctx=ctx)
    resumed = retry_model.context_resume(
        ctx=ctx, response=initial_response, content="Follow up"
    )

    assert isinstance(resumed, llm.ContextRetryResponse)
    assert resumed.model_id == "mock/test-model"


def test_context_resume_with_retry(mock_provider: MockProvider) -> None:
    """Test that context_resume retries on failure."""
    ctx = llm.Context(deps=None)
    retry_model = llm.retry_model("mock/test-model", max_retries=1)

    initial_response = retry_model.context_call("Hello", ctx=ctx)

    # Set exception for resume
    mock_provider.set_exceptions([CONNECTION_ERROR])

    resumed = retry_model.context_resume(
        ctx=ctx, response=initial_response, content="Follow up"
    )

    assert isinstance(resumed, llm.ContextRetryResponse)
    assert len(resumed.retry_failures) == 1


@pytest.mark.asyncio
async def test_context_resume_async_returns_async_context_retry_response(
    mock_provider: MockProvider,
) -> None:
    """Test that context_resume_async returns an AsyncContextRetryResponse."""
    ctx = llm.Context(deps=None)
    retry_model = llm.retry_model("mock/test-model", max_retries=1)

    initial_response = await retry_model.context_call_async("Hello", ctx=ctx)
    resumed = await retry_model.context_resume_async(
        ctx=ctx, response=initial_response, content="Follow up"
    )

    assert isinstance(resumed, llm.AsyncContextRetryResponse)
    assert resumed.model_id == "mock/test-model"


@pytest.mark.asyncio
async def test_context_resume_async_with_retry(mock_provider: MockProvider) -> None:
    """Test that context_resume_async retries on failure."""
    ctx = llm.Context(deps=None)
    retry_model = llm.retry_model("mock/test-model", max_retries=1)

    initial_response = await retry_model.context_call_async("Hello", ctx=ctx)

    # Set exception for resume
    mock_provider.set_exceptions([CONNECTION_ERROR])

    resumed = await retry_model.context_resume_async(
        ctx=ctx, response=initial_response, content="Follow up"
    )

    assert isinstance(resumed, llm.AsyncContextRetryResponse)
    assert len(resumed.retry_failures) == 1
