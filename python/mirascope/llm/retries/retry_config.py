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

DEFAULT_MAX_RETRIES: int = 3
"""Default maximum number of retries after the initial attempt fails."""

DEFAULT_MAX_PARSE_RETRIES: int = 3
"""Default maximum number of parse validation retries (0 = disabled).

When set to a positive number, `.validate()` on retry responses will automatically
retry on ParseError by calling `resume(error.retry_message())` to ask the LLM
to fix its output.
"""


class RetryArgs(TypedDict, total=False):
    """Arguments for configuring retry behavior.

    This TypedDict is used for the user-facing API where all fields are optional.
    Use RetryConfig for the internal representation with defaults applied.

    Attributes:
        max_retries: Maximum number of retries after the initial attempt fails.
            Defaults to 3.
        retry_on: Tuple of exception types that should trigger a retry.
            Defaults to DEFAULT_RETRYABLE_ERRORS (ConnectionError, RateLimitError,
            ServerError, TimeoutError).
        max_parse_retries: Maximum number of parse validation retries.
            When set to a positive number, `.validate()` will automatically retry
            on ParseError by calling `resume(error.retry_message())`.
            Defaults to 3.
    """

    max_retries: int
    """Maximum number of retries after the initial attempt fails. Defaults to 3."""

    retry_on: tuple[type[Exception], ...]
    """Tuple of exception types that should trigger a retry.

    Defaults to DEFAULT_RETRYABLE_ERRORS (ConnectionError, RateLimitError,
    ServerError, TimeoutError).
    """

    max_parse_retries: int
    """Maximum number of parse validation retries.

    When set to a positive number, `.validate()` will automatically retry
    on ParseError by calling `resume(error.retry_message())`. Defaults to 3.
    """


@dataclass(frozen=True)
class RetryConfig:
    """Configuration for retry behavior with defaults applied.

    Attributes:
        max_retries: Maximum number of retries after the initial attempt fails.
        retry_on: Tuple of exception types that should trigger a retry.
        max_parse_retries: Maximum number of parse validation retries.
    """

    max_retries: int = DEFAULT_MAX_RETRIES
    """Maximum number of retries after the initial attempt fails."""

    retry_on: tuple[type[Exception], ...] = DEFAULT_RETRYABLE_ERRORS
    """Tuple of exception types that should trigger a retry."""

    max_parse_retries: int = DEFAULT_MAX_PARSE_RETRIES
    """Maximum number of parse validation retries.

    When set to a positive number, `.validate()` will automatically retry
    on ParseError by calling `resume(error.retry_message())`.
    """

    def __post_init__(self) -> None:
        """Validate configuration values."""
        if self.max_retries < 0:
            raise ValueError("max_retries must be non-negative")
        if self.max_parse_retries < 0:
            raise ValueError("max_parse_retries must be non-negative")

    @classmethod
    def from_args(cls, **args: Unpack[RetryArgs]) -> "RetryConfig":
        """Create a RetryConfig from RetryArgs kwargs."""
        return cls(
            max_retries=args.get("max_retries", DEFAULT_MAX_RETRIES),
            retry_on=args.get("retry_on", DEFAULT_RETRYABLE_ERRORS),
            max_parse_retries=args.get("max_parse_retries", DEFAULT_MAX_PARSE_RETRIES),
        )
