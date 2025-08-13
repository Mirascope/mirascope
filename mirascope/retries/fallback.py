"""The `fallback` module provides a fallback retry strategy."""

import inspect
from collections.abc import Callable, Coroutine
from typing import Any, ParamSpec, Protocol, TypeVar, overload

from pydantic import BaseModel
from typing_extensions import NotRequired, Required, TypedDict

from .. import llm
from ..core.base import CommonCallParams
from ..core.base.types import Provider

_P = ParamSpec("_P")
_R = TypeVar("_R")


class FallbackDecorator(Protocol):
    @overload
    def __call__(
        self, fn: Callable[_P, Coroutine[_R, Any, Any]]
    ) -> Callable[_P, Coroutine[_R, Any, Any]]: ...

    @overload
    def __call__(self, fn: Callable[_P, _R]) -> Callable[_P, _R]: ...

    def __call__(
        self,
        fn: Callable[_P, _R] | Callable[_P, Coroutine[_R, Any, Any]],
    ) -> Callable[_P, _R] | Callable[_P, Coroutine[_R, Any, Any]]: ...


class Fallback(TypedDict):
    """The override arguments to use for this fallback attempt."""

    catch: Required[type[Exception] | tuple[type[Exception]]]
    provider: Required[Provider]
    model: Required[str]
    call_params: NotRequired[CommonCallParams]
    client: NotRequired[Any]


class FallbackError(Exception):
    """An error raised when all fallbacks fail."""


def fallback(
    catch: type[Exception] | tuple[type[Exception]],
    fallbacks: list[Fallback],
) -> FallbackDecorator:
    """A decorator that retries the function call with a fallback strategy.

    This must use the provider-agnostic `llm.call` decorator.

    Args:
        catch: The exception(s) to catch for the original call.
        backups: The list of backup providers to try in order. Each backup provider
            is a tuple of the provider name, the model name, and the call params.
            The call params may be `None` if no change is wanted.

    Returns:
        The decorated function.

    Raises:
        FallbackError: If all fallbacks fail.
    """

    @overload
    def decorator(
        fn: Callable[_P, Coroutine[_R, Any, Any]],
    ) -> Callable[_P, Coroutine[_R, Any, Any]]: ...

    @overload
    def decorator(fn: Callable[_P, _R]) -> Callable[_P, _R]: ...

    def decorator(
        fn: Callable[_P, _R] | Callable[_P, Coroutine[_R, Any, Any]],
    ) -> Callable[_P, _R] | Callable[_P, Coroutine[_R, Any, Any]]:
        fn_to_check = fn._original_fn if hasattr(fn, "_original_fn") else fn  # pyright: ignore [reportFunctionMemberAccess]
        if inspect.iscoroutinefunction(fn_to_check):

            async def inner_async(*args: _P.args, **kwargs: _P.kwargs) -> _R:
                caught: list[Exception] = []
                try:
                    return await fn(*args, **kwargs)  # pyright: ignore [reportReturnType,reportGeneralTypeIssues]
                except catch as e:
                    caught.append(e)
                    for backup in fallbacks:
                        try:
                            with llm.context(
                                provider=backup["provider"],
                                model=backup["model"],
                                call_params=backup.get("call_params", None),
                                client=backup.get("client", None),
                            ):
                                response = await fn(*args, **kwargs)  # pyright: ignore [reportGeneralTypeIssues]
                                if isinstance(response, BaseModel):
                                    response._caught = caught  # pyright: ignore [reportAttributeAccessIssue]
                                return response  # pyright: ignore [reportReturnType]
                        except backup["catch"] as be:
                            caught.append(be)
                raise FallbackError(f"All fallbacks failed:\n{caught}")

            return inner_async
        else:

            def inner(*args: _P.args, **kwargs: _P.kwargs) -> _R:
                caught: list[Exception] = []
                try:
                    return fn(*args, **kwargs)  # pyright: ignore [reportReturnType]
                except catch as e:
                    caught.append(e)
                    for backup in fallbacks:
                        try:
                            with llm.context(
                                provider=backup["provider"],
                                model=backup["model"],
                                call_params=backup.get("call_params", None),
                                client=backup.get("client", None),
                            ):
                                response = fn(*args, **kwargs)
                                if isinstance(response, BaseModel):
                                    response._caught = caught  # pyright: ignore [reportAttributeAccessIssue]
                                return response  # pyright: ignore [reportReturnType]
                        except backup["catch"] as be:
                            caught.append(be)
                raise FallbackError(f"All fallbacks failed:\n{caught}")

            return inner

    return decorator
