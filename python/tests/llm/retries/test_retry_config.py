"""Tests for RetryConfig validation."""

import pytest

from mirascope import llm

from .mock_provider import MockProvider


def test_max_retries_negative_raises_value_error() -> None:
    """Test that negative max_retries raises ValueError."""
    with pytest.raises(ValueError, match="max_retries must be non-negative"):
        llm.retry(max_retries=-1)


def test_max_retries_zero_is_valid(mock_provider: MockProvider) -> None:
    """Test that max_retries=0 is valid (no retries, just one attempt)."""

    @llm.retry(max_retries=0)
    @llm.call("mock/test-model")
    def greet() -> str:
        return "Hello"

    response = greet()
    assert response.model.retry_config.max_retries == 0


def test_initial_delay_negative_raises_value_error() -> None:
    """Test that negative initial_delay raises ValueError."""
    with pytest.raises(ValueError, match="initial_delay must be non-negative"):
        llm.retry(initial_delay=-1.0)


def test_max_delay_negative_raises_value_error() -> None:
    """Test that negative max_delay raises ValueError."""
    with pytest.raises(ValueError, match="max_delay must be non-negative"):
        llm.retry(max_delay=-1.0)


def test_backoff_multiplier_less_than_one_raises_value_error() -> None:
    """Test that backoff_multiplier < 1 raises ValueError."""
    with pytest.raises(ValueError, match="backoff_multiplier must be >= 1"):
        llm.retry(backoff_multiplier=0.5)


def test_jitter_out_of_range_raises_value_error() -> None:
    """Test that jitter outside [0, 1] raises ValueError."""
    with pytest.raises(ValueError, match="jitter must be between 0.0 and 1.0"):
        llm.retry(jitter=-0.1)
    with pytest.raises(ValueError, match="jitter must be between 0.0 and 1.0"):
        llm.retry(jitter=1.1)
