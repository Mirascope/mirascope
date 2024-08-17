"""Utility for setting up a provider-specific call."""

import inspect
from typing import Any, Awaitable, Callable, TypeVar

from ..call_params import BaseCallParams
from ..dynamic_config import BaseDynamicConfig
from ..message_param import BaseMessageParam
from ..tool import BaseTool
from ._convert_base_model_to_base_tool import convert_base_model_to_base_tool
from ._convert_function_to_base_tool import convert_function_to_base_tool
from ._get_prompt_template import get_prompt_template
from ._parse_prompt_messages import parse_prompt_messages

_BaseToolT = TypeVar("_BaseToolT", bound=BaseTool)
_BaseDynamicConfigT = TypeVar("_BaseDynamicConfigT", bound=BaseDynamicConfig)


def setup_call(
    fn: Callable[..., _BaseDynamicConfigT | Awaitable[_BaseDynamicConfigT]],
    fn_args: dict[str, Any],
    dynamic_config: _BaseDynamicConfigT,
    tools: list[type[BaseTool] | Callable] | None,
    tool_type: type[_BaseToolT],
    call_params: BaseCallParams,
) -> tuple[
    str,
    list[BaseMessageParam | Any],
    list[type[_BaseToolT]] | None,
    dict[str, Any],
]:
    call_kwargs = call_params.copy()
    prompt_template, messages, computed_fields = None, None, None
    if dynamic_config is not None:
        computed_fields = dynamic_config.get("computed_fields", None)
        tools = dynamic_config.get("tools", tools)
        messages = dynamic_config.get("messages", None)
        dynamic_call_params = dynamic_config.get("call_params", None)
        if dynamic_call_params:
            call_kwargs |= dynamic_call_params

    if not messages:
        prompt_template = get_prompt_template(fn)
        assert prompt_template is not None, "The function must have a docstring."
        if computed_fields:
            fn_args |= computed_fields
        messages = parse_prompt_messages(
            roles=["system", "user", "assistant"],
            template=prompt_template,
            attrs=fn_args,
        )

    tool_types = None
    if tools:
        tool_types = [
            convert_base_model_to_base_tool(tool, tool_type)
            if inspect.isclass(tool)
            else convert_function_to_base_tool(tool, tool_type)
            for tool in tools
        ]
        call_kwargs["tools"] = [tool_type.tool_schema() for tool_type in tool_types]  # type: ignore

    return prompt_template, messages, tool_types, call_kwargs  # type: ignore
