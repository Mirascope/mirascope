"""Shared fixtures for retry tests."""

from collections.abc import Generator

import pytest

from mirascope import llm

from .mock_provider import MockProvider

SERVER_ERROR = llm.ServerError("server error", provider="test")
CONNECTION_ERROR = llm.ConnectionError("connection failed", provider="test")
RATE_LIMIT_ERROR = llm.RateLimitError("rate limited", provider="test")
TIMEOUT_ERROR = llm.TimeoutError("timeout", provider="test")

# Common exception sequences used across tests
DEFAULT_RETRYABLE_EXCEPTIONS: list[llm.Error] = [
    SERVER_ERROR,
    CONNECTION_ERROR,
    RATE_LIMIT_ERROR,
    TIMEOUT_ERROR,
]

RESUME_TEST_EXCEPTIONS: list[llm.Error] = [
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
