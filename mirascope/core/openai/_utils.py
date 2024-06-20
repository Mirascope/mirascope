"""Utilities for the Mirascope Core OpenAI module."""

import inspect
import json
from textwrap import dedent
from typing import Any, Callable, overload

from openai.types.chat import ChatCompletionMessageParam

from ..base import BaseTool, _utils
from .call_params import OpenAICallParams
from .function_return import OpenAICallFunctionReturn
from .tools import OpenAITool


@overload
def setup_call(
    fn: Callable,
    fn_args: dict[str, Any],
    fn_return: OpenAICallFunctionReturn,
    tools: None,
    call_params: OpenAICallParams,
) -> tuple[
    str | None,
    list[ChatCompletionMessageParam],
    None,
    OpenAICallParams,
]:
    ...  # pragma: no cover


@overload
def setup_call(
    fn: Callable,
    fn_args: dict[str, Any],
    fn_return: OpenAICallFunctionReturn,
    tools: list[type[BaseTool] | Callable],
    call_params: OpenAICallParams,
) -> tuple[
    str | None,
    list[ChatCompletionMessageParam],
    list[type[OpenAITool]],
    OpenAICallParams,
]:
    ...  # pragma: no cover


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
        messages = _utils.parse_prompt_messages(
            roles=["system", "user", "assistant", "tool"],
            template=prompt_template,
            attrs=fn_args,
        )

    tool_types = None
    if tools:
        tool_types = [
            _utils.convert_base_model_to_base_tool(tool, OpenAITool)
            if inspect.isclass(tool)
            else _utils.convert_function_to_base_tool(tool, OpenAITool)
            for tool in tools
        ]
        call_kwargs["tools"] = [tool_type.tool_schema() for tool_type in tool_types]  # type: ignore

    return prompt_template, messages, tool_types, call_kwargs  # type: ignore


def setup_extract(
    fn: Callable,
    fn_args: dict[str, Any],
    fn_return: OpenAICallFunctionReturn,
    tool: type[BaseTool],
    call_params: OpenAICallParams,
) -> tuple[
    bool,
    list[ChatCompletionMessageParam],
    OpenAICallParams,
]:
    _, messages, [tool_type], call_kwargs = setup_call(
        fn, fn_args, fn_return, [tool], call_params
    )

    response_format = call_kwargs.get("response_format", None)
    if json_mode := bool(
        response_format
        and "type" in response_format
        and response_format["type"] == "json_object"
    ):
        messages.append(
            {
                "role": "user",
                "content": dedent(
                    f"""\
            Extract a valid JSON object instance from the content using this schema:
                        
            {json.dumps(tool_type.model_json_schema(), indent=2)}"""
                ),
            }
        )
        call_kwargs["tools"] = None  # type: ignore
    else:
        call_kwargs["tools"] = [tool_type.tool_schema()]  # type: ignore
        call_kwargs["tool_choice"] = "required"

    return json_mode, messages, call_kwargs
