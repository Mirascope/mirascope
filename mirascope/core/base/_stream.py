"""This module contains the base classes for streaming responses from LLMs."""

import inspect
from abc import ABC
from collections.abc import AsyncGenerator, Generator
from functools import wraps
from typing import Any, Awaitable, Callable, Generic, ParamSpec, TypeVar, overload

from ._utils import get_fn_args
from .call_params import BaseCallParams
from .call_response_chunk import BaseCallResponseChunk
from .dynamic_config import BaseDynamicConfig
from .tool import BaseTool

_BaseCallResponseChunkT = TypeVar(
    "_BaseCallResponseChunkT", bound=BaseCallResponseChunk
)
_UserMessageParamT = TypeVar("_UserMessageParamT")
_AssistantMessageParamT = TypeVar("_AssistantMessageParamT")
_MessageParamT = TypeVar("_MessageParamT")
_BaseToolT = TypeVar("_BaseToolT", bound=BaseTool)
_CallParamsT = TypeVar("_CallParamsT", bound=BaseCallParams)
_BaseDynamicConfigT = TypeVar("_BaseDynamicConfigT", bound=BaseDynamicConfig)


class BaseStream(
    Generic[
        _BaseCallResponseChunkT,
        _UserMessageParamT,
        _AssistantMessageParamT,
        _MessageParamT,
        _BaseToolT,
        _BaseDynamicConfigT,
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
    tags: list[str]
    tools_types: list[type[_BaseToolT]] | None
    message_param_type: type[_AssistantMessageParamT]
    model: str | None = None
    cost: float | None = None
    prompt_template: str | None = None
    fn_args: dict[str, Any] | None = None
    dynamic_config: _BaseDynamicConfigT
    messages: list[_MessageParamT]
    call_params: _CallParamsT
    input_tokens: int | float | None = None
    output_tokens: int | float | None = None
    user_message_param: _UserMessageParamT | None = None
    message_param: _AssistantMessageParamT
    provider: str

    def __init__(
        self,
        stream: Generator[tuple[_BaseCallResponseChunkT, _BaseToolT | None], None, None]
        | AsyncGenerator[
            tuple[_BaseCallResponseChunkT, _BaseToolT | None],
            None,
        ],
        *,
        tags: list[str],
        tool_types: list[type[_BaseToolT]] | None,
        message_param_type: type[_AssistantMessageParamT],
        model: str,
        cost: float | None,
        prompt_template: str,
        fn_args: dict[str, Any],
        dynamic_config: _BaseDynamicConfigT,
        messages: list[_MessageParamT],
        call_params: _CallParamsT,
        user_message_param: _UserMessageParamT | None,
    ):
        """Initializes an instance of `BaseStream`."""
        self.stream = stream
        self.tags = tags
        self.tool_types = tool_types
        self.message_param_type = message_param_type
        self.model = model
        self.cost = cost
        self.prompt_template = prompt_template
        self.fn_args = fn_args
        self.dynamic_config = dynamic_config
        self.messages = messages
        self.call_params = call_params
        self.user_message_param = user_message_param

    def __iter__(
        self,
    ) -> Generator[tuple[_BaseCallResponseChunkT, _BaseToolT | None], None, None]:
        """Iterator over the stream and stores useful information."""
        assert isinstance(
            self.stream, Generator
        ), "Stream must be a generator for __iter__"
        content, tool_calls = "", []
        for chunk, tool in self.stream:
            content += chunk.content
            if chunk.input_tokens is not None:
                self.input_tokens = chunk.input_tokens
            if chunk.output_tokens is not None:
                self.output_tokens = chunk.output_tokens
            if chunk.model is not None:
                self.model = chunk.model
            if tool:
                tool_calls.append(tool.tool_call)  # type: ignore
            yield chunk, tool
        kwargs = {"role": "assistant"}
        if "message" in self.message_param_type.__annotations__:
            kwargs["message"] = content
        else:
            kwargs["content"] = content
        if tool_calls:
            kwargs["tool_calls"] = tool_calls
        self.message_param = self.message_param_type(**kwargs)

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
                if chunk.input_tokens is not None:
                    self.input_tokens = chunk.input_tokens
                if chunk.output_tokens is not None:
                    self.output_tokens = chunk.output_tokens
                if chunk.model is not None:
                    self.model = chunk.model
                if tool:
                    tool_calls.append(tool.tool_call)  # type: ignore
                yield chunk, None
            kwargs = {"role": "assistant"}
            if "message" in self.message_param_type.__annotations__:
                kwargs["message"] = content
                if tool_calls:
                    kwargs["tool_calls"] = tool_calls
            else:
                kwargs["content"] = content
                if tool_calls:
                    kwargs["content"] = [kwargs["content"]] + tool_calls
            self.message_param = self.message_param_type(**kwargs)

        return generator()


_BaseCallResponseChunkT = TypeVar(
    "_BaseCallResponseChunkT", bound=BaseCallResponseChunk
)
_BaseDynamicConfigT = TypeVar("_BaseDynamicConfigT", bound=BaseDynamicConfig)
_BaseClientT = TypeVar("_BaseClientT", bound=object)
_BaseCallParamsT = TypeVar("_BaseCallParamsT", bound=BaseCallParams)
_ResponseT = TypeVar("_ResponseT")
_P = ParamSpec("_P")


def stream_factory(
    TCallResponseChunk: type[_BaseCallResponseChunkT],
    TStream: type[BaseStream],
    TMessageParamType: type[_AssistantMessageParamT],
    setup_call: Callable[
        [
            str,
            _BaseClientT,
            Callable[_P, _BaseDynamicConfigT | Awaitable[_BaseDynamicConfigT]],
            dict[str, Any],
            _BaseDynamicConfigT,
            list[type[BaseTool] | Callable] | None,
            _BaseCallParamsT,
            bool,
        ],
        tuple[
            Callable[..., _ResponseT],
            str,
            list[dict[str, Any]],
            list[type[BaseTool]],
            dict[str, Any],
        ],
    ],
    handle_stream: Callable[
        [Generator[_BaseCallResponseChunkT, None, None], list[type[_BaseToolT]]],
        Generator[tuple[_BaseCallResponseChunkT, _BaseToolT], None, None],
    ],
    handle_stream_async: Callable[
        [AsyncGenerator[_BaseCallResponseChunkT, None], list[type[_BaseToolT]]],
        Awaitable[AsyncGenerator[tuple[_BaseCallResponseChunkT, _BaseToolT], None]],
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
        fn: Callable[_P, _BaseDynamicConfigT],
        model: str,
        tools: list[type[BaseTool] | Callable] | None,
        json_mode: bool,
        client: _BaseClientT | None,
        call_params: _BaseCallParamsT,
    ) -> Callable[_P, TStream | Awaitable[TStream]]:
        is_async = inspect.iscoroutinefunction(fn)

        @wraps(fn)
        def inner(*args: _P.args, **kwargs: _P.kwargs) -> TStream:
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
                    yield TCallResponseChunk(chunk=chunk), tool

            return TStream(
                generator(),
                tags=fn.__annotations__.get("tags", []),
                tool_types=tool_types,
                message_param_type=TMessageParamType,
                model=model,
                cost=None,
                prompt_template=prompt_template,
                fn_args=fn_args,
                dynamic_config=dynamic_config,
                messages=messages,
                call_params=call_params,
                user_message_param=messages[-1]
                if messages[-1]["role"] == "user"
                else None,
            )

        @wraps(fn)
        async def inner_async(*args: _P.args, **kwargs: _P.kwargs) -> TStream:
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
                    yield TCallResponseChunk(chunk=chunk), tool

            return TStream(
                generator(),
                tags=fn.__annotations__.get("tags", []),
                tool_types=tool_types,
                message_param_type=TMessageParamType,
                model=model,
                cost=None,
                prompt_template=prompt_template,
                fn_args=fn_args,
                dynamic_config=dynamic_config,
                messages=messages,
                call_params=call_params,
                user_message_param=messages[-1]
                if messages[-1]["role"] == "user"
                else None,
            )

        return inner_async if is_async else inner

    return decorator
