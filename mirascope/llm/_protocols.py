"""Protocols for reusable type hints."""

from collections.abc import (
    AsyncIterable,
    Awaitable,
    Callable,
    Coroutine,
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

from ..core import BaseDynamicConfig, BaseTool, Messages
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
from .agent_context import AgentContext
from .call_response import AgentResponse, CallResponse
from .call_response_chunk import CallResponseChunk
from .stream import AgentStream, Stream
from .tool import AgentTool

_P = ParamSpec("_P")
_CovariantR = TypeVar("_CovariantR", covariant=True)

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
_ResponseT = TypeVar("_ResponseT", covariant=True)
_AsyncResponseT = TypeVar("_AsyncResponseT", covariant=True)
_BaseCallParamsT = TypeVar("_BaseCallParamsT", contravariant=True)
_AsyncBaseDynamicConfigT = TypeVar("_AsyncBaseDynamicConfigT", contravariant=True)
_BaseDynamicConfigT = TypeVar("_BaseDynamicConfigT", contravariant=True)
_AsyncAgentDynamicConfigT = TypeVar("_AsyncAgentDynamicConfigT", covariant=True)
_AgentDynamicConfigT = TypeVar("_AgentDynamicConfigT", covariant=True)
_ParsedOutputT = TypeVar("_ParsedOutputT")
_ContravariantDepsT = TypeVar("_ContravariantDepsT", contravariant=True)
_InvariantDepsT = TypeVar("_InvariantDepsT")


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


class AgentFunctionDynamicConfigDefinition(
    Protocol[_P, _InvariantDepsT, _AgentDynamicConfigT]
):
    def __call__(
        self,
        ctx: AgentContext[_InvariantDepsT],
        *args: _P.args,
        **kwargs: _P.kwargs,
    ) -> _AgentDynamicConfigT: ...


class AsyncAgentFunctionDynamicConfigDefinition(
    Protocol[_P, _InvariantDepsT, _AsyncAgentDynamicConfigT]
):
    def __call__(
        self,
        ctx: AgentContext[_InvariantDepsT],
        *args: _P.args,
        **kwargs: _P.kwargs,
    ) -> (
        Awaitable[_AsyncAgentDynamicConfigT]
        | Coroutine[Any, Any, _AsyncAgentDynamicConfigT]
    ): ...


class AgentFunctionMessagesDefinition(Protocol[_P, _InvariantDepsT]):
    def __call__(
        self,
        ctx: AgentContext[_InvariantDepsT],
        *args: _P.args,
        **kwargs: _P.kwargs,
    ) -> Messages.Type: ...


class AsyncAgentFunctionMessagesDefinition(Protocol[_P, _InvariantDepsT]):
    def __call__(
        self,
        ctx: AgentContext[_InvariantDepsT],
        *args: _P.args,
        **kwargs: _P.kwargs,
    ) -> Awaitable[Messages.Type] | Coroutine[Any, Any, Messages.Type]: ...


class AgentDecoratedFunction(Protocol[_P, _ContravariantDepsT, _CovariantR]):
    def __call__(
        self,
        query: str,
        deps: _ContravariantDepsT,
        *args: _P.args,
        **kwargs: _P.kwargs,
    ) -> _CovariantR: ...


class AsyncAgentFunctionDecorator(
    Protocol[_InvariantDepsT, _AsyncBaseDynamicConfigT, _AsyncResponseT]
):
    @overload
    def __call__(
        self,
        fn: AsyncAgentFunctionDynamicConfigDefinition[
            _P, _InvariantDepsT, _AsyncBaseDynamicConfigT
        ],
    ) -> AgentDecoratedFunction[_P, _InvariantDepsT, Awaitable[_AsyncResponseT]]: ...

    @overload
    def __call__(
        self,
        fn: AsyncAgentFunctionMessagesDefinition,
    ) -> AgentDecoratedFunction[_P, _InvariantDepsT, Awaitable[_AsyncResponseT]]: ...

    def __call__(
        self,
        fn: AsyncAgentFunctionDynamicConfigDefinition[
            _P, _InvariantDepsT, _AsyncBaseDynamicConfigT
        ]
        | AsyncAgentFunctionMessagesDefinition[_P, _InvariantDepsT],
    ) -> AgentDecoratedFunction[
        _P, _InvariantDepsT, Awaitable[_AsyncResponseT]
    ]: ...  # pragma: no cover


class SyncAgentFunctionDecorator(
    Protocol[_InvariantDepsT, _BaseDynamicConfigT, _ResponseT]
):
    @overload
    def __call__(
        self,
        fn: AgentFunctionDynamicConfigDefinition[
            _P, _InvariantDepsT, _BaseDynamicConfigT
        ],
    ) -> AgentDecoratedFunction[_P, _InvariantDepsT, _ResponseT]: ...

    @overload
    def __call__(
        self, fn: AgentFunctionMessagesDefinition[_P, _InvariantDepsT]
    ) -> AgentDecoratedFunction[_P, _InvariantDepsT, _ResponseT]: ...

    def __call__(
        self,
        fn: AgentFunctionDynamicConfigDefinition[
            _P, _InvariantDepsT, _BaseDynamicConfigT
        ]
        | AgentFunctionMessagesDefinition[_P, _InvariantDepsT],
    ) -> AgentDecoratedFunction[
        _P, _InvariantDepsT, _ResponseT
    ]: ...  # pragma: no cover


class AgentFunctionDecorator(
    Protocol[
        _InvariantDepsT,
        _BaseDynamicConfigT,
        _AsyncBaseDynamicConfigT,
        _ResponseT,
        _AsyncResponseT,
    ]
):
    @overload
    def __call__(
        self,
        fn: AgentFunctionDynamicConfigDefinition[
            _P, _InvariantDepsT, _BaseDynamicConfigT
        ],
    ) -> AgentDecoratedFunction[_P, _InvariantDepsT, _ResponseT]: ...

    @overload
    def __call__(
        self,
        fn: AsyncAgentFunctionDynamicConfigDefinition[
            _P, _InvariantDepsT, _AsyncBaseDynamicConfigT
        ],
    ) -> AgentDecoratedFunction[_P, _InvariantDepsT, _ResponseT]: ...

    @overload
    def __call__(
        self, fn: AgentFunctionMessagesDefinition[_P, _InvariantDepsT]
    ) -> AgentDecoratedFunction[_P, _InvariantDepsT, _ResponseT]: ...

    @overload
    def __call__(
        self, fn: AsyncAgentFunctionMessagesDefinition[_P, _InvariantDepsT]
    ) -> AgentDecoratedFunction[_P, _InvariantDepsT, Awaitable[_AsyncResponseT]]: ...

    def __call__(
        self,
        fn: AgentFunctionDynamicConfigDefinition[
            _P, _InvariantDepsT, _BaseDynamicConfigT
        ]
        | AsyncAgentFunctionDynamicConfigDefinition[
            _P, _InvariantDepsT, _AsyncBaseDynamicConfigT
        ]
        | AgentFunctionMessagesDefinition[_P, _InvariantDepsT]
        | AsyncAgentFunctionMessagesDefinition[_P, _InvariantDepsT],
    ) -> AgentDecoratedFunction[
        _P, _InvariantDepsT, _ResponseT | Awaitable[_AsyncResponseT]
    ]: ...  # pragma: no cover


class _AgentDecorator(
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
        *,
        method: str = "simple",
        deps_type: type[_InvariantDepsT],
        model: str,
        stream: Literal[False] = False,
        tools: list[type[AgentTool[_InvariantDepsT]]] | None = None,
        response_model: None = None,
        output_parser: None = None,
        json_mode: bool = False,
        client: _SameSyncAndAsyncClientT | None = None,
        call_params: _BaseCallParamsT | None = None,
    ) -> AgentFunctionDecorator[
        _InvariantDepsT,
        _BaseDynamicConfigT,
        _AsyncBaseDynamicConfigT,
        AgentResponse[_InvariantDepsT],
        AgentResponse[_InvariantDepsT],
    ]: ...

    @overload
    def __call__(  # pyright: ignore[reportOverlappingOverload]
        self,
        *,
        method: str = "simple",
        deps_type: type[_InvariantDepsT],
        model: str,
        stream: Literal[False] = False,
        tools: list[type[AgentTool[_InvariantDepsT]]] | None = None,
        response_model: None = None,
        output_parser: None = None,
        json_mode: bool = False,
        client: _AsyncBaseClientT = ...,
        call_params: _BaseCallParamsT | None = None,
    ) -> AsyncAgentFunctionDecorator[
        _InvariantDepsT,
        _AsyncBaseDynamicConfigT,
        AgentResponse[_InvariantDepsT],
    ]: ...

    @overload
    def __call__(
        self,
        *,
        method: str = "simple",
        deps_type: type[_InvariantDepsT],
        model: str,
        stream: Literal[False] = False,
        tools: list[type[AgentTool[_InvariantDepsT]]] | None = None,
        response_model: None = None,
        output_parser: None = None,
        json_mode: bool = False,
        client: _SyncBaseClientT = ...,
        call_params: _BaseCallParamsT | None = None,
    ) -> SyncAgentFunctionDecorator[
        _InvariantDepsT,
        _BaseDynamicConfigT,
        AgentResponse[_InvariantDepsT],
    ]: ...

    @overload
    def __call__(  # pyright: ignore[reportOverlappingOverload]
        self,
        *,
        method: str = "simple",
        deps_type: type[_InvariantDepsT],
        model: str,
        stream: Literal[False] = False,
        tools: list[type[AgentTool[_InvariantDepsT]]] | None = None,
        response_model: None = None,
        output_parser: Callable[[_BaseCallResponseT], _ParsedOutputT],
        json_mode: bool = False,
        client: _SameSyncAndAsyncClientT | None = None,
        call_params: _BaseCallParamsT | None = None,
    ) -> AgentFunctionDecorator[
        _InvariantDepsT,
        _BaseDynamicConfigT,
        _AsyncBaseDynamicConfigT,
        _ParsedOutputT,
        _ParsedOutputT,
    ]: ...

    @overload
    def __call__(  # type: ignore[reportOverlappingOverload]
        self,
        *,
        method: str = "simple",
        deps_type: type[_InvariantDepsT],
        model: str,
        stream: Literal[False] = False,
        tools: list[type[AgentTool[_InvariantDepsT]]] | None = None,
        response_model: None = None,
        output_parser: Callable[[_BaseCallResponseT], _ParsedOutputT],
        json_mode: bool = False,
        client: _AsyncBaseClientT = ...,
        call_params: _BaseCallParamsT | None = None,
    ) -> AsyncAgentFunctionDecorator[
        _InvariantDepsT, _AsyncBaseDynamicConfigT, _ParsedOutputT
    ]: ...

    @overload
    def __call__(
        self,
        *,
        method: str = "simple",
        deps_type: type[_InvariantDepsT],
        model: str,
        stream: Literal[False] = False,
        tools: list[type[AgentTool[_InvariantDepsT]]] | None = None,
        response_model: None = None,
        output_parser: Callable[[_BaseCallResponseT], _ParsedOutputT],
        json_mode: bool = False,
        client: _SyncBaseClientT = ...,
        call_params: _BaseCallParamsT | None = None,
    ) -> SyncAgentFunctionDecorator[
        _InvariantDepsT, _BaseDynamicConfigT, _ParsedOutputT
    ]: ...

    @overload
    def __call__(
        self,
        *,
        method: str = "simple",
        deps_type: type[_InvariantDepsT],
        model: str,
        stream: Literal[False] = False,
        tools: list[type[AgentTool[_InvariantDepsT]]] | None = None,
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
        *,
        method: str = "simple",
        deps_type: type[_InvariantDepsT],
        model: str,
        stream: Literal[True] | StreamConfig = True,
        tools: list[type[AgentTool[_InvariantDepsT]]] | None = None,
        response_model: None = None,
        output_parser: None = None,
        json_mode: bool = False,
        client: _SameSyncAndAsyncClientT | None = None,
        call_params: _BaseCallParamsT | None = None,
    ) -> AgentFunctionDecorator[
        _InvariantDepsT,
        _BaseDynamicConfigT,
        _AsyncBaseDynamicConfigT,
        AgentStream[_InvariantDepsT],
        AgentStream[_InvariantDepsT],
    ]: ...

    @overload
    def __call__(
        self,
        *,
        method: str = "simple",
        deps_type: type[_InvariantDepsT],
        model: str,
        stream: Literal[True] | StreamConfig = True,
        tools: list[type[AgentTool[_InvariantDepsT]]] | None = None,
        response_model: None = None,
        output_parser: None = None,
        json_mode: bool = False,
        client: _AsyncBaseClientT = ...,
        call_params: _BaseCallParamsT | None = None,
    ) -> AsyncAgentFunctionDecorator[
        _InvariantDepsT,
        _AsyncBaseDynamicConfigT,
        AgentStream[_InvariantDepsT],
    ]: ...

    @overload
    def __call__(
        self,
        *,
        method: str = "simple",
        deps_type: type[_InvariantDepsT],
        model: str,
        stream: Literal[True] | StreamConfig = True,
        tools: list[type[AgentTool[_InvariantDepsT]]] | None = None,
        response_model: None = None,
        output_parser: None = None,
        json_mode: bool = False,
        client: _SyncBaseClientT = ...,
        call_params: _BaseCallParamsT | None = None,
    ) -> SyncAgentFunctionDecorator[
        _InvariantDepsT,
        _BaseDynamicConfigT,
        AgentStream[_InvariantDepsT],
    ]: ...

    @overload
    def __call__(
        self,
        *,
        method: str = "simple",
        deps_type: type[_InvariantDepsT],
        model: str,
        stream: Literal[True] | StreamConfig = True,
        tools: list[type[AgentTool[_InvariantDepsT]]] | None = None,
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
        *,
        method: str = "simple",
        deps_type: type[_InvariantDepsT],
        model: str,
        stream: Literal[True] | StreamConfig = True,
        tools: list[type[AgentTool[_InvariantDepsT]]] | None = None,
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
        *,
        method: str = "simple",
        deps_type: type[_InvariantDepsT],
        model: str,
        stream: Literal[False] = False,
        tools: list[type[AgentTool[_InvariantDepsT]]] | None = None,
        response_model: type[_ResponseModelT],
        output_parser: None = None,
        json_mode: bool = False,
        client: _SameSyncAndAsyncClientT | None = None,
        call_params: _BaseCallParamsT | None = None,
    ) -> AgentFunctionDecorator[
        _InvariantDepsT,
        _BaseDynamicConfigT,
        _AsyncBaseDynamicConfigT,
        _ResponseModelT,
        _ResponseModelT,
    ]: ...

    @overload
    def __call__(  # type: ignore[reportOverlappingOverload]
        self,
        *,
        method: str = "simple",
        deps_type: type[_InvariantDepsT],
        model: str,
        stream: Literal[False] = False,
        tools: list[type[AgentTool[_InvariantDepsT]]] | None = None,
        response_model: type[_ResponseModelT],
        output_parser: None = None,
        json_mode: bool = False,
        client: _AsyncBaseClientT = ...,
        call_params: _BaseCallParamsT | None = None,
    ) -> AsyncAgentFunctionDecorator[
        _InvariantDepsT, _AsyncBaseDynamicConfigT, _ResponseModelT
    ]: ...

    @overload
    def __call__(
        self,
        *,
        method: str = "simple",
        deps_type: type[_InvariantDepsT],
        model: str,
        stream: Literal[False] = False,
        tools: list[type[AgentTool[_InvariantDepsT]]] | None = None,
        response_model: type[_ResponseModelT],
        output_parser: None = None,
        json_mode: bool = False,
        client: _SyncBaseClientT = ...,
        call_params: _BaseCallParamsT | None = None,
    ) -> SyncAgentFunctionDecorator[
        _InvariantDepsT, _BaseDynamicConfigT, _ResponseModelT
    ]: ...

    @overload
    def __call__(
        self,
        *,
        method: str = "simple",
        deps_type: type[_InvariantDepsT],
        model: str,
        stream: Literal[False] = False,
        tools: list[type[AgentTool[_InvariantDepsT]]] | None = None,
        response_model: type[_ResponseModelT],
        output_parser: Callable[[_ResponseModelT], _ParsedOutputT],
        json_mode: bool = False,
        client: _SameSyncAndAsyncClientT | None = None,
        call_params: _BaseCallParamsT | None = None,
    ) -> AgentFunctionDecorator[
        _InvariantDepsT,
        _BaseDynamicConfigT,
        _AsyncBaseDynamicConfigT,
        _ParsedOutputT,
        _ParsedOutputT,
    ]: ...

    @overload
    def __call__(
        self,
        *,
        method: str = "simple",
        deps_type: type[_InvariantDepsT],
        model: str,
        stream: Literal[False] = False,
        tools: list[type[AgentTool[_InvariantDepsT]]] | None = None,
        response_model: type[_ResponseModelT],
        output_parser: Callable[[_ResponseModelT], _ParsedOutputT],
        json_mode: bool = False,
        client: _AsyncBaseClientT = ...,
        call_params: _BaseCallParamsT | None = None,
    ) -> AsyncAgentFunctionDecorator[
        _InvariantDepsT, _AsyncBaseDynamicConfigT, _ParsedOutputT
    ]: ...

    @overload
    def __call__(
        self,
        *,
        method: str = "simple",
        deps_type: type[_InvariantDepsT],
        model: str,
        stream: Literal[False] = False,
        tools: list[type[AgentTool[_InvariantDepsT]]] | None = None,
        response_model: type[_ResponseModelT],
        output_parser: Callable[[_ResponseModelT], _ParsedOutputT],
        json_mode: bool = False,
        client: _SyncBaseClientT = ...,
        call_params: _BaseCallParamsT | None = None,
    ) -> SyncAgentFunctionDecorator[
        _InvariantDepsT, _BaseDynamicConfigT, _ParsedOutputT
    ]: ...

    @overload
    def __call__(
        self,
        *,
        method: str = "simple",
        deps_type: type[_InvariantDepsT],
        model: str,
        stream: Literal[True] | StreamConfig = True,
        tools: list[type[AgentTool[_InvariantDepsT]]] | None = None,
        response_model: type[_ResponseModelT],
        output_parser: None = None,
        json_mode: bool = False,
        client: _SameSyncAndAsyncClientT | None = None,
        call_params: _BaseCallParamsT | None = None,
    ) -> AgentFunctionDecorator[
        _InvariantDepsT,
        _BaseDynamicConfigT,
        _AsyncBaseDynamicConfigT,
        Iterable[_ResponseModelT],
        AsyncIterable[_ResponseModelT],
    ]: ...

    @overload
    def __call__(
        self,
        *,
        method: str = "simple",
        deps_type: type[_InvariantDepsT],
        model: str,
        stream: Literal[True] | StreamConfig = True,
        tools: list[type[AgentTool[_InvariantDepsT]]] | None = None,
        response_model: type[_ResponseModelT],
        output_parser: None = None,
        json_mode: bool = False,
        client: _AsyncBaseClientT = ...,
        call_params: _BaseCallParamsT | None = None,
    ) -> AsyncAgentFunctionDecorator[
        _InvariantDepsT,
        _AsyncBaseDynamicConfigT,
        AsyncIterable[_ResponseModelT],
    ]: ...

    @overload
    def __call__(
        self,
        *,
        method: str = "simple",
        deps_type: type[_InvariantDepsT],
        model: str,
        stream: Literal[True] | StreamConfig = True,
        tools: list[type[AgentTool[_InvariantDepsT]]] | None = None,
        response_model: type[_ResponseModelT],
        output_parser: None = None,
        json_mode: bool = False,
        client: _SyncBaseClientT = ...,
        call_params: _BaseCallParamsT | None = None,
    ) -> SyncAgentFunctionDecorator[
        _InvariantDepsT, _BaseDynamicConfigT, Iterable[_ResponseModelT]
    ]: ...

    @overload
    def __call__(
        self,
        *,
        method: str = "simple",
        deps_type: type[_InvariantDepsT],
        model: str,
        stream: Literal[True] | StreamConfig = True,
        tools: list[type[AgentTool[_InvariantDepsT]]] | None = None,
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
        *,
        method: str = "simple",
        deps_type: type[_InvariantDepsT],
        model: str,
        stream: bool | StreamConfig = False,
        tools: list[type[AgentTool[_InvariantDepsT]]] | None = None,
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
        AsyncAgentFunctionDecorator[
            _InvariantDepsT,
            _AsyncBaseDynamicConfigT,
            AgentResponse[_InvariantDepsT]
            | _ParsedOutputT
            | AgentStream[_InvariantDepsT]
            | _ResponseModelT
            | AsyncIterable[_ResponseModelT],
        ]
        | SyncAgentFunctionDecorator[
            _InvariantDepsT,
            _BaseDynamicConfigT,
            AgentResponse[_InvariantDepsT]
            | _ParsedOutputT
            | AgentStream[_InvariantDepsT]
            | _ResponseModelT
            | Iterable[_ResponseModelT],
        ]
        | AgentFunctionDecorator[
            _InvariantDepsT,
            _BaseDynamicConfigT,
            _AsyncBaseDynamicConfigT,
            AgentResponse[_InvariantDepsT]
            | _ParsedOutputT
            | AgentStream[_InvariantDepsT]
            | _ResponseModelT
            | Iterable[_ResponseModelT],
            AgentResponse[_InvariantDepsT]
            | _ParsedOutputT
            | AgentStream[_InvariantDepsT]
            | _ResponseModelT
            | AsyncIterable[_ResponseModelT],
        ]
    ): ...


AgentDecorator: TypeAlias = _AgentDecorator[
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
