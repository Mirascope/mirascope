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


@pytest.fixture(autouse=True)
def mock_sleep(monkeypatch: pytest.MonkeyPatch) -> list[float]:
    """Auto-mock time.sleep and asyncio.sleep to avoid actual delays in tests.

    Returns a list that captures all sleep durations for assertions.
    """
    sleep_calls: list[float] = []

    def sync_sleep(seconds: float) -> None:
        sleep_calls.append(seconds)

    async def async_sleep(seconds: float) -> None:
        sleep_calls.append(seconds)

    monkeypatch.setattr("mirascope.llm.retries.retry_models.time.sleep", sync_sleep)
    monkeypatch.setattr("mirascope.llm.retries.retry_models.asyncio.sleep", async_sleep)
    return sleep_calls


class TestSyncRetryCall:
    """Tests for sync @llm.retry with @llm.call decorator pattern."""

    def test_call_succeeds_first_attempt(self, mock_provider: MockProvider) -> None:
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

    def test_call_retries_on_default_exceptions(
        self, mock_provider: MockProvider
    ) -> None:
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

    def test_call_retries_on_custom_exception(
        self, mock_provider: MockProvider
    ) -> None:
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

    def test_call_raises_after_max_attempts_exhausted(
        self, mock_provider: MockProvider
    ) -> None:
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

    def test_resume_retries_on_failure(self, mock_provider: MockProvider) -> None:
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
        assert [f.exception for f in resumed.retry_failures] == list(
            RESUME_TEST_EXCEPTIONS
        )
        assert mock_provider.call_count == 4  # 1 initial + 3 resume attempts

    def test_resume_raises_after_max_attempts_exhausted(
        self, mock_provider: MockProvider
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


@pytest.mark.asyncio
class TestAsyncRetryCall:
    """Tests for async @llm.retry with @llm.call decorator pattern."""

    async def test_call_async_succeeds_first_attempt(
        self, mock_provider: MockProvider
    ) -> None:
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

    async def test_call_async_retries_on_default_exceptions(
        self, mock_provider: MockProvider
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

    async def test_call_async_retries_on_custom_exception(
        self, mock_provider: MockProvider
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

    async def test_call_async_raises_after_max_attempts_exhausted(
        self, mock_provider: MockProvider
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

    async def test_resume_async_retries_on_failure(
        self, mock_provider: MockProvider
    ) -> None:
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
        assert [f.exception for f in resumed.retry_failures] == list(
            RESUME_TEST_EXCEPTIONS
        )
        assert mock_provider.call_count == 4  # 1 initial + 3 resume attempts

    async def test_resume_async_raises_after_max_attempts_exhausted(
        self, mock_provider: MockProvider
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


class TestRetryConfigValidation:
    """Tests for RetryConfig validation."""

    def test_max_retries_negative_raises_value_error(self) -> None:
        """Test that negative max_retries raises ValueError."""
        with pytest.raises(ValueError, match="max_retries must be non-negative"):
            llm.retry(max_retries=-1)

    def test_max_retries_zero_is_valid(self, mock_provider: MockProvider) -> None:
        """Test that max_retries=0 is valid (no retries, just one attempt)."""

        @llm.retry(max_retries=0)
        @llm.call("mock/test-model")
        def greet() -> str:
            return "Hello"

        response = greet()
        assert response.model.retry_config.max_retries == 0

    def test_initial_delay_negative_raises_value_error(self) -> None:
        """Test that negative initial_delay raises ValueError."""
        with pytest.raises(ValueError, match="initial_delay must be non-negative"):
            llm.retry(initial_delay=-1.0)

    def test_max_delay_negative_raises_value_error(self) -> None:
        """Test that negative max_delay raises ValueError."""
        with pytest.raises(ValueError, match="max_delay must be non-negative"):
            llm.retry(max_delay=-1.0)

    def test_backoff_multiplier_less_than_one_raises_value_error(self) -> None:
        """Test that backoff_multiplier < 1 raises ValueError."""
        with pytest.raises(ValueError, match="backoff_multiplier must be >= 1"):
            llm.retry(backoff_multiplier=0.5)

    def test_jitter_out_of_range_raises_value_error(self) -> None:
        """Test that jitter outside [0, 1] raises ValueError."""
        with pytest.raises(ValueError, match="jitter must be between 0.0 and 1.0"):
            llm.retry(jitter=-0.1)
        with pytest.raises(ValueError, match="jitter must be between 0.0 and 1.0"):
            llm.retry(jitter=1.1)


class TestExponentialBackoff:
    """Tests for exponential backoff delay behavior."""

    def test_backoff_delays_are_applied(
        self, mock_provider: MockProvider, mock_sleep: list[float]
    ) -> None:
        """Test that exponential backoff delays are applied between retries."""
        # Fail twice, then succeed
        mock_provider.set_exceptions([SERVER_ERROR, SERVER_ERROR])

        @llm.retry(max_retries=3, initial_delay=0.1, backoff_multiplier=2.0)
        @llm.call("mock/test-model")
        def greet() -> str:
            return "Hello"

        response = greet()
        assert len(response.retry_failures) == 2
        # First delay: 0.1, second delay: 0.2 (0.1 * 2)
        assert len(mock_sleep) == 2
        assert mock_sleep[0] == pytest.approx(0.1)
        assert mock_sleep[1] == pytest.approx(0.2)

    def test_backoff_respects_max_delay(
        self, mock_provider: MockProvider, mock_sleep: list[float]
    ) -> None:
        """Test that backoff delay is capped at max_delay."""
        # Fail 3 times, then succeed
        mock_provider.set_exceptions([SERVER_ERROR, SERVER_ERROR, SERVER_ERROR])

        @llm.retry(
            max_retries=4, initial_delay=1.0, backoff_multiplier=10.0, max_delay=5.0
        )
        @llm.call("mock/test-model")
        def greet() -> str:
            return "Hello"

        response = greet()
        assert len(response.retry_failures) == 3
        # First: 1.0, second: min(10.0, 5.0) = 5.0, third: min(100.0, 5.0) = 5.0
        assert len(mock_sleep) == 3
        assert mock_sleep[0] == pytest.approx(1.0)
        assert mock_sleep[1] == pytest.approx(5.0)
        assert mock_sleep[2] == pytest.approx(5.0)

    def test_backoff_with_jitter(
        self,
        mock_provider: MockProvider,
        mock_sleep: list[float],
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """Test that jitter adds randomness to delays."""
        # Mock random.uniform to return a predictable value
        monkeypatch.setattr(
            "mirascope.llm.retries.utils.random.uniform", lambda a, b: (a + b) / 2
        )

        mock_provider.set_exceptions([SERVER_ERROR])

        @llm.retry(max_retries=2, initial_delay=1.0, jitter=0.5)
        @llm.call("mock/test-model")
        def greet() -> str:
            return "Hello"

        response = greet()
        assert len(response.retry_failures) == 1
        # With jitter=0.5 and our mock returning midpoint, jitter_range = 0.5
        # random.uniform(-0.5, 0.5) returns 0, so delay stays at 1.0
        assert len(mock_sleep) == 1
        assert mock_sleep[0] == pytest.approx(1.0)


class TestExponentialBackoffAsync:
    """Tests for async exponential backoff delay behavior."""

    @pytest.mark.asyncio
    async def test_async_backoff_delays_are_applied(
        self, mock_provider: MockProvider, mock_sleep: list[float]
    ) -> None:
        """Test that exponential backoff delays are applied between async retries."""
        # Fail twice, then succeed
        mock_provider.set_exceptions([SERVER_ERROR, SERVER_ERROR])

        @llm.retry(max_retries=3, initial_delay=0.1, backoff_multiplier=2.0)
        @llm.call("mock/test-model")
        async def greet() -> str:
            return "Hello"

        response = await greet()
        assert len(response.retry_failures) == 2
        # First delay: 0.1, second delay: 0.2 (0.1 * 2)
        assert len(mock_sleep) == 2
        assert mock_sleep[0] == pytest.approx(0.1)
        assert mock_sleep[1] == pytest.approx(0.2)


class TestRetryDecorator:
    """Tests for the @llm.retry decorator itself."""

    def test_retry_on_model(self, mock_provider: MockProvider) -> None:
        """Test that retry() works directly on a Model."""
        model = llm.Model("mock/test-model")
        retry_model = llm.retry(model, max_retries=2)

        response = retry_model.call("hello")

        assert response.pretty() == "mock response"
        assert len(response.retry_failures) == 0
        assert response.model.retry_config.max_retries == 2

    def test_retry_on_retry_model_updates_config(
        self, mock_provider: MockProvider
    ) -> None:
        """Test that retry() on a RetryModel updates the config."""
        model = llm.Model("mock/test-model")
        retry_model = llm.retry(model, max_retries=2)
        updated_retry_model = llm.retry(retry_model, max_retries=4)

        response = updated_retry_model.call("hello")

        assert response.model.retry_config.max_retries == 4

    def test_retry_on_call_produces_retry_call(
        self, mock_provider: MockProvider
    ) -> None:
        """Test that retry() on a Call produces a RetryCall."""

        @llm.call("mock/test-model")
        def greet() -> str:
            return "Hello"

        retry_call = llm.retry(greet, max_retries=2)

        assert isinstance(retry_call, llm.RetryCall)
        response = retry_call()
        assert response.model.retry_config.max_retries == 2

    def test_retry_on_retry_call_updates_config(
        self, mock_provider: MockProvider
    ) -> None:
        """Test that retry() on a RetryCall updates the config."""

        @llm.retry(max_retries=2)
        @llm.call("mock/test-model")
        def greet() -> str:
            return "Hello"

        updated = llm.retry(greet, max_retries=4)
        response = updated()
        assert response.model.retry_config.max_retries == 4

    def test_retry_on_prompt(self, mock_provider: MockProvider) -> None:
        """Test that retry() works on a Prompt."""

        @llm.prompt
        def greet() -> str:
            return "Hello"

        retry_prompt = llm.retry(greet, max_retries=2)

        assert isinstance(retry_prompt, llm.RetryPrompt)
        model = llm.Model("mock/test-model")
        response = retry_prompt(model)
        assert response.model.retry_config.max_retries == 2

    def test_retry_on_retry_prompt_updates_config(
        self, mock_provider: MockProvider
    ) -> None:
        """Test that retry() on a RetryPrompt updates the config."""

        @llm.prompt
        def greet() -> str:
            return "Hello"

        retry_prompt = llm.retry(greet, max_retries=2)
        updated = llm.retry(retry_prompt, max_retries=4)

        model = llm.Model("mock/test-model")
        response = updated(model)
        assert response.model.retry_config.max_retries == 4


@pytest.mark.asyncio
class TestAsyncRetryDecorator:
    """Tests for @llm.retry with async prompts and calls."""

    async def test_retry_on_async_call(self, mock_provider: MockProvider) -> None:
        """Test that retry() works on an AsyncCall."""

        @llm.call("mock/test-model")
        async def greet() -> str:
            return "Hello"

        retry_call = llm.retry(greet, max_retries=2)

        assert isinstance(retry_call, llm.AsyncRetryCall)
        response = await retry_call()
        assert response.model.retry_config.max_retries == 2

    async def test_retry_on_async_retry_call_updates_config(
        self, mock_provider: MockProvider
    ) -> None:
        """Test that retry() on an AsyncRetryCall updates the config."""

        @llm.retry(max_retries=2)
        @llm.call("mock/test-model")
        async def greet() -> str:
            return "Hello"

        updated = llm.retry(greet, max_retries=4)
        response = await updated()
        assert response.model.retry_config.max_retries == 4

    async def test_retry_on_async_prompt(self, mock_provider: MockProvider) -> None:
        """Test that retry() works on an AsyncPrompt."""

        @llm.prompt
        async def greet() -> str:
            return "Hello"

        retry_prompt = llm.retry(greet, max_retries=2)

        assert isinstance(retry_prompt, llm.AsyncRetryPrompt)
        model = llm.Model("mock/test-model")
        response = await retry_prompt(model)
        assert response.model.retry_config.max_retries == 2

    async def test_retry_on_async_retry_prompt_updates_config(
        self, mock_provider: MockProvider
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


class TestRetryResponseProperties:
    """Tests for RetryResponse property delegation."""

    def test_response_properties_delegate_to_wrapped(
        self, mock_provider: MockProvider
    ) -> None:
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

    def test_execute_tools(self, mock_provider: MockProvider) -> None:  # noqa: ARG002
        """Test that execute_tools delegates to wrapped response."""

        @llm.retry(max_retries=1)
        @llm.call("mock/test-model")
        def greet() -> str:
            return "Hello"

        response = greet()
        result = response.execute_tools()
        assert result == []  # No tool calls in mock response


@pytest.mark.asyncio
class TestAsyncRetryResponseProperties:
    """Tests for AsyncRetryResponse property delegation."""

    async def test_async_execute_tools(
        self,
        mock_provider: MockProvider,  # noqa: ARG002
    ) -> None:
        """Test that async execute_tools delegates to wrapped response."""

        @llm.retry(max_retries=1)
        @llm.call("mock/test-model")
        async def greet() -> str:
            return "Hello"

        response = await greet()
        result = await response.execute_tools()
        assert result == []  # No tool calls in mock response


class TestRetryModelProperties:
    """Tests for RetryModel property delegation."""

    def test_model_id_property(self, mock_provider: MockProvider) -> None:  # noqa: ARG002
        """Test that model_id delegates to wrapped model."""
        model = llm.Model("mock/test-model")
        retry_model = llm.retry(model, max_retries=2)

        assert retry_model.model_id == "mock/test-model"

    def test_params_property(self, mock_provider: MockProvider) -> None:  # noqa: ARG002
        """Test that params delegates to wrapped model."""
        model = llm.Model("mock/test-model")
        retry_model = llm.retry(model, max_retries=2)

        assert retry_model.params is not None


class TestRetryPromptProperties:
    """Tests for RetryPrompt property delegation."""

    def test_fn_property(self, mock_provider: MockProvider) -> None:  # noqa: ARG002
        """Test that fn delegates to wrapped prompt."""

        @llm.prompt
        def greet() -> str:
            return "Hello"

        retry_prompt = llm.retry(greet, max_retries=2)

        assert retry_prompt.fn is greet.fn

    def test_call_with_string_model_id(self, mock_provider: MockProvider) -> None:
        """Test that RetryPrompt.call accepts a string model ID."""

        @llm.prompt
        def greet() -> str:
            return "Hello"

        retry_prompt = llm.retry(greet, max_retries=2)

        # Pass model as string instead of Model object
        response = retry_prompt.call("mock/test-model")

        assert response.pretty() == "mock response"
        assert mock_provider.call_count == 1


@pytest.mark.asyncio
class TestAsyncRetryPromptProperties:
    """Tests for AsyncRetryPrompt property delegation."""

    async def test_async_fn_property(
        self,
        mock_provider: MockProvider,  # noqa: ARG002
    ) -> None:
        """Test that fn delegates to wrapped async prompt."""

        @llm.prompt
        async def greet() -> str:
            return "Hello"

        retry_prompt = llm.retry(greet, max_retries=2)

        assert retry_prompt.fn is greet.fn

    async def test_call_with_string_model_id(self, mock_provider: MockProvider) -> None:
        """Test that AsyncRetryPrompt.call accepts a string model ID."""

        @llm.prompt
        async def greet() -> str:
            return "Hello"

        retry_prompt = llm.retry(greet, max_retries=2)

        # Pass model as string instead of Model object
        response = await retry_prompt.call("mock/test-model")

        assert response.pretty() == "mock response"
        assert mock_provider.call_count == 1


class TestRetryCallProperties:
    """Tests for RetryCall property delegation."""

    def test_default_model_property(
        self,
        mock_provider: MockProvider,  # noqa: ARG002
    ) -> None:
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
        self,
        mock_provider: MockProvider,  # noqa: ARG002
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


class TestRetryDecoratorErrors:
    """Tests for error handling in retry decorator."""

    def test_retry_raises_value_error_for_unsupported_type(self) -> None:
        """Test that retry raises ValueError for unsupported target types."""
        with pytest.raises(ValueError, match="Unsupported target type for retry"):
            llm.retry("not a valid target", max_retries=2)  # type: ignore[arg-type]


class TestSyncStreamRetry:
    """Tests for sync streaming with retry support."""

    def test_stream_succeeds_first_attempt(self, mock_provider: MockProvider) -> None:
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

    def test_stream_raises_stream_restarted_on_error(
        self, mock_provider: MockProvider
    ) -> None:
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

        assert exc_info.value.attempt == 1
        assert exc_info.value.error is CONNECTION_ERROR
        assert len(response.retry_failures) == 1
        assert [f.exception for f in response.retry_failures] == [CONNECTION_ERROR]

    def test_stream_can_continue_after_restart(
        self, mock_provider: MockProvider
    ) -> None:
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

    def test_stream_raises_original_error_after_max_attempts(
        self, mock_provider: MockProvider
    ) -> None:
        """Test that original error is raised when max attempts exhausted."""
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

        # Second attempt also fails, should raise original error (not StreamRestarted)
        with pytest.raises(llm.RateLimitError, match="rate limited"):
            list(response.text_stream())

        # retry_failures is 2 because 2 failures occurred (max_retries=1 allows 1 retry,
        # but the second error happens during the retry so counter goes to 2)
        assert len(response.retry_failures) == 2
        assert mock_provider.stream_count == 2

    def test_stream_retry_failures_accessible(
        self, mock_provider: MockProvider
    ) -> None:
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

    def test_stream_model_property(
        self,
        mock_provider: MockProvider,  # noqa: ARG002
    ) -> None:
        """Test that model property returns RetryModel."""

        @llm.retry(max_retries=2)
        @llm.call("mock/test-model")
        def greet() -> str:
            return "Hello"

        response = greet.stream()

        assert isinstance(response.model, llm.RetryModel)
        assert response.model.model_id == "mock/test-model"


@pytest.mark.asyncio
class TestAsyncStreamRetry:
    """Tests for async streaming with retry support."""

    async def test_stream_async_succeeds_first_attempt(
        self, mock_provider: MockProvider
    ) -> None:
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

    async def test_stream_async_raises_stream_restarted_on_error(
        self, mock_provider: MockProvider
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

        assert exc_info.value.attempt == 1
        assert exc_info.value.error is TIMEOUT_ERROR
        assert len(response.retry_failures) == 1

    async def test_stream_async_can_continue_after_restart(
        self, mock_provider: MockProvider
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

    async def test_stream_async_raises_original_error_after_max_attempts(
        self, mock_provider: MockProvider
    ) -> None:
        """Test that original error is raised when max attempts exhausted."""
        mock_provider.set_stream_exceptions([CONNECTION_ERROR, SERVER_ERROR])

        @llm.retry(max_retries=1)
        @llm.call("mock/test-model")
        async def greet() -> str:
            return "Hello"

        response = await greet.stream()

        # First attempt fails, catch StreamRestarted
        with pytest.raises(llm.StreamRestarted):
            _ = [chunk async for chunk in response.text_stream()]

        # Second attempt also fails, should raise original error
        with pytest.raises(llm.ServerError, match="server error"):
            _ = [chunk async for chunk in response.text_stream()]

        # retry_failures is 2 because 2 failures occurred (max_retries=1 allows 1 retry,
        # but the second error happens during the retry so counter goes to 2)
        assert len(response.retry_failures) == 2
        assert mock_provider.stream_count == 2


class TestRetryStreamResponseProperties:
    """Tests for RetryStreamResponse property delegation."""

    def test_delegated_properties(self, mock_provider: MockProvider) -> None:
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

    def test_finish_method(self, mock_provider: MockProvider) -> None:
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

    def test_pretty_stream(self, mock_provider: MockProvider) -> None:
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

    def test_streams_method(self, mock_provider: MockProvider) -> None:
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

    def test_execute_tools_sync(self, mock_provider: MockProvider) -> None:  # noqa: ARG002
        """Test that execute_tools delegates to wrapped response."""

        @llm.retry(max_retries=1)
        @llm.call("mock/test-model")
        def greet() -> str:
            return "Hello"

        response = greet.stream()
        response.finish()

        result = response.execute_tools()
        assert result == []

    def test_pretty_method(self, mock_provider: MockProvider) -> None:
        """Test that pretty() returns formatted text after consumption."""

        @llm.retry(max_retries=1)
        @llm.call("mock/test-model")
        def greet() -> str:
            return "Hello"

        response = greet.stream()
        response.finish()

        output = response.pretty()
        assert "mock response" in output


class TestRetryStreamResponseStructuredStream:
    """Tests for structured_stream() method on RetryStreamResponse."""

    def test_structured_stream_raises_without_format(
        self,
        mock_provider: MockProvider,  # noqa: ARG002
    ) -> None:
        """Test that structured_stream raises ValueError without format."""

        @llm.retry(max_retries=1)
        @llm.call("mock/test-model")
        def greet() -> str:
            return "Hello"

        response = greet.stream()

        with pytest.raises(ValueError, match="structured_stream\\(\\) requires format"):
            list(response.structured_stream())


class TestRetryStreamResponseResume:
    """Tests for resume() method on RetryStreamResponse."""

    def test_resume_returns_retry_stream_response(
        self, mock_provider: MockProvider
    ) -> None:
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


@pytest.mark.asyncio
class TestAsyncRetryStreamResponseProperties:
    """Tests for AsyncRetryStreamResponse property delegation."""

    async def test_delegated_properties(self, mock_provider: MockProvider) -> None:
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

    async def test_finish_method(self, mock_provider: MockProvider) -> None:
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

    async def test_pretty_stream(self, mock_provider: MockProvider) -> None:
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

    async def test_streams_method(self, mock_provider: MockProvider) -> None:
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

    async def test_execute_tools_async(
        self,
        mock_provider: MockProvider,  # noqa: ARG002
    ) -> None:
        """Test that execute_tools delegates to wrapped response."""

        @llm.retry(max_retries=1)
        @llm.call("mock/test-model")
        async def greet() -> str:
            return "Hello"

        response = await greet.stream()
        await response.finish()

        result = await response.execute_tools()
        assert result == []

    async def test_pretty_method(self, mock_provider: MockProvider) -> None:
        """Test that pretty() returns formatted text after consumption."""

        @llm.retry(max_retries=1)
        @llm.call("mock/test-model")
        async def greet() -> str:
            return "Hello"

        response = await greet.stream()
        await response.finish()

        output = response.pretty()
        assert "mock response" in output


@pytest.mark.asyncio
class TestAsyncRetryStreamResponseStructuredStream:
    """Tests for structured_stream() method on AsyncRetryStreamResponse."""

    async def test_structured_stream_raises_without_format(
        self,
        mock_provider: MockProvider,  # noqa: ARG002
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
class TestAsyncRetryStreamResponseResume:
    """Tests for resume() method on AsyncRetryStreamResponse."""

    async def test_resume_returns_async_retry_stream_response(
        self, mock_provider: MockProvider
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

    async def test_resume_stream_factory_called_on_retry(
        self, mock_provider: MockProvider
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


class TestRetryStreamResponseStructuredStreamHappyPath:
    """Tests for structured_stream() happy path on RetryStreamResponse."""

    def test_structured_stream_yields_partials(
        self, mock_provider: MockProvider
    ) -> None:
        """Test that structured_stream yields partial outputs."""
        from pydantic import BaseModel

        class Person(BaseModel):
            name: str
            age: int

        # Set up mock to return valid JSON
        mock_provider.set_stream_text('{"name": "Alice", "age": 30}')

        model = llm.Model("mock/test-model")
        retry_model = llm.retry(model, max_retries=1)

        response = retry_model.stream("Get person", format=Person)

        partials = list(response.structured_stream())

        # Should have yielded at least one partial
        assert len(partials) >= 1

    def test_structured_stream_raises_for_output_parser(
        self,
        mock_provider: MockProvider,  # noqa: ARG002
    ) -> None:
        """Test that structured_stream raises NotImplementedError for OutputParser."""

        @llm.output_parser(formatting_instructions="Return text")
        def custom_parser(response: llm.RootResponse[llm.Toolkit, None]) -> str:
            return response.text()

        model = llm.Model("mock/test-model")
        retry_model = llm.retry(model, max_retries=1)

        response = retry_model.stream("Hello", format=custom_parser)

        with pytest.raises(
            NotImplementedError, match="structured_stream\\(\\) not supported"
        ):
            list(response.structured_stream())


@pytest.mark.asyncio
class TestAsyncRetryStreamResponseStructuredStreamHappyPath:
    """Tests for structured_stream() happy path on AsyncRetryStreamResponse."""

    async def test_structured_stream_yields_partials(
        self, mock_provider: MockProvider
    ) -> None:
        """Test that async structured_stream yields partial outputs."""
        from pydantic import BaseModel

        class Person(BaseModel):
            name: str
            age: int

        # Set up mock to return valid JSON
        mock_provider.set_stream_text('{"name": "Bob", "age": 25}')

        model = llm.Model("mock/test-model")
        retry_model = llm.retry(model, max_retries=1)

        response = await retry_model.stream_async("Get person", format=Person)

        partials = [p async for p in response.structured_stream()]

        # Should have yielded at least one partial
        assert len(partials) >= 1

    async def test_structured_stream_raises_for_output_parser(
        self,
        mock_provider: MockProvider,  # noqa: ARG002
    ) -> None:
        """Test that async structured_stream raises NotImplementedError for OutputParser."""

        @llm.output_parser(formatting_instructions="Return text")
        def custom_parser(response: llm.RootResponse[llm.Toolkit, None]) -> str:
            return response.text()

        model = llm.Model("mock/test-model")
        retry_model = llm.retry(model, max_retries=1)

        response = await retry_model.stream_async("Hello", format=custom_parser)

        with pytest.raises(
            NotImplementedError, match="structured_stream\\(\\) not supported"
        ):
            _ = [p async for p in response.structured_stream()]


class TestFallbackModels:
    """Tests for fallback model functionality."""

    def test_fallback_with_model_id_inherits_params(
        self, mock_provider: MockProvider
    ) -> None:
        """Test that ModelId fallbacks inherit params from primary model."""
        model = llm.Model("mock/primary", temperature=0.5)
        retry_model = llm.retry(model, max_retries=0, fallback_models=["mock/fallback"])

        # Access internal models to verify params inheritance
        models = retry_model._models  # pyright: ignore[reportPrivateUsage]
        assert len(models) == 2
        assert models[0].model_id == "mock/primary"
        assert models[1].model_id == "mock/fallback"
        assert models[1].params.get("temperature") == 0.5

    def test_fallback_with_model_instance_uses_own_params(
        self, mock_provider: MockProvider
    ) -> None:
        """Test that Model instance fallbacks use their own params."""
        primary = llm.Model("mock/primary", temperature=0.5)
        fallback = llm.Model("mock/fallback", temperature=0.9)
        retry_model = llm.retry(primary, max_retries=0, fallback_models=[fallback])

        models = retry_model._models  # pyright: ignore[reportPrivateUsage]
        assert len(models) == 2
        assert models[0].params.get("temperature") == 0.5
        assert models[1].params.get("temperature") == 0.9

    def test_fallback_strips_retry_model_wrapper(
        self, mock_provider: MockProvider
    ) -> None:
        """Test that RetryModel fallbacks are stripped to plain Model."""
        primary = llm.Model("mock/primary")
        nested_retry = llm.retry(
            llm.Model("mock/fallback", temperature=0.7),
            max_retries=5,
            fallback_models=["mock/nested-fallback"],
        )
        retry_model = llm.retry(primary, max_retries=0, fallback_models=[nested_retry])

        models = retry_model._models  # pyright: ignore[reportPrivateUsage]
        assert len(models) == 2
        # The nested RetryModel should be stripped to a plain Model
        assert type(models[1]) is llm.Model
        assert models[1].model_id == "mock/fallback"
        assert models[1].params.get("temperature") == 0.7

    def test_fallback_model_tried_after_primary_exhausted(
        self, mock_provider: MockProvider
    ) -> None:
        """Test that fallback model is tried when primary exhausts retries."""
        # Primary model will fail, fallback will succeed
        mock_provider.set_exceptions([CONNECTION_ERROR])

        primary = llm.Model("mock/primary")
        retry_model = llm.retry(
            primary, max_retries=0, fallback_models=["mock/fallback"]
        )

        response = retry_model.call("Hello")

        # Should have succeeded on fallback
        assert response.model_id == "mock/fallback"
        assert len(response.retry_failures) == 1

    def test_fallback_model_gets_own_retry_budget(
        self, mock_provider: MockProvider
    ) -> None:
        """Test that each fallback model gets its own full retry budget."""
        # Primary fails twice, fallback fails once then succeeds
        mock_provider.set_exceptions(
            [
                CONNECTION_ERROR,  # primary attempt 1
                CONNECTION_ERROR,  # primary attempt 2 (retry)
                RATE_LIMIT_ERROR,  # fallback attempt 1
            ]
        )

        primary = llm.Model("mock/primary")
        retry_model = llm.retry(
            primary, max_retries=1, fallback_models=["mock/fallback"]
        )

        response = retry_model.call("Hello")

        # Should have succeeded on fallback's second attempt
        assert response.model_id == "mock/fallback"
        assert len(response.retry_failures) == 3  # 2 primary + 1 fallback failures

    def test_response_model_property_returns_retry_model_with_successful_active(
        self, mock_provider: MockProvider
    ) -> None:
        """Test that response.model returns RetryModel with successful model as active."""
        mock_provider.set_exceptions([CONNECTION_ERROR])

        primary = llm.Model("mock/primary")
        retry_model = llm.retry(
            primary, max_retries=0, fallback_models=["mock/fallback"]
        )

        response = retry_model.call("Hello")

        # response.model should be a RetryModel with fallback as active
        assert isinstance(response.model, llm.retries.RetryModel)
        assert response.model.model_id == "mock/fallback"
        assert response.model.model_id == response.model_id


class TestRetryFailureTracking:
    """Tests for retry failure tracking."""

    def test_retry_failures_track_model_and_exception(
        self, mock_provider: MockProvider
    ) -> None:
        """Test that retry_failures tracks both model and exception."""
        mock_provider.set_exceptions([CONNECTION_ERROR])

        model = llm.Model("mock/test-model")
        retry_model = llm.retry(model, max_retries=1)

        response = retry_model.call("Hello")

        assert len(response.retry_failures) == 1
        assert response.retry_failures[0].model.model_id == "mock/test-model"
        assert response.retry_failures[0].exception is CONNECTION_ERROR
