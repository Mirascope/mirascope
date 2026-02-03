"""Tests for RetryStreamResponse and AsyncRetryStreamResponse."""

import pytest
from pydantic import BaseModel

from mirascope import llm

from .conftest import CONNECTION_ERROR, RATE_LIMIT_ERROR, SERVER_ERROR, TIMEOUT_ERROR
from .mock_provider import MockProvider

# --- Sync streaming tests ---


def test_stream_succeeds_first_attempt(mock_provider: MockProvider) -> None:
    """Test that a successful stream completes without raising StreamRestarted."""

    @llm.retry(max_retries=2)
    @llm.call("mock/test-model")
    def greet() -> str:
        return "Hello"

    response = greet.stream()

    # Consume the stream
    chunks = list(response.text_stream())

    assert "mock " in "".join(chunks)
    assert "response" in "".join(chunks)
    assert len(response.retry_failures) == 0
    assert mock_provider.stream_count == 1


def test_stream_raises_stream_restarted_on_error(mock_provider: MockProvider) -> None:
    """Test that StreamRestarted is raised when a retryable error occurs mid-stream."""
    mock_provider.set_stream_exceptions([CONNECTION_ERROR])

    @llm.retry(max_retries=2)
    @llm.call("mock/test-model")
    def greet() -> str:
        return "Hello"

    response = greet.stream()

    # First iteration should raise StreamRestarted
    with pytest.raises(llm.StreamRestarted) as exc_info:
        list(response.text_stream())

    assert exc_info.value.failure.exception is CONNECTION_ERROR
    assert len(response.retry_failures) == 1
    assert [f.exception for f in response.retry_failures] == [CONNECTION_ERROR]


def test_stream_can_continue_after_restart(mock_provider: MockProvider) -> None:
    """Test that user can re-iterate after catching StreamRestarted."""
    mock_provider.set_stream_exceptions([CONNECTION_ERROR])

    @llm.retry(max_retries=2)
    @llm.call("mock/test-model")
    def greet() -> str:
        return "Hello"

    response = greet.stream()
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


def test_stream_raises_retries_exhausted_after_max_attempts(
    mock_provider: MockProvider,
) -> None:
    """Test that RetriesExhausted is raised when max attempts exhausted."""
    # Set more errors than max_attempts allows
    mock_provider.set_stream_exceptions([CONNECTION_ERROR, RATE_LIMIT_ERROR])

    @llm.retry(max_retries=1)
    @llm.call("mock/test-model")
    def greet() -> str:
        return "Hello"

    response = greet.stream()

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


def test_stream_retry_failures_accessible(mock_provider: MockProvider) -> None:
    """Test that retry_failures is accessible from the response."""
    mock_provider.set_stream_exceptions([SERVER_ERROR])

    @llm.retry(max_retries=4)
    @llm.call("mock/test-model")
    def greet() -> str:
        return "Hello"

    response = greet.stream()

    # Initial state
    assert response.model.retry_config.max_retries == 4
    assert len(response.retry_failures) == 0

    # After first error
    with pytest.raises(llm.StreamRestarted):
        list(response.text_stream())

    assert len(response.retry_failures) == 1


def test_stream_model_property(mock_provider: MockProvider) -> None:  # noqa: ARG001
    """Test that model property returns RetryModel."""

    @llm.retry(max_retries=2)
    @llm.call("mock/test-model")
    def greet() -> str:
        return "Hello"

    response = greet.stream()

    assert isinstance(response.model, llm.RetryModel)
    assert response.model.model_id == "mock/test-model"


def test_stream_retry_config_property(mock_provider: MockProvider) -> None:  # noqa: ARG001
    """Test that retry_config property returns the retry configuration."""

    @llm.retry(max_retries=3)
    @llm.call("mock/test-model")
    def greet() -> str:
        return "Hello"

    response = greet.stream()

    assert response.retry_config.max_retries == 3


@pytest.mark.asyncio
async def test_async_stream_retry_config_property(
    mock_provider: MockProvider,  # noqa: ARG001
) -> None:
    """Test that async retry_config property returns the retry configuration."""

    @llm.retry(max_retries=3)
    @llm.call("mock/test-model")
    async def greet() -> str:
        return "Hello"

    response = await greet.stream()

    assert response.retry_config.max_retries == 3


# --- Async streaming tests ---


