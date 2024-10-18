from collections.abc import AsyncGenerator, Awaitable, Callable, Coroutine
from typing import (
    Any,
    Protocol,
    TypeAlias,
    TypeVar,
)

from ..tool import OpenAIRealtimeTool

_ToolTypeBase: TypeAlias = type[OpenAIRealtimeTool] | Callable

_ResponseBaseType = str | bytes
_ResponseT = TypeVar("_ResponseT", bound=_ResponseBaseType)
_ReceiverArgumentT = TypeVar("_ReceiverArgumentT")
_ToolType = TypeVar("_ToolType", bound=_ToolTypeBase)
# TODO: Improve the type of context
Context: TypeAlias = dict[str, Any]
_OpenAIRealtimeToolT = TypeVar("_OpenAIRealtimeToolT", bound=OpenAIRealtimeTool)


class SenderFunc(Protocol[_ResponseT]):
    def __call__(
        self, context: Context
    ) -> (
        AsyncGenerator[
            _ResponseT | tuple[_ResponseT, list[type[OpenAIRealtimeTool] | Callable]],
            None,
        ]
        | Coroutine[
            Any,
            Any,
            _ResponseT | tuple[_ResponseT, list[type[OpenAIRealtimeTool] | Callable]],
        ]
        | Awaitable[
            _ResponseT | tuple[_ResponseT, list[type[OpenAIRealtimeTool] | Callable]]
        ]
    ): ...


class ReceiverFunc(Protocol[_ReceiverArgumentT]):
    def __call__(
        self, response: _ReceiverArgumentT, context: Context
    ) -> Awaitable[None]: ...


class FunctionCallHandlerFunc(Protocol):
    def __call__(
        self, tool: _OpenAIRealtimeToolT, context: Context
    ) -> Awaitable[str] | str: ...
