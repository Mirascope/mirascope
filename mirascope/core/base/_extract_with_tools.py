"""The `extract_with_tools_factory` method."""

from collections.abc import Awaitable, Callable
from functools import wraps
from typing import ParamSpec, TypeVar, overload

from pydantic import BaseModel

from ._create import create_factory
from ._utils import (
    BaseType,
    GetJsonOutput,
    SameSyncAndAsyncClientSetupCall,
    SetupCall,
    extract_tool_return,
    fn_is_async,
)
from ._utils._get_fields_from_call_args import get_fields_from_call_args
from .call_params import BaseCallParams
from .call_response import BaseCallResponse
from .dynamic_config import BaseDynamicConfig
from .tool import BaseTool

_BaseCallResponseT = TypeVar("_BaseCallResponseT", bound=BaseCallResponse)
_SameSyncAndAsyncClientT = TypeVar("_SameSyncAndAsyncClientT", contravariant=True)
_SyncBaseClientT = TypeVar("_SyncBaseClientT", contravariant=True)
_AsyncBaseClientT = TypeVar("_AsyncBaseClientT", contravariant=True)
_BaseDynamicConfigT = TypeVar("_BaseDynamicConfigT", bound=BaseDynamicConfig)
_AsyncBaseDynamicConfigT = TypeVar("_AsyncBaseDynamicConfigT", bound=BaseDynamicConfig)
_ParsedOutputT = TypeVar("_ParsedOutputT")
_BaseCallParamsT = TypeVar("_BaseCallParamsT", bound=BaseCallParams)
_ResponseT = TypeVar("_ResponseT")
_ResponseChunkT = TypeVar("_ResponseChunkT")
_AsyncResponseT = TypeVar("_AsyncResponseT")
_AsyncResponseChunkT = TypeVar("_AsyncResponseChunkT")
_BaseToolT = TypeVar("_BaseToolT", bound=BaseTool)
_ResponseModelT = TypeVar("_ResponseModelT", bound=BaseModel | BaseType)
_P = ParamSpec("_P")


def extract_with_tools_factory(  # noqa: ANN202
    *,
    TCallResponse: type[_BaseCallResponseT],
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
    get_json_output: GetJsonOutput[_BaseCallResponseT],
):
    """Returns the wrapped function with the provider specific interfaces."""
    create_decorator = create_factory(
        TCallResponse=TCallResponse, setup_call=setup_call
    )

    @overload
    def decorator(
        fn: Callable[_P, _BaseDynamicConfigT],
        model: str,
        tools: list[type[BaseTool] | Callable],
        response_model: type[_ResponseModelT],
        output_parser: Callable[[_ResponseModelT], _ParsedOutputT] | None,
        client: _SameSyncAndAsyncClientT | _SyncBaseClientT | None,
        call_params: _BaseCallParamsT,
    ) -> Callable[
        _P,
        (_ResponseModelT | _BaseCallResponseT) | (_ParsedOutputT | _BaseCallResponseT),
    ]: ...

    @overload
    def decorator(
        fn: Callable[_P, Awaitable[_AsyncBaseDynamicConfigT]],
        model: str,
        tools: list[type[BaseTool] | Callable],
        response_model: type[_ResponseModelT],
        output_parser: Callable[[_ResponseModelT], _ParsedOutputT] | None,
        client: _SameSyncAndAsyncClientT | _AsyncBaseClientT | None,
        call_params: _BaseCallParamsT,
    ) -> Callable[
        _P,
        Awaitable[
            (_ResponseModelT | _BaseCallResponseT)
            | (_ParsedOutputT | _BaseCallResponseT)
        ],
    ]: ...

    def decorator(
        fn: Callable[_P, _BaseDynamicConfigT]
        | Callable[_P, Awaitable[_AsyncBaseDynamicConfigT]],
        model: str,
        tools: list[type[BaseTool] | Callable],
        response_model: type[_ResponseModelT],
        output_parser: Callable[[_ResponseModelT], _ParsedOutputT] | None,
        client: _SameSyncAndAsyncClientT | _SyncBaseClientT | None,
        call_params: _BaseCallParamsT,
    ) -> Callable[
        _P,
        (_ResponseModelT | _BaseCallResponseT)
        | (_ParsedOutputT | _BaseCallResponseT)
        | Awaitable[
            (_ResponseModelT | _BaseCallResponseT)
            | (_ParsedOutputT | _BaseCallResponseT)
        ],
    ]:
        fn._model = model  # pyright: ignore [reportFunctionMemberAccess]
        fn.__mirascope_call__ = True  # pyright: ignore [reportFunctionMemberAccess]
        create_decorator_kwargs = {
            "model": model,
            "tools": tools,
            "response_model": response_model,
            "output_parser": None,
            "json_mode": True,
            "client": client,
            "call_params": call_params,
        }
        if fn_is_async(fn):

            @wraps(fn)
            async def inner_async(*args: _P.args, **kwargs: _P.kwargs) -> (
                _ResponseModelT | _BaseCallResponseT
            ) | (_ParsedOutputT | _BaseCallResponseT):
                call_response = await create_decorator(
                    fn=fn, **create_decorator_kwargs
                )(*args, **kwargs)
                try:
                    if call_response.tools:
                        return call_response
                    fields_from_call_args = get_fields_from_call_args(
                        response_model, fn, args, kwargs
                    )
                    json_output = get_json_output(call_response, True)
                    output = extract_tool_return(
                        response_model, json_output, False, fields_from_call_args
                    )
                except Exception as e:
                    e._response = call_response  # pyright: ignore [reportAttributeAccessIssue]
                    raise e
                if isinstance(output, BaseModel):
                    output._response = call_response  # pyright: ignore [reportAttributeAccessIssue]
                return output if not output_parser else output_parser(output)  # pyright: ignore [reportArgumentType, reportReturnType]

            return inner_async
        else:

            @wraps(fn)
            def inner(*args: _P.args, **kwargs: _P.kwargs) -> (
                _ResponseModelT | _BaseCallResponseT
            ) | (_ParsedOutputT | _BaseCallResponseT):
                call_response = create_decorator(fn=fn, **create_decorator_kwargs)(
                    *args, **kwargs
                )
                try:
                    if call_response.tools:
                        return call_response
                    fields_from_call_args = get_fields_from_call_args(
                        response_model, fn, args, kwargs
                    )
                    json_output = get_json_output(call_response, True)
                    output = extract_tool_return(
                        response_model, json_output, False, fields_from_call_args
                    )
                except Exception as e:
                    e._response = call_response  # pyright: ignore [reportAttributeAccessIssue]
                    raise e
                if isinstance(output, BaseModel):
                    output._response = call_response  # pyright: ignore [reportAttributeAccessIssue]
                return output if not output_parser else output_parser(output)  # pyright: ignore [reportArgumentType, reportReturnType]

            return inner

    return decorator