@pytest.mark.asyncio
async def test_stream_async_succeeds_first_attempt(mock_provider: MockProvider) -> None:
    """Test that a successful async stream completes without raising StreamRestarted."""

    @llm.retry(max_retries=2)
    @llm.call("mock/test-model")
    async def greet() -> str:
        return "Hello"

    response = await greet.stream()

    # Consume the stream
    chunks = [chunk async for chunk in response.text_stream()]

    assert "mock " in "".join(chunks)
    assert "response" in "".join(chunks)
    assert len(response.retry_failures) == 0
    assert mock_provider.stream_count == 1


@pytest.mark.asyncio
async def test_stream_async_raises_stream_restarted_on_error(
    mock_provider: MockProvider,
) -> None:
    """Test that StreamRestarted is raised when a retryable error occurs mid-stream."""
    mock_provider.set_stream_exceptions([TIMEOUT_ERROR])

    @llm.retry(max_retries=2)
    @llm.call("mock/test-model")
    async def greet() -> str:
        return "Hello"

    response = await greet.stream()

    # First iteration should raise StreamRestarted
    with pytest.raises(llm.StreamRestarted) as exc_info:
        _ = [chunk async for chunk in response.text_stream()]

    assert exc_info.value.failure.exception is TIMEOUT_ERROR
    assert len(response.retry_failures) == 1


@pytest.mark.asyncio
async def test_stream_async_can_continue_after_restart(
    mock_provider: MockProvider,
) -> None:
    """Test that user can re-iterate after catching StreamRestarted."""
    mock_provider.set_stream_exceptions([SERVER_ERROR])

    @llm.retry(max_retries=2)
    @llm.call("mock/test-model")
    async def greet() -> str:
        return "Hello"

    response = await greet.stream()
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
async def test_stream_async_raises_retries_exhausted_after_max_attempts(
    mock_provider: MockProvider,
) -> None:
    """Test that RetriesExhausted is raised when max attempts exhausted."""
    mock_provider.set_stream_exceptions([CONNECTION_ERROR, SERVER_ERROR])

    @llm.retry(max_retries=1)
    @llm.call("mock/test-model")
    async def greet() -> str:
        return "Hello"

    response = await greet.stream()

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


# --- Sync RetryStreamResponse property tests ---


def test_delegated_properties(mock_provider: MockProvider) -> None:
    """Test that all properties delegate to the wrapped stream response."""

    @llm.retry(max_retries=1)
    @llm.call("mock/test-model")
    def greet() -> str:
        return "Hello"

    response = greet.stream()

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


def test_finish_method(mock_provider: MockProvider) -> None:
    """Test that finish() consumes the stream."""

    @llm.retry(max_retries=1)
    @llm.call("mock/test-model")
    def greet() -> str:
        return "Hello"

    response = greet.stream()
    assert response.consumed is False

    response.finish()

    assert response.consumed is True
    assert mock_provider.stream_count == 1


def test_pretty_stream(mock_provider: MockProvider) -> None:
    """Test that pretty_stream() yields formatted text."""

    @llm.retry(max_retries=1)
    @llm.call("mock/test-model")
    def greet() -> str:
        return "Hello"

    response = greet.stream()

    output = list(response.pretty_stream())

    # Should have content from the mock stream
    full_output = "".join(output)
    assert "mock " in full_output or "response" in full_output
    assert mock_provider.stream_count == 1


def test_streams_method(mock_provider: MockProvider) -> None:
    """Test that streams() yields Stream objects."""

    @llm.retry(max_retries=1)
    @llm.call("mock/test-model")
    def greet() -> str:
        return "Hello"

    response = greet.stream()
    streams = list(response.streams())

    assert len(streams) == 1
    assert streams[0].content_type == "text"
    assert mock_provider.stream_count == 1


def test_execute_tools_sync(mock_provider: MockProvider) -> None:  # noqa: ARG001
    """Test that execute_tools delegates to wrapped response."""

    @llm.retry(max_retries=1)
    @llm.call("mock/test-model")
    def greet() -> str:
        return "Hello"

    response = greet.stream()
    response.finish()

    result = response.execute_tools()
    assert result == []


def test_pretty_method(mock_provider: MockProvider) -> None:
    """Test that pretty() returns formatted text after consumption."""

    @llm.retry(max_retries=1)
    @llm.call("mock/test-model")
    def greet() -> str:
        return "Hello"

    response = greet.stream()
    response.finish()

    output = response.pretty()
    assert "mock response" in output


# --- Async RetryStreamResponse property tests ---


