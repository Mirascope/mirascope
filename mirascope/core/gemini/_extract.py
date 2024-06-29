"""This module contains the Gemini `extract_decorator` function."""

from functools import wraps
from typing import Callable, ParamSpec, TypeVar

from google.generativeai import GenerativeModel  # type: ignore
from pydantic import BaseModel

from ..base import _utils
from ._utils import setup_extract
from .call_params import GeminiCallParams
from .dynamic_config import GeminiDynamicConfig
from .tool import GeminiTool

_P = ParamSpec("_P")
_ResponseModelT = TypeVar("_ResponseModelT", bound=BaseModel | _utils.BaseType)


def extract_decorator(
    fn: Callable[_P, GeminiDynamicConfig],
    model: str,
    response_model: type[_ResponseModelT],
    client: GenerativeModel | None,
    call_params: GeminiCallParams,
) -> Callable[_P, _ResponseModelT]:
    assert response_model is not None
    tool = _utils.setup_extract_tool(response_model, GeminiTool)

    @wraps(fn)
    def inner(*args: _P.args, **kwargs: _P.kwargs) -> _ResponseModelT:
        assert response_model is not None
        fn_args = _utils.get_fn_args(fn, args, kwargs)
        fn_return = fn(*args, **kwargs)
        json_mode, messages, call_kwargs = setup_extract(
            fn, fn_args, fn_return, tool, call_params
        )
        _client = client or GenerativeModel(model_name=model)
        response = _client.generate_content(
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
        output = _utils.extract_tool_return(response_model, json_output, False)
        if isinstance(output, BaseModel):
            output._response = response  # type: ignore
        return output

    return inner
