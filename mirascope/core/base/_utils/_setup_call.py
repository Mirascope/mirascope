"""Utility for setting up a provider-specific call."""

import inspect
from collections.abc import (
    Awaitable,
    Callable,
    Sequence,
)
from typing import Any, Protocol, TypeVar, cast

from ..call_kwargs import BaseCallKwargs
from ..call_params import BaseCallParams, CommonCallParams
from ..dynamic_config import BaseDynamicConfig
from ..message_param import BaseMessageParam
from ..tool import BaseTool
from . import get_prompt_template, parse_prompt_messages
from ._convert_base_model_to_base_tool import convert_base_model_to_base_tool
from ._convert_function_to_base_tool import convert_function_to_base_tool

_BaseToolT = TypeVar("_BaseToolT", bound=BaseTool)
_BaseDynamicConfigT = TypeVar("_BaseDynamicConfigT", bound=BaseDynamicConfig)
_BaseCallParamsT = TypeVar("_BaseCallParamsT", bound=BaseCallParams, covariant=True)
_CALL_PARAMS_KEYS = set(CommonCallParams.__annotations__)


class ConvertCommonParamsFunc(Protocol[_BaseCallParamsT]):
    def __call__(self, common_params: CommonCallParams) -> _BaseCallParamsT: ...


def setup_call(
    fn: Callable[..., _BaseDynamicConfigT | Awaitable[_BaseDynamicConfigT]]
    | Callable[..., Sequence[BaseMessageParam]]
    | Callable[..., Awaitable[Sequence[BaseMessageParam]]],
    fn_args: dict[str, Any],
    dynamic_config: _BaseDynamicConfigT,
    tools: Sequence[type[BaseTool] | Callable] | None,
    tool_type: type[_BaseToolT],
    call_params: _BaseCallParamsT | CommonCallParams,
    convert_common_call_params: ConvertCommonParamsFunc[_BaseCallParamsT],
) -> tuple[
    str | None,
    list[BaseMessageParam | Any],
    list[type[_BaseToolT]] | None,
    BaseCallKwargs,
]:
    if isinstance(call_params, dict) and call_params.keys() <= _CALL_PARAMS_KEYS:
        call_params = convert_common_call_params(cast(CommonCallParams, call_params))
    call_kwargs = cast(BaseCallKwargs[_BaseToolT], dict(call_params))
    prompt_template, messages = None, None
    if dynamic_config is not None:
        tools = dynamic_config.get("tools", tools)
        messages = dynamic_config.get("messages", None)
        if messages is not None and not isinstance(messages, list):
            messages = list(messages)
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