@pytest.mark.asyncio
async def test_async_delegated_properties(mock_provider: MockProvider) -> None:
    """Test that all properties delegate to the wrapped async stream response."""

    @llm.retry(max_retries=1)
    @llm.call("mock/test-model")
    async def greet() -> str:
        return "Hello"

    response = await greet.stream()

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
async def test_async_finish_method(mock_provider: MockProvider) -> None:
    """Test that finish() consumes the async stream."""

    @llm.retry(max_retries=1)
    @llm.call("mock/test-model")
    async def greet() -> str:
        return "Hello"

    response = await greet.stream()
    assert response.consumed is False

    await response.finish()

    assert response.consumed is True
    assert mock_provider.stream_count == 1


@pytest.mark.asyncio
async def test_async_pretty_stream(mock_provider: MockProvider) -> None:
    """Test that pretty_stream() yields formatted text."""

    @llm.retry(max_retries=1)
    @llm.call("mock/test-model")
    async def greet() -> str:
        return "Hello"

    response = await greet.stream()

    output = [chunk async for chunk in response.pretty_stream()]

    # Should have content from the mock stream
    full_output = "".join(output)
    assert "mock " in full_output or "response" in full_output
    assert mock_provider.stream_count == 1


@pytest.mark.asyncio
async def test_async_streams_method(mock_provider: MockProvider) -> None:
    """Test that streams() yields AsyncStream objects."""

    @llm.retry(max_retries=1)
    @llm.call("mock/test-model")
    async def greet() -> str:
        return "Hello"

    response = await greet.stream()
    streams = [s async for s in response.streams()]

    assert len(streams) == 1
    assert streams[0].content_type == "text"
    assert mock_provider.stream_count == 1


@pytest.mark.asyncio
async def test_async_execute_tools(mock_provider: MockProvider) -> None:  # noqa: ARG001
    """Test that execute_tools delegates to wrapped response."""

    @llm.retry(max_retries=1)
    @llm.call("mock/test-model")
    async def greet() -> str:
        return "Hello"

    response = await greet.stream()
    await response.finish()

    result = await response.execute_tools()
    assert result == []


@pytest.mark.asyncio
async def test_async_pretty_method(mock_provider: MockProvider) -> None:
    """Test that pretty() returns formatted text after consumption."""

    @llm.retry(max_retries=1)
    @llm.call("mock/test-model")
    async def greet() -> str:
        return "Hello"

    response = await greet.stream()
    await response.finish()

    output = response.pretty()
    assert "mock response" in output


# --- Sync structured_stream tests ---


def test_structured_stream_raises_without_format(
    mock_provider: MockProvider,  # noqa: ARG001
) -> None:
    """Test that structured_stream raises ValueError without format."""

    @llm.retry(max_retries=1)
    @llm.call("mock/test-model")
    def greet() -> str:
        return "Hello"

    response = greet.stream()

    with pytest.raises(ValueError, match="structured_stream\\(\\) requires format"):
        list(response.structured_stream())


def test_structured_stream_yields_partials(mock_provider: MockProvider) -> None:
    """Test that structured_stream yields partial outputs."""

    class Person(BaseModel):
        name: str
        age: int

    # Set up mock to return valid JSON
    mock_provider.set_stream_text('{"name": "Alice", "age": 30}')

    retry_model = llm.retry_model("mock/test-model", max_retries=1)

    response = retry_model.stream("Get person", format=Person)

    partials = list(response.structured_stream())

    # Should have yielded at least one partial
    assert len(partials) >= 1


def test_structured_stream_raises_for_output_parser(
    mock_provider: MockProvider,  # noqa: ARG001
) -> None:
    """Test that structured_stream raises NotImplementedError for OutputParser."""

    @llm.output_parser(formatting_instructions="Return text")
    def custom_parser(response: llm.RootResponse[llm.Toolkit, None]) -> str:
        return response.text()

    retry_model = llm.retry_model("mock/test-model", max_retries=1)

    response = retry_model.stream("Hello", format=custom_parser)

    with pytest.raises(
        NotImplementedError, match="structured_stream\\(\\) not supported"
    ):
        list(response.structured_stream())


# --- Async structured_stream tests ---


@pytest.mark.asyncio
async def test_async_structured_stream_raises_without_format(
    mock_provider: MockProvider,  # noqa: ARG001
) -> None:
    """Test that structured_stream raises ValueError without format."""

    @llm.retry(max_retries=1)
    @llm.call("mock/test-model")
    async def greet() -> str:
        return "Hello"

    response = await greet.stream()

    with pytest.raises(ValueError, match="structured_stream\\(\\) requires format"):
        _ = [chunk async for chunk in response.structured_stream()]


