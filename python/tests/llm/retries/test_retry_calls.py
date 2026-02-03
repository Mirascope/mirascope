"""Tests for sync and async @llm.retry with @llm.call decorator pattern."""

import pytest

from mirascope import llm

from .conftest import (
    DEFAULT_RETRYABLE_EXCEPTIONS,
    RESUME_TEST_EXCEPTIONS,
    SERVER_ERROR,
)
from .mock_provider import MockProvider

# --- Sync retry call tests ---


def test_call_succeeds_first_attempt(mock_provider: MockProvider) -> None:
    """Test that a successful first call returns immediately with correct state."""

    @llm.retry(max_retries=2)
    @llm.call("mock/test-model")
    def greet() -> str:
        return "Hello"

    response = greet()

    assert response.pretty() == "mock response"
    assert len(response.retry_failures) == 0
    assert response.model.retry_config.max_retries == 2
    assert response.model_id == "mock/test-model"
    assert mock_provider.call_count == 1


def test_call_retries_on_default_exceptions(mock_provider: MockProvider) -> None:
    """Test that all default retryable exceptions are caught and retried."""
    mock_provider.set_exceptions(DEFAULT_RETRYABLE_EXCEPTIONS)

    @llm.retry(max_retries=4)
    @llm.call("mock/test-model")
    def greet() -> str:
        return "Hello"

    response = greet()

    assert response.pretty() == "mock response"
    assert len(response.retry_failures) == 4
    assert [f.exception for f in response.retry_failures] == list(
        DEFAULT_RETRYABLE_EXCEPTIONS
    )
    assert mock_provider.call_count == 5


def test_call_retries_on_custom_exception(mock_provider: MockProvider) -> None:
    """Test that custom retry_on exceptions are caught."""
    exceptions: list[BaseException] = [AssertionError("custom error")]
    mock_provider.set_exceptions(exceptions)

    @llm.retry(max_retries=1, retry_on=(AssertionError,))
    @llm.call("mock/test-model")
    def greet() -> str:
        return "Hello"

    response = greet()

    assert response.pretty() == "mock response"
    assert len(response.retry_failures) == 1
    assert [f.exception for f in response.retry_failures] == exceptions
    assert mock_provider.call_count == 2


def test_call_raises_after_max_attempts_exhausted(mock_provider: MockProvider) -> None:
    """Test that exception is re-raised when max_attempts is exhausted."""
    mock_provider.set_exceptions(
        [llm.ConnectionError("connection failed", provider="test")]
    )

    @llm.retry(max_retries=0)
    @llm.call("mock/test-model")
    def greet() -> str:
        return "Hello"

    with pytest.raises(llm.ConnectionError, match="connection failed"):
        greet()

    assert mock_provider.call_count == 1


def test_resume_retries_on_failure(mock_provider: MockProvider) -> None:
    """Test that resume retries on transient errors."""

    @llm.retry(max_retries=2)
    @llm.call("mock/test-model")
    def greet() -> str:
        return "Hello"

    # Get initial successful response
    response = greet()
    assert mock_provider.call_count == 1

    # Configure errors for the resume call
    mock_provider.set_exceptions(RESUME_TEST_EXCEPTIONS)

    # Resume should retry through the errors
    resumed = response.resume("Follow up")
    assert resumed.pretty() == "mock response"
    assert len(resumed.retry_failures) == 2
    assert [f.exception for f in resumed.retry_failures] == list(RESUME_TEST_EXCEPTIONS)
    assert mock_provider.call_count == 4  # 1 initial + 3 resume attempts


def test_resume_raises_after_max_attempts_exhausted(
    mock_provider: MockProvider,
) -> None:
    """Test that resume re-raises when max_attempts is exhausted."""

    @llm.retry(max_retries=0)
    @llm.call("mock/test-model")
    def greet() -> str:
        return "Hello"

    # Get initial successful response
    response = greet()
    assert mock_provider.call_count == 1

    # Configure persistent error for the resume call
    mock_provider.set_exceptions([SERVER_ERROR])

    with pytest.raises(llm.ServerError, match="server error"):
        response.resume("Follow up")

    assert mock_provider.call_count == 2  # 1 initial + 1 resume attempt


