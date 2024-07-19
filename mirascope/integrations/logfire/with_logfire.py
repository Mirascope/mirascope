"""Mirascope x Logfire Integration."""

from typing import (
    AsyncIterable,
    Awaitable,
    Callable,
    Iterable,
    ParamSpec,
    TypeVar,
)

from pydantic import BaseModel

from ...core.base import BaseCallResponse
from ...core.base._stream import BaseStream
from ..middleware_factory import middleware_decorator
from ._utils import (
    custom_context_manager,
    handle_base_model,
    handle_base_model_async,
    handle_call_response,
    handle_call_response_async,
    handle_stream,
    handle_stream_async,
)

_BaseCallResponseT = TypeVar("_BaseCallResponseT", bound=BaseCallResponse)
_BaseStreamT = TypeVar("_BaseStreamT", bound=BaseStream)
_BaseModelT = TypeVar("_BaseModelT", bound=BaseModel)
_IterableT = TypeVar("_IterableT", bound=Iterable)
_AsyncIterableT = TypeVar("_AsyncIterableT", bound=AsyncIterable)
_P = ParamSpec("_P")
SyncFunc = Callable[_P, _BaseCallResponseT | _BaseStreamT | _BaseModelT | _IterableT]
AsyncFunc = Callable[
    _P, Awaitable[_BaseCallResponseT | _BaseStreamT | _BaseModelT | _AsyncIterableT]
]
_T = TypeVar("_T")


def with_logfire(
    fn: SyncFunc | AsyncFunc,
) -> SyncFunc | AsyncFunc:
    """Wraps a Mirascope function with Logfire tracing."""

    return middleware_decorator(
        fn,
        custom_context_manager=custom_context_manager,
        handle_call_response=handle_call_response,
        handle_call_response_async=handle_call_response_async,
        handle_stream=handle_stream,
        handle_stream_async=handle_stream_async,
        handle_base_model=handle_base_model,
        handle_base_model_async=handle_base_model_async,
    )
