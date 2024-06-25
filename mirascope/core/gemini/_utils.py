"""Utilities for the Mirascope Core OpenAI module."""

import inspect
import json
from textwrap import dedent
from typing import Any, Callable, overload

from google.generativeai.types import ContentsType  # type: ignore

from ..base import BaseTool, _utils
from .call_params import GeminiCallParams
from .call_response_chunk import GeminiCallResponseChunk
from .function_return import GeminiCallFunctionReturn
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
    fn_return: GeminiCallFunctionReturn,
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
    fn_return: GeminiCallFunctionReturn,
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
    fn_return: GeminiCallFunctionReturn,
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


# def handle_chunk(
#     chunk: GeminiCallResponseChunk,
#     current_tool_call: ChatCompletionMessageToolCall,
#     current_tool_type: type[GeminiTool] | None,
# ) -> tuple[
#     GeminiTool | None,
#     ChatCompletionMessageToolCall,
#     type[GeminiTool] | None,
# ]:
#     """Handles a chunk of the stream."""
#     if not chunk.tool_types or not chunk.tool_calls:
#         return None, current_tool_call, current_tool_type

#     tool_call = chunk.tool_calls[0]
#     # Reset on new tool
#     if tool_call.id and tool_call.function is not None:
#         previous_tool_call = current_tool_call.model_copy()
#         previous_tool_type = current_tool_type
#         current_tool_call = ChatCompletionMessageToolCall(
#             id=tool_call.id,
#             function=Function(
#                 arguments="",
#                 name=tool_call.function.name if tool_call.function.name else "",
#             ),
#             type="function",
#         )
#         current_tool_type = None
#         for tool_type in chunk.tool_types:
#             if tool_type._name() == tool_call.function.name:
#                 current_tool_type = tool_type
#                 break
#         if current_tool_type is None:
#             raise RuntimeError(
#                 f"Unknown tool type in stream: {tool_call.function.name}"
#             )
#         if previous_tool_call.id and previous_tool_type is not None:
#             return (
#                 previous_tool_type.from_tool_call(previous_tool_call),
#                 current_tool_call,
#                 current_tool_type,
#             )

#     # Update arguments with each chunk
#     if tool_call.function and tool_call.function.arguments:
#         current_tool_call.function.arguments += tool_call.function.arguments

#     return None, current_tool_call, current_tool_type


def setup_extract(
    fn: Callable,
    fn_args: dict[str, Any],
    fn_return: GeminiCallFunctionReturn,
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
        and generation_config.response_mime_type == "application/json"
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
        tool_config = call_kwargs.get("tool_config", {})
        tool_config["function_calling_config"] = {"mode": "auto"}
        call_kwargs["tool_config"] = tool_config

    return json_mode, messages, call_kwargs
