from collections.abc import AsyncGenerator, Awaitable
from typing import (
    Any,
    Protocol,
    TypeAlias,
    TypeVar,
)

from mirascope.beta.rag.base.embedding_response import ResponseT

_RealtimeT = TypeVar("_RealtimeT", contravariant=True)
_ResponseT = TypeVar("_ResponseT", covariant=True)

# TODO: Improve the type of context
Context: TypeAlias = dict[str, Any]


class SenderFunc(Protocol[_ResponseT]):
    def __call__(
        self, context: Context
    ) -> AsyncGenerator[_ResponseT, None] | ResponseT: ...


class ReceiverFunc(Protocol[_ResponseT]):
    def __call__(self, response: _ResponseT, context: Context) -> Awaitable[None]: ...
