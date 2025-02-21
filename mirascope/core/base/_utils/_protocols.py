"""Protocols for reusable type hints."""

from collections.abc import (
    AsyncGenerator,
    AsyncIterable,
    Awaitable,
    Callable,
    Coroutine,
    Generator,
    Iterable,
)
from enum import Enum
from typing import (
    Any,
    Literal,
    NoReturn,
    ParamSpec,
    Protocol,
    TypeVar,
    overload,
)

from pydantic import BaseModel

from ..call_kwargs import BaseCallKwargs
from ..call_response import BaseCallResponse
from ..call_response_chunk import BaseCallResponseChunk
from ..messages import Messages
from ..stream_config import StreamConfig
from ..tool import BaseTool
from ._base_type import BaseType

_BaseCallResponseT = TypeVar(
    "_BaseCallResponseT", covariant=True, bound=BaseCallResponse
)
_BaseCallResponseChunkT = TypeVar(
    "_BaseCallResponseChunkT", covariant=True, bound=BaseCallResponseChunk
)
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


class AsyncCreateFn(Protocol[_ResponseT, _ResponseChunkT]):
    @overload
    def __call__(  # pyright: ignore[reportOverlappingOverload]
        self,
        *,
        stream: Literal[False] = False,
        **kwargs: Any,  # noqa: ANN401
    ) -> Awaitable[_ResponseT]: ...

    @overload
    def __call__(
        self,
        *,
        stream: Literal[True] | StreamConfig = True,
        **kwargs: Any,  # noqa: ANN401
    ) -> Awaitable[AsyncGenerator[_ResponseChunkT, None]]: ...

    def __call__(
        self, *, stream: bool | StreamConfig = False, **kwargs: Any
    ) -> Awaitable[
        _ResponseT | AsyncGenerator[_ResponseChunkT, None]
    ]: ...  # pragma: no cover


class CreateFn(Protocol[_ResponseT, _ResponseChunkT]):
    @overload
    def __call__(  # pyright: ignore[reportOverlappingOverload]
        self,
        *,
        stream: Literal[False] = False,
        **kwargs: Any,  # noqa: ANN401
    ) -> _ResponseT: ...

    @overload
    def __call__(
        self,
        *,
        stream: Literal[True] | StreamConfig = True,
        **kwargs: Any,  # noqa: ANN401
    ) -> Generator[_ResponseChunkT, None, None]: ...

    def __call__(
        self,
        *,
        stream: bool | StreamConfig = False,
        **kwargs: Any,  # noqa: F821
    ) -> _ResponseT | Generator[_ResponseChunkT, None, None]: ...


class SetupCall(
    Protocol[
        _SyncBaseClientT,
        _AsyncBaseClientT,
        _BaseDynamicConfigT,
        _AsyncBaseDynamicConfigT,
        _BaseCallParamsT,
        _ResponseT,
        _ResponseChunkT,
        _AsyncResponseT,
        _AsyncResponseChunkT,
        _BaseToolT,
    ]
):
    @overload
    def __call__(
        self,
        *,
        model: str,
        client: _AsyncBaseClientT | None,
        fn: Callable[..., Awaitable[_AsyncBaseDynamicConfigT]],
        fn_args: dict[str, Any],
        dynamic_config: _AsyncBaseDynamicConfigT,
        tools: list[type[BaseTool] | Callable] | None,
        json_mode: bool,
        call_params: _BaseCallParamsT,
        response_model: type[BaseModel] | None,
        stream: bool | StreamConfig,
    ) -> tuple[
        AsyncCreateFn[_AsyncResponseT, _AsyncResponseChunkT],
        str | None,
        list[Any],
        list[type[_BaseToolT]] | None,
        BaseCallKwargs,
    ]: ...

    @overload
    def __call__(
        self,
        *,
        model: str,
        client: _SyncBaseClientT | None,
        fn: Callable[..., _BaseDynamicConfigT],
        fn_args: dict[str, Any],
        dynamic_config: _BaseDynamicConfigT,
        tools: list[type[BaseTool] | Callable] | None,
        json_mode: bool,
        call_params: _BaseCallParamsT,
        response_model: type[BaseModel] | None,
        stream: bool | StreamConfig,
    ) -> tuple[
        CreateFn[_ResponseT, _ResponseChunkT],
        str | None,
        list[Any],
        list[type[_BaseToolT]] | None,
        BaseCallKwargs,
    ]: ...

    def __call__(
        self,
        *,
        model: str,
        client: _SyncBaseClientT | _AsyncBaseClientT | None,
        fn: Callable[..., _BaseDynamicConfigT | Awaitable[_AsyncBaseDynamicConfigT]],
        fn_args: dict[str, Any],
        dynamic_config: _BaseDynamicConfigT | _AsyncBaseDynamicConfigT,
        tools: list[type[BaseTool] | Callable] | None,
        json_mode: bool,
        call_params: _BaseCallParamsT,
        response_model: type[BaseModel] | None,
        stream: bool | StreamConfig,
    ) -> tuple[
        CreateFn[_ResponseT, _ResponseChunkT]
        | AsyncCreateFn[_AsyncResponseT, _AsyncResponseChunkT],
        str | None,
        list[Any],
        list[type[_BaseToolT]] | None,
        BaseCallKwargs,
    ]: ...  # pragma: no cover


