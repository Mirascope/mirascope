"""This module contains the base classes for streaming responses from LLMs."""

import datetime
from abc import ABC, abstractmethod
from collections.abc import AsyncGenerator, Awaitable, Callable, Coroutine, Generator
from functools import wraps
from typing import (
    Any,
    ClassVar,
    Generic,
    ParamSpec,
    TypeVar,
    cast,
    overload,
)

from ..costs import calculate_cost
from ._utils import (
    HandleStream,
    HandleStreamAsync,
    SameSyncAndAsyncClientSetupCall,
    SetupCall,
    fn_is_async,
    get_dynamic_configuration,
    get_fn_args,
    get_metadata,
    get_possible_user_message_param,
    is_prompt_template,
)
from .call_kwargs import BaseCallKwargs
from .call_params import BaseCallParams
from .call_response import BaseCallResponse, JsonableType
from .call_response_chunk import BaseCallResponseChunk
from .dynamic_config import BaseDynamicConfig
from .messages import Messages
from .metadata import Metadata
from .prompt import prompt_template
from .tool import BaseTool
from .types import CostMetadata, Provider

_BaseCallResponseT = TypeVar("_BaseCallResponseT", bound=BaseCallResponse)
_BaseCallResponseChunkT = TypeVar(
    "_BaseCallResponseChunkT", bound=BaseCallResponseChunk
)
_UserMessageParamT = TypeVar("_UserMessageParamT")
_AssistantMessageParamT = TypeVar("_AssistantMessageParamT")
_ToolMessageParamT = TypeVar("_ToolMessageParamT")
_MessageParamT = TypeVar("_MessageParamT")
_BaseToolT = TypeVar("_BaseToolT", bound=BaseTool)
_ToolSchemaT = TypeVar("_ToolSchemaT")
_BaseCallParamsT = TypeVar("_BaseCallParamsT", bound=BaseCallParams)
_BaseDynamicConfigT = TypeVar("_BaseDynamicConfigT", bound=BaseDynamicConfig)
_AsyncBaseDynamicConfigT = TypeVar("_AsyncBaseDynamicConfigT", bound=BaseDynamicConfig)
_FinishReason = TypeVar("_FinishReason")
_DEFAULT = object()


