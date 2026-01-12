"""Configuration for retry behavior."""

from dataclasses import dataclass

from ..exceptions import (
    ConnectionError,
    RateLimitError,
    ServerError,
    TimeoutError,
)

DEFAULT_RETRYABLE_ERRORS: tuple[type[Exception], ...] = (
    ConnectionError,
    RateLimitError,
    ServerError,
    TimeoutError,
)
"""Default exceptions that trigger a retry.

These are transient errors that are likely to succeed on retry:
- ConnectionError: Network issues, DNS failures
- RateLimitError: Rate limits exceeded (429)
- ServerError: Provider-side errors (500+)
- TimeoutError: Request timeouts
"""

DEFAULT_MAX_ATTEMPTS: int = 3
"""Default maximum number of attempts (1 initial + 2 retries)."""


@dataclass(frozen=True)
class RetryConfig:
    """Configuration for retry behavior with defaults applied.

    Attributes:
        max_attempts: Maximum number of attempts (including the initial attempt).
        retry_on: Tuple of exception types that should trigger a retry.
    """

    max_attempts: int = DEFAULT_MAX_ATTEMPTS
    retry_on: tuple[type[Exception], ...] = DEFAULT_RETRYABLE_ERRORS
