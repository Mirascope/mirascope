"""This module defines the base class for structured streams."""

import inspect
from collections.abc import AsyncGenerator, Generator
from functools import wraps
from typing import Any, Awaitable, Callable, Generic, ParamSpec, TypeVar, overload

from pydantic import BaseModel

from ._utils import BaseType, extract_tool_return, get_fn_args, setup_extract_tool
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
_ResponseModelT = TypeVar("_ResponseModelT", bound=BaseModel | BaseType)


class BaseStructuredStream(Generic[_ResponseModelT]):
    """A base class for streaming structured outputs from LLMs."""

    stream: (
        Generator[_BaseCallResponseChunkT, None, None]
        | AsyncGenerator[_BaseCallResponseChunkT, None]
    )
    response_model: type[_ResponseModelT]
    json_mode: bool
    get_json_output: Callable
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
    user_message_param: _UserMessageParamT | None = None
    message_param: _AssistantMessageParamT
    provider: str

    def __init__(
        self,
        stream: Generator[_BaseCallResponseChunkT, None, None],
        *,
        response_model: type[_ResponseModelT],
        json_mode: bool,
        get_json_output: Callable,
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
        """Initializes an instance of `BaseStructuredStream`."""
        self.stream = stream
        self.response_model = response_model
        self.json_mode = json_mode
        self.get_json_output = get_json_output
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

    def __iter__(self) -> Generator[_ResponseModelT, None, None]:
        """Iterates over the stream and extracts structured outputs."""
        assert isinstance(
            self.stream, Generator
        ), "Stream must be a generator for __iter__"
        json_output = ""
        for chunk in self.stream:
            json_output += self.get_json_output(chunk, self.json_mode)
            if json_output and json_output[0] != "{":
                try:
                    json_start = json_output.index("{")
                    json_output = json_output[json_start:]
                except ValueError:
                    json_output = ""
            if chunk.model is not None:
                self.model = chunk.model
            if json_output:
                yield extract_tool_return(self.response_model, json_output, True)
        if json_output:
            json_output = json_output[: json_output.rfind("}") + 1]
        yield extract_tool_return(self.response_model, json_output, False)
        kwargs = {"role": "assistant"}
        if "message" in self.message_param_type.__annotations__:
            kwargs["message"] = json_output
        else:
            kwargs["content"] = json_output
        self.message_param = self.message_param_type(**kwargs)

    def __aiter__(self) -> AsyncGenerator[_ResponseModelT, None]:
        """Iterates over the stream and extracts structured outputs."""

        async def generator():
            assert isinstance(
                self.stream, AsyncGenerator
            ), "Stream must be an async generator for __aiter__"
            json_output = ""
            async for chunk in self.stream:
                json_output += self.get_json_output(chunk, self.json_mode)
                if json_output and json_output[0] != "{":
                    try:
                        json_start = json_output.index("{")
                        json_output = json_output[json_start:]
                    except ValueError:
                        json_output = ""
                if chunk.model is not None:
                    self.model = chunk.model
                if json_output:
                    yield extract_tool_return(self.response_model, json_output, True)
            if json_output:
                json_output = json_output[: json_output.rfind("}") + 1]
            yield extract_tool_return(self.response_model, json_output, False)
            kwargs = {"role": "assistant"}
            if "message" in self.message_param_type.__annotations__:
                kwargs["message"] = json_output
            else:
                kwargs["content"] = json_output
            self.message_param = self.message_param_type(**kwargs)

        return generator()


_BaseDynamicConfigT = TypeVar("_BaseDynamicConfigT", bound=BaseDynamicConfig)
_BaseClientT = TypeVar("_BaseClientT", bound=object)
_BaseCallParamsT = TypeVar("_BaseCallParamsT", bound=BaseCallParams)
_ResponseT = TypeVar("_ResponseT")
_P = ParamSpec("_P")


def structured_stream_factory(
    *,
    TCallResponseChunk: type[_BaseCallResponseChunkT],
    TMessageParamType: type[_AssistantMessageParamT],
    TToolType: type[BaseTool],
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
    get_json_output: Callable,
):
    @overload
    def decorator(
        fn: Callable[_P, _BaseDynamicConfigT],
        model: str,
        response_model: type[_ResponseModelT],
        json_mode: bool,
        client: _BaseClientT | None,
        call_params: _BaseCallParamsT,
    ) -> Callable[_P, BaseStructuredStream[_ResponseModelT]]: ...  # pragma: no cover

    @overload
    def decorator(
        fn: Callable[_P, Awaitable[_BaseDynamicConfigT]],
        model: str,
        response_model: type[_ResponseModelT],
        json_mode: bool,
        client: _BaseClientT | None,
        call_params: _BaseCallParamsT,
    ) -> Callable[
        _P, Awaitable[BaseStructuredStream[_ResponseModelT]]
    ]: ...  # pragma: no cover

    def decorator(
        fn: Callable[_P, _BaseDynamicConfigT | Awaitable[_BaseDynamicConfigT]],
        model: str,
        response_model: type[_ResponseModelT],
        json_mode: bool,
        client: _BaseClientT | None,
        call_params: _BaseCallParamsT,
    ) -> Callable[
        _P,
        BaseStructuredStream[_ResponseModelT]
        | Awaitable[BaseStructuredStream[_ResponseModelT]],
    ]:
        tool = setup_extract_tool(response_model, TToolType)
        is_async = inspect.iscoroutinefunction(fn)

        @wraps(fn)
        def inner(
            *args: _P.args, **kwargs: _P.kwargs
        ) -> BaseStructuredStream[_ResponseModelT]:
            fn_args = get_fn_args(fn, args, kwargs)
            dynamic_config = fn(*args, **kwargs)
            create, prompt_template, messages, tool_types, call_kwargs = setup_call(
                model=model,
                client=client,
                fn=fn,
                fn_args=fn_args,
                dynamic_config=dynamic_config,
                tools=[tool],
                json_mode=json_mode,
                call_params=call_params,
                extract=True,
            )
            stream = create(stream=True, **call_kwargs)
            return BaseStructuredStream[response_model](
                (TCallResponseChunk(chunk=chunk) for chunk in stream),
                response_model=response_model,
                json_mode=json_mode,
                get_json_output=get_json_output,
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

        async def inner_async(
            *args: _P.args, **kwargs: _P.kwargs
        ) -> BaseStructuredStream[_ResponseModelT]:
            fn_args = get_fn_args(fn, args, kwargs)
            dynamic_config = await fn(*args, **kwargs)
            create, prompt_template, messages, tool_types, call_kwargs = setup_call(
                model=model,
                client=client,
                fn=fn,
                fn_args=fn_args,
                dynamic_config=dynamic_config,
                tools=[tool],
                json_mode=json_mode,
                call_params=call_params,
                extract=True,
            )
            stream = await create(stream=True, **call_kwargs)
            return BaseStructuredStream[response_model](
                (TCallResponseChunk(chunk=chunk) async for chunk in stream),
                response_model=response_model,
                json_mode=json_mode,
                get_json_output=get_json_output,
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
