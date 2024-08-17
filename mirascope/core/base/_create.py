"""The `create_factory` method for generating provider specific create decorators."""

import datetime
import inspect
from functools import wraps
from typing import Awaitable, Callable, ParamSpec, TypeVar, overload

from ._utils import (
    SetupCall,
    get_fn_args,
    get_metadata,
    get_possible_user_message_param,
)
from .call_params import BaseCallParams
from .call_response import BaseCallResponse
from .dynamic_config import BaseDynamicConfig
from .tool import BaseTool

_BaseCallResponseT = TypeVar("_BaseCallResponseT", bound=BaseCallResponse)
_BaseClientT = TypeVar("_BaseClientT", bound=object)
_BaseDynamicConfigT = TypeVar("_BaseDynamicConfigT", bound=BaseDynamicConfig)
_ParsedOutputT = TypeVar("_ParsedOutputT")
_BaseCallParamsT = TypeVar("_BaseCallParamsT", bound=BaseCallParams)
_ResponseT = TypeVar("_ResponseT")
_ResponseChunkT = TypeVar("_ResponseChunkT")
_BaseToolT = TypeVar("_BaseToolT", bound=BaseTool)
_P = ParamSpec("_P")


def create_factory(
    *,
    TCallResponse: type[_BaseCallResponseT],
    setup_call: SetupCall[
        _BaseClientT,
        _BaseDynamicConfigT,
        _BaseCallParamsT,
        _ResponseT,
        _ResponseChunkT,
        _BaseToolT,
    ],
):
    """Returns the wrapped function with the provider specific interfaces."""

    @overload
    def decorator(
        fn: Callable[_P, _BaseDynamicConfigT],
        model: str,
        tools: list[type[BaseTool] | Callable] | None,
        output_parser: Callable[[_BaseCallResponseT], _ParsedOutputT] | None,
        json_mode: bool,
        client: _BaseClientT | None,
        call_params: _BaseCallParamsT,
    ) -> Callable[_P, _BaseCallResponseT | _ParsedOutputT]: ...  # pragma: no cover

    @overload
    def decorator(
        fn: Callable[_P, Awaitable[_BaseDynamicConfigT]],
        model: str,
        tools: list[type[BaseTool] | Callable] | None,
        output_parser: Callable[[_BaseCallResponseT], _ParsedOutputT] | None,
        json_mode: bool,
        client: _BaseClientT | None,
        call_params: _BaseCallParamsT,
    ) -> Callable[
        _P,
        Awaitable[_BaseCallResponseT | _ParsedOutputT],
    ]: ...  # pragma: no cover

    def decorator(
        fn: Callable[_P, _BaseDynamicConfigT | Awaitable[_BaseDynamicConfigT]],
        model: str,
        tools: list[type[BaseTool] | Callable] | None,
        output_parser: Callable[[_BaseCallResponseT], _ParsedOutputT] | None,
        json_mode: bool,
        client: _BaseClientT | None,
        call_params: _BaseCallParamsT,
    ) -> Callable[
        _P,
        _BaseCallResponseT
        | _ParsedOutputT
        | Awaitable[_BaseCallResponseT | _ParsedOutputT],
    ]:
        is_async = inspect.iscoroutinefunction(fn)

        @wraps(fn)
        def inner(
            *args: _P.args, **kwargs: _P.kwargs
        ) -> TCallResponse | _ParsedOutputT:
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
            start_time = datetime.datetime.now().timestamp() * 1000
            response = create(stream=False, **call_kwargs)
            end_time = datetime.datetime.now().timestamp() * 1000
            output = TCallResponse(
                metadata=get_metadata(fn, dynamic_config),
                response=response,
                tool_types=tool_types,  # type: ignore
                prompt_template=prompt_template,
                fn_args=fn_args,
                dynamic_config=dynamic_config,
                messages=messages,
                call_params=call_params,
                call_kwargs=call_kwargs,
                user_message_param=get_possible_user_message_param(messages),
                start_time=start_time,
                end_time=end_time,
            )
            output._model = model
            return output if not output_parser else output_parser(output)

        @wraps(fn)
        async def inner_async(
            *args: _P.args, **kwargs: _P.kwargs
        ) -> TCallResponse | _ParsedOutputT:
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
            start_time = datetime.datetime.now().timestamp() * 1000
            response = await create(stream=False, **call_kwargs)
            end_time = datetime.datetime.now().timestamp() * 1000
            output = TCallResponse(
                metadata=get_metadata(fn, dynamic_config),
                response=response,
                tool_types=tool_types,  # type: ignore
                prompt_template=prompt_template,
                fn_args=fn_args,
                dynamic_config=dynamic_config,
                messages=messages,
                call_params=call_params,
                call_kwargs=call_kwargs,
                user_message_param=get_possible_user_message_param(messages),
                start_time=start_time,
                end_time=end_time,
            )
            output._model = model
            return output if not output_parser else output_parser(output)

        return inner_async if is_async else inner

    return decorator
