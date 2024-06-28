"""This module contains the Anthropic `call_decorator` function."""

import datetime
from functools import wraps
from typing import Callable, ParamSpec, TypeVar

from anthropic import Anthropic

from ..base import BaseTool, _utils
from ._utils import anthropic_api_calculate_cost, setup_call
from .call_params import AnthropicCallParams
from .call_response import AnthropicCallResponse
from .function_return import AnthropicDynamicConfig

_P = ParamSpec("_P")
_ParsedOutputT = TypeVar("_ParsedOutputT")


def create_decorator(
    fn: Callable[_P, AnthropicDynamicConfig],
    model: str,
    tools: list[type[BaseTool] | Callable] | None,
    output_parser: Callable[[AnthropicCallResponse], _ParsedOutputT] | None,
    call_params: AnthropicCallParams,
) -> Callable[_P, AnthropicCallResponse | _ParsedOutputT]:
    @wraps(fn)
    def inner(
        *args: _P.args, **kwargs: _P.kwargs
    ) -> AnthropicCallResponse | _ParsedOutputT:
        fn_args = _utils.get_fn_args(fn, args, kwargs)
        fn_return = fn(*args, **kwargs)
        prompt_template, messages, tool_types, call_kwargs = setup_call(
            fn, fn_args, fn_return, tools, call_params
        )
        client = Anthropic()
        start_time = datetime.datetime.now().timestamp() * 1000
        response = client.messages.create(
            model=model, stream=False, messages=messages, **call_kwargs
        )
        output = AnthropicCallResponse(
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
            cost=anthropic_api_calculate_cost(response.usage, response.model),
        )
        return output if not output_parser else output_parser(output)

    return inner