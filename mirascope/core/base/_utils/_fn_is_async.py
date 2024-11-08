"""This module contains the `fn_is_async` function."""

import inspect
from collections.abc import Awaitable, Callable, Coroutine
from typing import Any, TypeVar

from typing_extensions import TypeIs

_R = TypeVar("_R")


def fn_is_async(
    fn: Callable[..., Awaitable[_R] | Coroutine[Any, Any, _R]] | Callable[..., _R],
) -> TypeIs[Callable[..., Awaitable[_R]]]:
    return inspect.iscoroutinefunction(fn)
