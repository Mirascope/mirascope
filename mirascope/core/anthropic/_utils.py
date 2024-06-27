"""Utilities for the Mirascope Core Anthropic module."""

import inspect
import json
from textwrap import dedent
from typing import Any, Callable, overload

from anthropic.types import MessageParam, ToolUseBlock, Usage

from ..base import BaseTool, _utils
from .call_params import AnthropicCallParams
from .call_response_chunk import AnthropicCallResponseChunk
from .function_return import AnthropicCallFunctionReturn
from .tool import AnthropicTool


@overload
def setup_call(
    fn: Callable,
    fn_args: dict[str, Any],
    fn_return: AnthropicCallFunctionReturn,
    tools: None,
    call_params: AnthropicCallParams,
) -> tuple[
    str | None,
    list[MessageParam],
    None,
    AnthropicCallParams,
]: ...  # pragma: no cover


@overload
def setup_call(
    fn: Callable,
    fn_args: dict[str, Any],
    fn_return: AnthropicCallFunctionReturn,
    tools: list[type[BaseTool] | Callable],
    call_params: AnthropicCallParams,
) -> tuple[
    str | None,
    list[MessageParam],
    list[type[AnthropicTool]],
    AnthropicCallParams,
]: ...  # pragma: no cover


def setup_call(
    fn: Callable,
    fn_args: dict[str, Any],
    fn_return: AnthropicCallFunctionReturn,
    tools: list[type[BaseTool] | Callable] | None,
    call_params: AnthropicCallParams,
) -> tuple[
    str | None,
    list[MessageParam],
    list[type[AnthropicTool]] | None,
    AnthropicCallParams,
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
        prompt_template = fn.__annotations__.get("prompt_template", inspect.getdoc(fn))
        assert prompt_template is not None, "The function must have a docstring."
        if computed_fields:
            fn_args |= computed_fields
        messages = _utils.parse_prompt_messages(
            roles=["system", "user", "assistant", "tool"],
            template=prompt_template,
            attrs=fn_args,
        )
        if messages[0]["role"] == "system":
            call_kwargs["system"] = messages.pop(0)["content"]

    tool_types = None
    if tools:
        tool_types = [
            _utils.convert_base_model_to_base_tool(tool, AnthropicTool)
            if inspect.isclass(tool)
            else _utils.convert_function_to_base_tool(tool, AnthropicTool)
            for tool in tools
        ]
        call_kwargs["tools"] = [tool_type.tool_schema() for tool_type in tool_types]  # type: ignore

    return prompt_template, messages, tool_types, call_kwargs  # type: ignore


def handle_chunk(
    buffer: str,
    chunk: AnthropicCallResponseChunk,
    current_tool_call: ToolUseBlock,
    current_tool_type: type[AnthropicTool] | None,
) -> tuple[
    str,
    AnthropicTool | None,
    ToolUseBlock,
    type[AnthropicTool] | None,
]:
    """Handles a chunk of the stream."""
    if not chunk.tool_types:
        return buffer, None, current_tool_call, current_tool_type

    if chunk.chunk.type == "content_block_stop" and current_tool_type and buffer:
        current_tool_call.input = json.loads(buffer)
        return (
            "",
            current_tool_type.from_tool_call(current_tool_call),
            ToolUseBlock(id="", input={}, name="", type="tool_use"),
            None,
        )

    if chunk.chunk.type == "content_block_start" and isinstance(
        chunk.chunk.content_block, ToolUseBlock
    ):
        content_block = chunk.chunk.content_block
        current_tool_type = None
        for tool_type in chunk.tool_types:
            if tool_type._name() == content_block.name:
                current_tool_type = tool_type
                break
        if current_tool_type is None:
            raise RuntimeError(f"Unknown tool type in stream: {content_block.name}.")
        return (
            "",
            None,
            ToolUseBlock(
                id=content_block.id, input={}, name=content_block.name, type="tool_use"
            ),
            current_tool_type,
        )

    if (
        chunk.chunk.type == "content_block_delta"
        and chunk.chunk.delta.type == "input_json_delta"
    ):
        buffer += chunk.chunk.delta.partial_json

    return buffer, None, current_tool_call, current_tool_type


def setup_extract(
    fn: Callable,
    fn_args: dict[str, Any],
    fn_return: AnthropicCallFunctionReturn,
    tool: type[BaseTool],
    call_params: AnthropicCallParams,
) -> tuple[
    bool,
    list[MessageParam],
    AnthropicCallParams,
]:
    _, messages, [tool_type], call_kwargs = setup_call(
        fn, fn_args, fn_return, [tool], call_params
    )

    response_format = call_kwargs.get("response_format", None)
    if json_mode := bool(response_format == "json"):
        messages[-1]["content"] += dedent(
            f"""
                
                Extract a valid JSON object instance from the content using this schema:
                
                {json.dumps(tool_type.model_json_schema(), indent=2)}"""
        )
        call_kwargs["tools"] = None  # type: ignore
    else:
        call_kwargs["tools"] = [tool_type.tool_schema()]  # type: ignore
        call_kwargs["tool_choice"] = {"name": tool_type._name(), "type": "tool"}

    return json_mode, messages, call_kwargs


def anthropic_api_calculate_cost(
    usage: Usage, model="claude-3-haiku-20240229"
) -> float | None:
    """Calculate the cost of a completion using the Anthropic API.

    https://www.anthropic.com/api

    claude-instant-1.2        $0.80 / 1M tokens   $2.40 / 1M tokens
    claude-2.0                $8.00 / 1M tokens   $24.00 / 1M tokens
    claude-2.1                $8.00 / 1M tokens   $24.00 / 1M tokens
    claude-3-haiku            $0.25 / 1M tokens   $1.25 / 1M tokens
    claude-3-sonnet           $3.00 / 1M tokens   $15.00 / 1M tokens
    claude-3-opus             $15.00 / 1M tokens   $75.00 / 1M tokens
    """
    pricing = {
        "claude-instant-1.2": {
            "prompt": 0.000_000_8,
            "completion": 0.000_002_4,
        },
        "claude-2.0": {
            "prompt": 0.000_008,
            "completion": 0.000_024,
        },
        "claude-2.1": {
            "prompt": 0.000_008,
            "completion": 0.000_024,
        },
        "claude-3-haiku-20240307": {
            "prompt": 0.000_002_5,
            "completion": 0.000_012_5,
        },
        "claude-3-sonnet-20240229": {
            "prompt": 0.000_003,
            "completion": 0.000_015,
        },
        "claude-3-opus-20240229": {
            "prompt": 0.000_015,
            "completion": 0.000_075,
        },
    }

    try:
        model_pricing = pricing[model]
    except KeyError:
        return None

    prompt_cost = usage.input_tokens * model_pricing["prompt"]
    completion_cost = usage.output_tokens * model_pricing["completion"]
    total_cost = prompt_cost + completion_cost

    return total_cost
