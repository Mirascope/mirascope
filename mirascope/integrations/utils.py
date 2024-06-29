"""Mirascope middleware utils."""

import inspect
import types
from contextlib import contextmanager
from functools import wraps
from typing import (
    Any,
    Awaitable,
    Callable,
    Generator,
    Iterable,
    ParamSpec,
    TypeVar,
)

from pydantic import BaseModel

from ..core.base import (
    BaseAsyncStream,
    BaseCallResponse,
    BaseStream,
)

_P = ParamSpec("_P")
_R = TypeVar("_R", bound=BaseCallResponse | BaseStream | BaseModel | BaseAsyncStream)
_F = TypeVar("_F", bound=Callable[..., Any])
_DecoratorType = Callable[[_F], _F]
_T = TypeVar("_T")


@contextmanager
def default_context_manager():
    yield None


def middleware(
    fn: Callable[_P, _R] | Callable[_P, Awaitable[_R]],
    *,
    custom_context_manager: Callable[
        [], Generator[_T, Any, None]
    ] = default_context_manager,
    custom_decorator: _DecoratorType | None = None,
    handle_call_response: Callable[[BaseCallResponse, _T | None], None] | None = None,
    handle_call_response_async: Callable[[BaseCallResponse, _T | None], Awaitable[None]]
    | None = None,
    handle_stream: Callable[[BaseStream, _T | None], None] | None = None,
    handle_stream_async: Callable[[BaseStream, _T | None], Awaitable[None]]
    | None = None,
    handle_base_model: Callable[[BaseModel, _T | None], None] | None = None,
    handle_base_model_async: Callable[[BaseModel, _T | None], Awaitable[None]]
    | None = None,
) -> Callable[_P, _R] | Callable[_P, Awaitable[_R]]:
    """Wraps a Mirascope function with middleware."""

    async def handlers_async(result: _R):
        if (
            isinstance(result, BaseCallResponse)
            and handle_call_response_async is not None
        ):
            with custom_context_manager() as context:
                if context is None:
                    await handle_call_response_async(result)
                else:
                    await handle_call_response_async(result, context)
        elif isinstance(result, BaseAsyncStream) and handle_stream_async is not None:
            original_aiter = result.__aiter__

            def new_aiter(self):
                async def generator():
                    with custom_context_manager() as context:
                        async for chunk, tool in original_aiter():
                            yield chunk, tool
                        if handle_stream_async is not None:
                            if context is None:
                                await handle_stream_async(result)
                            else:
                                await handle_stream_async(result, context)

                return generator()

            result.__class__.__aiter__ = types.MethodType(new_aiter, result)
        elif isinstance(result, BaseModel) and handle_base_model_async is not None:
            with custom_context_manager() as context:
                if context is None:
                    await handle_base_model_async(result)
                else:
                    await handle_base_model_async(result, context)
        elif isinstance(result, Iterable[BaseModel]):
            ...

    def inner(*args: _P.args, **kwargs: _P.kwargs) -> _R:
        result = fn(*args, **kwargs)
        if isinstance(result, BaseCallResponse) and handle_call_response is not None:
            with custom_context_manager() as context:
                if context is None:
                    handle_call_response(result)
                else:
                    handle_call_response(result, context)
        elif isinstance(result, BaseStream) and handle_stream is not None:
            original_iter = result.__iter__

            def new_iter(self):
                # Create the context manager when user iterates over the stream
                with custom_context_manager() as context:
                    for chunk, tool in original_iter():
                        yield chunk, tool
                    if handle_stream is not None:
                        if context is None:
                            handle_stream(result)
                        else:
                            handle_stream(result, context)

            result.__class__.__iter__ = new_iter
        elif isinstance(result, BaseModel) and handle_base_model is not None:
            with custom_context_manager() as context:
                if context is not None:
                    handle_base_model(result, context)
                else:
                    handle_base_model(result)
        elif isinstance(result, Iterable[BaseModel]):
            ...
        return result

    async def inner_async(*args: _P.args, **kwargs: _P.kwargs) -> Awaitable[_R]:
        result = await fn(*args, **kwargs)
        await handlers_async(result)
        return result

    inner_fn = inner_async if inspect.iscoroutinefunction(fn) else inner
    decorated_fn = custom_decorator(inner_fn) if custom_decorator else inner_fn
    return wraps(fn)(decorated_fn)
