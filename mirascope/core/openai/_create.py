"""This module contains the OpenAI `call_decorator` function."""

import datetime
from functools import wraps
from typing import Callable, ParamSpec, TypeVar

from openai import OpenAI
from openai._base_client import BaseClient

from ..base import BaseTool, _utils
from ._utils import openai_api_calculate_cost, setup_call
from .call_params import OpenAICallParams
from .call_response import OpenAICallResponse
from .function_return import OpenAIDynamicConfig

_P = ParamSpec("_P")
_ParsedOutputT = TypeVar("_ParsedOutputT")


def create_decorator(
    fn: Callable[_P, OpenAIDynamicConfig],
    model: str,
    tools: list[type[BaseTool] | Callable] | None,
    output_parser: Callable[[OpenAICallResponse], _ParsedOutputT] | None,
    client: BaseClient | None,
    call_params: OpenAICallParams,
) -> Callable[_P, OpenAICallResponse | _ParsedOutputT]:
    @wraps(fn)
    def inner(
        *args: _P.args, **kwargs: _P.kwargs
    ) -> OpenAICallResponse | _ParsedOutputT:
        fn_args = _utils.get_fn_args(fn, args, kwargs)
        fn_return = fn(*args, **kwargs)
        prompt_template, messages, tool_types, call_kwargs = setup_call(
            fn, fn_args, fn_return, tools, call_params
        )
        _client = client or OpenAI()
        start_time = datetime.datetime.now().timestamp() * 1000
        response = _client.chat.completions.create(
            model=model, stream=False, messages=messages, **call_kwargs
        )
        output = OpenAICallResponse(
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
            cost=openai_api_calculate_cost(response.usage, response.model),
        )
        return output if not output_parser else output_parser(output)

    return inner
