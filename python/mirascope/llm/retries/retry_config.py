"""Configuration for retry behavior."""

from dataclasses import dataclass
from typing_extensions import TypedDict, Unpack

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


class RetryArgs(TypedDict, total=False):
    """Arguments for configuring retry behavior.

    This TypedDict is used for the user-facing API where all fields are optional.
    Use RetryConfig for the internal representation with defaults applied.

    Attributes:
        max_attempts: Maximum number of attempts (including the initial attempt).
            Defaults to 3.
        retry_on: Tuple of exception types that should trigger a retry.
            Defaults to DEFAULT_RETRYABLE_ERRORS (ConnectionError, RateLimitError,
            ServerError, TimeoutError).
    """

    max_attempts: int
    retry_on: tuple[type[Exception], ...]


@dataclass(frozen=True)
class RetryConfig:
    """Configuration for retry behavior with defaults applied.

    Attributes:
        max_attempts: Maximum number of attempts (including the initial attempt).
        retry_on: Tuple of exception types that should trigger a retry.
    """

    max_attempts: int = DEFAULT_MAX_ATTEMPTS
    retry_on: tuple[type[Exception], ...] = DEFAULT_RETRYABLE_ERRORS

    @classmethod
    def from_args(cls, **args: Unpack[RetryArgs]) -> "RetryConfig":
        """Create a RetryConfig from RetryArgs kwargs."""
        return cls(
            max_attempts=args.get("max_attempts", DEFAULT_MAX_ATTEMPTS),
            retry_on=args.get("retry_on", DEFAULT_RETRYABLE_ERRORS),
        )
