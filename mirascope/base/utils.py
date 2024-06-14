"""Base utility functions."""

import inspect
from functools import wraps
from typing import (
    Any,
    Callable,
    TypeVar,
    cast,
)

from tenacity import AsyncRetrying, RetryError, Retrying, stop_after_attempt

F = TypeVar("F", bound=Callable[..., Any])


def retry(fn: F) -> F:
    """Decorator for retrying a function."""

    @wraps(fn)
    def wrapper(*args, **kwargs):
        """Wrapper for retrying a function."""
        retries = kwargs.pop("retries", 0)
        if isinstance(retries, int):
            if retries > 0:
                retries = Retrying(stop=stop_after_attempt(retries))
            else:
                return fn(*args, **kwargs)
        try:
            for attempt in retries:
                with attempt:
                    result = fn(*args, **kwargs)
                if (
                    attempt.retry_state.outcome
                    and not attempt.retry_state.outcome.failed
                ):
                    attempt.retry_state.set_result(result)
            return result
        except RetryError:
            raise

    @wraps(fn)
    async def wrapper_async(*args, **kwargs):
        """Wrapper for retrying an async function."""
        retries = kwargs.pop("retries", 0)
        if isinstance(retries, int):
            if retries > 0:
                retries = AsyncRetrying(stop=stop_after_attempt(retries))
            else:
                return await fn(*args, **kwargs)
        try:
            async for attempt in retries:
                with attempt:
                    result = await fn(*args, **kwargs)
                if (
                    attempt.retry_state.outcome
                    and not attempt.retry_state.outcome.failed
                ):
                    attempt.retry_state.set_result(result)
            return result
        except RetryError:
            raise

    @wraps(fn)
    def wrapper_generator(*args, **kwargs):
        """Wrapper for retrying a generator function."""
        retries = kwargs.pop("retries", 0)
        if isinstance(retries, int):
            if retries > 0:
                retries = Retrying(stop=stop_after_attempt(retries))
            else:
                for value in fn(*args, **kwargs):
                    yield value
                return
        try:
            for attempt in retries:
                with attempt:
                    for value in fn(*args, **kwargs):
                        yield value
        except RetryError:
            raise

    @wraps(fn)
    async def wrapper_generator_async(*args, **kwargs):
        """Wrapper for retrying an async generator function."""
        retries = kwargs.pop("retries", 0)
        if isinstance(retries, int):
            if retries > 0:
                retries = AsyncRetrying(stop=stop_after_attempt(retries))
            else:
                async for value in fn(*args, **kwargs):
                    yield value
                return
        try:
            async for attempt in retries:
                with attempt:
                    async for value in fn(*args, **kwargs):
                        yield value
        except RetryError:
            raise

    if inspect.iscoroutinefunction(fn):
        return cast(F, wrapper_async)
    elif inspect.isgeneratorfunction(fn):
        return cast(F, wrapper_generator)
    elif inspect.isasyncgenfunction(fn):
        return cast(F, wrapper_generator_async)
    else:
        return cast(F, wrapper)
