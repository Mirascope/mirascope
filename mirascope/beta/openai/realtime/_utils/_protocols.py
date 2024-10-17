from collections.abc import AsyncGenerator, Awaitable, Coroutine
from typing import (
    Any,
    Protocol,
    TypeAlias,
    TypeVar,
)

from ..tool import OpenAIRealtimeTool

_ResponseBaseType = str | bytes
_ResponseT = TypeVar("_ResponseT", bound=_ResponseBaseType)
_ReceiverArgumentT = TypeVar("_ReceiverArgumentT")
# TODO: Improve the type of context
Context: TypeAlias = dict[str, Any]


class SenderFunc(Protocol[_ResponseT]):
    def __call__(
        self, context: Context
    ) -> (
        AsyncGenerator[_ResponseT | tuple[_ResponseT, OpenAIRealtimeTool], None]
        | Coroutine[Any, Any, _ResponseT | tuple[_ResponseT, OpenAIRealtimeTool]]
        | Awaitable[_ResponseT | tuple[_ResponseT, OpenAIRealtimeTool]]
    ): ...


class ReceiverFunc(Protocol[_ReceiverArgumentT]):
    def __call__(
        self, response: _ReceiverArgumentT, context: Context
    ) -> Awaitable[None]: ...
