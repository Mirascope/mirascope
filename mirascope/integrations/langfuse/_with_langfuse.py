"""Mirascope x Langfuse Integration."""

from typing import (
    Awaitable,
    Callable,
    ParamSpec,
    TypeVar,
)

from langfuse.decorators import observe
from pydantic import BaseModel

from mirascope.core.base._structured_stream import BaseStructuredStream

from ...core.base import BaseCallResponse
from ...core.base._stream import BaseStream
from ..middleware_factory import middleware_decorator
from ._utils import (
    handle_call_response,
    handle_call_response_async,
    handle_response_model,
    handle_response_model_async,
    handle_stream,
    handle_stream_async,
    handle_structured_stream,
    handle_structured_stream_async,
)

_BaseCallResponseT = TypeVar("_BaseCallResponseT", bound=BaseCallResponse)
_BaseStreamT = TypeVar("_BaseStreamT", bound=BaseStream)
_BaseModelT = TypeVar("_BaseModelT", bound=BaseModel)
_BaseStructuredStreamT = TypeVar("_BaseStructuredStreamT", bound=BaseStructuredStream)
_P = ParamSpec("_P")
SyncFunc = Callable[
    _P, _BaseCallResponseT | _BaseStreamT | _BaseModelT | _BaseStructuredStreamT
]
AsyncFunc = Callable[
    _P,
    Awaitable[_BaseCallResponseT | _BaseStreamT | _BaseModelT | _BaseStructuredStreamT],
]


def with_langfuse(fn):
    """Wraps a Mirascope function with Langfuse."""

    return middleware_decorator(
        fn,
        custom_decorator=observe(
            name=fn.__name__,
            as_type="generation",
            capture_input=False,
            capture_output=False,
        ),
        handle_call_response=handle_call_response,
        handle_call_response_async=handle_call_response_async,
        handle_stream=handle_stream,
        handle_stream_async=handle_stream_async,
        handle_response_model=handle_response_model,
        handle_response_model_async=handle_response_model_async,
        handle_structured_stream=handle_structured_stream,
        handle_structured_stream_async=handle_structured_stream_async,
    )