class SameSyncAndAsyncClientSetupCall(
    Protocol[
        _SameSyncAndAsyncClientT,
        _BaseDynamicConfigT,
        _AsyncBaseDynamicConfigT,
        _BaseCallParamsT,
        _ResponseT,
        _ResponseChunkT,
        _AsyncResponseT,
        _AsyncResponseChunkT,
        _BaseToolT,
    ]
):
    @overload
    def __call__(
        self,
        *,
        model: str,
        client: _SameSyncAndAsyncClientT | None,
        fn: Callable[..., Awaitable[_AsyncBaseDynamicConfigT]],
        fn_args: dict[str, Any],
        dynamic_config: _AsyncBaseDynamicConfigT,
        tools: list[type[BaseTool] | Callable] | None,
        json_mode: bool,
        call_params: _BaseCallParamsT,
        response_model: type[BaseModel] | None,
        stream: bool | StreamConfig,
    ) -> tuple[
        AsyncCreateFn[_AsyncResponseT, _AsyncResponseChunkT],
        str | None,
        list[Any],
        list[type[_BaseToolT]] | None,
        BaseCallKwargs,
    ]: ...

    @overload
    def __call__(
        self,
        *,
        model: str,
        client: _SameSyncAndAsyncClientT | None,
        fn: Callable[..., _BaseDynamicConfigT],
        fn_args: dict[str, Any],
        dynamic_config: _BaseDynamicConfigT,
        tools: list[type[BaseTool] | Callable] | None,
        json_mode: bool,
        call_params: _BaseCallParamsT,
        response_model: type[BaseModel] | None,
        stream: bool | StreamConfig,
    ) -> tuple[
        CreateFn[_ResponseT, _ResponseChunkT],
        str | None,
        list[Any],
        list[type[_BaseToolT]] | None,
        BaseCallKwargs,
    ]: ...

    def __call__(
        self,
        *,
        model: str,
        client: _SameSyncAndAsyncClientT | None,
        fn: Callable[..., _BaseDynamicConfigT | Awaitable[_AsyncBaseDynamicConfigT]],
        fn_args: dict[str, Any],
        dynamic_config: _BaseDynamicConfigT | _AsyncBaseDynamicConfigT,
        tools: list[type[BaseTool] | Callable] | None,
        json_mode: bool,
        call_params: _BaseCallParamsT,
        response_model: type[BaseModel] | None,
        stream: bool | StreamConfig,
    ) -> tuple[
        CreateFn[_ResponseT, _ResponseChunkT]
        | AsyncCreateFn[_AsyncResponseT, _AsyncResponseChunkT],
        str | None,
        list[Any],
        list[type[_BaseToolT]] | None,
        BaseCallKwargs,
    ]: ...  # pragma: no cover


