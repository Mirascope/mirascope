"""Configuration for retry behavior."""

from typing_extensions import TypedDict

from ..exceptions import ConnectionError, RateLimitError, ServerError, TimeoutError

DEFAULT_RETRYABLE_ERRORS: tuple[type[BaseException], ...] = (
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


class RetryConfig(TypedDict, total=False):
    """Configuration for retry behavior.

    Attributes:
        max_attempts: Maximum number of attempts (including the initial attempt).
            Defaults to 3.
        retry_on: Tuple of exception types that should trigger a retry.
            Defaults to DEFAULT_RETRYABLE_ERRORS (ConnectionError, RateLimitError,
            ServerError, TimeoutError).
    """

    max_attempts: int
    retry_on: tuple[type[BaseException], ...]
