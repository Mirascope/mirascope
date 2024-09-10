"""Utility for setting up a provider-specific call."""

import inspect
from collections.abc import (
    Awaitable,
    Callable,
)
from typing import (
    Any,
    TypeVar,
    cast,
)

from ..call_kwargs import BaseCallKwargs
from ..call_params import BaseCallParams
from ..dynamic_config import BaseDynamicConfig
from ..message_param import BaseMessageParam
from ..tool import BaseTool
from . import get_prompt_template, parse_prompt_messages
from ._convert_base_model_to_base_tool import convert_base_model_to_base_tool
from ._convert_function_to_base_tool import convert_function_to_base_tool

_BaseToolT = TypeVar("_BaseToolT", bound=BaseTool)
_BaseDynamicConfigT = TypeVar("_BaseDynamicConfigT", bound=BaseDynamicConfig)


def setup_call(
    fn: Callable[..., _BaseDynamicConfigT | Awaitable[_BaseDynamicConfigT]]
    | Callable[..., list[BaseMessageParam]]
    | Callable[..., Awaitable[list[BaseMessageParam]]],
    fn_args: dict[str, Any],
    dynamic_config: _BaseDynamicConfigT,
    tools: list[type[BaseTool] | Callable] | None,
    tool_type: type[_BaseToolT],
    call_params: BaseCallParams,
) -> tuple[
    str | None,
    list[BaseMessageParam | Any],
    list[type[_BaseToolT]] | None,
    BaseCallKwargs,
]:
    call_kwargs = cast(BaseCallKwargs[_BaseToolT], dict(call_params))
    prompt_template, messages = None, None
    if dynamic_config is not None:
        tools = dynamic_config.get("tools", tools)
        messages = dynamic_config.get("messages", None)
        dynamic_call_params = dynamic_config.get("call_params", None)
        if dynamic_call_params:
            call_kwargs |= dynamic_call_params

    if not messages:
        prompt_template = get_prompt_template(fn)
        assert prompt_template is not None, "The function must have a prompt template."
        messages = parse_prompt_messages(
            roles=["system", "user", "assistant"],
            template=prompt_template,
            attrs=fn_args,
            dynamic_config=dynamic_config,
        )

    tool_types = None
    if tools:
        tool_types = [
            convert_base_model_to_base_tool(tool, tool_type)
            if inspect.isclass(tool)
            else convert_function_to_base_tool(tool, tool_type)
            for tool in tools
        ]
        call_kwargs["tools"] = [tool_type.tool_schema() for tool_type in tool_types]

    return prompt_template, messages, tool_types, call_kwargs
