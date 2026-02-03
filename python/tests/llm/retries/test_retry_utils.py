"""Tests for exponential backoff delay behavior."""

import pytest

from mirascope import llm

from .conftest import SERVER_ERROR
from .mock_provider import MockProvider


def test_backoff_delays_are_applied(
    mock_provider: MockProvider, mock_sleep: list[float]
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
    mock_provider: MockProvider, mock_sleep: list[float]
) -> None:
    """Test that backoff delay is capped at max_delay."""
    # Fail 3 times, then succeed
    mock_provider.set_exceptions([SERVER_ERROR, SERVER_ERROR, SERVER_ERROR])

    @llm.retry(max_retries=4, initial_delay=1.0, backoff_multiplier=10.0, max_delay=5.0)
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


@pytest.mark.asyncio
async def test_async_backoff_delays_are_applied(
    mock_provider: MockProvider, mock_sleep: list[float]
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
