"""Tests for ContextRetryStreamResponse and AsyncContextRetryStreamResponse."""

import pytest

from mirascope import llm

from .conftest import CONNECTION_ERROR, RATE_LIMIT_ERROR, SERVER_ERROR, TIMEOUT_ERROR
from .mock_provider import MockProvider

# --- Sync ContextRetryStreamResponse tests ---


def test_context_stream_succeeds_first_attempt(mock_provider: MockProvider) -> None:
    """Test that a successful context stream completes without raising StreamRestarted."""
    ctx = llm.Context(deps=None)
    retry_model = llm.retry_model("mock/test-model", max_retries=2)

    response = retry_model.context_stream("Hello", ctx=ctx)

    # Consume the stream
    chunks = list(response.text_stream())

    assert "mock " in "".join(chunks)
    assert "response" in "".join(chunks)
    assert len(response.retry_failures) == 0
    assert mock_provider.stream_count == 1


def test_context_stream_raises_stream_restarted_on_error(
    mock_provider: MockProvider,
) -> None:
    """Test that StreamRestarted is raised when a retryable error occurs mid-stream."""
    mock_provider.set_stream_exceptions([CONNECTION_ERROR])
    ctx = llm.Context(deps=None)
    retry_model = llm.retry_model("mock/test-model", max_retries=2)

    response = retry_model.context_stream("Hello", ctx=ctx)

    # First iteration should raise StreamRestarted
    with pytest.raises(llm.StreamRestarted) as exc_info:
        list(response.text_stream())

    assert exc_info.value.failure.exception is CONNECTION_ERROR
    assert len(response.retry_failures) == 1
    assert [f.exception for f in response.retry_failures] == [CONNECTION_ERROR]


def test_context_stream_can_continue_after_restart(mock_provider: MockProvider) -> None:
    """Test that user can re-iterate after catching StreamRestarted."""
    mock_provider.set_stream_exceptions([CONNECTION_ERROR])
    ctx = llm.Context(deps=None)
    retry_model = llm.retry_model("mock/test-model", max_retries=2)

    response = retry_model.context_stream("Hello", ctx=ctx)
    restart_count = 0

    # Use the recommended pattern: catch StreamRestarted and re-iterate
    while True:
        try:
            chunks = list(response.text_stream())
            break
        except llm.StreamRestarted:
            restart_count += 1

    assert restart_count == 1
    assert "mock " in "".join(chunks)
    assert "response" in "".join(chunks)
    assert len(response.retry_failures) == 1
    assert mock_provider.stream_count == 2


def test_context_stream_raises_retries_exhausted_after_max_attempts(
    mock_provider: MockProvider,
) -> None:
    """Test that RetriesExhausted is raised when max attempts exhausted."""
    # Set more errors than max_attempts allows
    mock_provider.set_stream_exceptions([CONNECTION_ERROR, RATE_LIMIT_ERROR])
    ctx = llm.Context(deps=None)
    retry_model = llm.retry_model("mock/test-model", max_retries=1)

    response = retry_model.context_stream("Hello", ctx=ctx)

    # First attempt fails, catch StreamRestarted
    with pytest.raises(llm.StreamRestarted):
        list(response.text_stream())

    # Second attempt also fails, should raise RetriesExhausted (not StreamRestarted)
    with pytest.raises(llm.RetriesExhausted) as exc_info:
        list(response.text_stream())

    # RetriesExhausted contains both failures
    assert len(exc_info.value.failures) == 2
    assert isinstance(exc_info.value.failures[0].exception, llm.ConnectionError)
    assert isinstance(exc_info.value.failures[1].exception, llm.RateLimitError)
    assert mock_provider.stream_count == 2


def test_context_stream_model_property(mock_provider: MockProvider) -> None:  # noqa: ARG001
    """Test that model property returns RetryModel."""
    ctx = llm.Context(deps=None)
    retry_model = llm.retry_model("mock/test-model", max_retries=2)

    response = retry_model.context_stream("Hello", ctx=ctx)

    assert isinstance(response.model, llm.RetryModel)
    assert response.model.model_id == "mock/test-model"


