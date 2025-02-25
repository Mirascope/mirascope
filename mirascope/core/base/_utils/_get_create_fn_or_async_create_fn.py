import inspect
from collections.abc import (
    AsyncGenerator,
    AsyncIterable,
    AsyncIterator,
    Awaitable,
    Callable,
    Coroutine,
    Generator,
    Iterable,
    Iterator,
)
from typing import (
    Any,
    Literal,
    TypeAlias,
    TypeVar,
    cast,
    overload,
)

from typing_extensions import TypeIs

from ..stream_config import StreamConfig
from ._protocols import AsyncCreateFn, CreateFn

_StreamedResponse = TypeVar("_StreamedResponse")
_NonStreamedResponse = TypeVar("_NonStreamedResponse")
_T = TypeVar("_T")


def is_awaitable(value: _T | Awaitable[_T]) -> TypeIs[Awaitable[_T]]:
    return inspect.isawaitable(value)


_AsyncFunc: TypeAlias = Callable[..., Awaitable[_NonStreamedResponse]]
_AsyncGeneratorFunc: TypeAlias = (
    Callable[..., Awaitable[AsyncGenerator[_StreamedResponse, None]]]
    | Callable[..., AsyncGenerator[_StreamedResponse, None]]
    | Callable[..., AsyncIterator[_StreamedResponse]]
    | Callable[..., AsyncIterable[_StreamedResponse]]
    | Callable[..., Coroutine[Any, Any, _StreamedResponse]]
)

_SyncFunc: TypeAlias = Callable[..., _NonStreamedResponse]
_SyncGeneratorFunc: TypeAlias = Callable[
    ..., Iterator[_StreamedResponse] | Iterable[_StreamedResponse]
]


def get_async_create_fn(
    async_func: _AsyncFunc[_NonStreamedResponse],
    async_generator_func: _AsyncGeneratorFunc[_StreamedResponse] | None = None,
) -> AsyncCreateFn[_NonStreamedResponse, _StreamedResponse]:
    @overload
    def create_or_stream(  # pyright: ignore[reportOverlappingOverload]
        *,
        stream: Literal[True] | StreamConfig = True,
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
        stream: bool | StreamConfig = False,
        **kwargs: Any,  # noqa: ANN401
    ) -> (
        Awaitable[AsyncGenerator[_StreamedResponse, None]]
        | Awaitable[_NonStreamedResponse]
    ):
        if not stream:
            return cast(Awaitable[_NonStreamedResponse], async_func(**kwargs))
        else:
            if async_generator_func is None:
                async_generator = async_func(**kwargs, stream=True)
            else:
                async_generator = async_generator_func(**kwargs)
            if inspect.isasyncgen(async_generator) or not is_awaitable(async_generator):

                async def _stream() -> AsyncGenerator[_StreamedResponse]:
                    return cast(AsyncGenerator[_StreamedResponse], async_generator)

                return _stream()
            else:
                return cast(
                    Awaitable[AsyncGenerator[_StreamedResponse]], async_generator
                )

    return create_or_stream


def get_create_fn(
    sync_func: _SyncFunc[_NonStreamedResponse],
    sync_generator_func: _SyncGeneratorFunc[_StreamedResponse] | None = None,
) -> CreateFn[_NonStreamedResponse, _StreamedResponse]:
    @overload
    def create_or_stream(  # pyright: ignore[reportOverlappingOverload]
        *,
        stream: Literal[True] | StreamConfig = True,
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
        stream: bool | StreamConfig = False,
        **kwargs: Any,  # noqa: ANN401
    ) -> Generator[_StreamedResponse, None, None] | _NonStreamedResponse:
        if stream:
            if sync_generator_func is None:
                generator = cast(
                    Iterator[_StreamedResponse],
                    sync_func(**kwargs, stream=True),
                )
            else:
                generator = sync_generator_func(**kwargs)

            def _stream() -> Generator[_StreamedResponse, None, None]:
                yield from generator

            return _stream()

        return cast(_NonStreamedResponse, sync_func(**kwargs))

    return create_or_stream
