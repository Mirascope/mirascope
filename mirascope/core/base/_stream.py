"""This module contains the base classes for streaming responses from LLMs."""

import datetime
import inspect
from abc import ABC, abstractmethod
from collections.abc import AsyncGenerator, Generator
from functools import wraps
from typing import (
    Any,
    Awaitable,
    Callable,
    ClassVar,
    Generic,
    ParamSpec,
    TypeVar,
    overload,
)

from ._utils import (
    HandleStream,
    HandleStreamAsync,
    SetupCall,
    get_fn_args,
    get_metadata,
    get_possible_user_message_param,
)
from .call_params import BaseCallParams
from .call_response import BaseCallResponse
from .call_response_chunk import BaseCallResponseChunk
from .dynamic_config import BaseDynamicConfig
from .metadata import Metadata
from .tool import BaseTool

_BaseCallResponseT = TypeVar("_BaseCallResponseT", bound=BaseCallResponse)
_BaseCallResponseChunkT = TypeVar(
    "_BaseCallResponseChunkT", bound=BaseCallResponseChunk
)
_UserMessageParamT = TypeVar("_UserMessageParamT")
_AssistantMessageParamT = TypeVar("_AssistantMessageParamT")
_ToolMessageParamT = TypeVar("_ToolMessageParamT")
_MessageParamT = TypeVar("_MessageParamT")
_BaseToolT = TypeVar("_BaseToolT", bound=BaseTool)
_BaseCallParamsT = TypeVar("_BaseCallParamsT", bound=BaseCallParams)
_BaseDynamicConfigT = TypeVar("_BaseDynamicConfigT", bound=BaseDynamicConfig)
_FinishReason = TypeVar("_FinishReason")