def test_context_stream_delegated_properties(mock_provider: MockProvider) -> None:
    """Test that all properties delegate to the wrapped stream response."""
    ctx = llm.Context(deps=None)
    retry_model = llm.retry_model("mock/test-model", max_retries=1)

    response = retry_model.context_stream("Hello", ctx=ctx)

    # Consume the stream to populate properties
    list(response.chunk_stream())

    # Test all delegated properties
    assert response.raw_stream_events is not None
    assert response.chunks is not None
    assert response.provider_id == "mock"
    assert response.model_id == "mock/test-model"
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
    assert response.consumed is True
    assert response.format is None
    assert response.parse() is None


def test_context_stream_execute_tools(mock_provider: MockProvider) -> None:  # noqa: ARG001
    """Test that execute_tools delegates to wrapped response with ctx."""
    ctx = llm.Context(deps=None)
    retry_model = llm.retry_model("mock/test-model", max_retries=1)

    response = retry_model.context_stream("Hello", ctx=ctx)
    response.finish()

    result = response.execute_tools(ctx)
    assert result == []


def test_context_stream_resume(mock_provider: MockProvider) -> None:
    """Test that resume returns a new ContextRetryStreamResponse."""
    ctx = llm.Context(deps=None)
    retry_model = llm.retry_model("mock/test-model", max_retries=2)

    response = retry_model.context_stream("Hello", ctx=ctx)
    response.finish()

    resumed = response.resume(ctx, "Follow up")

    assert isinstance(resumed, llm.ContextRetryStreamResponse)
    assert mock_provider.stream_count == 2


def test_context_stream_resume_uses_fallback_model(mock_provider: MockProvider) -> None:
    """Test that stream resume uses the fallback model when original succeeded on fallback."""
    # First stream: primary fails, fallback succeeds
    mock_provider.set_stream_exceptions([CONNECTION_ERROR])
    ctx = llm.Context(deps=None)
    retry_model = llm.retry_model(
        "mock/primary", max_retries=0, fallback_models=["mock/fallback"]
    )

    response = retry_model.context_stream("Hello", ctx=ctx)

    # First iteration fails (primary), raises StreamRestarted
    with pytest.raises(llm.StreamRestarted):
        list(response.chunk_stream())

    # After restart, should be on fallback model
    assert response.model.model_id == "mock/fallback"

    # Second iteration succeeds on fallback
    list(response.chunk_stream())

    # Resume should use the fallback model (which succeeded)
    resumed = response.resume(ctx, "Follow up")

    # Should start on fallback (no errors set)
    assert resumed.model.model_id == "mock/fallback"

    # Should succeed on fallback
    chunks = list(resumed.chunk_stream())
    assert len(chunks) > 0


def test_context_stream_resume_can_fall_back(mock_provider: MockProvider) -> None:
    """Test that stream resume can fall back to original model if fallback fails."""
    # First stream: primary fails, fallback succeeds
    mock_provider.set_stream_exceptions([CONNECTION_ERROR])
    ctx = llm.Context(deps=None)
    retry_model = llm.retry_model(
        "mock/primary", max_retries=0, fallback_models=["mock/fallback"]
    )

    response = retry_model.context_stream("Hello", ctx=ctx)

    # First iteration fails (primary), raises StreamRestarted
    with pytest.raises(llm.StreamRestarted):
        list(response.chunk_stream())

    # After restart, should be on fallback model
    assert response.model.model_id == "mock/fallback"

    # Second iteration succeeds on fallback
    list(response.chunk_stream())

    # For resume: fallback fails, primary succeeds
    mock_provider.set_stream_exceptions([RATE_LIMIT_ERROR])

    resumed = response.resume(ctx, "Follow up")

    # Should start on fallback model (which succeeded before)
    assert resumed.model.model_id == "mock/fallback"

    # First iteration of resume fails (fallback), raises StreamRestarted
    with pytest.raises(llm.StreamRestarted):
        list(resumed.chunk_stream())

    # After restart, should be on primary model
    assert resumed.model.model_id == "mock/primary"
    assert len(resumed.retry_failures) == 1
    assert resumed.retry_failures[0].model.model_id == "mock/fallback"

    # Second iteration succeeds on primary
    chunks = list(resumed.chunk_stream())
    assert len(chunks) > 0


# --- Async AsyncContextRetryStreamResponse tests ---


