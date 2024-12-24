"""Protocols for reusable type hints."""

from collections.abc import (
    Awaitable,
    Callable,
    Coroutine,
)
from enum import Enum
from typing import (
    Any,
    Literal,
    ParamSpec,
    Protocol,
    TypeAlias,
    TypeVar,
    overload,
)

from pydantic import BaseModel

from mirascope.core import BaseTool, Messages
from mirascope.core.base import BaseType

_BaseStreamT = TypeVar("_BaseStreamT", covariant=True)
_ResponseModelT = TypeVar("_ResponseModelT", bound=BaseModel | BaseType | Enum)
_SameSyncAndAsyncClientT = TypeVar("_SameSyncAndAsyncClientT", contravariant=True)
_SyncBaseClientT = TypeVar("_SyncBaseClientT", contravariant=True)
_AsyncBaseClientT = TypeVar("_AsyncBaseClientT", contravariant=True)
_BaseCallParamsT = TypeVar("_BaseCallParamsT", contravariant=True)
_AsyncBaseDynamicConfigT = TypeVar("_AsyncBaseDynamicConfigT", contravariant=True)
_BaseDynamicConfigT = TypeVar("_BaseDynamicConfigT", contravariant=True)
_ResponseT = TypeVar("_ResponseT", covariant=True)
_AsyncResponseT = TypeVar("_AsyncResponseT", covariant=True)
_ResponseChunkT = TypeVar("_ResponseChunkT", covariant=True)
_AsyncResponseChunkT = TypeVar("_AsyncResponseChunkT", covariant=True)
_InvariantResponseChunkT = TypeVar("_InvariantResponseChunkT", contravariant=True)
_BaseToolT = TypeVar("_BaseToolT", bound=BaseTool)
_ParsedOutputT = TypeVar("_ParsedOutputT")
_P = ParamSpec("_P")
_R = TypeVar("_R", contravariant=True)


class AsyncLLMFunctionDecorator(Protocol[_AsyncBaseDynamicConfigT, _AsyncResponseT]):
    @overload
    def __call__(
        self,
        fn: Callable[
            _P,
            Awaitable[_AsyncBaseDynamicConfigT]
            | Coroutine[Any, Any, _AsyncBaseDynamicConfigT],
        ],
    ) -> Callable[_P, Awaitable[_AsyncResponseT]]: ...

    @overload
    def __call__(
        self,
        fn: Callable[_P, Awaitable[Messages.Type] | Coroutine[Any, Any, Messages.Type]],
    ) -> Callable[_P, Awaitable[_AsyncResponseT]]: ...

    def __call__(
        self,
        fn: Callable[
            _P,
            Awaitable[_AsyncBaseDynamicConfigT]
            | Coroutine[Any, Any, _AsyncBaseDynamicConfigT],
        ]
        | Callable[_P, Awaitable[Messages.Type] | Coroutine[Any, Any, Messages.Type]],
    ) -> Callable[_P, Awaitable[_AsyncResponseT]]: ...  # pragma: no cover


class SyncLLMFunctionDecorator(Protocol[_BaseDynamicConfigT, _ResponseT]):
    @overload
    def __call__(
        self, fn: Callable[_P, _BaseDynamicConfigT]
    ) -> Callable[_P, _ResponseT]: ...

    @overload
    def __call__(self, fn: Callable[_P, Messages.Type]) -> Callable[_P, _ResponseT]: ...

    def __call__(
        self, fn: Callable[_P, _BaseDynamicConfigT] | Callable[_P, Messages.Type]
    ) -> Callable[_P, _ResponseT]: ...  # pragma: no cover


class LLMFunctionDecorator(
    Protocol[_BaseDynamicConfigT, _AsyncBaseDynamicConfigT, _ResponseT, _AsyncResponseT]
):
    @overload
    def __call__(
        self, fn: Callable[_P, _BaseDynamicConfigT]
    ) -> Callable[_P, _ResponseT]: ...

    @overload
    def __call__(self, fn: Callable[_P, Messages.Type]) -> Callable[_P, _ResponseT]: ...

    @overload
    def __call__(
        self, fn: Callable[_P, Awaitable[_AsyncBaseDynamicConfigT]]
    ) -> Callable[_P, Awaitable[_AsyncResponseT]]: ...

    @overload
    def __call__(
        self, fn: Callable[_P, Awaitable[Messages.Type]]
    ) -> Callable[_P, Awaitable[_AsyncResponseT]]: ...

    def __call__(
        self,
        fn: Callable[_P, _BaseDynamicConfigT]
        | Callable[_P, Awaitable[_AsyncBaseDynamicConfigT]]
        | Callable[_P, Messages.Type]
        | Callable[_P, Awaitable[Messages.Type]],
    ) -> Callable[_P, _ResponseT | Awaitable[_AsyncResponseT]]: ...  # pragma: no cover


Provider: TypeAlias = Literal[
    "anthropic",
    "azure",
    "bedrock",
    "cohere",
    "gemini",
    "groq",
    "litellm",
    "mistral",
    "openai",
    "vertex",
]

_ProviderT = TypeVar("_ProviderT", bound=Provider)
