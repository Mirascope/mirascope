"""The `middleware_factory` method for handling the call response."""

import inspect
from contextlib import AbstractContextManager, contextmanager
from functools import wraps
from typing import (
    Awaitable,
    Callable,
    ParamSpec,
    TypeVar,
    cast,
    overload,
)

from pydantic import BaseModel

from ..core.base._stream import BaseStream
from ..core.base._structured_stream import BaseStructuredStream
from ..core.base.call_response import BaseCallResponse

_BaseCallResponseT = TypeVar("_BaseCallResponseT", bound=BaseCallResponse)
_BaseStructuredStreamT = TypeVar("_BaseStructuredStreamT", bound=BaseStructuredStream)
_BaseStreamT = TypeVar("_BaseStreamT", bound=BaseStream)
_BaseModelT = TypeVar("_BaseModelT", bound=BaseModel)
_P = ParamSpec("_P")
SyncFunc = Callable[
    _P, _BaseCallResponseT | _BaseStreamT | _BaseModelT | _BaseStructuredStreamT
]
AsyncFunc = Callable[
    _P,
    Awaitable[_BaseCallResponseT | _BaseStreamT | _BaseModelT | _BaseStructuredStreamT],
]
_T = TypeVar("_T")


@contextmanager
def default_context_manager(
    fn: SyncFunc | AsyncFunc,
):
    yield None


@overload
def middleware_decorator(
    fn: SyncFunc,
    *,
    custom_context_manager: Callable[
        [SyncFunc], AbstractContextManager[_T]
    ] = default_context_manager,
    custom_decorator: Callable | None = None,
    handle_call_response: Callable[[BaseCallResponse, _T | None], None] | None = None,
    handle_call_response_async: Callable[[BaseCallResponse, _T | None], Awaitable[None]]
    | None = None,
    handle_stream: Callable[[BaseStream, _T | None], None] | None = None,
    handle_stream_async: Callable[[BaseStream, _T | None], Awaitable[None]]
    | None = None,
    handle_base_model: Callable[[BaseModel | BaseStructuredStream, _T | None], None]
    | None = None,
    handle_base_model_async: Callable[
        [BaseModel | BaseStructuredStream, _T | None], Awaitable[None]
    ]
    | None = None,
) -> SyncFunc: ...  # pragma: no cover


@overload
def middleware_decorator(
    fn: AsyncFunc,
    *,
    custom_context_manager: Callable[
        [AsyncFunc], AbstractContextManager[_T]
    ] = default_context_manager,
    custom_decorator: Callable | None = None,
    handle_call_response: Callable[[BaseCallResponse, _T | None], None] | None = None,
    handle_call_response_async: Callable[[BaseCallResponse, _T | None], Awaitable[None]]
    | None = None,
    handle_stream: Callable[[BaseStream, _T | None], None] | None = None,
    handle_stream_async: Callable[[BaseStream, _T | None], Awaitable[None]]
    | None = None,
    handle_base_model: Callable[[BaseModel | BaseStructuredStream, _T | None], None]
    | None = None,
    handle_base_model_async: Callable[
        [BaseModel | BaseStructuredStream, _T | None], Awaitable[None]
    ]
    | None = None,
) -> AsyncFunc: ...  # pragma: no cover


