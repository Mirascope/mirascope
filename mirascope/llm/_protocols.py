"""Protocols for reusable type hints."""

from collections.abc import (
    AsyncIterable,
    Callable,
    Iterable,
)
from enum import Enum
from typing import (
    Any,
    Literal,
    NoReturn,
    ParamSpec,
    Protocol,
    TypeAlias,
    TypeVar,
    overload,
)

from pydantic import BaseModel

from ..core import BaseDynamicConfig, BaseTool
from ..core.base import (
    BaseCallResponse,
    BaseCallResponseChunk,
    BaseType,
    CommonCallParams,
)
from ..core.base._utils._protocols import (
    AsyncLLMFunctionDecorator,
    LLMFunctionDecorator,
    SyncLLMFunctionDecorator,
)
from ..core.base.stream_config import StreamConfig
from ..core.base.types import LocalProvider, Provider
from .call_response import CallResponse
from .call_response_chunk import CallResponseChunk
from .stream import Stream

_P = ParamSpec("_P")
_R = TypeVar("_R", contravariant=True)

_BaseStreamT = TypeVar("_BaseStreamT", covariant=True)
_ResponseModelT = TypeVar("_ResponseModelT", bound=BaseModel | BaseType | Enum)
_SameSyncAndAsyncClientT = TypeVar("_SameSyncAndAsyncClientT", contravariant=True)
_SyncBaseClientT = TypeVar("_SyncBaseClientT", contravariant=True)
_AsyncBaseClientT = TypeVar("_AsyncBaseClientT", contravariant=True)
_BaseCallParamsT = TypeVar("_BaseCallParamsT", contravariant=True)
_AsyncBaseDynamicConfigT = TypeVar("_AsyncBaseDynamicConfigT", contravariant=True)
_BaseDynamicConfigT = TypeVar("_BaseDynamicConfigT", contravariant=True)
_ParsedOutputT = TypeVar("_ParsedOutputT")
_BaseCallResponseT = TypeVar(
    "_BaseCallResponseT", bound=BaseCallResponse, covariant=True
)
_BaseCallResponseChunkT = TypeVar(
    "_BaseCallResponseChunkT", bound=BaseCallResponseChunk, covariant=True
)


