"""Tests for retry decorator with @llm.call pattern."""

from collections.abc import Generator, Sequence

import pytest

from mirascope import llm

from .mock_provider import MockProvider

SERVER_ERROR = llm.ServerError("server error", provider="test")
CONNECTION_ERROR = llm.ConnectionError("connection failed", provider="test")
RATE_LIMIT_ERROR = llm.RateLimitError("rate limited", provider="test")
TIMEOUT_ERROR = llm.TimeoutError("timeout", provider="test")

# Common exception sequences used across tests
DEFAULT_RETRYABLE_EXCEPTIONS: Sequence[llm.Error] = [
    SERVER_ERROR,
    CONNECTION_ERROR,
    RATE_LIMIT_ERROR,
    TIMEOUT_ERROR,
]

RESUME_TEST_EXCEPTIONS: Sequence[llm.Error] = [
    CONNECTION_ERROR,
    RATE_LIMIT_ERROR,
]


@pytest.fixture
def mock_provider() -> Generator[MockProvider, None, None]:
    """Fixture that provides a MockProvider and cleans up after the test."""
    llm.reset_provider_registry()
    provider = MockProvider()
    llm.register_provider(provider, scope="mock/")
    yield provider
    llm.reset_provider_registry()


class TestSyncRetryCall:
    """Tests for sync @llm.retry with @llm.call decorator pattern."""

    def test_call_succeeds_first_attempt(self, mock_provider: MockProvider) -> None:
        """Test that a successful first call returns immediately with correct state."""

        @llm.retry(max_attempts=3)
        @llm.call("mock/test-model")
        def greet() -> str:
            return "Hello"

        response = greet()

        assert response.pretty() == "mock response"
        assert response.retry_state.attempts == 1
        assert response.retry_state.exceptions == []
        assert response.retry_state.max_attempts == 3
        assert response.model_id == "mock/test-model"
        assert mock_provider.call_count == 1

    def test_call_retries_on_default_exceptions(
        self, mock_provider: MockProvider
    ) -> None:
        """Test that all default retryable exceptions are caught and retried."""
        mock_provider.set_exceptions(DEFAULT_RETRYABLE_EXCEPTIONS)

        @llm.retry(max_attempts=5)
        @llm.call("mock/test-model")
        def greet() -> str:
            return "Hello"

        response = greet()

        assert response.pretty() == "mock response"
        assert response.retry_state.attempts == 5
        assert response.retry_state.exceptions == DEFAULT_RETRYABLE_EXCEPTIONS
        assert mock_provider.call_count == 5

    def test_call_retries_on_custom_exception(
        self, mock_provider: MockProvider
    ) -> None:
        """Test that custom retry_on exceptions are caught."""
        exceptions: list[BaseException] = [AssertionError("custom error")]
        mock_provider.set_exceptions(exceptions)

        @llm.retry(max_attempts=2, retry_on=(AssertionError,))
        @llm.call("mock/test-model")
        def greet() -> str:
            return "Hello"

        response = greet()

        assert response.pretty() == "mock response"
        assert response.retry_state.attempts == 2
        assert response.retry_state.exceptions == exceptions
        assert mock_provider.call_count == 2

    def test_call_raises_after_max_attempts_exhausted(
        self, mock_provider: MockProvider
    ) -> None:
        """Test that exception is re-raised when max_attempts is exhausted."""
        mock_provider.set_exceptions(
            [llm.ConnectionError("connection failed", provider="test")]
        )

        @llm.retry(max_attempts=1)
        @llm.call("mock/test-model")
        def greet() -> str:
            return "Hello"

        with pytest.raises(llm.ConnectionError, match="connection failed"):
            greet()

        assert mock_provider.call_count == 1

    def test_resume_retries_on_failure(self, mock_provider: MockProvider) -> None:
        """Test that resume retries on transient errors."""

        @llm.retry(max_attempts=3)
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
        assert resumed.retry_state.attempts == 3
        assert resumed.retry_state.exceptions == RESUME_TEST_EXCEPTIONS
        assert mock_provider.call_count == 4  # 1 initial + 3 resume attempts

    def test_resume_raises_after_max_attempts_exhausted(
        self, mock_provider: MockProvider
    ) -> None:
        """Test that resume re-raises when max_attempts is exhausted."""

        @llm.retry(max_attempts=1)
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


