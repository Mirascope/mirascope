"""This module contains the OpenAI `extract_decorator` function."""

import inspect
import json
from functools import wraps
from typing import Callable, ParamSpec, TypeVar

from google.generativeai import GenerativeModel  # type: ignore
from pydantic import BaseModel

from ..base import _utils
from ._utils import setup_extract
from .call_params import GeminiCallParams
from .function_return import GeminiCallFunctionReturn
from .tool import GeminiTool

_P = ParamSpec("_P")
_ResponseModelT = TypeVar("_ResponseModelT", bound=BaseModel | _utils.BaseType)


def extract_decorator(
    fn: Callable[_P, GeminiCallFunctionReturn],
    model: str,
    response_model: type[_ResponseModelT],
    call_params: GeminiCallParams,
) -> Callable[_P, _ResponseModelT]:
    assert response_model is not None
    tool = _utils.setup_extract_tool(response_model, GeminiTool)

    @wraps(fn)
    def inner(*args: _P.args, **kwargs: _P.kwargs) -> _ResponseModelT:
        assert response_model is not None
        fn_args = inspect.signature(fn).bind(*args, **kwargs).arguments
        fn_return = fn(*args, **kwargs)
        json_mode, messages, call_kwargs = setup_extract(
            fn, fn_args, fn_return, tool, call_params
        )
        client = GenerativeModel(model_name=model)
        response = client.generate_content(
            messages,
            stream=False,
            **call_kwargs,
        )
        content = response.candidates[0].content.parts
        if json_mode and content is not None:
            json_output = content[0].text
        elif tool_calls := content:
            json_output = tool_calls[0].function_call.args
        else:
            raise ValueError("No tool call or JSON object found in response.")
        output = _utils.extract_tool_return(
            response_model, json.dumps(dict(json_output)), False
        )
        if isinstance(response_model, BaseModel):
            output._response = response  # type: ignore
        return output

    return inner
