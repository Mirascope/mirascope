"""This module contains the Gemini `call_decorator` function."""

import datetime
import inspect
from functools import wraps
from typing import Callable, ParamSpec

from google.generativeai import GenerativeModel  # type: ignore

from ..base import BaseTool
from ._utils import setup_call
from .call_params import GeminiCallParams
from .call_response import GeminiCallResponse
from .function_return import GeminiCallFunctionReturn

_P = ParamSpec("_P")


def create_decorator(
    fn: Callable[_P, GeminiCallFunctionReturn],
    model: str,
    tools: list[type[BaseTool] | Callable] | None,
    call_params: GeminiCallParams,
) -> Callable[_P, GeminiCallResponse]:
    @wraps(fn)
    def inner(*args: _P.args, **kwargs: _P.kwargs) -> GeminiCallResponse:
        fn_args = inspect.signature(fn).bind(*args, **kwargs).arguments
        fn_return = fn(*args, **kwargs)
        prompt_template, messages, tool_types, call_kwargs = setup_call(
            fn, fn_args, fn_return, tools, call_params
        )
        client = GenerativeModel(model_name=model)
        start_time = datetime.datetime.now().timestamp() * 1000
        response = client.generate_content(
            messages,
            stream=False,
            tools=tools,
            **call_kwargs,
        )
        return GeminiCallResponse(
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

    return inner
