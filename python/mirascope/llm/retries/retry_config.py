"""Configuration for retry behavior."""

from collections.abc import Sequence
from dataclasses import dataclass
from typing import TYPE_CHECKING, TypedDict
from typing_extensions import Unpack

from ..exceptions import (
    ConnectionError,
    RateLimitError,
    ServerError,
    TimeoutError,
)

if TYPE_CHECKING:
    from ..models import Model
    from ..providers import ModelId

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

DEFAULT_INITIAL_DELAY: float = 0.5
"""Default initial delay in seconds before the first retry."""

DEFAULT_MAX_DELAY: float = 60.0
"""Default maximum delay in seconds between retries."""

DEFAULT_BACKOFF_MULTIPLIER: float = 2.0
"""Default multiplier for exponential backoff (delay *= multiplier after each retry)."""

DEFAULT_JITTER: float = 0.0
"""Default jitter factor (0.0 to 1.0) to add randomness to delays.

A jitter of 0.1 means +/- 10% random variation on the calculated delay.
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
        initial_delay: Initial delay in seconds before the first retry. Defaults to 0.5.
        max_delay: Maximum delay in seconds between retries. Defaults to 60.0.
        backoff_multiplier: Multiplier for exponential backoff. Defaults to 2.0.
        jitter: Jitter factor (0.0 to 1.0) to add randomness to delays. Defaults to 0.0.
    """

    max_retries: int
    """Maximum number of retries after the initial attempt fails. Defaults to 3."""

    retry_on: tuple[type[Exception], ...]
    """Tuple of exception types that should trigger a retry.

    Defaults to DEFAULT_RETRYABLE_ERRORS (ConnectionError, RateLimitError,
    ServerError, TimeoutError).
    """

    initial_delay: float
    """Initial delay in seconds before the first retry. Defaults to 1.0."""

    max_delay: float
    """Maximum delay in seconds between retries. Defaults to 60.0."""

    backoff_multiplier: float
    """Multiplier for exponential backoff (delay *= multiplier after each retry). Defaults to 2.0."""

    jitter: float
    """Jitter factor (0.0 to 1.0) to add randomness to delays. Defaults to 0.0."""

    fallback_models: "Sequence[Model | ModelId]"
    """Sequence of fallback models to try if the primary model fails.

    Each model gets its own full retry budget (max_retries applies per model).
    ModelId strings inherit params from the primary model; Model instances
    use their own params. Defaults to empty tuple (no fallbacks).
    """


@dataclass(frozen=True)
class RetryConfig:
    """Configuration for retry behavior with defaults applied.

    Attributes:
        max_retries: Maximum number of retries after the initial attempt fails.
        retry_on: Tuple of exception types that should trigger a retry.
        initial_delay: Initial delay in seconds before the first retry.
        max_delay: Maximum delay in seconds between retries.
        backoff_multiplier: Multiplier for exponential backoff.
        jitter: Jitter factor (0.0 to 1.0) to add randomness to delays.
    """

    max_retries: int = DEFAULT_MAX_RETRIES
    """Maximum number of retries after the initial attempt fails."""

    retry_on: tuple[type[Exception], ...] = DEFAULT_RETRYABLE_ERRORS
    """Tuple of exception types that should trigger a retry."""

    fallback_models: "tuple[Model | ModelId, ...]" = ()
    """Sequence of fallback models to try if the primary model fails.

    Each model gets its own full retry budget (max_retries applies per model).
    ModelId strings inherit params from the primary model; Model instances
    use their own params. Defaults to empty tuple (no fallbacks).
    """

    initial_delay: float = DEFAULT_INITIAL_DELAY
    """Initial delay in seconds before the first retry."""

    max_delay: float = DEFAULT_MAX_DELAY
    """Maximum delay in seconds between retries."""

    backoff_multiplier: float = DEFAULT_BACKOFF_MULTIPLIER
    """Multiplier for exponential backoff (delay *= multiplier after each retry)."""

    jitter: float = DEFAULT_JITTER
    """Jitter factor (0.0 to 1.0) to add randomness to delays."""

    def __post_init__(self) -> None:
        """Validate configuration values."""
        if self.max_retries < 0:
            raise ValueError("max_retries must be non-negative")
        if self.initial_delay < 0:
            raise ValueError("initial_delay must be non-negative")
        if self.max_delay < 0:
            raise ValueError("max_delay must be non-negative")
        if self.backoff_multiplier < 1:
            raise ValueError("backoff_multiplier must be >= 1")
        if not 0 <= self.jitter <= 1:
            raise ValueError("jitter must be between 0.0 and 1.0")

    @classmethod
    def from_args(cls, **args: Unpack[RetryArgs]) -> "RetryConfig":
        """Create a RetryConfig from RetryArgs kwargs."""
        fallback_models = args.get("fallback_models", ())
        return cls(
            max_retries=args.get("max_retries", DEFAULT_MAX_RETRIES),
            retry_on=args.get("retry_on", DEFAULT_RETRYABLE_ERRORS),
            fallback_models=tuple(fallback_models),
            initial_delay=args.get("initial_delay", DEFAULT_INITIAL_DELAY),
            max_delay=args.get("max_delay", DEFAULT_MAX_DELAY),
            backoff_multiplier=args.get(
                "backoff_multiplier", DEFAULT_BACKOFF_MULTIPLIER
            ),
            jitter=args.get("jitter", DEFAULT_JITTER),
        )
