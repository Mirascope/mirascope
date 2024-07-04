"""The `extract_factory` method for generating provider specific create decorators."""

import datetime
import inspect
from functools import wraps
from typing import Awaitable, Callable, ParamSpec, TypeVar, overload

from pydantic import BaseModel, ValidationError

from ._utils import (
    BaseType,
    CalculateCost,
    GetJsonOutput,
    SetupCall,
    extract_tool_return,
    get_fn_args,
    get_tags,
    setup_extract_tool,
)
from .call_params import BaseCallParams
from .call_response import BaseCallResponse
from .dynamic_config import BaseDynamicConfig
from .tool import BaseTool

_BaseCallResponseT = TypeVar("_BaseCallResponseT", bound=BaseCallResponse)
_BaseClientT = TypeVar("_BaseClientT", bound=object)
_BaseDynamicConfigT = TypeVar("_BaseDynamicConfigT", bound=BaseDynamicConfig)
_BaseCallParamsT = TypeVar("_BaseCallParamsT", bound=BaseCallParams)
_ResponseT = TypeVar("_ResponseT")
_ResponseChunkT = TypeVar("_ResponseChunkT")
_BaseToolT = TypeVar("_BaseToolT", bound=BaseTool)
_ResponseModelT = TypeVar("_ResponseModelT", bound=BaseModel | BaseType)
_P = ParamSpec("_P")


def extract_factory(
    *,
    TCallResponse: type[_BaseCallResponseT],
    TToolType: type[BaseTool],
    setup_call: SetupCall[
        _BaseClientT,
        _BaseDynamicConfigT,
        _BaseCallParamsT,
        _ResponseT,
        _ResponseChunkT,
        _BaseToolT,
    ],
    get_json_output: GetJsonOutput[_BaseCallResponseT],
    calculate_cost: CalculateCost[_ResponseT],
):
    """Returns the wrapped function with the provider specific interfaces."""

    @overload
    def decorator(
        fn: Callable[_P, _BaseDynamicConfigT],
        model: str,
        response_model: type[_ResponseModelT],
        json_mode: bool,
        client: _BaseClientT | None,
        call_params: _BaseCallParamsT,
    ) -> Callable[_P, _ResponseModelT]: ...  # pragma: no cover

    @overload
    def decorator(
        fn: Callable[_P, Awaitable[_BaseDynamicConfigT]],
        model: str,
        response_model: type[_ResponseModelT],
        json_mode: bool,
        client: _BaseClientT | None,
        call_params: _BaseCallParamsT,
    ) -> Callable[_P, Awaitable[_ResponseModelT]]: ...  # pragma: no cover

    def decorator(
        fn: Callable[_P, _BaseDynamicConfigT | Awaitable[_BaseDynamicConfigT]],
        model: str,
        response_model: type[_ResponseModelT],
        json_mode: bool,
        client: _BaseClientT | None,
        call_params: _BaseCallParamsT,
    ) -> Callable[_P, _ResponseModelT | Awaitable[_ResponseModelT]]:
        tool = setup_extract_tool(response_model, TToolType)
        is_async = inspect.iscoroutinefunction(fn)

        @wraps(fn)
        def inner(*args: _P.args, **kwargs: _P.kwargs) -> _ResponseModelT:
            assert SetupCall.fn_is_sync(fn)
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
            start_time = datetime.datetime.now().timestamp() * 1000
            response = create(stream=False, **call_kwargs)
            end_time = datetime.datetime.now().timestamp() * 1000
            call_response = TCallResponse(
                tags=get_tags(fn, dynamic_config),
                response=response,
                tool_types=tool_types,
                prompt_template=prompt_template,
                fn_args=fn_args,
                dynamic_config=dynamic_config,
                messages=messages,
                call_params=call_kwargs,
                user_message_param=messages[-1]
                if messages[-1]["role"] == "user"
                else None,
                start_time=start_time,
                end_time=end_time,
                cost=calculate_cost(response, model),
            )
            json_output = get_json_output(call_response, json_mode)
            try:
                output = extract_tool_return(response_model, json_output, False)
            except ValidationError as e:
                e._response = call_response  # type: ignore
                raise e
            if isinstance(output, BaseModel):
                output._response = call_response  # type: ignore
            return output  # type: ignore

        @wraps(fn)
        async def inner_async(*args: _P.args, **kwargs: _P.kwargs) -> _ResponseModelT:
            assert SetupCall.fn_is_async(fn)
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
            start_time = datetime.datetime.now().timestamp() * 1000
            response = await create(stream=False, **call_kwargs)
            end_time = datetime.datetime.now().timestamp() * 1000
            call_response = TCallResponse(
                tags=get_tags(fn, dynamic_config),
                response=response,
                tool_types=tool_types,
                prompt_template=prompt_template,
                fn_args=fn_args,
                dynamic_config=dynamic_config,
                messages=messages,
                call_params=call_kwargs,
                user_message_param=messages[-1]
                if messages[-1]["role"] == "user"
                else None,
                start_time=start_time,
                end_time=end_time,
                cost=calculate_cost(response, model),
            )
            json_output = get_json_output(call_response, json_mode)
            output = extract_tool_return(response_model, json_output, False)
            if isinstance(output, BaseModel):
                output._response = call_response  # type: ignore
            return output  # type: ignore

        return inner_async if is_async else inner

    return decorator