class _CallDecorator(
    Protocol[
        _BaseCallResponseT,
        _BaseCallResponseChunkT,
        _BaseDynamicConfigT,
        _AsyncBaseDynamicConfigT,
        _BaseCallParamsT,
        _BaseStreamT,
        _SyncBaseClientT,
        _AsyncBaseClientT,
        _SameSyncAndAsyncClientT,
    ],
):
    @overload
    def __call__(  # pyright: ignore[reportOverlappingOverload]
        self,
        provider: Provider | LocalProvider,
        model: str,
        *,
        stream: Literal[False] = False,
        tools: list[type[BaseTool] | Callable] | None = None,
        response_model: None = None,
        output_parser: None = None,
        json_mode: bool = False,
        client: _SameSyncAndAsyncClientT | None = None,
        call_params: _BaseCallParamsT | None = None,
    ) -> LLMFunctionDecorator[
        _BaseDynamicConfigT,
        _AsyncBaseDynamicConfigT,
        _BaseCallResponseT,
        _BaseCallResponseT,
    ]: ...

    @overload
    def __call__(  # pyright: ignore[reportOverlappingOverload]
        self,
        provider: Provider | LocalProvider,
        model: str,
        *,
        stream: Literal[False] = False,
        tools: list[type[BaseTool] | Callable] | None = None,
        response_model: None = None,
        output_parser: None = None,
        json_mode: bool = False,
        client: _AsyncBaseClientT = ...,
        call_params: _BaseCallParamsT | None = None,
    ) -> AsyncLLMFunctionDecorator[_AsyncBaseDynamicConfigT, _BaseCallResponseT]: ...

    @overload
    def __call__(
        self,
        provider: Provider | LocalProvider,
        model: str,
        *,
        stream: Literal[False] = False,
        tools: list[type[BaseTool] | Callable] | None = None,
        response_model: None = None,
        output_parser: None = None,
        json_mode: bool = False,
        client: _SyncBaseClientT = ...,
        call_params: _BaseCallParamsT | None = None,
    ) -> SyncLLMFunctionDecorator[_BaseDynamicConfigT, _BaseCallResponseT]: ...

    @overload
    def __call__(  # pyright: ignore[reportOverlappingOverload]
        self,
        provider: Provider | LocalProvider,
        model: str,
        *,
        stream: Literal[False] = False,
        tools: list[type[BaseTool] | Callable] | None = None,
        response_model: None = None,
        output_parser: Callable[[_BaseCallResponseT], _ParsedOutputT],
        json_mode: bool = False,
        client: _SameSyncAndAsyncClientT | None = None,
        call_params: _BaseCallParamsT | None = None,
    ) -> LLMFunctionDecorator[
        _BaseDynamicConfigT, _AsyncBaseDynamicConfigT, _ParsedOutputT, _ParsedOutputT
    ]: ...

    @overload
    def __call__(
        self,
        provider: Provider | LocalProvider,
        model: str,
        *,
        stream: Literal[False] = False,
        tools: list[type[BaseTool] | Callable] | None = None,
        response_model: None = None,
        output_parser: Callable[[_BaseCallResponseT], _ParsedOutputT],
        json_mode: bool = False,
        client: _AsyncBaseClientT = ...,
        call_params: _BaseCallParamsT | None = None,
    ) -> AsyncLLMFunctionDecorator[_AsyncBaseDynamicConfigT, _ParsedOutputT]: ...

    @overload
    def __call__(
        self,
        provider: Provider | LocalProvider,
        model: str,
        *,
        stream: Literal[False] = False,
        tools: list[type[BaseTool] | Callable] | None = None,
        response_model: None = None,
        output_parser: Callable[[_BaseCallResponseT], _ParsedOutputT],
        json_mode: bool = False,
        client: _SyncBaseClientT = ...,
        call_params: _BaseCallParamsT | None = None,
    ) -> SyncLLMFunctionDecorator[_BaseDynamicConfigT, _ParsedOutputT]: ...

    @overload
    def __call__(
        self,
        provider: Provider | LocalProvider,
        model: str,
        *,
        stream: Literal[False] = False,
        tools: list[type[BaseTool] | Callable] | None = None,
        response_model: None = None,
        output_parser: Callable[[_BaseCallResponseChunkT], _ParsedOutputT],
        json_mode: bool = False,
        client: _SameSyncAndAsyncClientT
        | _SyncBaseClientT
        | _AsyncBaseClientT
        | None = None,
        call_params: _BaseCallParamsT | None = None,
    ) -> NoReturn: ...

    @overload
    def __call__(
        self,
        provider: Provider | LocalProvider,
        model: str,
        *,
        stream: Literal[True] | StreamConfig = True,
        tools: list[type[BaseTool] | Callable] | None = None,
        response_model: None = None,
        output_parser: None = None,
        json_mode: bool = False,
        client: _SameSyncAndAsyncClientT | None = None,
        call_params: _BaseCallParamsT | None = None,
    ) -> LLMFunctionDecorator[
        _BaseDynamicConfigT, _AsyncBaseDynamicConfigT, _BaseStreamT, _BaseStreamT
    ]: ...

    @overload
    def __call__(
        self,
        provider: Provider | LocalProvider,
        model: str,
        *,
        stream: Literal[True] | StreamConfig = True,
        tools: list[type[BaseTool] | Callable] | None = None,
        response_model: None = None,
        output_parser: None = None,
        json_mode: bool = False,
        client: _AsyncBaseClientT = ...,
        call_params: _BaseCallParamsT | None = None,
    ) -> AsyncLLMFunctionDecorator[_AsyncBaseDynamicConfigT, _BaseStreamT]: ...

    @overload
    def __call__(
        self,
        provider: Provider | LocalProvider,
        model: str,
        *,
        stream: Literal[True] | StreamConfig = True,
        tools: list[type[BaseTool] | Callable] | None = None,
        response_model: None = None,
        output_parser: None = None,
        json_mode: bool = False,
        client: _SyncBaseClientT = ...,
        call_params: _BaseCallParamsT | None = None,
    ) -> SyncLLMFunctionDecorator[_BaseDynamicConfigT, _BaseStreamT]: ...

    @overload
    def __call__(
        self,
        provider: Provider | LocalProvider,
        model: str,
        *,
        stream: Literal[True] | StreamConfig = True,
        tools: list[type[BaseTool] | Callable] | None = None,
        response_model: None = None,
        output_parser: Callable[[_BaseCallResponseChunkT], _ParsedOutputT],
        json_mode: bool = False,
        client: _SameSyncAndAsyncClientT
        | _SyncBaseClientT
        | _AsyncBaseClientT
        | None = None,
        call_params: _BaseCallParamsT | None = None,
    ) -> NoReturn: ...

    @overload
    def __call__(
        self,
        provider: Provider | LocalProvider,
        model: str,
        *,
        stream: Literal[True] | StreamConfig = True,
        tools: list[type[BaseTool] | Callable] | None = None,
        response_model: None = None,
        output_parser: Callable[[_BaseCallResponseT], _ParsedOutputT],
        json_mode: bool = False,
        client: _SameSyncAndAsyncClientT
        | _SyncBaseClientT
        | _AsyncBaseClientT
        | None = None,
        call_params: _BaseCallParamsT | None = None,
    ) -> NoReturn: ...

    @overload
    def __call__(  # pyright: ignore[reportOverlappingOverload]
        self,
        provider: Provider | LocalProvider,
        model: str,
        *,
        stream: Literal[False] = False,
        tools: list[type[BaseTool] | Callable] | None = None,
        response_model: type[_ResponseModelT],
        output_parser: None = None,
        json_mode: bool = False,
        client: _SameSyncAndAsyncClientT | None = None,
        call_params: _BaseCallParamsT | None = None,
    ) -> LLMFunctionDecorator[
        _BaseDynamicConfigT, _AsyncBaseDynamicConfigT, _ResponseModelT, _ResponseModelT
    ]: ...

    @overload
    def __call__(
        self,
        provider: Provider | LocalProvider,
        model: str,
        *,
        stream: Literal[False] = False,
        tools: list[type[BaseTool] | Callable] | None = None,
        response_model: type[_ResponseModelT],
        output_parser: None = None,
        json_mode: bool = False,
        client: _AsyncBaseClientT = ...,
        call_params: _BaseCallParamsT | None = None,
    ) -> AsyncLLMFunctionDecorator[_AsyncBaseDynamicConfigT, _ResponseModelT]: ...

    @overload
    def __call__(
        self,
        provider: Provider | LocalProvider,
        model: str,
        *,
        stream: Literal[False] = False,
        tools: list[type[BaseTool] | Callable] | None = None,
        response_model: type[_ResponseModelT],
        output_parser: None = None,
        json_mode: bool = False,
        client: _SyncBaseClientT = ...,
        call_params: _BaseCallParamsT | None = None,
    ) -> SyncLLMFunctionDecorator[_BaseDynamicConfigT, _ResponseModelT]: ...

    @overload
    def __call__(
        self,
        provider: Provider | LocalProvider,
        model: str,
        *,
        stream: Literal[False] = False,
        tools: list[type[BaseTool] | Callable] | None = None,
        response_model: type[_ResponseModelT],
        output_parser: Callable[[_ResponseModelT], _ParsedOutputT],
        json_mode: bool = False,
        client: _SameSyncAndAsyncClientT | None = None,
        call_params: _BaseCallParamsT | None = None,
    ) -> LLMFunctionDecorator[
        _BaseDynamicConfigT, _AsyncBaseDynamicConfigT, _ParsedOutputT, _ParsedOutputT
    ]: ...

    @overload
    def __call__(
        self,
        provider: Provider | LocalProvider,
        model: str,
        *,
        stream: Literal[False] = False,
        tools: list[type[BaseTool] | Callable] | None = None,
        response_model: type[_ResponseModelT],
        output_parser: Callable[[_ResponseModelT], _ParsedOutputT],
        json_mode: bool = False,
        client: _AsyncBaseClientT = ...,
        call_params: _BaseCallParamsT | None = None,
    ) -> AsyncLLMFunctionDecorator[_AsyncBaseDynamicConfigT, _ParsedOutputT]: ...

    @overload
    def __call__(
        self,
        provider: Provider | LocalProvider,
        model: str,
        *,
        stream: Literal[False] = False,
        tools: list[type[BaseTool] | Callable] | None = None,
        response_model: type[_ResponseModelT],
        output_parser: Callable[[_ResponseModelT], _ParsedOutputT],
        json_mode: bool = False,
        client: _SyncBaseClientT = ...,
        call_params: _BaseCallParamsT | None = None,
    ) -> SyncLLMFunctionDecorator[_BaseDynamicConfigT, _ParsedOutputT]: ...

    @overload
    def __call__(  # pyright: ignore[reportOverlappingOverload]
        self,
        provider: Provider | LocalProvider,
        model: str,
        *,
        stream: Literal[True] | StreamConfig,
        tools: list[type[BaseTool] | Callable] | None = None,
        response_model: type[_ResponseModelT],
        output_parser: None = None,
        json_mode: bool = False,
        client: _SameSyncAndAsyncClientT | None = None,
        call_params: _BaseCallParamsT | None = None,
    ) -> LLMFunctionDecorator[
        _BaseDynamicConfigT,
        _AsyncBaseDynamicConfigT,
        Iterable[_ResponseModelT],
        AsyncIterable[_ResponseModelT],
    ]: ...

    @overload
    def __call__(
        self,
        provider: Provider | LocalProvider,
        model: str,
        *,
        stream: Literal[True] | StreamConfig,
        tools: list[type[BaseTool] | Callable] | None = None,
        response_model: type[_ResponseModelT],
        output_parser: None = None,
        json_mode: bool = False,
        client: _AsyncBaseClientT = ...,
        call_params: _BaseCallParamsT | None = None,
    ) -> AsyncLLMFunctionDecorator[
        _AsyncBaseDynamicConfigT, AsyncIterable[_ResponseModelT]
    ]: ...

    @overload
    def __call__(
        self,
        provider: Provider | LocalProvider,
        model: str,
        *,
        stream: Literal[True] | StreamConfig,
        tools: list[type[BaseTool] | Callable] | None = None,
        response_model: type[_ResponseModelT],
        output_parser: None = None,
        json_mode: bool = False,
        client: _SyncBaseClientT = ...,
        call_params: _BaseCallParamsT | None = None,
    ) -> SyncLLMFunctionDecorator[_BaseDynamicConfigT, Iterable[_ResponseModelT]]: ...

    @overload
    def __call__(
        self,
        provider: Provider | LocalProvider,
        model: str,
        *,
        stream: Literal[True] | StreamConfig,
        tools: list[type[BaseTool] | Callable] | None = None,
        response_model: type[_ResponseModelT],
        output_parser: Callable[[_BaseCallResponseT], _ParsedOutputT]
        | Callable[[_BaseCallResponseChunkT], _ParsedOutputT]
        | Callable[[_ResponseModelT], _ParsedOutputT]
        | None,
        json_mode: bool = False,
        client: _SameSyncAndAsyncClientT
        | _AsyncBaseClientT
        | _SyncBaseClientT
        | None = None,
        call_params: _BaseCallParamsT | None = None,
    ) -> NoReturn: ...

    def __call__(
        self,
        provider: Provider | LocalProvider,
        model: str,
        *,
        stream: bool | StreamConfig = False,
        tools: list[type[BaseTool] | Callable] | None = None,
        response_model: type[_ResponseModelT] | None = None,
        output_parser: Callable[[_BaseCallResponseT], _ParsedOutputT]
        | Callable[[_BaseCallResponseChunkT], _ParsedOutputT]
        | Callable[[_ResponseModelT], _ParsedOutputT]
        | None = None,
        json_mode: bool = False,
        client: _SameSyncAndAsyncClientT
        | _AsyncBaseClientT
        | _SyncBaseClientT
        | None = None,
        call_params: _BaseCallParamsT | None = None,
    ) -> (
        AsyncLLMFunctionDecorator[
            _AsyncBaseDynamicConfigT,
            _BaseCallResponseT
            | _ParsedOutputT
            | _BaseStreamT
            | _ResponseModelT
            | AsyncIterable[_ResponseModelT],
        ]
        | SyncLLMFunctionDecorator[
            _BaseDynamicConfigT,
            _BaseCallResponseT
            | _ParsedOutputT
            | _BaseStreamT
            | _ResponseModelT
            | Iterable[_ResponseModelT],
        ]
        | LLMFunctionDecorator[
            _BaseDynamicConfigT,
            _AsyncBaseDynamicConfigT,
            _BaseCallResponseT
            | _ParsedOutputT
            | _BaseStreamT
            | _ResponseModelT
            | Iterable[_ResponseModelT],
            _BaseCallResponseT
            | _ParsedOutputT
            | _BaseStreamT
            | _ResponseModelT
            | AsyncIterable[_ResponseModelT],
        ]
    ): ...


CallDecorator: TypeAlias = _CallDecorator[
    CallResponse,
    CallResponseChunk,
    BaseDynamicConfig,
    BaseDynamicConfig,
    CommonCallParams,
    Stream,
    Any,
    Any,
    Any,
]