class HandleStream(
    Protocol[_InvariantResponseChunkT, _BaseCallResponseChunkT, _BaseToolT]
):
    def __call__(
        self,
        stream: Generator[_InvariantResponseChunkT, None, None],
        tool_types: list[type[_BaseToolT]] | None,
        partial_tools: bool = False,
    ) -> Generator[
        tuple[_BaseCallResponseChunkT, _BaseToolT | None], None, None
    ]: ...  # pragma: no cover


class HandleStreamAsync(
    Protocol[_InvariantResponseChunkT, _BaseCallResponseChunkT, _BaseToolT]
):
    def __call__(
        self,
        stream: AsyncGenerator[_InvariantResponseChunkT, None],
        tool_types: list[type[_BaseToolT]] | None,
        partial_tools: bool = False,
    ) -> AsyncGenerator[
        tuple[_BaseCallResponseChunkT, _BaseToolT | None], None
    ]: ...  # pragma: no cover


class GetJsonOutput(Protocol[_R]):
    def __call__(self, response: _R, json_mode: bool) -> str: ...  # pragma: no cover


class CalculateCost(Protocol):
    def __call__(
        self,
        input_tokens: int | float | None,
        cached_tokens: int | float | None,
        output_tokens: int | float | None,
        model: str,
    ) -> float | None: ...  # pragma: no cover