@pytest.mark.asyncio
async def test_async_context_stream_succeeds_first_attempt(
    mock_provider: MockProvider,
) -> None:
    """Test that a successful async context stream completes without raising StreamRestarted."""
    ctx = llm.Context(deps=None)
    retry_model = llm.retry_model("mock/test-model", max_retries=2)

    response = await retry_model.context_stream_async("Hello", ctx=ctx)

    # Consume the stream
    chunks = [chunk async for chunk in response.text_stream()]

    assert "mock " in "".join(chunks)
    assert "response" in "".join(chunks)
    assert len(response.retry_failures) == 0
    assert mock_provider.stream_count == 1


@pytest.mark.asyncio
async def test_async_context_stream_raises_stream_restarted_on_error(
    mock_provider: MockProvider,
) -> None:
    """Test that StreamRestarted is raised when a retryable error occurs mid-stream."""
    mock_provider.set_stream_exceptions([TIMEOUT_ERROR])
    ctx = llm.Context(deps=None)
    retry_model = llm.retry_model("mock/test-model", max_retries=2)

    response = await retry_model.context_stream_async("Hello", ctx=ctx)

    # First iteration should raise StreamRestarted
    with pytest.raises(llm.StreamRestarted) as exc_info:
        _ = [chunk async for chunk in response.text_stream()]

    assert exc_info.value.failure.exception is TIMEOUT_ERROR
    assert len(response.retry_failures) == 1


@pytest.mark.asyncio
async def test_async_context_stream_can_continue_after_restart(
    mock_provider: MockProvider,
) -> None:
    """Test that user can re-iterate after catching StreamRestarted."""
    mock_provider.set_stream_exceptions([SERVER_ERROR])
    ctx = llm.Context(deps=None)
    retry_model = llm.retry_model("mock/test-model", max_retries=2)

    response = await retry_model.context_stream_async("Hello", ctx=ctx)
    restart_count = 0

    # Use the recommended pattern: catch StreamRestarted and re-iterate
    while True:
        try:
            chunks = [chunk async for chunk in response.text_stream()]
            break
        except llm.StreamRestarted:
            restart_count += 1

    assert restart_count == 1
    assert "mock " in "".join(chunks)
    assert "response" in "".join(chunks)
    assert len(response.retry_failures) == 1
    assert mock_provider.stream_count == 2


@pytest.mark.asyncio
async def test_async_context_stream_raises_retries_exhausted_after_max_attempts(
    mock_provider: MockProvider,
) -> None:
    """Test that RetriesExhausted is raised when max attempts exhausted."""
    mock_provider.set_stream_exceptions([CONNECTION_ERROR, SERVER_ERROR])
    ctx = llm.Context(deps=None)
    retry_model = llm.retry_model("mock/test-model", max_retries=1)

    response = await retry_model.context_stream_async("Hello", ctx=ctx)

    # First attempt fails, catch StreamRestarted
    with pytest.raises(llm.StreamRestarted):
        _ = [chunk async for chunk in response.text_stream()]

    # Second attempt also fails, should raise RetriesExhausted
    with pytest.raises(llm.RetriesExhausted) as exc_info:
        _ = [chunk async for chunk in response.text_stream()]

    # RetriesExhausted contains both failures
    assert len(exc_info.value.failures) == 2
    assert isinstance(exc_info.value.failures[0].exception, llm.ConnectionError)
    assert isinstance(exc_info.value.failures[1].exception, llm.ServerError)
    assert mock_provider.stream_count == 2


@pytest.mark.asyncio
async def test_async_context_stream_model_property(
    mock_provider: MockProvider,
) -> None:  # noqa: ARG001
    """Test that model property returns RetryModel."""
    ctx = llm.Context(deps=None)
    retry_model = llm.retry_model("mock/test-model", max_retries=2)

    response = await retry_model.context_stream_async("Hello", ctx=ctx)

    assert isinstance(response.model, llm.RetryModel)
    assert response.model.model_id == "mock/test-model"


@pytest.mark.asyncio
async def test_async_context_stream_delegated_properties(
    mock_provider: MockProvider,
) -> None:
    """Test that all properties delegate to the wrapped async stream response."""
    ctx = llm.Context(deps=None)
    retry_model = llm.retry_model("mock/test-model", max_retries=1)

    response = await retry_model.context_stream_async("Hello", ctx=ctx)

    # Consume the stream to populate properties
    async for _ in response.chunk_stream():
        pass

    # Test all delegated properties
    assert response.raw_stream_events is not None
    assert response.chunks is not None
    assert response.provider_id == "mock"
    assert response.model_id == "mock/test-model"
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
    assert response.consumed is True
    assert response.format is None
    assert response.parse() is None


