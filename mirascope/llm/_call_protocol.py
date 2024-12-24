"""Protocols for reusable type hints."""

from collections.abc import (
    AsyncIterable,
    Callable,
    Iterable,
)
from typing import (
    Any,
    Literal,
    NoReturn,
    Protocol,
    TypeVar,
    overload,
)

from mirascope.core import BaseTool
from mirascope.core.base import BaseCallParams
from mirascope.core.base.stream_config import StreamConfig
from mirascope.llm._protocols import (
    AsyncLLMFunctionDecorator,
    LLMFunctionDecorator,
    SyncLLMFunctionDecorator,
)
from mirascope.llm.call_response import CallResponse
from mirascope.llm.call_response_chunk import CallResponseChunk
from mirascope.llm.stream import Stream

_ParsedOutputT = TypeVar("_ParsedOutputT")
_ResponseModelT = TypeVar("_ResponseModelT")


try:
    from openai import AsyncAzureOpenAI, AsyncOpenAI, AzureOpenAI, OpenAI
    from openai.types.chat import (
        ChatCompletion,
        ChatCompletionChunk,
        ChatCompletionMessageParam,
        ChatCompletionUserMessageParam,
    )

    from mirascope.core.openai import (
        AsyncOpenAIDynamicConfig,
        OpenAIDynamicConfig,
        OpenAITool,
    )
except ImportError:
    AsyncOpenAIDynamicConfig = OpenAITool = OpenAIDynamicConfig = None
    AsyncAzureOpenAI = AsyncOpenAI = AzureOpenAI = OpenAI = None
    ChatCompletion = ChatCompletionChunk = ChatCompletionMessageParam = (
        ChatCompletionUserMessageParam
    ) = None