class BaseStream(
    Generic[
        _BaseCallResponseT,
        _BaseCallResponseChunkT,
        _UserMessageParamT,
        _AssistantMessageParamT,
        _ToolMessageParamT,
        _MessageParamT,
        _BaseToolT,
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
    metadata: Metadata
    tool_types: list[type[_BaseToolT]] | None
    call_response_type: type[_BaseCallResponseT]
    model: str
    prompt_template: str | None = None
    fn_args: dict[str, Any] | None = None
    dynamic_config: _BaseDynamicConfigT
    messages: list[_MessageParamT]
    call_params: _BaseCallParamsT
    call_kwargs: dict[str, Any]
    user_message_param: _UserMessageParamT | None = None
    message_param: _AssistantMessageParamT
    input_tokens: int | float | None = None
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
        prompt_template: str,
        fn_args: dict[str, Any],
        dynamic_config: _BaseDynamicConfigT,
        messages: list[_MessageParamT],
        call_params: _BaseCallParamsT,
        call_kwargs: dict[str, Any],
    ):
        """Initializes an instance of `BaseStream`."""
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
        self.user_message_param = get_possible_user_message_param(messages)  # type: ignore

    def __iter__(
        self,
    ) -> Generator[tuple[_BaseCallResponseChunkT, _BaseToolT | None], None, None]:
        """Iterator over the stream and stores useful information."""
        assert isinstance(
            self.stream, Generator
        ), "Stream must be a generator for __iter__"
        content, tool_calls = "", []
        self.start_time = datetime.datetime.now().timestamp() * 1000
        for chunk, tool in self.stream:
            content += chunk.content
            self._update_properties(chunk)
            if tool:
                tool_calls.append(tool.tool_call)  # type: ignore
            yield chunk, tool
        self.end_time = datetime.datetime.now().timestamp() * 1000
        self.message_param = self._construct_message_param(tool_calls or None, content)

    def __aiter__(
        self,
    ) -> AsyncGenerator[tuple[_BaseCallResponseChunkT, _BaseToolT | None], None]:
        """Iterates over the stream and stores useful information."""

        async def generator():
            assert isinstance(
                self.stream, AsyncGenerator
            ), "Stream must be an async generator for __aiter__"
            content, tool_calls = "", []
            async for chunk, tool in self.stream:
                content += chunk.content
                self._update_properties(chunk)
                if tool:
                    tool_calls.append(tool.tool_call)  # type: ignore
                yield chunk, tool
            self.message_param = self._construct_message_param(
                tool_calls or None, content
            )

        return generator()

    def _update_properties(self, chunk: _BaseCallResponseChunkT):
        """Updates the properties of the stream."""
        if chunk.input_tokens is not None:
            self.input_tokens = (
                chunk.input_tokens
                if not self.input_tokens
                else self.input_tokens + chunk.input_tokens
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
    @abstractmethod
    def cost(self) -> float | None:
        """Returns the cost of the stream."""
        ...  # pragma: no cover

    @abstractmethod
    def _construct_message_param(
        self, tool_calls: list[Any] | None = None, content: str | None = None
    ) -> _AssistantMessageParamT:
        """Constructs the assistant message."""
        ...  # pragma: no cover

    def tool_message_params(self, tools_and_outputs) -> list[_ToolMessageParamT]:
        """Returns the tool message parameters for tool call results."""
        return self.call_response_type.tool_message_params(tools_and_outputs)

    @abstractmethod
    def construct_call_response(self) -> _BaseCallResponseT:
        """Constructs the call response."""
        ...  # pragma: no cover


_BaseCallResponseChunkT = TypeVar(
    "_BaseCallResponseChunkT", bound=BaseCallResponseChunk
)
_BaseDynamicConfigT = TypeVar("_BaseDynamicConfigT", bound=BaseDynamicConfig)
_BaseClientT = TypeVar("_BaseClientT", bound=object)
_BaseCallParamsT = TypeVar("_BaseCallParamsT", bound=BaseCallParams)
_ResponseT = TypeVar("_ResponseT")
_ResponseChunkT = TypeVar("_ResponseChunkT")
_P = ParamSpec("_P")


def stream_factory(
    *,
    TCallResponse: type[_BaseCallResponseT],
    TStream: type[BaseStream],
    setup_call: SetupCall[
        _BaseClientT,
        _BaseDynamicConfigT,
        _BaseCallParamsT,
        _ResponseT,
        _ResponseChunkT,
        _BaseToolT,
    ],
    handle_stream: HandleStream[_ResponseChunkT, _BaseCallResponseChunkT, _BaseToolT],
    handle_stream_async: HandleStreamAsync[
        _ResponseChunkT, _BaseCallResponseChunkT, _BaseToolT
    ],
):
    @overload
    def decorator(
        fn: Callable[_P, _BaseDynamicConfigT],
        model: str,
        tools: list[type[BaseTool] | Callable] | None,
        json_mode: bool,
        client: _BaseClientT | None,
        call_params: _BaseCallParamsT,
    ) -> Callable[_P, TStream]: ...  # pragma: no cover

    @overload
    def decorator(
        fn: Callable[_P, Awaitable[_BaseDynamicConfigT]],
        model: str,
        tools: list[type[BaseTool] | Callable] | None,
        json_mode: bool,
        client: _BaseClientT | None,
        call_params: _BaseCallParamsT,
    ) -> Callable[_P, Awaitable[TStream]]: ...  # pragma: no cover

    def decorator(
        fn: Callable[_P, _BaseDynamicConfigT | Awaitable[_BaseDynamicConfigT]],
        model: str,
        tools: list[type[BaseTool] | Callable] | None,
        json_mode: bool,
        client: _BaseClientT | None,
        call_params: _BaseCallParamsT,
    ) -> Callable[_P, TStream | Awaitable[TStream]]:
        is_async = inspect.iscoroutinefunction(fn)

        @wraps(fn)
        def inner(*args: _P.args, **kwargs: _P.kwargs) -> TStream:
            assert SetupCall.fn_is_sync(fn)
            fn_args = get_fn_args(fn, args, kwargs)
            dynamic_config = fn(*args, **kwargs)
            create, prompt_template, messages, tool_types, call_kwargs = setup_call(
                model=model,
                client=client,
                fn=fn,
                fn_args=fn_args,
                dynamic_config=dynamic_config,
                tools=tools,
                json_mode=json_mode,
                call_params=call_params,
                extract=False,
            )

            def generator():
                for chunk, tool in handle_stream(
                    create(stream=True, **call_kwargs), tool_types
                ):
                    yield chunk, tool

            return TStream(
                stream=generator(),
                metadata=get_metadata(fn, dynamic_config),
                tool_types=tool_types,  # type: ignore
                call_response_type=TCallResponse,
                model=model,
                prompt_template=prompt_template,
                fn_args=fn_args,
                dynamic_config=dynamic_config,
                messages=messages,
                call_params=call_params,
                call_kwargs=call_kwargs,
            )

        @wraps(fn)
        async def inner_async(*args: _P.args, **kwargs: _P.kwargs) -> TStream:
            assert SetupCall.fn_is_async(fn)
            fn_args = get_fn_args(fn, args, kwargs)
            dynamic_config = await fn(*args, **kwargs)
            create, prompt_template, messages, tool_types, call_kwargs = setup_call(
                model=model,
                client=client,
                fn=fn,
                fn_args=fn_args,
                dynamic_config=dynamic_config,
                tools=tools,
                json_mode=json_mode,
                call_params=call_params,
                extract=False,
            )

            async def generator():
                async for chunk, tool in handle_stream_async(
                    await create(stream=True, **call_kwargs), tool_types
                ):
                    yield chunk, tool

            return TStream(
                stream=generator(),
                metadata=get_metadata(fn, dynamic_config),
                tool_types=tool_types,  # type: ignore
                call_response_type=TCallResponse,
                model=model,
                prompt_template=prompt_template,
                fn_args=fn_args,
                dynamic_config=dynamic_config,
                messages=messages,
                call_params=call_params,
                call_kwargs=call_kwargs,
            )

        return inner_async if is_async else inner

    return decorator
