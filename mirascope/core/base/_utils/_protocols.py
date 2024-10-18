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
    Annotated,
    Any,
    Generic,
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
from ..tool import BaseTool
from ._base_type import BaseType

_BaseCallResponseT = TypeVar(
    "_BaseCallResponseT", covariant=True, bound=BaseCallResponse
)
_BaseCallResponseChunkT = TypeVar(
    "_BaseCallResponseChunkT", covariant=True, bound=BaseCallResponseChunk
)
_BaseStreamT = TypeVar("_BaseStreamT", covariant=True)
_ResponseModelT = TypeVar(
    "_ResponseModelT", bound=BaseModel | BaseType | Enum | Annotated
)
_SameSyncAndAsyncClientT = TypeVar("_SameSyncAndAsyncClientT", contravariant=True)
_SyncBaseClientT = TypeVar("_SyncBaseClientT", contravariant=True)
_AsyncBaseClientT = TypeVar("_AsyncBaseClientT", contravariant=True)
_BaseCallParamsT = TypeVar("_BaseCallParamsT", contravariant=True)
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


class AsyncLLMFunctionDecorator(Protocol[_BaseDynamicConfigT, _AsyncResponseT]):
    @overload
    def __call__(
        self,
        fn: Callable[
            _P,
            Awaitable[_BaseDynamicConfigT] | Coroutine[Any, Any, _BaseDynamicConfigT],
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
            Awaitable[_BaseDynamicConfigT] | Coroutine[Any, Any, _BaseDynamicConfigT],
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


class LLMFunctionDecorator(Protocol[_BaseDynamicConfigT, _ResponseT, _AsyncResponseT]):
    @overload
    def __call__(
        self, fn: Callable[_P, _BaseDynamicConfigT]
    ) -> Callable[_P, _ResponseT]: ...

    @overload
    def __call__(self, fn: Callable[_P, Messages.Type]) -> Callable[_P, _ResponseT]: ...

    @overload
    def __call__(
        self, fn: Callable[_P, Awaitable[_BaseDynamicConfigT]]
    ) -> Callable[_P, Awaitable[_AsyncResponseT]]: ...

    @overload
    def __call__(
        self, fn: Callable[_P, Awaitable[Messages.Type]]
    ) -> Callable[_P, Awaitable[_AsyncResponseT]]: ...

    def __call__(
        self,
        fn: Callable[_P, _BaseDynamicConfigT]
        | Callable[_P, Awaitable[_BaseDynamicConfigT]]
        | Callable[_P, Messages.Type]
        | Callable[_P, Awaitable[Messages.Type]],
    ) -> Callable[_P, _ResponseT | Awaitable[_AsyncResponseT]]: ...  # pragma: no cover


class AsyncCreateFn(Protocol[_ResponseT, _ResponseChunkT]):
    @overload
    def __call__(
        self,
        *,
        stream: Literal[False] = False,
        **kwargs: Any,  # noqa: ANN401
    ) -> Awaitable[_ResponseT]: ...

    @overload
    def __call__(
        self,
        *,
        stream: Literal[True] = True,
        **kwargs: Any,  # noqa: ANN401
    ) -> Awaitable[AsyncGenerator[_ResponseChunkT, None]]: ...

    def __call__(
        self, *, stream: bool = False, **kwargs: Any
    ) -> Awaitable[
        _ResponseT | AsyncGenerator[_ResponseChunkT, None]
    ]: ...  # pragma: no cover


class CreateFn(Protocol[_ResponseT, _ResponseChunkT]):
    @overload
    def __call__(
        self,
        *,
        stream: Literal[False] = False,
        **kwargs: Any,  # noqa: ANN401
    ) -> _ResponseT: ...

    @overload
    def __call__(
        self,
        *,
        stream: Literal[True] = True,
        **kwargs: Any,  # noqa: ANN401
    ) -> Generator[_ResponseChunkT, None, None]: ...

    def __call__(
        self, *, stream: bool = False, **kwargs: Any
    ) -> _ResponseT | Generator[_ResponseChunkT, None, None]: ...


class SetupCall(
    Protocol[
        _SyncBaseClientT,
        _AsyncBaseClientT,
        _BaseDynamicConfigT,
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
        fn: Callable[..., Awaitable[_BaseDynamicConfigT]],
        fn_args: dict[str, Any],
        dynamic_config: _BaseDynamicConfigT,
        tools: list[type[BaseTool] | Callable] | None,
        json_mode: bool,
        call_params: _BaseCallParamsT,
        extract: bool,
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
        extract: bool,
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
        fn: Callable[..., _BaseDynamicConfigT | Awaitable[_BaseDynamicConfigT]],
        fn_args: dict[str, Any],
        dynamic_config: _BaseDynamicConfigT,
        tools: list[type[BaseTool] | Callable] | None,
        json_mode: bool,
        call_params: _BaseCallParamsT,
        extract: bool,
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
        fn: Callable[..., Awaitable[_BaseDynamicConfigT]],
        fn_args: dict[str, Any],
        dynamic_config: _BaseDynamicConfigT,
        tools: list[type[BaseTool] | Callable] | None,
        json_mode: bool,
        call_params: _BaseCallParamsT,
        extract: bool,
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
        extract: bool,
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
        fn: Callable[..., _BaseDynamicConfigT | Awaitable[_BaseDynamicConfigT]],
        fn_args: dict[str, Any],
        dynamic_config: _BaseDynamicConfigT,
        tools: list[type[BaseTool] | Callable] | None,
        json_mode: bool,
        call_params: _BaseCallParamsT,
        extract: bool,
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
    ) -> AsyncGenerator[
        tuple[_BaseCallResponseChunkT, _BaseToolT | None], None
    ]: ...  # pragma: no cover


class GetJsonOutput(Protocol[_R]):
    def __call__(self, response: _R, json_mode: bool) -> str: ...  # pragma: no cover


class CalculateCost(Protocol):
    def __call__(
        self,
        input_tokens: int | float | None,
        output_tokens: int | float | None,
        model: str,
    ) -> float | None: ...  # pragma: no cover


class CallDecorator(
    Protocol,
    Generic[
        _BaseCallResponseT,
        _BaseCallResponseChunkT,
        _BaseDynamicConfigT,
        _BaseCallParamsT,
        _BaseStreamT,
        _SyncBaseClientT,
        _AsyncBaseClientT,
        _SameSyncAndAsyncClientT,
    ],
):
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
        client: _SameSyncAndAsyncClientT | None = None,
        call_params: _BaseCallParamsT | None = None,
    ) -> LLMFunctionDecorator[
        _BaseDynamicConfigT, _BaseCallResponseT, _BaseCallResponseT
    ]: ...

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
        client: _AsyncBaseClientT = ...,
        call_params: _BaseCallParamsT | None = None,
    ) -> AsyncLLMFunctionDecorator[_BaseDynamicConfigT, _BaseCallResponseT]: ...

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
    def __call__(
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
    ) -> LLMFunctionDecorator[_BaseDynamicConfigT, _ParsedOutputT, _ParsedOutputT]: ...

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
    ) -> AsyncLLMFunctionDecorator[_BaseDynamicConfigT, _ParsedOutputT]: ...

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
        stream: Literal[True] = True,
        tools: list[type[BaseTool] | Callable] | None = None,
        response_model: None = None,
        output_parser: None = None,
        json_mode: bool = False,
        client: _SameSyncAndAsyncClientT | None = None,
        call_params: _BaseCallParamsT | None = None,
    ) -> LLMFunctionDecorator[_BaseDynamicConfigT, _BaseStreamT, _BaseStreamT]: ...

    @overload
    def __call__(
        self,
        model: str,
        *,
        stream: Literal[True] = True,
        tools: list[type[BaseTool] | Callable] | None = None,
        response_model: None = None,
        output_parser: None = None,
        json_mode: bool = False,
        client: _AsyncBaseClientT = ...,
        call_params: _BaseCallParamsT | None = None,
    ) -> AsyncLLMFunctionDecorator[_BaseDynamicConfigT, _BaseStreamT]: ...

    @overload
    def __call__(
        self,
        model: str,
        *,
        stream: Literal[True] = True,
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
        stream: Literal[True] = True,
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
        stream: Literal[True] = True,
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
    def __call__(
        self,
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
        _BaseDynamicConfigT, _ResponseModelT, _ResponseModelT
    ]: ...

    @overload
    def __call__(
        self,
        model: str,
        *,
        stream: Literal[False] = False,
        tools: list[type[BaseTool] | Callable] | None = None,
        response_model: type[_ResponseModelT],
        output_parser: None = None,
        json_mode: bool = False,
        client: _AsyncBaseClientT = ...,
        call_params: _BaseCallParamsT | None = None,
    ) -> AsyncLLMFunctionDecorator[_BaseDynamicConfigT, _ResponseModelT]: ...

    @overload
    def __call__(
        self,
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
        model: str,
        *,
        stream: Literal[False] = False,
        tools: list[type[BaseTool] | Callable] | None = None,
        response_model: type[_ResponseModelT],
        output_parser: Callable[[_ResponseModelT], _ParsedOutputT],
        json_mode: bool = False,
        client: _SameSyncAndAsyncClientT | None = None,
        call_params: _BaseCallParamsT | None = None,
    ) -> LLMFunctionDecorator[_BaseDynamicConfigT, _ParsedOutputT, _ParsedOutputT]: ...

    @overload
    def __call__(
        self,
        model: str,
        *,
        stream: Literal[False] = False,
        tools: list[type[BaseTool] | Callable] | None = None,
        response_model: type[_ResponseModelT],
        output_parser: Callable[[_ResponseModelT], _ParsedOutputT],
        json_mode: bool = False,
        client: _AsyncBaseClientT = ...,
        call_params: _BaseCallParamsT | None = None,
    ) -> AsyncLLMFunctionDecorator[_BaseDynamicConfigT, _ParsedOutputT]: ...

    @overload
    def __call__(
        self,
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
    def __call__(
        self,
        model: str,
        *,
        stream: Literal[True],
        tools: list[type[BaseTool] | Callable] | None = None,
        response_model: type[_ResponseModelT],
        output_parser: None = None,
        json_mode: bool = False,
        client: _SameSyncAndAsyncClientT | None = None,
        call_params: _BaseCallParamsT | None = None,
    ) -> LLMFunctionDecorator[
        _BaseDynamicConfigT, Iterable[_ResponseModelT], AsyncIterable[_ResponseModelT]
    ]: ...

    @overload
    def __call__(
        self,
        model: str,
        *,
        stream: Literal[True],
        tools: list[type[BaseTool] | Callable] | None = None,
        response_model: type[_ResponseModelT],
        output_parser: None = None,
        json_mode: bool = False,
        client: _AsyncBaseClientT = ...,
        call_params: _BaseCallParamsT | None = None,
    ) -> AsyncLLMFunctionDecorator[
        _BaseDynamicConfigT, AsyncIterable[_ResponseModelT]
    ]: ...

    @overload
    def __call__(
        self,
        model: str,
        *,
        stream: Literal[True],
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
        stream: Literal[True],
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
        stream: bool = False,
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
            _BaseDynamicConfigT,
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