@pytest.mark.asyncio
class TestAsyncRetryCall:
    """Tests for async @llm.retry with @llm.call decorator pattern."""

    async def test_call_async_succeeds_first_attempt(
        self, mock_provider: MockProvider
    ) -> None:
        """Test that a successful first call returns immediately with correct state."""

        @llm.retry(max_attempts=3)
        @llm.call("mock/test-model")
        async def greet() -> str:
            return "Hello"

        response = await greet()

        assert response.pretty() == "mock response"
        assert response.retry_state.attempts == 1
        assert response.retry_state.exceptions == []
        assert response.retry_state.max_attempts == 3
        assert response.model_id == "mock/test-model"
        assert mock_provider.call_count == 1

    async def test_call_async_retries_on_default_exceptions(
        self, mock_provider: MockProvider
    ) -> None:
        """Test that all default retryable exceptions are caught and retried."""
        mock_provider.set_exceptions(DEFAULT_RETRYABLE_EXCEPTIONS)

        @llm.retry(max_attempts=5)
        @llm.call("mock/test-model")
        async def greet() -> str:
            return "Hello"

        response = await greet()

        assert response.pretty() == "mock response"
        assert response.retry_state.attempts == 5
        assert response.retry_state.exceptions == DEFAULT_RETRYABLE_EXCEPTIONS
        assert mock_provider.call_count == 5

    async def test_call_async_retries_on_custom_exception(
        self, mock_provider: MockProvider
    ) -> None:
        """Test that custom retry_on exceptions are caught."""
        exceptions: list[BaseException] = [AssertionError("custom error")]
        mock_provider.set_exceptions(exceptions)

        @llm.retry(max_attempts=2, retry_on=(AssertionError,))
        @llm.call("mock/test-model")
        async def greet() -> str:
            return "Hello"

        response = await greet()

        assert response.pretty() == "mock response"
        assert response.retry_state.attempts == 2
        assert response.retry_state.exceptions == exceptions
        assert mock_provider.call_count == 2

    async def test_call_async_raises_after_max_attempts_exhausted(
        self, mock_provider: MockProvider
    ) -> None:
        """Test that exception is re-raised when max_attempts is exhausted."""
        mock_provider.set_exceptions(
            [llm.ConnectionError("connection failed", provider="test")]
        )

        @llm.retry(max_attempts=1)
        @llm.call("mock/test-model")
        async def greet() -> str:
            return "Hello"

        with pytest.raises(llm.ConnectionError, match="connection failed"):
            await greet()

        assert mock_provider.call_count == 1

    async def test_resume_async_retries_on_failure(
        self, mock_provider: MockProvider
    ) -> None:
        """Test that async resume retries on transient errors."""

        @llm.retry(max_attempts=3)
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
        assert resumed.retry_state.attempts == 3
        assert resumed.retry_state.exceptions == RESUME_TEST_EXCEPTIONS
        assert mock_provider.call_count == 4  # 1 initial + 3 resume attempts

    async def test_resume_async_raises_after_max_attempts_exhausted(
        self, mock_provider: MockProvider
    ) -> None:
        """Test that async resume re-raises when max_attempts is exhausted."""

        @llm.retry(max_attempts=1)
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


class TestRetryConfigValidation:
    """Tests for RetryConfig validation."""

    def test_max_attempts_zero_raises_value_error(self) -> None:
        """Test that max_attempts=0 raises ValueError."""
        with pytest.raises(ValueError, match="max_attempts must be at least 1"):
            llm.retry(max_attempts=0)

    def test_max_attempts_negative_raises_value_error(self) -> None:
        """Test that negative max_attempts raises ValueError."""
        with pytest.raises(ValueError, match="max_attempts must be at least 1"):
            llm.retry(max_attempts=-1)

    def test_max_attempts_one_is_valid(self, mock_provider: MockProvider) -> None:
        """Test that max_attempts=1 is valid (no retries, just one attempt)."""

        @llm.retry(max_attempts=1)
        @llm.call("mock/test-model")
        def greet() -> str:
            return "Hello"

        response = greet()
        assert response.retry_state.max_attempts == 1


