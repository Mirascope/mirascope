"""Utility functions for retry logic."""

from collections.abc import Awaitable, Callable
from dataclasses import dataclass, field
from typing import TypeVar

from .retry_config import RetryConfig

_ResultT = TypeVar("_ResultT")


def _empty_exception_list() -> list[BaseException]:
    return []


@dataclass
class RetryState:
    """Tracks the state of retry attempts with resolved configuration.

    This captures both the concrete retry settings that were used and the
    results of the retry process.

    Attributes:
        max_attempts: The maximum attempts that were configured.
        retry_on: The exception types that triggered retries.
        attempts: The number of attempts made (1 = succeeded on first try).
        exceptions: The list of exceptions caught during failed attempts.
    """

    max_attempts: int
    retry_on: tuple[type[BaseException], ...]
    attempts: int = 1
    exceptions: list[BaseException] = field(default_factory=_empty_exception_list)


def with_retry(
    fn: Callable[[], _ResultT],
    config: RetryConfig,
) -> tuple[_ResultT, RetryState]:
    """Execute a function with retry logic.

    Args:
        fn: The function to execute.
        config: Retry configuration.

    Returns:
        A tuple of (result, retry_state).

    Raises:
        Exception: The last exception encountered if all retry attempts fail.
    """
    state = RetryState(max_attempts=config.max_attempts, retry_on=config.retry_on)
    for attempt in range(1, config.max_attempts + 1):
        try:
            result = fn()
            state.attempts = attempt
            return result, state
        except config.retry_on as e:
            state.exceptions.append(e)
            if attempt == config.max_attempts:
                state.attempts = attempt
                raise
    raise AssertionError("Unreachable")  # pragma: no cover


async def with_retry_async(
    fn: Callable[[], Awaitable[_ResultT]],
    config: RetryConfig,
) -> tuple[_ResultT, RetryState]:
    """Execute an async function with retry logic.

    Args:
        fn: The async function to execute.
        config: Retry configuration.

    Returns:
        A tuple of (result, retry_state).

    Raises:
        Exception: The last exception encountered if all retry attempts fail.
    """
    state = RetryState(max_attempts=config.max_attempts, retry_on=config.retry_on)
    for attempt in range(1, config.max_attempts + 1):
        try:
            result = await fn()
            state.attempts = attempt
            return result, state
        except config.retry_on as e:
            state.exceptions.append(e)
            if attempt == config.max_attempts:
                state.attempts = attempt
                raise
    raise AssertionError("Unreachable")  # pragma: no cover