class CallDecorator(
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
        model: str,
        *,
        stream: Literal[False] = False,
        tools: None = None,
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
        model: str,
        *,
        stream: Literal[False] = False,
        tools: None = None,
        response_model: type[_ResponseModelT],
        output_parser: None = None,
        json_mode: bool = False,
        client: _AsyncBaseClientT = ...,
        call_params: _BaseCallParamsT | None = None,
    ) -> AsyncLLMFunctionDecorator[_AsyncBaseDynamicConfigT, _ResponseModelT]: ...

    @overload
    def __call__(
        self,
        model: str,
        *,
        stream: Literal[False] = False,
        tools: None = None,
        response_model: type[_ResponseModelT],
        output_parser: None = None,
        json_mode: bool = False,
        client: _SyncBaseClientT = ...,
        call_params: _BaseCallParamsT | None = None,
    ) -> SyncLLMFunctionDecorator[_BaseDynamicConfigT, _ResponseModelT]: ...

    @overload
    def __call__(
        self,
        model: str,
        *,
        stream: Literal[False] = False,
        tools: None = None,
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
        model: str,
        *,
        stream: Literal[False] = False,
        tools: None = None,
        response_model: type[_ResponseModelT],
        output_parser: Callable[[_ResponseModelT], _ParsedOutputT],
        json_mode: bool = False,
        client: _AsyncBaseClientT = ...,
        call_params: _BaseCallParamsT | None = None,
    ) -> AsyncLLMFunctionDecorator[_AsyncBaseDynamicConfigT, _ParsedOutputT]: ...

    @overload
    def __call__(
        self,
        model: str,
        *,
        stream: Literal[False] = False,
        tools: None = None,
        response_model: type[_ResponseModelT],
        output_parser: Callable[[_ResponseModelT], _ParsedOutputT],
        json_mode: bool = False,
        client: _SyncBaseClientT = ...,
        call_params: _BaseCallParamsT | None = None,
    ) -> SyncLLMFunctionDecorator[_BaseDynamicConfigT, _ParsedOutputT]: ...

    @overload
    def __call__(  # pyright: ignore[reportOverlappingOverload]
        self,
        model: str,
        *,
        stream: Literal[False] = False,
        tools: list[type[BaseTool] | Callable],
        response_model: type[_ResponseModelT],
        output_parser: None = None,
        json_mode: bool = False,
        client: _SameSyncAndAsyncClientT | None = None,
        call_params: _BaseCallParamsT | None = None,
    ) -> LLMFunctionDecorator[
        _BaseDynamicConfigT,
        _AsyncBaseDynamicConfigT,
        _ResponseModelT | _BaseCallResponseT,
        _ResponseModelT | _BaseCallResponseT,
    ]: ...

    @overload
    def __call__(
        self,
        model: str,
        *,
        stream: Literal[False] = False,
        tools: list[type[BaseTool] | Callable],
        response_model: type[_ResponseModelT],
        output_parser: None = None,
        json_mode: bool = False,
        client: _SyncBaseClientT = ...,
        call_params: _BaseCallParamsT | None = None,
    ) -> SyncLLMFunctionDecorator[
        _BaseDynamicConfigT,
        _ResponseModelT | _BaseCallResponseT,
    ]: ...

    @overload
    def __call__(
        self,
        model: str,
        *,
        stream: Literal[False] = False,
        tools: list[type[BaseTool] | Callable],
        response_model: type[_ResponseModelT],
        output_parser: None = None,
        json_mode: bool = False,
        client: _AsyncBaseClientT = ...,
        call_params: _BaseCallParamsT | None = None,
    ) -> AsyncLLMFunctionDecorator[
        _AsyncBaseDynamicConfigT,
        _ResponseModelT | _BaseCallResponseT,
    ]: ...

    ####

    @overload
    def __call__(
        self,
        model: str,
        *,
        stream: Literal[False] = False,
        tools: list[type[BaseTool] | Callable],
        response_model: type[_ResponseModelT],
        output_parser: Callable[[_ResponseModelT], _ParsedOutputT],
        json_mode: bool = False,
        client: _SameSyncAndAsyncClientT | None = None,
        call_params: _BaseCallParamsT | None = None,
    ) -> LLMFunctionDecorator[
        _BaseDynamicConfigT,
        _AsyncBaseDynamicConfigT,
        _ParsedOutputT | _BaseCallResponseT,
        _ParsedOutputT | _BaseCallResponseT,
    ]: ...

    @overload
    def __call__(
        self,
        model: str,
        *,
        stream: Literal[False] = False,
        tools: list[type[BaseTool] | Callable],
        response_model: type[_ResponseModelT],
        output_parser: Callable[[_ResponseModelT], _ParsedOutputT],
        json_mode: bool = False,
        client: _SyncBaseClientT = ...,
        call_params: _BaseCallParamsT | None = None,
    ) -> SyncLLMFunctionDecorator[
        _BaseDynamicConfigT,
        _ParsedOutputT | _BaseCallResponseT,
    ]: ...

    @overload
    def __call__(
        self,
        model: str,
        *,
        stream: Literal[False] = False,
        tools: list[type[BaseTool] | Callable],
        response_model: type[_ResponseModelT],
        output_parser: Callable[[_ResponseModelT], _ParsedOutputT],
        json_mode: bool = False,
        client: _AsyncBaseClientT = ...,
        call_params: _BaseCallParamsT | None = None,
    ) -> AsyncLLMFunctionDecorator[
        _AsyncBaseDynamicConfigT,
        _ParsedOutputT | _BaseCallResponseT,
    ]: ...

    ####

    @overload
    def __call__(  # pyright: ignore[reportOverlappingOverload]
        self,
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
            | (_ResponseModelT | _BaseCallResponseT)
            | AsyncIterable[_ResponseModelT],
        ]
        | SyncLLMFunctionDecorator[
            _BaseDynamicConfigT,
            _BaseCallResponseT
            | _ParsedOutputT
            | _BaseStreamT
            | _ResponseModelT
            | (_ResponseModelT | _BaseCallResponseT)
            | (_ParsedOutputT | _BaseCallResponseT)
            | Iterable[_ResponseModelT],
        ]
        | LLMFunctionDecorator[
            _BaseDynamicConfigT,
            _AsyncBaseDynamicConfigT,
            _BaseCallResponseT
            | _ParsedOutputT
            | _BaseStreamT
            | _ResponseModelT
            | (_ResponseModelT | _BaseCallResponseT)
            | (_ParsedOutputT | _BaseCallResponseT)
            | Iterable[_ResponseModelT],
            _BaseCallResponseT
            | _ParsedOutputT
            | _BaseStreamT
            | _ResponseModelT
            | (_ResponseModelT | _BaseCallResponseT)
            | (_ParsedOutputT | _BaseCallResponseT)
            | AsyncIterable[_ResponseModelT],
        ]
    ): ...
