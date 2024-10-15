from collections.abc import AsyncGenerator, Awaitable, Coroutine
from typing import (
    Any,
    Protocol,
    TypeAlias,
    TypeVar,
)

from mirascope.beta.rag.base.embedding_response import ResponseT

_ResponseBaseType = str | bytes
_ResponseT = TypeVar("_ResponseT", bound=_ResponseBaseType)

# TODO: Improve the type of context
Context: TypeAlias = dict[str, Any]


class SenderFunc(Protocol[_ResponseT]):
    def __call__(
        self, context: Context
    ) -> (
        AsyncGenerator[_ResponseT, None]
        | Coroutine[Any, Any, _ResponseT]
        | Awaitable[ResponseT]
    ): ...


class ReceiverFunc(Protocol[_ResponseT]):
    def __call__(self, response: _ResponseT, context: Context) -> Awaitable[None]: ...