@pytest.mark.asyncio
async def test_async_context_stream_execute_tools(
    mock_provider: MockProvider,
) -> None:  # noqa: ARG001
    """Test that async execute_tools delegates to wrapped response with ctx."""
    ctx = llm.Context(deps=None)
    retry_model = llm.retry_model("mock/test-model", max_retries=1)

    response = await retry_model.context_stream_async("Hello", ctx=ctx)
    await response.finish()

    result = await response.execute_tools(ctx)
    assert result == []


@pytest.mark.asyncio
async def test_async_context_stream_resume(mock_provider: MockProvider) -> None:
    """Test that async resume returns a new AsyncContextRetryStreamResponse."""
    ctx = llm.Context(deps=None)
    retry_model = llm.retry_model("mock/test-model", max_retries=2)

    response = await retry_model.context_stream_async("Hello", ctx=ctx)
    await response.finish()

    resumed = await response.resume(ctx, "Follow up")

    assert isinstance(resumed, llm.AsyncContextRetryStreamResponse)
    assert mock_provider.stream_count == 2


@pytest.mark.asyncio
async def test_async_context_stream_resume_uses_fallback_model(
    mock_provider: MockProvider,
) -> None:
    """Test that async stream resume uses the fallback model when original succeeded on fallback."""
    # First stream: primary fails, fallback succeeds
    mock_provider.set_stream_exceptions([CONNECTION_ERROR])
    ctx = llm.Context(deps=None)
    retry_model = llm.retry_model(
        "mock/primary", max_retries=0, fallback_models=["mock/fallback"]
    )

    response = await retry_model.context_stream_async("Hello", ctx=ctx)

    # First iteration fails (primary), raises StreamRestarted
    with pytest.raises(llm.StreamRestarted):
        _ = [chunk async for chunk in response.chunk_stream()]

    # After restart, should be on fallback model
    assert response.model.model_id == "mock/fallback"

    # Second iteration succeeds on fallback
    _ = [chunk async for chunk in response.chunk_stream()]

    # Resume should use the fallback model (which succeeded)
    resumed = await response.resume(ctx, "Follow up")

    # Should start on fallback (no errors set)
    assert resumed.model.model_id == "mock/fallback"

    # Should succeed on fallback
    chunks = [chunk async for chunk in resumed.chunk_stream()]
    assert len(chunks) > 0


@pytest.mark.asyncio
async def test_async_context_stream_resume_can_fall_back(
    mock_provider: MockProvider,
) -> None:
    """Test that async stream resume can fall back to original model if fallback fails."""
    # First stream: primary fails, fallback succeeds
    mock_provider.set_stream_exceptions([CONNECTION_ERROR])
    ctx = llm.Context(deps=None)
    retry_model = llm.retry_model(
        "mock/primary", max_retries=0, fallback_models=["mock/fallback"]
    )

    response = await retry_model.context_stream_async("Hello", ctx=ctx)

    # First iteration fails (primary), raises StreamRestarted
    with pytest.raises(llm.StreamRestarted):
        _ = [chunk async for chunk in response.chunk_stream()]

    # After restart, should be on fallback model
    assert response.model.model_id == "mock/fallback"

    # Second iteration succeeds on fallback
    _ = [chunk async for chunk in response.chunk_stream()]

    # For resume: fallback fails, primary succeeds
    mock_provider.set_stream_exceptions([RATE_LIMIT_ERROR])

    resumed = await response.resume(ctx, "Follow up")

    # Should start on fallback model (which succeeded before)
    assert resumed.model.model_id == "mock/fallback"

    # First iteration of resume fails (fallback), raises StreamRestarted
    with pytest.raises(llm.StreamRestarted):
        _ = [chunk async for chunk in resumed.chunk_stream()]

    # After restart, should be on primary model
    assert resumed.model.model_id == "mock/primary"
    assert len(resumed.retry_failures) == 1
    assert resumed.retry_failures[0].model.model_id == "mock/fallback"

    # Second iteration succeeds on primary
    chunks = [chunk async for chunk in resumed.chunk_stream()]
    assert len(chunks) > 0
