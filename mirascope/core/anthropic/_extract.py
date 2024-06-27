"""This module contains the Anthropic `extract_decorator` function."""

from functools import wraps
from typing import Callable, ParamSpec, TypeVar

from anthropic import Anthropic
from pydantic import BaseModel

from ..base import _utils
from ._utils import setup_extract
from .call_params import AnthropicCallParams
from .function_return import AnthropicDynamicConfig
from .tool import AnthropicTool

_P = ParamSpec("_P")
_ResponseModelT = TypeVar("_ResponseModelT", bound=BaseModel | _utils.BaseType)


def extract_decorator(
    fn: Callable[_P, AnthropicDynamicConfig],
    model: str,
    response_model: type[_ResponseModelT],
    call_params: AnthropicCallParams,
) -> Callable[_P, _ResponseModelT]:
    assert response_model is not None
    tool = _utils.setup_extract_tool(response_model, AnthropicTool)

    @wraps(fn)
    def inner(*args: _P.args, **kwargs: _P.kwargs) -> _ResponseModelT:
        assert response_model is not None
        fn_args = _utils.get_fn_args(fn, args, kwargs)
        fn_return = fn(*args, **kwargs)
        json_mode, messages, call_kwargs = setup_extract(
            fn, fn_args, fn_return, tool, call_params
        )
        client = Anthropic()
        response = client.messages.create(
            model=model, stream=False, messages=messages, **call_kwargs
        )

        block = response.content[0]
        if json_mode and block.type == "text":
            json_output = block.text
        elif block.type == "tool_use":
            json_output = block.input
        else:
            raise ValueError("No tool call or JSON object found in response.")

        output = _utils.extract_tool_return(response_model, json_output, False)
        if isinstance(output, BaseModel):
            output._response = response  # type: ignore
        return output

    return inner
