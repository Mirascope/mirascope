"""Utility functions for retry logic."""

import asyncio
import random
import time
from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from typing import TYPE_CHECKING, TypeVar

from .retry_config import RetryConfig

if TYPE_CHECKING:
    from ..models import Model
    from .retry_models import RetryModel

_ResultT = TypeVar("_ResultT")


@dataclass
class RetryFailure:
    """A failed attempt to call a model.

    Attributes:
        model: The model that was tried.
        exception: The exception that was raised.
    """

    model: "Model"
    exception: BaseException


def _calculate_delay(config: RetryConfig, attempt_for_model: int) -> float:
    """Calculate the delay before the next retry attempt.

    Args:
        config: The retry configuration with backoff settings.
        attempt_for_model: The retry attempt number for this model (1-indexed).

    Returns:
        The delay in seconds, with exponential backoff, capped at max_delay,
        and optionally with jitter applied.
    """
    # Calculate base delay with exponential backoff
    delay = config.initial_delay * (
        config.backoff_multiplier ** (attempt_for_model - 1)
    )

    # Cap at max_delay
    delay = min(delay, config.max_delay)

    # Apply jitter if configured
    if config.jitter > 0:
        jitter_range = delay * config.jitter
        delay = delay + random.uniform(-jitter_range, jitter_range)
        # Ensure delay doesn't go negative
        delay = max(0, delay)

    return delay


def with_retry(
    fn: Callable[["Model"], _ResultT],
    retry_model: "RetryModel",
) -> tuple[_ResultT, list[RetryFailure], "RetryModel"]:
    """Execute a function with retry logic across the RetryModel's models.

    Tries the active model first, then fallbacks. Each model gets its own
    full retry budget. Returns an updated RetryModel with the successful
    model set as active.

    Args:
        fn: Function that takes a Model and returns a result.
        retry_model: The RetryModel containing models and retry config.

    Returns:
        A tuple of (result, failures, updated_retry_model).
        failures contains all failed attempts before success.
        The updated_retry_model has the successful model as active.

    Raises:
        Exception: The last exception encountered if all models exhaust retries.
    """
    config = retry_model.retry_config
    failures: list[RetryFailure] = []

    for variant in retry_model._attempt_variants():  # pyright: ignore[reportPrivateUsage]
        model = variant.get_active_model()
        retries_for_model = 0
        for _ in range(config.max_retries + 1):
            try:
                result = fn(model)
                return result, failures, variant
            except config.retry_on as e:
                failures.append(RetryFailure(model=model, exception=e))
                retries_for_model += 1
                if retries_for_model <= config.max_retries:
                    delay = _calculate_delay(config, retries_for_model)
                    time.sleep(delay)
        # Exhausted retries for this model, try next (backoff resets)

    # All models exhausted - raise the last exception
    if failures:
        raise failures[-1].exception
    raise AssertionError("Unreachable: no models provided")  # pragma: no cover


async def with_retry_async(
    fn: Callable[["Model"], Awaitable[_ResultT]],
    retry_model: "RetryModel",
) -> tuple[_ResultT, list[RetryFailure], "RetryModel"]:
    """Execute an async function with retry logic across the RetryModel's models.

    Tries the active model first, then fallbacks. Each model gets its own
    full retry budget. Returns an updated RetryModel with the successful
    model set as active.

    Args:
        fn: Async function that takes a Model and returns a result.
        retry_model: The RetryModel containing models and retry config.

    Returns:
        A tuple of (result, failures, updated_retry_model).
        failures contains all failed attempts before success.
        The updated_retry_model has the successful model as active.

    Raises:
        Exception: The last exception encountered if all models exhaust retries.
    """
    config = retry_model.retry_config
    failures: list[RetryFailure] = []

    for variant in retry_model._attempt_variants():  # pyright: ignore[reportPrivateUsage]
        model = variant.get_active_model()
        retries_for_model = 0
        for _ in range(config.max_retries + 1):
            try:
                result = await fn(model)
                return result, failures, variant
            except config.retry_on as e:
                failures.append(RetryFailure(model=model, exception=e))
                retries_for_model += 1
                if retries_for_model <= config.max_retries:
                    delay = _calculate_delay(config, retries_for_model)
                    await asyncio.sleep(delay)
        # Exhausted retries for this model, try next (backoff resets)

    # All models exhausted - raise the last exception
    if failures:
        raise failures[-1].exception
    raise AssertionError("Unreachable: no models provided")  # pragma: no cover