@pytest.mark.asyncio
async def test_async_structured_stream_yields_partials(
    mock_provider: MockProvider,
) -> None:
    """Test that async structured_stream yields partial outputs."""

    class Person(BaseModel):
        name: str
        age: int

    # Set up mock to return valid JSON
    mock_provider.set_stream_text('{"name": "Bob", "age": 25}')

    retry_model = llm.retry_model("mock/test-model", max_retries=1)

    response = await retry_model.stream_async("Get person", format=Person)

    partials = [p async for p in response.structured_stream()]

    # Should have yielded at least one partial
    assert len(partials) >= 1


@pytest.mark.asyncio
async def test_async_structured_stream_raises_for_output_parser(
    mock_provider: MockProvider,  # noqa: ARG001
) -> None:
    """Test that async structured_stream raises NotImplementedError for OutputParser."""

    @llm.output_parser(formatting_instructions="Return text")
    def custom_parser(response: llm.RootResponse[llm.Toolkit, None]) -> str:
        return response.text()

    retry_model = llm.retry_model("mock/test-model", max_retries=1)

    response = await retry_model.stream_async("Hello", format=custom_parser)

    with pytest.raises(
        NotImplementedError, match="structured_stream\\(\\) not supported"
    ):
        _ = [p async for p in response.structured_stream()]


# --- Sync resume tests ---


def test_resume_returns_retry_stream_response(mock_provider: MockProvider) -> None:
    """Test that resume returns a new RetryStreamResponse."""

    @llm.retry(max_retries=2)
    @llm.call("mock/test-model")
    def greet() -> str:
        return "Hello"

    response = greet.stream()
    response.finish()

    resumed = response.resume("Follow up")

    assert isinstance(resumed, llm.RetryStreamResponse)
    assert mock_provider.stream_count == 2


# --- Async resume tests ---


@pytest.mark.asyncio
async def test_async_resume_returns_async_retry_stream_response(
    mock_provider: MockProvider,
) -> None:
    """Test that resume returns a new AsyncRetryStreamResponse."""

    @llm.retry(max_retries=2)
    @llm.call("mock/test-model")
    async def greet() -> str:
        return "Hello"

    response = await greet.stream()
    await response.finish()

    resumed = await response.resume("Follow up")

    assert isinstance(resumed, llm.AsyncRetryStreamResponse)
    assert mock_provider.stream_count == 2


@pytest.mark.asyncio
async def test_async_resume_stream_factory_called_on_retry(
    mock_provider: MockProvider,
) -> None:
    """Test that resume's stream_factory is invoked when a retry happens."""

    @llm.retry(max_retries=2)
    @llm.call("mock/test-model")
    async def greet() -> str:
        return "Hello"

    response = await greet.stream()
    await response.finish()

    # Set up error for resumed stream
    mock_provider.set_stream_exceptions([CONNECTION_ERROR])

    resumed = await response.resume("Follow up")

    # First iteration fails, raises StreamRestarted
    with pytest.raises(llm.StreamRestarted):
        _ = [chunk async for chunk in resumed.text_stream()]

    # Stream factory was called for the retry:
    # 1 = original stream, 2 = resume initial stream, 3 = retry (via stream_factory)
    assert mock_provider.stream_count == 3

    # Can successfully complete after retry (uses stream #3 that was already created)
    chunks = [chunk async for chunk in resumed.text_stream()]
    assert "mock " in "".join(chunks) or "response" in "".join(chunks)
    # No new stream created - we're using the one created by stream_factory
    assert mock_provider.stream_count == 3


# --- Sync resume with fallback tests ---


def test_resume_uses_fallback_model_when_original_succeeded_on_fallback(
    mock_provider: MockProvider,
) -> None:
    """Test that stream resume uses the fallback model when original response succeeded on fallback."""
    # First stream: primary fails, fallback succeeds
    mock_provider.set_stream_exceptions([CONNECTION_ERROR])

    retry_model = llm.retry_model(
        "mock/primary", max_retries=0, fallback_models=["mock/fallback"]
    )

    response = retry_model.stream("Hello")

    # First iteration fails (primary), raises StreamRestarted
    with pytest.raises(llm.StreamRestarted):
        list(response.chunk_stream())

    # After restart, should be on fallback model
    assert response.model.model_id == "mock/fallback"

    # Second iteration succeeds on fallback
    list(response.chunk_stream())

    # Resume should use the fallback model (which succeeded)
    resumed = response.resume("Follow up")

    # Should start on fallback (no errors set)
    assert resumed.model.model_id == "mock/fallback"

    # Should succeed on fallback
    chunks = list(resumed.chunk_stream())
    assert len(chunks) > 0


