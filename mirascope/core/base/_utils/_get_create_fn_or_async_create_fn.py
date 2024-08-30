import inspect
from collections.abc import (
    AsyncGenerator,
    AsyncIterator,
    Awaitable,
    Callable,
    Generator,
    Iterable,
    Iterator,
)
from typing import (
    Any,
    Literal,
    TypeAlias,
    TypeVar,
    overload,
)

from ._protocols import AsyncCreateFn, CreateFn

_StreamedResponse = TypeVar("_StreamedResponse")
_NonStreamedResponse = TypeVar("_NonStreamedResponse")

_AsyncFunc: TypeAlias = Callable[..., Awaitable[_NonStreamedResponse]]
_AsyncGeneratorFunc: TypeAlias = (
    Callable[..., Awaitable[AsyncGenerator[_StreamedResponse, None]]]
    | Callable[..., AsyncGenerator[_StreamedResponse, None]]
    | Callable[..., AsyncIterator[_StreamedResponse]]
)

_SyncFunc: TypeAlias = Callable[..., _NonStreamedResponse]
_SyncGeneratorFunc: TypeAlias = Callable[
    ..., Iterator[_StreamedResponse] | Iterable[_StreamedResponse]
]


def get_async_create_fn(
    async_func: _AsyncFunc[_NonStreamedResponse],
    async_generator_func: _AsyncGeneratorFunc[_StreamedResponse],
) -> AsyncCreateFn[_NonStreamedResponse, _StreamedResponse]:
    @overload
    def create_or_stream(
        *,
        stream: Literal[True] = True,
        **kwargs: Any,  # noqa: ANN401
    ) -> Awaitable[AsyncGenerator[_StreamedResponse, None]]: ...

    @overload
    def create_or_stream(
        *,
        stream: Literal[False] = False,
        **kwargs: Any,  # noqa: ANN401
    ) -> Awaitable[_NonStreamedResponse]: ...

    def create_or_stream(
        *,
        stream: bool = False,
        **kwargs: Any,  # noqa: ANN401
    ) -> (
        Awaitable[AsyncGenerator[_StreamedResponse, None]]
        | Awaitable[_NonStreamedResponse]
    ):
        if not stream:
            return async_func(**kwargs)
        else:
            async_generator = async_generator_func(**kwargs)
            if inspect.isasyncgen(async_generator) or not isinstance(
                async_generator, Awaitable
            ):

                async def _stream() -> AsyncGenerator[_StreamedResponse]:
                    return async_generator  # pyright: ignore [reportReturnType]

                return _stream()
            else:  # pragma: no cover
                return async_generator

    return create_or_stream


def get_create_fn(
    sync_func: _SyncFunc[_NonStreamedResponse],
    sync_generator_func: _SyncGeneratorFunc[_StreamedResponse],
) -> CreateFn[_NonStreamedResponse, _StreamedResponse]:
    @overload
    def create_or_stream(
        *,
        stream: Literal[True] = True,
        **kwargs: Any,  # noqa: ANN401
    ) -> Generator[_StreamedResponse, None, None]: ...

    @overload
    def create_or_stream(
        *,
        stream: Literal[False] = False,
        **kwargs: Any,  # noqa: ANN401
    ) -> _NonStreamedResponse: ...

    def create_or_stream(
        *,
        stream: bool = False,
        **kwargs: Any,  # noqa: ANN401
    ) -> Generator[_StreamedResponse, None, None] | _NonStreamedResponse:
        if stream:
            generator = sync_generator_func(**kwargs)

            def _stream() -> Generator[_StreamedResponse, None, None]:
                yield from generator

            return _stream()
        return sync_func(**kwargs)

    return create_or_stream
