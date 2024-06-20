"""Utilities for the Mirascope Core OpenAI module."""

import inspect
from typing import Any, Callable

from openai.types.chat import ChatCompletionMessageParam

from .._internal import utils
from ..base import BaseTool
from .call_params import OpenAICallParams
from .function_return import OpenAICallFunctionReturn
from .tools import OpenAITool


def setup_call(
    fn: Callable,
    fn_args: dict[str, Any],
    fn_return: OpenAICallFunctionReturn,
    tools: list[type[BaseTool] | Callable] | None,
    call_params: OpenAICallParams,
) -> tuple[
    str | None,
    list[ChatCompletionMessageParam],
    list[type[OpenAITool]] | None,
    OpenAICallParams,
]:
    call_kwargs = call_params.copy()
    prompt_template, messages, computed_fields = None, None, None
    if fn_return is not None:
        computed_fields = fn_return.get("computed_fields", None)
        tools = fn_return.get("tools", tools)
        messages = fn_return.get("messages", None)
        dynamic_call_params = fn_return.get("call_params", None)
        if dynamic_call_params:
            call_kwargs |= dynamic_call_params

    if not messages:
        prompt_template = inspect.getdoc(fn)
        assert prompt_template is not None, "The function must have a docstring."
        if computed_fields:
            fn_args |= computed_fields
        messages = utils.parse_prompt_messages(
            roles=["system", "user", "assistant", "tool"],
            template=prompt_template,
            attrs=fn_args,
        )

    tool_types = None
    if tools:
        tool_types = [
            utils.convert_base_model_to_base_tool(tool, OpenAITool)
            if inspect.isclass(tool)
            else utils.convert_function_to_base_tool(tool, OpenAITool)
            for tool in tools
        ]
        call_kwargs["tools"] = [tool_type.tool_schema() for tool_type in tool_types]  # type: ignore

    return prompt_template, messages, tool_types, call_kwargs  # type: ignore
