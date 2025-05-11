"""This module contains the `fn_is_async` function."""

import inspect
from collections.abc import Awaitable, Callable, Coroutine
from typing import Any, TypeVar

from typing_extensions import TypeIs

_R = TypeVar("_R")


def fn_is_async(
    fn: Callable[..., Awaitable[_R] | Coroutine[Any, Any, _R]] | Callable[..., _R],
) -> TypeIs[Callable[..., Awaitable[_R]]]:
    if inspect.iscoroutinefunction(fn):
        return True

    # Check if it's a wrapper around an `async def` function (using functools.wraps).
    _fn = fn
    while hasattr(_fn, "__wrapped__"):
        _fn = _fn.__wrapped__  # pyright: ignore[reportFunctionMemberAccess]
        if inspect.iscoroutinefunction(_fn):
            return True
    return False