class BaseStream(
    Generic[
        _BaseCallResponseT,
        _BaseCallResponseChunkT,
        _UserMessageParamT,
        _AssistantMessageParamT,
        _ToolMessageParamT,
        _MessageParamT,
        _BaseToolT,
        _ToolSchemaT,
        _BaseDynamicConfigT,
        _BaseCallParamsT,
        _FinishReason,
    ],
    ABC,
):
    """A base class for streaming responses from LLMs."""

    stream: (
        Generator[tuple[_BaseCallResponseChunkT, _BaseToolT | None], None, None]
        | AsyncGenerator[
            tuple[_BaseCallResponseChunkT, _BaseToolT | None],
            None,
        ]
    )
    content: str
    metadata: Metadata
    tool_types: list[type[_BaseToolT]] | None
    call_response_type: type[_BaseCallResponseT]
    model: str
    prompt_template: str | None = None
    fn_args: dict[str, Any] | None = None
    dynamic_config: _BaseDynamicConfigT
    messages: list[_MessageParamT]
    call_params: _BaseCallParamsT
    call_kwargs: BaseCallKwargs[_ToolSchemaT]
    user_message_param: _UserMessageParamT | None = None
    message_param: _AssistantMessageParamT
    input_tokens: int | float | None = None
    cached_tokens: int | float | None = None
    output_tokens: int | float | None = None
    id: str | None = None
    finish_reasons: list[_FinishReason] | None = None
    start_time: float = 0
    end_time: float = 0

    _provider: ClassVar[str] = "NO PROVIDER"

    def __init__(
        self,
        *,
        stream: Generator[tuple[_BaseCallResponseChunkT, _BaseToolT | None], None, None]
        | AsyncGenerator[
            tuple[_BaseCallResponseChunkT, _BaseToolT | None],
            None,
        ],
        metadata: Metadata,
        tool_types: list[type[_BaseToolT]] | None,
        call_response_type: type[_BaseCallResponseT],
        model: str,
        prompt_template: str | None,
        fn_args: dict[str, Any],
        dynamic_config: _BaseDynamicConfigT,
        messages: list[_MessageParamT],
        call_params: _BaseCallParamsT,
        call_kwargs: BaseCallKwargs[_ToolSchemaT],
    ) -> None:
        """Initializes an instance of `BaseStream`."""
        self.content = ""
        self.stream = stream
        self.metadata = metadata
        self.tool_types = tool_types
        self.call_response_type = call_response_type
        self.model = model
        self.prompt_template = prompt_template
        self.fn_args = fn_args
        self.dynamic_config = dynamic_config
        self.messages = messages
        self.call_params = call_params
        self.call_kwargs = call_kwargs
        self.user_message_param = get_possible_user_message_param(messages)  # pyright: ignore [reportAttributeAccessIssue]

    def __iter__(
        self,
    ) -> Generator[tuple[_BaseCallResponseChunkT, _BaseToolT | None], None, None]:
        """Iterator over the stream and stores useful information."""
        assert isinstance(self.stream, Generator), (
            "Stream must be a generator for __iter__"
        )
        self.content, tool_calls = "", []
        self.start_time = datetime.datetime.now().timestamp() * 1000
        for chunk, tool in self.stream:
            self._update_properties(chunk)
            if tool:
                tool_call = getattr(tool, "tool_call", _DEFAULT)
                if tool_call != _DEFAULT:
                    tool_calls.append(tool_call)
            yield chunk, tool
        self.end_time = datetime.datetime.now().timestamp() * 1000
        self.message_param = self._construct_message_param(
            tool_calls or None, self.content
        )

    def __aiter__(
        self,
    ) -> AsyncGenerator[tuple[_BaseCallResponseChunkT, _BaseToolT | None], None]:
        """Iterates over the stream and stores useful information."""
        self.content = ""

        async def generator() -> AsyncGenerator[
            tuple[_BaseCallResponseChunkT, _BaseToolT | None], None
        ]:
            assert isinstance(self.stream, AsyncGenerator), (
                "Stream must be an async generator for __aiter__"
            )
            tool_calls = []
            async for chunk, tool in self.stream:
                self._update_properties(chunk)
                if tool:
                    tool_call = getattr(tool, "tool_call", _DEFAULT)
                    if tool_call != _DEFAULT:
                        tool_calls.append(tool_call)
                yield chunk, tool
            self.message_param = self._construct_message_param(
                tool_calls or None, self.content
            )

        return generator()

    def _update_properties(self, chunk: _BaseCallResponseChunkT) -> None:
        """Updates the properties of the stream."""
        self.content += chunk.content
        if chunk.input_tokens is not None:
            self.input_tokens = (
                chunk.input_tokens
                if not self.input_tokens
                else self.input_tokens + chunk.input_tokens
            )
        if chunk.cached_tokens is not None:
            self.cached_tokens = (
                chunk.cached_tokens
                if not self.cached_tokens
                else self.cached_tokens + chunk.cached_tokens
            )
        if chunk.output_tokens is not None:
            self.output_tokens = (
                chunk.output_tokens
                if not self.output_tokens
                else self.output_tokens + chunk.output_tokens
            )
        if chunk.model is not None:
            self.model = chunk.model
        if chunk.id is not None:
            self.id = chunk.id
        if chunk.finish_reasons is not None:
            self.finish_reasons = chunk.finish_reasons

    @property
    def provider(self) -> Provider:
        return cast(Provider, self._provider)

    @property
    def cost_metadata(self) -> CostMetadata:
        """Returns metadata needed for cost calculation."""
        return CostMetadata(
            input_tokens=self.input_tokens,
            output_tokens=self.output_tokens,
            cached_tokens=self.cached_tokens,
        )

    @property
    def cost(self) -> float | None:
        """Calculate the cost of this streaming API call."""

        if self.input_tokens is None or self.output_tokens is None:
            return None

        return calculate_cost(
            provider=self.provider,
            model=self.model,
            metadata=self.cost_metadata,
        )

    @abstractmethod
    def _construct_message_param(
        self, tool_calls: list[Any] | None = None, content: str | None = None
    ) -> _AssistantMessageParamT:
        """Constructs the assistant message."""
        ...

    def tool_message_params(
        self, tools_and_outputs: list[tuple[_BaseToolT, JsonableType]]
    ) -> list[_ToolMessageParamT]:
        """Returns the tool message parameters for tool call results.

        Args:
            tools_and_outputs: The list of tools and their outputs from which the tool
                message parameters should be constructed.
        """
        return self.call_response_type.tool_message_params(tools_and_outputs)

    @abstractmethod
    def construct_call_response(self) -> _BaseCallResponseT:
        """Constructs the call response."""
        ...


