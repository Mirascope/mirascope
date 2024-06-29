"""The `extract_factory` method for generating provider specific create decorators."""

import datetime
import inspect
from functools import wraps
from typing import Any, Awaitable, Callable, ParamSpec, TypeVar, overload

from pydantic import BaseModel

from . import _utils
from ._utils import BaseType, get_fn_args
from .call_params import BaseCallParams
from .call_response import BaseCallResponse
from .dynamic_config import BaseDynamicConfig
from .tool import BaseTool

_BaseCallResponseT = TypeVar("_BaseCallResponseT", bound=BaseCallResponse)
_BaseClientT = TypeVar("_BaseClientT", bound=object)
_BaseDynamicConfigT = TypeVar("_BaseDynamicConfigT", bound=BaseDynamicConfig)
_BaseCallParamsT = TypeVar("_BaseCallParamsT", bound=BaseCallParams)
_ResponseT = TypeVar("_ResponseT")
_ResponseModelT = TypeVar("_ResponseModelT", bound=BaseModel | BaseType)
_P = ParamSpec("_P")


def extract_factory(
    *,
    TCallResponse: type[_BaseCallResponseT],
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
    get_json_output: Callable[[_ResponseT, bool], str],
    calculate_cost: Callable[[_ResponseT, str], float],
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
        assert response_model is not None
        tool = _utils.setup_extract_tool(response_model, TToolType)
        is_async = inspect.iscoroutinefunction(fn)

        @wraps(fn)
        def inner(*args: _P.args, **kwargs: _P.kwargs) -> _ResponseModelT:
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
            response = create(**call_kwargs)
            end_time = datetime.datetime.now().timestamp() * 1000
            call_response = TCallResponse(
                tags=fn.__annotations__.get("tags", []),
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
            json_output = get_json_output(response, json_mode)
            output = _utils.extract_tool_return(response_model, json_output, False)
            if isinstance(output, BaseModel):
                output._response = call_response
            else:
                output = _utils.create_base_type_with_response(response_model)(output)
                output._response = call_response
            return output

        @wraps(fn)
        async def inner_async(*args: _P.args, **kwargs: _P.kwargs) -> _ResponseModelT:
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
            response = await create(**call_kwargs)
            end_time = datetime.datetime.now().timestamp() * 1000
            call_response = TCallResponse(
                tags=fn.__annotations__.get("tags", []),
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
            json_output = get_json_output(response, json_mode)
            output = _utils.extract_tool_return(response_model, json_output, False)
            if isinstance(output, BaseModel):
                output._response = call_response
            else:
                output = _utils.create_base_type_with_response(response_model)(output)
                output._response = call_response
            return output

        return inner_async if is_async else inner

    return decorator