def middleware_decorator(
    fn: SyncFunc | AsyncFunc,
    *,
    custom_context_manager: Callable[
        [SyncFunc | AsyncFunc], AbstractContextManager[_T]
    ] = default_context_manager,
    custom_decorator: Callable | None = None,
    handle_call_response: Callable[[BaseCallResponse, _T | None], None] | None = None,
    handle_call_response_async: Callable[[BaseCallResponse, _T | None], Awaitable[None]]
    | None = None,
    handle_stream: Callable[[BaseStream, _T | None], None] | None = None,
    handle_stream_async: Callable[[BaseStream, _T | None], Awaitable[None]]
    | None = None,
    handle_base_model: Callable[[BaseModel | BaseStructuredStream, _T | None], None]
    | None = None,
    handle_base_model_async: Callable[
        [BaseModel | BaseStructuredStream, _T | None], Awaitable[None]
    ]
    | None = None,
) -> SyncFunc | AsyncFunc:
    is_async = inspect.iscoroutinefunction(fn)

    @wraps(fn)
    def inner(*args: _P.args, **kwargs: _P.kwargs) -> SyncFunc:
        result = fn(*args, **kwargs)
        if isinstance(result, BaseCallResponse) and handle_call_response is not None:
            with custom_context_manager(fn) as context:
                if context is None:
                    handle_call_response(result, None)
                else:
                    handle_call_response(result, context)
        elif isinstance(result, BaseStream):
            original_iter = result.__iter__

            def new_stream_iter(self):
                # Create the context manager when user iterates over the stream
                with custom_context_manager(fn) as context:
                    for chunk, tool in original_iter():
                        yield chunk, tool
                    if handle_stream is not None:
                        if context is None:
                            handle_stream(result, None)
                        else:
                            handle_stream(result, context)

            result.__class__.__iter__ = (
                custom_decorator(new_stream_iter)
                if custom_decorator
                else new_stream_iter
            )
        elif isinstance(result, BaseModel) and handle_base_model is not None:
            with custom_context_manager(fn) as context:
                if context is not None:
                    handle_base_model(result, context)
                else:
                    handle_base_model(result, None)
        elif isinstance(result, BaseStructuredStream) and handle_base_model is not None:
            original_iter = result.__iter__

            def new_iter(self):
                # Create the context manager when user iterates over the stream
                with custom_context_manager(fn) as context:
                    for chunk in original_iter():
                        yield chunk
                    if handle_base_model is not None:
                        if context is None:
                            handle_base_model(result, None)
                        else:
                            handle_base_model(result, context)

            result.__class__.__iter__ = (
                custom_decorator(new_iter) if custom_decorator else new_iter
            )
        return cast(SyncFunc, result)

    @wraps(fn)
    async def inner_async(*args: _P.args, **kwargs: _P.kwargs) -> AsyncFunc:
        result = await fn(*args, **kwargs)
        if (
            isinstance(result, BaseCallResponse)
            and handle_call_response_async is not None
        ):
            with custom_context_manager(fn) as context:
                if context is None:
                    await handle_call_response_async(result, None)
                else:
                    await handle_call_response_async(result, context)
        elif isinstance(result, BaseStream):
            original_aiter = result.__aiter__

            def new_aiter_stream(self):
                async def generator():
                    with custom_context_manager(fn) as context:
                        async for chunk, tool in original_aiter():
                            yield chunk, tool
                        if handle_stream_async is not None:
                            if context is None:
                                await handle_stream_async(result, None)
                            else:
                                await handle_stream_async(result, context)

                return generator()

            result.__class__.__aiter__ = (
                custom_decorator(new_aiter_stream)
                if custom_decorator
                else new_aiter_stream
            )
        elif isinstance(result, BaseModel) and handle_base_model_async is not None:
            with custom_context_manager(fn) as context:
                if context is None:
                    await handle_base_model_async(result, None)
                else:
                    await handle_base_model_async(result, context)
        elif isinstance(result, BaseStructuredStream):
            original_aiter = result.__aiter__

            def new_aiter(self):
                async def generator():
                    with custom_context_manager(fn) as context:
                        async for chunk in original_aiter():
                            yield chunk
                        if handle_base_model_async is not None:
                            if context is None:
                                await handle_base_model_async(result, None)
                            else:
                                await handle_base_model_async(result, context)

                return generator()

            result.__class__.__aiter__ = (
                custom_decorator(new_aiter) if custom_decorator else new_aiter
            )
        return cast(AsyncFunc, result)

    inner_fn = inner_async if is_async else inner
    decorated_fn = custom_decorator(inner_fn) if custom_decorator else inner_fn
    return decorated_fn