def test_resume_can_fall_back_to_original_if_fallback_fails(
    mock_provider: MockProvider,
) -> None:
    """Test that stream resume can fall back to original model if the fallback model fails."""
    # First stream: primary fails, fallback succeeds
    mock_provider.set_stream_exceptions([CONNECTION_ERROR])

    retry_model = llm.retry_model(
        "mock/primary", max_retries=0, fallback_models=["mock/fallback"]
    )

    response = retry_model.stream("Hello")

    # First iteration fails (primary), raises StreamRestarted
    with pytest.raises(llm.StreamRestarted):
        list(response.chunk_stream())

    # After restart, should be on fallback model
    assert response.model.model_id == "mock/fallback"

    # Second iteration succeeds on fallback
    list(response.chunk_stream())

    # For resume: fallback fails, primary succeeds
    mock_provider.set_stream_exceptions([RATE_LIMIT_ERROR])

    resumed = response.resume("Follow up")

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


# --- Async resume with fallback tests ---


@pytest.mark.asyncio
async def test_async_resume_uses_fallback_model_when_original_succeeded_on_fallback(
    mock_provider: MockProvider,
) -> None:
    """Test that async stream resume uses the fallback model when original response succeeded on fallback."""
    # First stream: primary fails, fallback succeeds
    mock_provider.set_stream_exceptions([CONNECTION_ERROR])

    retry_model = llm.retry_model(
        "mock/primary", max_retries=0, fallback_models=["mock/fallback"]
    )

    response = await retry_model.stream_async("Hello")

    # First iteration fails (primary), raises StreamRestarted
    with pytest.raises(llm.StreamRestarted):
        _ = [chunk async for chunk in response.chunk_stream()]

    # After restart, should be on fallback model
    assert response.model.model_id == "mock/fallback"

    # Second iteration succeeds on fallback
    _ = [chunk async for chunk in response.chunk_stream()]

    # Resume should use the fallback model (which succeeded)
    resumed = await response.resume("Follow up")

    # Should start on fallback (no errors set)
    assert resumed.model.model_id == "mock/fallback"

    # Should succeed on fallback
    chunks = [chunk async for chunk in resumed.chunk_stream()]
    assert len(chunks) > 0


@pytest.mark.asyncio
async def test_async_resume_can_fall_back_to_original_if_fallback_fails(
    mock_provider: MockProvider,
) -> None:
    """Test that async stream resume can fall back to original model if the fallback model fails."""
    # First stream: primary fails, fallback succeeds
    mock_provider.set_stream_exceptions([CONNECTION_ERROR])

    retry_model = llm.retry_model(
        "mock/primary", max_retries=0, fallback_models=["mock/fallback"]
    )

    response = await retry_model.stream_async("Hello")

    # First iteration fails (primary), raises StreamRestarted
    with pytest.raises(llm.StreamRestarted):
        _ = [chunk async for chunk in response.chunk_stream()]

    # After restart, should be on fallback model
    assert response.model.model_id == "mock/fallback"

    # Second iteration succeeds on fallback
    _ = [chunk async for chunk in response.chunk_stream()]

    # For resume: fallback fails, primary succeeds
    mock_provider.set_stream_exceptions([RATE_LIMIT_ERROR])

    resumed = await response.resume("Follow up")

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


# --- Context stream retry_config tests ---


def test_context_stream_retry_config_property(
    mock_provider: MockProvider,  # noqa: ARG001
) -> None:
    """Test that ContextRetryStreamResponse.retry_config property returns the retry configuration."""
    retry_model = llm.retry_model("mock/test-model", max_retries=3)
    ctx = llm.Context(deps=None)

    response = retry_model.context_stream("Hello", ctx=ctx)

    assert response.retry_config.max_retries == 3


@pytest.mark.asyncio
async def test_async_context_stream_retry_config_property(
    mock_provider: MockProvider,  # noqa: ARG001
) -> None:
    """Test that AsyncContextRetryStreamResponse.retry_config property returns the retry configuration."""
    retry_model = llm.retry_model("mock/test-model", max_retries=3)
    ctx = llm.Context(deps=None)

    response = await retry_model.context_stream_async("Hello", ctx=ctx)

    assert response.retry_config.max_retries == 3