_SameSyncAndAsyncClientT = TypeVar("_SameSyncAndAsyncClientT", contravariant=True)
_SyncBaseClientT = TypeVar("_SyncBaseClientT", contravariant=True)
_AsyncBaseClientT = TypeVar("_AsyncBaseClientT", contravariant=True)
_ResponseT = TypeVar("_ResponseT")
_ResponseChunkT = TypeVar("_ResponseChunkT")
_AsyncResponseT = TypeVar("_AsyncResponseT")
_AsyncResponseChunkT = TypeVar("_AsyncResponseChunkT")
_P = ParamSpec("_P")


def stream_factory(  # noqa: ANN201
    *,
    TCallResponse: type[_BaseCallResponseT],
    TStream: type[BaseStream],
    setup_call: SameSyncAndAsyncClientSetupCall[
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
    | SetupCall[
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
    ],
    handle_stream: HandleStream[_ResponseChunkT, _BaseCallResponseChunkT, _BaseToolT],
    handle_stream_async: HandleStreamAsync[
        _AsyncResponseChunkT, _BaseCallResponseChunkT, _BaseToolT
    ],
):
    @overload
    def decorator(
        fn: Callable[_P, _BaseDynamicConfigT],
        model: str,
        tools: list[type[BaseTool] | Callable] | None,
        json_mode: bool,
        client: _SameSyncAndAsyncClientT | _SyncBaseClientT | None,
        call_params: _BaseCallParamsT,
        partial_tools: bool,
    ) -> Callable[_P, BaseStream]: ...

    @overload
    def decorator(
        fn: Callable[_P, Messages.Type],
        model: str,
        tools: list[type[BaseTool] | Callable] | None,
        json_mode: bool,
        client: _SameSyncAndAsyncClientT | _SyncBaseClientT | None,
        call_params: _BaseCallParamsT,
        partial_tools: bool,
    ) -> Callable[_P, BaseStream]: ...

    @overload
    def decorator(
        fn: Callable[
            _P,
            Awaitable[_AsyncBaseDynamicConfigT]
            | Coroutine[Any, Any, _AsyncBaseDynamicConfigT],
        ],
        model: str,
        tools: list[type[BaseTool] | Callable] | None,
        json_mode: bool,
        client: _SameSyncAndAsyncClientT | _AsyncBaseClientT | None,
        call_params: _BaseCallParamsT,
        partial_tools: bool,
    ) -> Callable[_P, Awaitable[BaseStream]]: ...

    @overload
    def decorator(
        fn: Callable[_P, Awaitable[Messages.Type] | Coroutine[Any, Any, Messages.Type]],
        model: str,
        tools: list[type[BaseTool] | Callable] | None,
        json_mode: bool,
        client: _SameSyncAndAsyncClientT | _AsyncBaseClientT | None,
        call_params: _BaseCallParamsT,
        partial_tools: bool,
    ) -> Callable[_P, Awaitable[BaseStream]]: ...

    def decorator(
        fn: Callable[_P, _BaseDynamicConfigT]
        | Callable[_P, Messages.Type]
        | Callable[
            _P,
            Awaitable[_AsyncBaseDynamicConfigT]
            | Coroutine[Any, Any, _AsyncBaseDynamicConfigT],
        ]
        | Callable[_P, Awaitable[Messages.Type] | Coroutine[Any, Any, Messages.Type]],
        model: str,
        tools: list[type[BaseTool] | Callable] | None,
        json_mode: bool,
        client: _SameSyncAndAsyncClientT | _SyncBaseClientT | _AsyncBaseClientT | None,
        call_params: _BaseCallParamsT,
        partial_tools: bool = False,
    ) -> Callable[_P, BaseStream] | Callable[_P, Awaitable[BaseStream]]:
        if not is_prompt_template(fn):
            fn = cast(
                Callable[_P, Messages.Type] | Callable[_P, Awaitable[Messages.Type]], fn
            )
            fn = prompt_template()(fn)
            fn = cast(
                Callable[_P, _BaseDynamicConfigT]
                | Callable[_P, Awaitable[_AsyncBaseDynamicConfigT]],
                fn,
            )
        fn._model = model  # pyright: ignore [reportFunctionMemberAccess]
        fn.__mirascope_call__ = True  # pyright: ignore [reportFunctionMemberAccess]
        if fn_is_async(fn):

            @wraps(fn)
            async def inner_async(*args: _P.args, **kwargs: _P.kwargs) -> BaseStream:
                fn_args = get_fn_args(fn, args, kwargs)
                dynamic_config = await get_dynamic_configuration(fn, args, kwargs)
                nonlocal client
                if dynamic_config is not None:
                    client = dynamic_config.get("client", None) or client
                create, prompt_template, messages, tool_types, call_kwargs = setup_call(  # pyright: ignore [reportCallIssue]
                    model=model,
                    client=client,  # pyright: ignore [reportArgumentType]
                    fn=fn,
                    fn_args=fn_args,
                    dynamic_config=dynamic_config,
                    tools=tools,
                    json_mode=json_mode,
                    call_params=call_params,
                    response_model=None,
                    stream=True,
                )

                async def generator() -> AsyncGenerator[
                    tuple[_BaseCallResponseChunkT, _BaseToolT | None], None
                ]:
                    async for chunk, tool in handle_stream_async(
                        await create(stream=True, **call_kwargs),
                        tool_types,
                        partial_tools=partial_tools,
                    ):
                        yield chunk, tool

                return TStream(
                    stream=generator(),
                    metadata=get_metadata(fn, dynamic_config),
                    tool_types=tool_types,  # pyright: ignore [reportArgumentType]
                    call_response_type=TCallResponse,
                    model=model,
                    prompt_template=prompt_template,
                    fn_args=fn_args,
                    dynamic_config=dynamic_config,
                    messages=messages,
                    call_params=call_params,
                    call_kwargs=call_kwargs,
                )

            return inner_async
        else:

            @wraps(fn)
            def inner(*args: _P.args, **kwargs: _P.kwargs) -> BaseStream:
                fn_args = get_fn_args(fn, args, kwargs)
                dynamic_config = get_dynamic_configuration(fn, args, kwargs)
                nonlocal client
                if dynamic_config is not None:
                    client = dynamic_config.get("client", None) or client
                create, prompt_template, messages, tool_types, call_kwargs = setup_call(  # pyright: ignore [reportCallIssue]
                    model=model,
                    client=client,  # pyright: ignore [reportArgumentType]
                    fn=fn,
                    fn_args=fn_args,
                    dynamic_config=dynamic_config,
                    tools=tools,
                    json_mode=json_mode,
                    call_params=call_params,
                    response_model=None,
                    stream=True,
                )

                def generator() -> Generator[
                    tuple[_BaseCallResponseChunkT, _BaseToolT | None],
                    None,
                    None,
                ]:
                    yield from handle_stream(
                        create(stream=True, **call_kwargs),
                        tool_types,
                        partial_tools=partial_tools,
                    )

                return TStream(
                    stream=generator(),
                    metadata=get_metadata(fn, dynamic_config),
                    tool_types=tool_types,  # pyright: ignore [reportArgumentType]
                    call_response_type=TCallResponse,
                    model=model,
                    prompt_template=prompt_template,
                    fn_args=fn_args,
                    dynamic_config=dynamic_config,
                    messages=messages,
                    call_params=call_params,
                    call_kwargs=call_kwargs,
                )

            return inner

    return decorator
