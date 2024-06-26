"""This module contains the Gemini `call_async_decorator` function."""

import datetime
from functools import wraps
from typing import Awaitable, Callable, ParamSpec, TypeVar

from google.generativeai import GenerativeModel  # type: ignore

from ..base import BaseTool, _utils
from ._utils import setup_call
from .call_params import GeminiCallParams
from .call_response import GeminiCallResponse
from .function_return import GeminiCallFunctionReturn

_P = ParamSpec("_P")
_ParsedOutputT = TypeVar("_ParsedOutputT")


def create_async_decorator(
    fn: Callable[_P, GeminiCallFunctionReturn],
    model: str,
    tools: list[type[BaseTool] | Callable] | None,
    output_parser: Callable[[GeminiCallResponse], _ParsedOutputT] | None,
    call_params: GeminiCallParams,
) -> Callable[_P, Awaitable[GeminiCallResponse | _ParsedOutputT]]:
    @wraps(fn)
    async def inner_async(
        *args: _P.args, **kwargs: _P.kwargs
    ) -> GeminiCallResponse | _ParsedOutputT:
        fn_args = _utils.get_fn_args(fn, args, kwargs)
        fn_return = await fn(*args, **kwargs)
        prompt_template, messages, tool_types, call_kwargs = setup_call(
            fn, fn_args, fn_return, tools, call_params
        )
        client = GenerativeModel(model_name=model)
        start_time = datetime.datetime.now().timestamp() * 1000
        response = client.generate_content(
            messages,
            stream=False,
            **call_kwargs,
        )
        output = GeminiCallResponse(
            tags=fn.__annotations__.get("tags", []),
            response=response,
            tool_types=tool_types,
            prompt_template=prompt_template,
            fn_args=fn_args,
            fn_return=fn_return,
            messages=messages,
            call_params=call_kwargs,
            user_message_param=messages[-1] if messages[-1]["role"] == "user" else None,
            start_time=start_time,
            end_time=datetime.datetime.now().timestamp() * 1000,
            cost=None,
        )
        return output if not output_parser else output_parser(output)

    return inner_async