# --- Async retry call tests ---


@pytest.mark.asyncio
async def test_call_async_succeeds_first_attempt(mock_provider: MockProvider) -> None:
    """Test that a successful first call returns immediately with correct state."""

    @llm.retry(max_retries=2)
    @llm.call("mock/test-model")
    async def greet() -> str:
        return "Hello"

    response = await greet()

    assert response.pretty() == "mock response"
    assert len(response.retry_failures) == 0
    assert response.model.retry_config.max_retries == 2
    assert response.model_id == "mock/test-model"
    assert mock_provider.call_count == 1


@pytest.mark.asyncio
async def test_call_async_retries_on_default_exceptions(
    mock_provider: MockProvider,
) -> None:
    """Test that all default retryable exceptions are caught and retried."""
    mock_provider.set_exceptions(DEFAULT_RETRYABLE_EXCEPTIONS)

    @llm.retry(max_retries=4)
    @llm.call("mock/test-model")
    async def greet() -> str:
        return "Hello"

    response = await greet()

    assert response.pretty() == "mock response"
    assert len(response.retry_failures) == 4
    assert [f.exception for f in response.retry_failures] == list(
        DEFAULT_RETRYABLE_EXCEPTIONS
    )
    assert mock_provider.call_count == 5


@pytest.mark.asyncio
async def test_call_async_retries_on_custom_exception(
    mock_provider: MockProvider,
) -> None:
    """Test that custom retry_on exceptions are caught."""
    exceptions: list[BaseException] = [AssertionError("custom error")]
    mock_provider.set_exceptions(exceptions)

    @llm.retry(max_retries=1, retry_on=(AssertionError,))
    @llm.call("mock/test-model")
    async def greet() -> str:
        return "Hello"

    response = await greet()

    assert response.pretty() == "mock response"
    assert len(response.retry_failures) == 1
    assert [f.exception for f in response.retry_failures] == exceptions
    assert mock_provider.call_count == 2


@pytest.mark.asyncio
async def test_call_async_raises_after_max_attempts_exhausted(
    mock_provider: MockProvider,
) -> None:
    """Test that exception is re-raised when max_attempts is exhausted."""
    mock_provider.set_exceptions(
        [llm.ConnectionError("connection failed", provider="test")]
    )

    @llm.retry(max_retries=0)
    @llm.call("mock/test-model")
    async def greet() -> str:
        return "Hello"

    with pytest.raises(llm.ConnectionError, match="connection failed"):
        await greet()

    assert mock_provider.call_count == 1


@pytest.mark.asyncio
async def test_resume_async_retries_on_failure(mock_provider: MockProvider) -> None:
    """Test that async resume retries on transient errors."""

    @llm.retry(max_retries=2)
    @llm.call("mock/test-model")
    async def greet() -> str:
        return "Hello"

    # Get initial successful response
    response = await greet()
    assert mock_provider.call_count == 1

    # Configure errors for the resume call
    mock_provider.set_exceptions(RESUME_TEST_EXCEPTIONS)

    # Resume should retry through the errors
    resumed = await response.resume("Follow up")
    assert resumed.pretty() == "mock response"
    assert len(resumed.retry_failures) == 2
    assert [f.exception for f in resumed.retry_failures] == list(RESUME_TEST_EXCEPTIONS)
    assert mock_provider.call_count == 4  # 1 initial + 3 resume attempts


@pytest.mark.asyncio
async def test_resume_async_raises_after_max_attempts_exhausted(
    mock_provider: MockProvider,
) -> None:
    """Test that async resume re-raises when max_attempts is exhausted."""

    @llm.retry(max_retries=0)
    @llm.call("mock/test-model")
    async def greet() -> str:
        return "Hello"

    # Get initial successful response
    response = await greet()
    assert mock_provider.call_count == 1

    # Configure persistent error for the resume call
    mock_provider.set_exceptions([SERVER_ERROR])

    with pytest.raises(llm.ServerError, match="server error"):
        await response.resume("Follow up")

    assert mock_provider.call_count == 2  # 1 initial + 1 resume attempt