class TestRetryDecorator:
    """Tests for the @llm.retry decorator itself."""

    def test_retry_on_model(self, mock_provider: MockProvider) -> None:
        """Test that retry() works directly on a Model."""
        model = llm.Model("mock/test-model")
        retry_model = llm.retry(model, max_attempts=3)

        response = retry_model.call("hello")

        assert response.pretty() == "mock response"
        assert response.retry_state.attempts == 1
        assert response.retry_state.max_attempts == 3

    def test_retry_on_retry_model_updates_config(
        self, mock_provider: MockProvider
    ) -> None:
        """Test that retry() on a RetryModel updates the config."""
        model = llm.Model("mock/test-model")
        retry_model = llm.retry(model, max_attempts=3)
        updated_retry_model = llm.retry(retry_model, max_attempts=5)

        response = updated_retry_model.call("hello")

        assert response.retry_state.max_attempts == 5

    def test_retry_on_call_produces_retry_call(
        self, mock_provider: MockProvider
    ) -> None:
        """Test that retry() on a Call produces a RetryCall."""

        @llm.call("mock/test-model")
        def greet() -> str:
            return "Hello"

        retry_call = llm.retry(greet, max_attempts=3)

        assert isinstance(retry_call, llm.RetryCall)
        response = retry_call()
        assert response.retry_state.max_attempts == 3

    def test_retry_on_retry_call_updates_config(
        self, mock_provider: MockProvider
    ) -> None:
        """Test that retry() on a RetryCall updates the config."""

        @llm.retry(max_attempts=3)
        @llm.call("mock/test-model")
        def greet() -> str:
            return "Hello"

        updated = llm.retry(greet, max_attempts=5)
        response = updated()
        assert response.retry_state.max_attempts == 5

    def test_retry_on_prompt(self, mock_provider: MockProvider) -> None:
        """Test that retry() works on a Prompt."""

        @llm.prompt
        def greet() -> str:
            return "Hello"

        retry_prompt = llm.retry(greet, max_attempts=3)

        assert isinstance(retry_prompt, llm.RetryPrompt)
        model = llm.Model("mock/test-model")
        response = retry_prompt(model)
        assert response.retry_state.max_attempts == 3

    def test_retry_on_retry_prompt_updates_config(
        self, mock_provider: MockProvider
    ) -> None:
        """Test that retry() on a RetryPrompt updates the config."""

        @llm.prompt
        def greet() -> str:
            return "Hello"

        retry_prompt = llm.retry(greet, max_attempts=3)
        updated = llm.retry(retry_prompt, max_attempts=5)

        model = llm.Model("mock/test-model")
        response = updated(model)
        assert response.retry_state.max_attempts == 5


@pytest.mark.asyncio
class TestAsyncRetryDecorator:
    """Tests for @llm.retry with async prompts and calls."""

    async def test_retry_on_async_call(self, mock_provider: MockProvider) -> None:
        """Test that retry() works on an AsyncCall."""

        @llm.call("mock/test-model")
        async def greet() -> str:
            return "Hello"

        retry_call = llm.retry(greet, max_attempts=3)

        assert isinstance(retry_call, llm.AsyncRetryCall)
        response = await retry_call()
        assert response.retry_state.max_attempts == 3

    async def test_retry_on_async_retry_call_updates_config(
        self, mock_provider: MockProvider
    ) -> None:
        """Test that retry() on an AsyncRetryCall updates the config."""

        @llm.retry(max_attempts=3)
        @llm.call("mock/test-model")
        async def greet() -> str:
            return "Hello"

        updated = llm.retry(greet, max_attempts=5)
        response = await updated()
        assert response.retry_state.max_attempts == 5

    async def test_retry_on_async_prompt(self, mock_provider: MockProvider) -> None:
        """Test that retry() works on an AsyncPrompt."""

        @llm.prompt
        async def greet() -> str:
            return "Hello"

        retry_prompt = llm.retry(greet, max_attempts=3)

        assert isinstance(retry_prompt, llm.AsyncRetryPrompt)
        model = llm.Model("mock/test-model")
        response = await retry_prompt(model)
        assert response.retry_state.max_attempts == 3

    async def test_retry_on_async_retry_prompt_updates_config(
        self, mock_provider: MockProvider
    ) -> None:
        """Test that retry() on an AsyncRetryPrompt updates the config."""

        @llm.prompt
        async def greet() -> str:
            return "Hello"

        retry_prompt = llm.retry(greet, max_attempts=3)
        updated = llm.retry(retry_prompt, max_attempts=5)

        model = llm.Model("mock/test-model")
        response = await updated(model)
        assert response.retry_state.max_attempts == 5
