"""Utilities for the Mirascope Core OpenAI module."""

import inspect
import json
from textwrap import dedent
from typing import Any, Callable, overload

from openai.types.chat import (
    ChatCompletionMessageParam,
    ChatCompletionMessageToolCall,
)
from openai.types.chat.chat_completion_message_tool_call import Function
from openai.types.completion_usage import CompletionUsage

from ..base import BaseTool, _utils
from .call_params import OpenAICallParams
from .call_response_chunk import OpenAICallResponseChunk
from .function_return import OpenAICallFunctionReturn
from .tool import OpenAITool


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
]: ...  # pragma: no cover


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
]: ...  # pragma: no cover


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
        prompt_template = fn.__annotations__.get("prompt_template", inspect.getdoc(fn))
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


def handle_chunk(
    chunk: OpenAICallResponseChunk,
    current_tool_call: ChatCompletionMessageToolCall,
    current_tool_type: type[OpenAITool] | None,
) -> tuple[
    OpenAITool | None,
    ChatCompletionMessageToolCall,
    type[OpenAITool] | None,
]:
    """Handles a chunk of the stream."""
    if not chunk.tool_types or not chunk.tool_calls:
        return None, current_tool_call, current_tool_type

    tool_call = chunk.tool_calls[0]
    # Reset on new tool
    if tool_call.id and tool_call.function is not None:
        previous_tool_call = current_tool_call.model_copy()
        previous_tool_type = current_tool_type
        current_tool_call = ChatCompletionMessageToolCall(
            id=tool_call.id,
            function=Function(
                arguments="",
                name=tool_call.function.name if tool_call.function.name else "",
            ),
            type="function",
        )
        current_tool_type = None
        for tool_type in chunk.tool_types:
            if tool_type._name() == tool_call.function.name:
                current_tool_type = tool_type
                break
        if current_tool_type is None:
            raise RuntimeError(
                f"Unknown tool type in stream: {tool_call.function.name}"
            )
        if previous_tool_call.id and previous_tool_type is not None:
            return (
                previous_tool_type.from_tool_call(previous_tool_call),
                current_tool_call,
                current_tool_type,
            )

    # Update arguments with each chunk
    if tool_call.function and tool_call.function.arguments:
        current_tool_call.function.arguments += tool_call.function.arguments

    return None, current_tool_call, current_tool_type


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


def openai_api_calculate_cost(
    usage: CompletionUsage | None, model="gpt-3.5-turbo-16k"
) -> float | None:
    """Calculate the cost of a completion using the OpenAI API.

    https://openai.com/pricing

    Model                   Input               Output
    gpt-4o                  $5.00 / 1M tokens   $15.00 / 1M tokens
    gpt-4o-2024-05-13       $5.00 / 1M tokens   $15.00 / 1M tokens
    gpt-4-turbo             $10.00 / 1M tokens  $30.00 / 1M tokens
    gpt-4-turbo-2024-04-09  $10.00 / 1M tokens  $30.00 / 1M tokens
    gpt-3.5-turbo-0125	    $0.50 / 1M tokens	$1.50 / 1M tokens
    gpt-3.5-turbo-1106	    $1.00 / 1M tokens	$2.00 / 1M tokens
    gpt-4-1106-preview	    $10.00 / 1M tokens 	$30.00 / 1M tokens
    gpt-4	                $30.00 / 1M tokens	$60.00 / 1M tokens
    text-embedding-3-small	$0.02 / 1M tokens
    text-embedding-3-large	$0.13 / 1M tokens
    text-embedding-ada-0002	$0.10 / 1M tokens
    """
    pricing = {
        "gpt-4o": {
            "prompt": 0.000_005,
            "completion": 0.000_015,
        },
        "gpt-4o-2024-05-13": {
            "prompt": 0.000_005,
            "completion": 0.000_015,
        },
        "gpt-4-turbo": {
            "prompt": 0.000_01,
            "completion": 0.000_03,
        },
        "gpt-4-turbo-2024-04-09": {
            "prompt": 0.000_01,
            "completion": 0.000_03,
        },
        "gpt-3.5-turbo-0125": {
            "prompt": 0.000_000_5,
            "completion": 0.000_001_5,
        },
        "gpt-3.5-turbo-1106": {
            "prompt": 0.000_001,
            "completion": 0.000_002,
        },
        "gpt-4-1106-preview": {
            "prompt": 0.000_01,
            "completion": 0.000_03,
        },
        "gpt-4": {
            "prompt": 0.000_003,
            "completion": 0.000_006,
        },
        "gpt-3.5-turbo-4k": {
            "prompt": 0.000_015,
            "completion": 0.000_02,
        },
        "gpt-3.5-turbo-16k": {
            "prompt": 0.000_003,
            "completion": 0.000_004,
        },
        "gpt-4-8k": {
            "prompt": 0.000_003,
            "completion": 0.000_006,
        },
        "gpt-4-32k": {
            "prompt": 0.000_006,
            "completion": 0.000_012,
        },
        "text-embedding-3-small": {
            "prompt": 0.000_000_02,
            "completion": 0.000_000_02,
        },
        "text-embedding-ada-002": {
            "prompt": 0.000_000_1,
            "completion": 0.000_000_1,
        },
        "text-embedding-3-large": {
            "prompt": 0.000_000_13,
            "completion": 0.000_000_13,
        },
    }
    if usage is None:
        return None
    try:
        model_pricing = pricing[model]
    except KeyError:
        return None

    prompt_cost = usage.prompt_tokens * model_pricing["prompt"]
    completion_cost = usage.completion_tokens * model_pricing["completion"]
    total_cost = prompt_cost + completion_cost

    return total_cost