# --- RetryCall property tests ---


def test_default_model_property(mock_provider: MockProvider) -> None:  # noqa: ARG001
    """Test that default_model returns the underlying Model."""

    @llm.retry(max_retries=2)
    @llm.call("mock/test-model")
    def greet() -> str:
        return "Hello"

    # default_model is the underlying Model, not RetryModel
    default_model = greet.default_model
    assert isinstance(default_model, llm.Model)
    assert default_model.model_id == "mock/test-model"


def test_model_property_returns_retry_model(
    mock_provider: MockProvider,  # noqa: ARG001
) -> None:
    """Test that model property returns a RetryModel wrapping the default model."""

    @llm.retry(max_retries=2)
    @llm.call("mock/test-model")
    def greet() -> str:
        return "Hello"

    # model property wraps default_model in RetryModel
    model = greet.model
    assert isinstance(model, llm.RetryModel)
    assert model.model_id == "mock/test-model"


# --- RetryCall model override tests ---


def _create_retry_call(
    retry_config: llm.retries.RetryConfig,
) -> llm.RetryCall[..., None]:
    """Helper to create a RetryCall for testing."""

    def my_prompt() -> str:
        return "test"

    prompt = llm.RetryPrompt(
        fn=my_prompt,
        toolkit=llm.tools.Toolkit(tools=None),
        format=None,
        retry_config=retry_config,
    )
    return llm.RetryCall(
        default_model=llm.Model("openai/gpt-4o"),
        prompt=prompt,
    )


def test_retry_call_wraps_default_model_in_retry_model() -> None:
    """Test that RetryCall.model wraps the default model in RetryModel."""
    retry_call = _create_retry_call(llm.retries.RetryConfig(max_retries=3))

    model = retry_call.model

    assert isinstance(model, llm.RetryModel)
    assert model.model_id == "openai/gpt-4o"
    assert model.retry_config.max_retries == 3


def test_retry_call_wraps_context_model_in_retry_model() -> None:
    """Test that RetryCall.model wraps context override in RetryModel."""
    retry_call = _create_retry_call(llm.retries.RetryConfig(max_retries=3))

    with llm.model("anthropic/claude-sonnet-4-0"):
        model = retry_call.model

        assert isinstance(model, llm.RetryModel)
        assert model.model_id == "anthropic/claude-sonnet-4-0"
        # Uses the prompt's retry config when wrapping
        assert model.retry_config.max_retries == 3


def test_retry_call_uses_override_retry_model_directly() -> None:
    """Test that if context override is a RetryModel, it's used as-is."""
    retry_call = _create_retry_call(llm.retries.RetryConfig(max_retries=3))

    override_retry_model = llm.RetryModel(
        "anthropic/claude-sonnet-4-0",
        llm.retries.RetryConfig(max_retries=5),
    )

    with override_retry_model:
        model = retry_call.model

        assert isinstance(model, llm.RetryModel)
        assert model.model_id == "anthropic/claude-sonnet-4-0"
        # The override's retry config should win, not the prompt's
        assert model.retry_config.max_retries == 5


def test_retry_call_override_retry_model_is_same_instance() -> None:
    """Test that the override RetryModel is returned directly, not re-wrapped."""
    retry_call = _create_retry_call(llm.retries.RetryConfig(max_retries=3))

    override_retry_model = llm.RetryModel(
        "anthropic/claude-sonnet-4-0",
        llm.retries.RetryConfig(max_retries=5),
    )

    with override_retry_model:
        model = retry_call.model
        # Should be the exact same instance, not wrapped
        assert model is override_retry_model


def test_retry_config_property_returns_prompt_config() -> None:
    """Test that retry_config property returns the prompt's retry config."""
    config = llm.retries.RetryConfig(max_retries=7)
    retry_call = _create_retry_call(config)

    assert retry_call.retry_config is config
    assert retry_call.retry_config.max_retries == 7
