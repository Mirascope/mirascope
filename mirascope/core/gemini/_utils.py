"""Utilities for the Mirascope Core OpenAI module."""

import inspect
import json
from textwrap import dedent
from typing import Any, Callable, overload

from google.generativeai.types import ContentsType  # type: ignore

from ..base import BaseTool, _utils
from .call_params import GeminiCallParams
from .function_return import GeminiDynamicConfig
from .tool import GeminiTool


def parse_prompt_messages(
    roles: list[str],
    template: str,
    attrs: dict[str, Any],
) -> list[ContentsType]:
    """Returns the `ContentsType` messages for Gemini `generate_content`."""
    return [
        {"role": message["role"], "parts": [message["content"]]}
        for message in _utils.parse_prompt_messages(
            roles=roles,
            template=template,
            attrs=attrs,
        )
    ]


@overload
def setup_call(
    fn: Callable,
    fn_args: dict[str, Any],
    fn_return: GeminiDynamicConfig,
    tools: None,
    call_params: GeminiCallParams,
) -> tuple[
    str | None,
    list[ContentsType],
    None,
    GeminiCallParams,
]: ...  # pragma: no cover


@overload
def setup_call(
    fn: Callable,
    fn_args: dict[str, Any],
    fn_return: GeminiDynamicConfig,
    tools: list[type[BaseTool] | Callable],
    call_params: GeminiCallParams,
) -> tuple[
    str | None,
    list[ContentsType],
    list[type[GeminiTool]],
    GeminiCallParams,
]: ...  # pragma: no cover


def setup_call(
    fn: Callable,
    fn_args: dict[str, Any],
    fn_return: GeminiDynamicConfig,
    tools: list[type[BaseTool] | Callable] | None,
    call_params: GeminiCallParams,
) -> tuple[
    str | None,
    list[ContentsType],
    list[type[GeminiTool]] | None,
    GeminiCallParams,
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
        messages = parse_prompt_messages(
            roles=["model", "user", "tool"],
            template=prompt_template,
            attrs=fn_args,
        )

    tool_types = None
    if tools:
        tool_types = [
            _utils.convert_base_model_to_base_tool(tool, GeminiTool)
            if inspect.isclass(tool)
            else _utils.convert_function_to_base_tool(tool, GeminiTool)
            for tool in tools
        ]
        call_kwargs["tools"] = [tool_type.tool_schema() for tool_type in tool_types]  # type: ignore

    return prompt_template, messages, tool_types, call_kwargs  # type: ignore


def setup_extract(
    fn: Callable,
    fn_args: dict[str, Any],
    fn_return: GeminiDynamicConfig,
    tool: type[BaseTool],
    call_params: GeminiCallParams,
) -> tuple[
    bool,
    list[ContentsType],
    GeminiCallParams,
]:
    _, messages, [tool_type], call_kwargs = setup_call(
        fn, fn_args, fn_return, [tool], call_params
    )
    if json_mode := bool(
        (generation_config := call_kwargs.get("generation_config", None))
        and generation_config.get("response_mime_type", "") == "application/json"
    ):
        messages.append(
            {
                "role": "user",
                "parts": [
                    dedent(
                        f"""\
            Extract a valid JSON object instance from the content using this schema:

            {json.dumps(tool_type.model_json_schema(), indent=2)}"""
                    )
                ],
            }
        )
        call_kwargs["tools"] = None  # type: ignore
    else:
        call_kwargs["tools"] = [tool_type.tool_schema()]  # type: ignore
        tool_config = call_kwargs.get("tool_config", {})
        tool_config["function_calling_config"] = {"mode": "auto"}
        call_kwargs["tool_config"] = tool_config

    return json_mode, messages, call_kwargs
