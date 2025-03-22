"""Protocols For Proper Typing."""

from typing import ParamSpec, Protocol, TypeVar, overload

_P = ParamSpec("_P")
_R = TypeVar("_R")
_CovariantR = TypeVar("_CovariantR", covariant=True)


class SyncFunction(Protocol[_P, _CovariantR]):
    """Protocol for a synchronous function."""

    __name__: str

    def __call__(self, *args: _P.args, **kwargs: _P.kwargs) -> _CovariantR: ...


class AsyncFunction(Protocol[_P, _CovariantR]):
    """Protocol for an asynchronous function."""

    __name__: str

    async def __call__(self, *args: _P.args, **kwargs: _P.kwargs) -> _CovariantR: ...


class PassthroughDecorator(Protocol):
    """Protocol for a decorator with passthrough types."""

    @overload
    def __call__(self, fn: AsyncFunction[_P, _R]) -> AsyncFunction[_P, _R]: ...

    @overload
    def __call__(self, fn: SyncFunction[_P, _R]) -> SyncFunction[_P, _R]: ...

    def __call__(
        self, fn: AsyncFunction[_P, _R] | SyncFunction[_P, _R]
    ) -> AsyncFunction[_P, _R] | SyncFunction[_P, _R]:
        """Protocol `call` definition for a decorator with passthrough types."""
        ...
