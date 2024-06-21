"""This module contains the OpenAI `extract_async_decorator` function."""

import inspect
from functools import wraps
from typing import Awaitable, Callable, ParamSpec, TypeVar

from openai import AsyncOpenAI
from pydantic import BaseModel

from ..base import _utils
from ._utils import setup_extract
from .call_params import OpenAICallParams
from .function_return import OpenAICallFunctionReturn
from .tool import OpenAITool

_P = ParamSpec("_P")
_ResponseModelT = TypeVar("_ResponseModelT", bound=BaseModel | _utils.BaseType)


def extract_async_decorator(
    fn: Callable[_P, Awaitable[OpenAICallFunctionReturn]],
    model: str,
    response_model: type[_ResponseModelT],
    call_params: OpenAICallParams,
) -> Callable[_P, Awaitable[_ResponseModelT]]:
    assert response_model is not None
    tool = _utils.setup_extract_tool(response_model, OpenAITool)

    @wraps(fn)
    async def inner(*args: _P.args, **kwargs: _P.kwargs) -> _ResponseModelT:
        assert response_model is not None
        fn_args = inspect.signature(fn).bind(*args, **kwargs).arguments
        fn_return = await fn(*args, **kwargs)
        json_mode, messages, call_kwargs = setup_extract(
            fn, fn_args, fn_return, tool, call_params
        )
        client = AsyncOpenAI()
        response = await client.chat.completions.create(
            model=model, stream=False, messages=messages, **call_kwargs
        )

        if json_mode and (content := response.choices[0].message.content):
            json_output = content
        elif tool_calls := response.choices[0].message.tool_calls:
            json_output = tool_calls[0].function.arguments
        else:
            raise ValueError("No tool call or JSON object found in response.")

        output = _utils.extract_tool_return(response_model, json_output, False)
        if isinstance(response_model, BaseModel):
            output._response = response  # type: ignore
        return output

    return inner
