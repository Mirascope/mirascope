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
    TYPE_CHECKING,
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

from mirascope.core import BaseDynamicConfig, BaseTool, Messages
from mirascope.core.base import (
    BaseCallParams,
    BaseCallResponse,
    BaseCallResponseChunk,
    BaseType,
    CommonCallParams,
)
from mirascope.core.base.stream_config import StreamConfig
from mirascope.llm.call_response import CallResponse
from mirascope.llm.call_response_chunk import CallResponseChunk
from mirascope.llm.stream import Stream

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
_R_co = TypeVar("_R_co", covariant=True)
_R = TypeVar("_R", contravariant=True)
_BaseCallResponseT = TypeVar(
    "_BaseCallResponseT", bound=BaseCallResponse, covariant=True
)
_BaseCallResponseChunkT = TypeVar(
    "_BaseCallResponseChunkT", bound=BaseCallResponseChunk, covariant=True
)


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

if TYPE_CHECKING:
    from mirascope.core.anthropic import AnthropicCallParams
    from mirascope.core.azure import AzureCallParams
    from mirascope.core.bedrock import BedrockCallParams
    from mirascope.core.cohere import CohereCallParams
    from mirascope.core.gemini import GeminiCallParams
    from mirascope.core.groq import GroqCallParams
    from mirascope.core.litellm import LiteLLMCallParams
    from mirascope.core.mistral import MistralCallParams
    from mirascope.core.openai import OpenAICallParams
    from mirascope.core.vertex import VertexCallParams
else:
    AnthropicCallParams = AzureCallParams = BedrockCallParams = CohereCallParams = (
        GeminiCallParams
    ) = GroqCallParams = LiteLLMCallParams = MistralCallParams = OpenAICallParams = (
        VertexCallParams
    ) = None


class DecoratedCall(Protocol[_P, _R_co]):
    @overload
    def __call__(
        self,
        provider_override: Literal["anthropic"] = "anthropic",
        model_override: str | None = None,
        call_params_override: CommonCallParams | AnthropicCallParams | None = None,
        *args: _P.args,
        **kwargs: _P.kwargs,
    ) -> _R_co: ...

    @overload
    def __call__(
        self,
        provider_override: Literal["azure"] = "azure",
        model_override: str | None = None,
        call_params_override: CommonCallParams | AzureCallParams | None = None,
        *args: _P.args,
        **kwargs: _P.kwargs,
    ) -> _R_co: ...

    @overload
    def __call__(
        self,
        provider_override: Literal["bedrock"] = "bedrock",
        model_override: str | None = None,
        call_params_override: CommonCallParams | BedrockCallParams | None = None,
        *args: _P.args,
        **kwargs: _P.kwargs,
    ) -> _R_co: ...

    @overload
    def __call__(
        self,
        provider_override: Literal["cohere"] = "cohere",
        model_override: str | None = None,
        call_params_override: CommonCallParams | CohereCallParams | None = None,
        *args: _P.args,
        **kwargs: _P.kwargs,
    ) -> _R_co: ...
    @overload
    def __call__(
        self,
        provider_override: Literal["gemini"] = "gemini",
        model_override: str | None = None,
        call_params_override: CommonCallParams | GeminiCallParams | None = None,
        *args: _P.args,
        **kwargs: _P.kwargs,
    ) -> _R_co: ...

    @overload
    def __call__(
        self,
        provider_override: Literal["groq"] = "groq",
        model_override: str | None = None,
        call_params_override: CommonCallParams | GroqCallParams | None = None,
        *args: _P.args,
        **kwargs: _P.kwargs,
    ) -> _R_co: ...

    @overload
    def __call__(
        self,
        provider_override: Literal["litellm"] = "litellm",
        model_override: str | None = None,
        call_params_override: CommonCallParams | LiteLLMCallParams | None = None,
        *args: _P.args,
        **kwargs: _P.kwargs,
    ) -> _R_co: ...

    @overload
    def __call__(
        self,
        provider_override: Literal["mistral"] = "mistral",
        model_override: str | None = None,
        call_params_override: CommonCallParams | MistralCallParams | None = None,
        *args: _P.args,
        **kwargs: _P.kwargs,
    ) -> _R_co: ...

    @overload
    def __call__(
        self,
        provider_override: Literal["openai"] = "openai",
        model_override: str | None = None,
        call_params_override: CommonCallParams | OpenAICallParams | None = None,
        *args: _P.args,
        **kwargs: _P.kwargs,
    ) -> _R_co: ...

    @overload
    def __call__(
        self,
        provider_override: Literal["vertex"] = "vertex",
        model_override: str | None = None,
        call_params_override: CommonCallParams | VertexCallParams | None = None,
        *args: _P.args,
        **kwargs: _P.kwargs,
    ) -> _R_co: ...

    @overload
    def __call__(
        self,
        provider_override: Provider | None,
        model_override: str | None,
        call_params_override: BaseCallParams | dict[str, Any],
        *args: _P.args,
        **kwargs: _P.kwargs,
    ) -> _R_co: ...
    @overload
    def __call__(
        self,
        provider_override: Provider | None,
        model_override: str | None,
        call_params_override: BaseCallParams | dict[str, Any],
        *args: _P.args,
        **kwargs: _P.kwargs,
    ) -> _R_co: ...

    def __call__(
        self,
        provider_override: Provider | None = None,
        model_override: str | None = None,
        call_params_override: BaseCallParams | dict[str, Any] | None = None,
        *args: _P.args,
        **kwargs: _P.kwargs,
    ) -> _R_co: ...