class Call(Protocol):
    @overload
    def __call__(
        self,
        provider: Literal["openai"],
        model: str,
        *,
        stream: Literal[False] = False,
        tools: list[type[BaseTool] | Callable] | None = None,
        response_model: None = None,
        output_parser: None = None,
        json_mode: bool = False,
        client: None = None,
        call_params: BaseCallParams | None = None,
    ) -> LLMFunctionDecorator[
        OpenAIDynamicConfig,
        AsyncOpenAIDynamicConfig,
        CallResponse[ChatCompletion, OpenAITool],
        CallResponse[ChatCompletion, OpenAITool],
    ]: ...

    @overload
    def __call__(
        self,
        provider: Literal["openai"],
        model: str,
        *,
        stream: Literal[False] = False,
        tools: list[type[BaseTool] | Callable] | None = None,
        response_model: None = None,
        output_parser: None = None,
        json_mode: bool = False,
        client: AsyncOpenAI | AsyncAzureOpenAI = ...,
        call_params: BaseCallParams | None = None,
    ) -> AsyncLLMFunctionDecorator[
        AsyncOpenAIDynamicConfig, CallResponse[ChatCompletion, OpenAITool]
    ]: ...

    @overload
    def __call__(
        self,
        provider: Literal["openai"],
        model: str,
        *,
        stream: Literal[False] = False,
        tools: list[type[BaseTool] | Callable] | None = None,
        response_model: None = None,
        output_parser: None = None,
        json_mode: bool = False,
        client: OpenAI | AzureOpenAI = ...,
        call_params: BaseCallParams | None = None,
    ) -> SyncLLMFunctionDecorator[
        OpenAIDynamicConfig,
        CallResponse[ChatCompletion, OpenAITool],
    ]: ...

    @overload
    def __call__(
        self,
        provider: Literal["openai"],
        model: str,
        *,
        stream: Literal[False] = False,
        tools: list[type[BaseTool] | Callable] | None = None,
        response_model: None = None,
        output_parser: Callable[
            [
                CallResponse[ChatCompletion, OpenAITool],
            ],
            _ParsedOutputT,
        ],
        json_mode: bool = False,
        client: None | None = None,
        call_params: BaseCallParams | None = None,
    ) -> LLMFunctionDecorator[
        OpenAIDynamicConfig, AsyncOpenAIDynamicConfig, _ParsedOutputT, _ParsedOutputT
    ]: ...

    @overload
    def __call__(
        self,
        provider: Literal["openai"],
        model: str,
        *,
        stream: Literal[False] = False,
        tools: list[type[BaseTool] | Callable] | None = None,
        response_model: None = None,
        output_parser: Callable[
            [
                CallResponse[ChatCompletion, OpenAITool],
            ],
            _ParsedOutputT,
        ],
        json_mode: bool = False,
        client: AsyncOpenAI | AsyncAzureOpenAI = ...,
        call_params: BaseCallParams | None = None,
    ) -> AsyncLLMFunctionDecorator[AsyncOpenAIDynamicConfig, _ParsedOutputT]: ...

    @overload
    def __call__(
        self,
        provider: Literal["openai"],
        model: str,
        *,
        stream: Literal[False] = False,
        tools: list[type[BaseTool] | Callable] | None = None,
        response_model: None = None,
        output_parser: Callable[
            [
                CallResponse[ChatCompletion, OpenAITool],
            ],
            _ParsedOutputT,
        ],
        json_mode: bool = False,
        client: OpenAI | AzureOpenAI = ...,
        call_params: BaseCallParams | None = None,
    ) -> SyncLLMFunctionDecorator[OpenAIDynamicConfig, _ParsedOutputT]: ...

    @overload
    def __call__(
        self,
        provider: Literal["openai"],
        model: str,
        *,
        stream: Literal[False] = False,
        tools: list[type[BaseTool] | Callable] | None = None,
        response_model: None = None,
        output_parser: Callable[
            [CallResponseChunk[ChatCompletionChunk]], _ParsedOutputT
        ],
        json_mode: bool = False,
        client: None
        | OpenAI
        | AzureOpenAI
        | AsyncOpenAI
        | AsyncAzureOpenAI
        | None = None,
        call_params: BaseCallParams | None = None,
    ) -> NoReturn: ...

    @overload
    def __call__(
        self,
        provider: Literal["openai"],
        model: str,
        *,
        stream: Literal[True] | StreamConfig = True,
        tools: list[type[BaseTool] | Callable] | None = None,
        response_model: None = None,
        output_parser: None = None,
        json_mode: bool = False,
        client: None | None = None,
        call_params: BaseCallParams | None = None,
    ) -> LLMFunctionDecorator[
        OpenAIDynamicConfig,
        AsyncOpenAIDynamicConfig,
        Stream[ChatCompletion, ChatCompletionChunk],
        Stream[ChatCompletion, ChatCompletionChunk],
    ]: ...

    @overload
    def __call__(
        self,
        provider: Literal["openai"],
        model: str,
        *,
        stream: Literal[True] | StreamConfig = True,
        tools: list[type[BaseTool] | Callable] | None = None,
        response_model: None = None,
        output_parser: None = None,
        json_mode: bool = False,
        client: AsyncOpenAI | AsyncAzureOpenAI = ...,
        call_params: BaseCallParams | None = None,
    ) -> AsyncLLMFunctionDecorator[
        AsyncOpenAIDynamicConfig, Stream[ChatCompletion, ChatCompletionChunk]
    ]: ...

    @overload
    def __call__(
        self,
        provider: Literal["openai"],
        model: str,
        *,
        stream: Literal[True] | StreamConfig = True,
        tools: list[type[BaseTool] | Callable] | None = None,
        response_model: None = None,
        output_parser: None = None,
        json_mode: bool = False,
        client: OpenAI | AzureOpenAI = ...,
        call_params: BaseCallParams | None = None,
    ) -> SyncLLMFunctionDecorator[
        OpenAIDynamicConfig, Stream[ChatCompletion, ChatCompletionChunk]
    ]: ...

    @overload
    def __call__(
        self,
        provider: Literal["openai"],
        model: str,
        *,
        stream: Literal[True] | StreamConfig = True,
        tools: list[type[BaseTool] | Callable] | None = None,
        response_model: None = None,
        output_parser: Callable[
            [CallResponseChunk[ChatCompletionChunk]], _ParsedOutputT
        ],
        json_mode: bool = False,
        client: None
        | OpenAI
        | AzureOpenAI
        | AsyncOpenAI
        | AsyncAzureOpenAI
        | None = None,
        call_params: BaseCallParams | None = None,
    ) -> NoReturn: ...

    @overload
    def __call__(
        self,
        provider: Literal["openai"],
        model: str,
        *,
        stream: Literal[True] | StreamConfig = True,
        tools: list[type[BaseTool] | Callable] | None = None,
        response_model: None = None,
        output_parser: Callable[
            [
                CallResponse[ChatCompletion, OpenAITool],
            ],
            _ParsedOutputT,
        ],
        json_mode: bool = False,
        client: None
        | OpenAI
        | AzureOpenAI
        | AsyncOpenAI
        | AsyncAzureOpenAI
        | None = None,
        call_params: BaseCallParams | None = None,
    ) -> NoReturn: ...

    @overload
    def __call__(
        self,
        provider: Literal["openai"],
        model: str,
        *,
        stream: Literal[False] = False,
        tools: list[type[BaseTool] | Callable] | None = None,
        response_model: type[_ResponseModelT],
        output_parser: None = None,
        json_mode: bool = False,
        client: None | None = None,
        call_params: BaseCallParams | None = None,
    ) -> LLMFunctionDecorator[
        OpenAIDynamicConfig, AsyncOpenAIDynamicConfig, _ResponseModelT, _ResponseModelT
    ]: ...

    @overload
    def __call__(
        self,
        provider: Literal["openai"],
        model: str,
        *,
        stream: Literal[False] = False,
        tools: list[type[BaseTool] | Callable] | None = None,
        response_model: type[_ResponseModelT],
        output_parser: None = None,
        json_mode: bool = False,
        client: AsyncOpenAI | AsyncAzureOpenAI = ...,
        call_params: BaseCallParams | None = None,
    ) -> AsyncLLMFunctionDecorator[AsyncOpenAIDynamicConfig, _ResponseModelT]: ...

    @overload
    def __call__(
        self,
        provider: Literal["openai"],
        model: str,
        *,
        stream: Literal[False] = False,
        tools: list[type[BaseTool] | Callable] | None = None,
        response_model: type[_ResponseModelT],
        output_parser: None = None,
        json_mode: bool = False,
        client: OpenAI | AzureOpenAI = ...,
        call_params: BaseCallParams | None = None,
    ) -> SyncLLMFunctionDecorator[OpenAIDynamicConfig, _ResponseModelT]: ...

    @overload
    def __call__(
        self,
        provider: Literal["openai"],
        model: str,
        *,
        stream: Literal[False] = False,
        tools: list[type[BaseTool] | Callable] | None = None,
        response_model: type[_ResponseModelT],
        output_parser: Callable[[_ResponseModelT], _ParsedOutputT],
        json_mode: bool = False,
        client: None | None = None,
        call_params: BaseCallParams | None = None,
    ) -> LLMFunctionDecorator[
        OpenAIDynamicConfig, AsyncOpenAIDynamicConfig, _ParsedOutputT, _ParsedOutputT
    ]: ...

    @overload
    def __call__(
        self,
        provider: Literal["openai"],
        model: str,
        *,
        stream: Literal[False] = False,
        tools: list[type[BaseTool] | Callable] | None = None,
        response_model: type[_ResponseModelT],
        output_parser: Callable[[_ResponseModelT], _ParsedOutputT],
        json_mode: bool = False,
        client: AsyncOpenAI | AsyncAzureOpenAI = ...,
        call_params: BaseCallParams | None = None,
    ) -> AsyncLLMFunctionDecorator[AsyncOpenAIDynamicConfig, _ParsedOutputT]: ...

    @overload
    def __call__(
        self,
        provider: Literal["openai"],
        model: str,
        *,
        stream: Literal[False] = False,
        tools: list[type[BaseTool] | Callable] | None = None,
        response_model: type[_ResponseModelT],
        output_parser: Callable[[_ResponseModelT], _ParsedOutputT],
        json_mode: bool = False,
        client: OpenAI | AzureOpenAI = ...,
        call_params: BaseCallParams | None = None,
    ) -> SyncLLMFunctionDecorator[OpenAIDynamicConfig, _ParsedOutputT]: ...

    @overload
    def __call__(
        self,
        provider: Literal["openai"],
        model: str,
        *,
        stream: Literal[True] | StreamConfig,
        tools: list[type[BaseTool] | Callable] | None = None,
        response_model: type[_ResponseModelT],
        output_parser: None = None,
        json_mode: bool = False,
        client: None | None = None,
        call_params: BaseCallParams | None = None,
    ) -> LLMFunctionDecorator[
        OpenAIDynamicConfig,
        AsyncOpenAIDynamicConfig,
        Iterable[_ResponseModelT],
        AsyncIterable[_ResponseModelT],
    ]: ...

    @overload
    def __call__(
        self,
        provider: Literal["openai"],
        model: str,
        *,
        stream: Literal[True] | StreamConfig,
        tools: list[type[BaseTool] | Callable] | None = None,
        response_model: type[_ResponseModelT],
        output_parser: None = None,
        json_mode: bool = False,
        client: AsyncOpenAI | AsyncAzureOpenAI = ...,
        call_params: BaseCallParams | None = None,
    ) -> AsyncLLMFunctionDecorator[
        AsyncOpenAIDynamicConfig, AsyncIterable[_ResponseModelT]
    ]: ...

    @overload
    def __call__(
        self,
        provider: Literal["openai"],
        model: str,
        *,
        stream: Literal[True] | StreamConfig,
        tools: list[type[BaseTool] | Callable] | None = None,
        response_model: type[_ResponseModelT],
        output_parser: None = None,
        json_mode: bool = False,
        client: OpenAI | AzureOpenAI = ...,
        call_params: BaseCallParams | None = None,
    ) -> SyncLLMFunctionDecorator[OpenAIDynamicConfig, Iterable[_ResponseModelT]]: ...

    @overload
    def __call__(
        self,
        provider: Literal["openai"],
        model: str,
        *,
        stream: Literal[True] | StreamConfig,
        tools: list[type[BaseTool] | Callable] | None = None,
        response_model: type[_ResponseModelT],
        output_parser: Callable[
            [
                CallResponse[ChatCompletion, OpenAITool],
            ],
            _ParsedOutputT,
        ]
        | Callable[[CallResponseChunk[ChatCompletionChunk]], _ParsedOutputT]
        | Callable[[_ResponseModelT], _ParsedOutputT]
        | None,
        json_mode: bool = False,
        client: None
        | AsyncOpenAI
        | AsyncAzureOpenAI
        | OpenAI
        | AzureOpenAI
        | None = None,
        call_params: BaseCallParams | None = None,
    ) -> NoReturn: ...
    def __call__(
        self,
        provider: Any,
        model: Any,
        *,
        stream: Any = False,
        tools: Any = None,
        response_model: Any = None,
        output_parser: Any = None,
        json_mode: bool = False,
        client: Any = None,
        call_params: Any = None,
    ) -> Any: ...