class AsyncLLMFunctionDecorator(Protocol[_AsyncBaseDynamicConfigT, _AsyncResponseT]):
    @overload
    def __call__(
        self,
        fn: Callable[
            _P,
            Awaitable[_AsyncBaseDynamicConfigT]
            | Coroutine[Any, Any, _AsyncBaseDynamicConfigT],
        ],
    ) -> DecoratedCall[_P, Awaitable[_AsyncResponseT]]: ...

    @overload
    def __call__(
        self,
        fn: Callable[_P, Awaitable[Messages.Type] | Coroutine[Any, Any, Messages.Type]],
    ) -> DecoratedCall[_P, Awaitable[_AsyncResponseT]]: ...

    def __call__(
        self,
        fn: Callable[
            _P,
            Awaitable[_AsyncBaseDynamicConfigT]
            | Coroutine[Any, Any, _AsyncBaseDynamicConfigT],
        ]
        | Callable[_P, Awaitable[Messages.Type] | Coroutine[Any, Any, Messages.Type]],
    ) -> DecoratedCall[_P, Awaitable[_AsyncResponseT]]: ...  # pragma: no cover


class SyncLLMFunctionDecorator(Protocol[_BaseDynamicConfigT, _ResponseT]):
    @overload
    def __call__(
        self, fn: Callable[_P, _BaseDynamicConfigT]
    ) -> DecoratedCall[_P, _ResponseT]: ...

    @overload
    def __call__(
        self, fn: Callable[_P, Messages.Type]
    ) -> DecoratedCall[_P, _ResponseT]: ...

    def __call__(
        self, fn: Callable[_P, _BaseDynamicConfigT] | Callable[_P, Messages.Type]
    ) -> DecoratedCall[_P, _ResponseT]: ...  # pragma: no cover


class LLMFunctionDecorator(
    Protocol[_BaseDynamicConfigT, _AsyncBaseDynamicConfigT, _ResponseT, _AsyncResponseT]
):
    @overload
    def __call__(
        self, fn: Callable[_P, _BaseDynamicConfigT]
    ) -> DecoratedCall[_P, _ResponseT]: ...

    @overload
    def __call__(
        self, fn: Callable[_P, Messages.Type]
    ) -> DecoratedCall[_P, _ResponseT]: ...

    @overload
    def __call__(
        self, fn: Callable[_P, Awaitable[_AsyncBaseDynamicConfigT]]
    ) -> DecoratedCall[_P, Awaitable[_AsyncResponseT]]: ...

    @overload
    def __call__(
        self, fn: Callable[_P, Awaitable[Messages.Type]]
    ) -> DecoratedCall[_P, Awaitable[_AsyncResponseT]]: ...

    def __call__(
        self,
        fn: Callable[_P, _BaseDynamicConfigT]
        | Callable[_P, Awaitable[_AsyncBaseDynamicConfigT]]
        | Callable[_P, Messages.Type]
        | Callable[_P, Awaitable[Messages.Type]],
    ) -> DecoratedCall[
        _P, _ResponseT | Awaitable[_AsyncResponseT]
    ]: ...  # pragma: no cover


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
    def __call__(
        self,
        provider: Provider,
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
    def __call__(
        self,
        provider: Provider,
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
        provider: Provider,
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
        provider: Provider,
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
        provider: Provider,
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
        provider: Provider,
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
        provider: Provider,
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
        provider: Provider,
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
        provider: Provider,
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
        provider: Provider,
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
        provider: Provider,
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
        provider: Provider,
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
    def __call__(
        self,
        provider: Provider,
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
        provider: Provider,
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
        provider: Provider,
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
        provider: Provider,
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
        provider: Provider,
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
        provider: Provider,
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
        provider: Provider,
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
        provider: Provider,
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
        provider: Provider,
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
        provider: Provider,
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
        provider: Provider,
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
