"""Utilities for the Mirascope Core OpenAI module."""

import inspect
from collections.abc import AsyncGenerator, Generator
from typing import Any, Awaitable, Callable

from openai import AsyncOpenAI, OpenAI
from openai._base_client import BaseClient
from openai.types.chat import (
    ChatCompletion,
    ChatCompletionChunk,
    ChatCompletionMessageParam,
    ChatCompletionMessageToolCall,
)
from openai.types.chat.chat_completion_message_tool_call import Function

from ..base import BaseTool, _utils
from .call_params import OpenAICallParams
from .call_response_chunk import OpenAICallResponseChunk
from .dyanmic_config import OpenAIDynamicConfig
from .tool import OpenAITool


def setup_call(
    *,
    model: str,
    client: BaseClient | None,
    fn: Callable[..., OpenAIDynamicConfig | Awaitable[OpenAIDynamicConfig]],
    fn_args: dict[str, any],
    dynamic_config: OpenAIDynamicConfig,
    tools: list[type[BaseTool] | Callable] | None,
    json_mode: bool,
    call_params: OpenAICallParams,
    extract: bool,
) -> tuple[
    Callable[..., ChatCompletion],
    str,
    list[dict[str, ChatCompletionMessageParam]],
    list[type[OpenAITool]],
    dict[str, Any],
]:
    prompt_template, messages, tool_types, call_kwargs = _utils.setup_call(
        fn, fn_args, dynamic_config, tools, OpenAITool, call_params
    )
    if client is None:
        client = AsyncOpenAI() if inspect.iscoroutinefunction(fn) else OpenAI()
    create = client.chat.completions.create
    call_kwargs |= {"model": model, "messages": messages}
    if json_mode:
        call_kwargs["response_format"] = {"type": "json_object"}
        messages[-1]["content"] += _utils.json_mode_content(tools[0] if tools else None)
        call_kwargs.pop("tools", None)
    elif extract:
        call_kwargs["tool_choice"] = "required"

    return create, prompt_template, messages, tool_types, call_kwargs


def get_json_output(response: ChatCompletion, json_mode: bool) -> str:
    """Get the JSON output from a completion response."""
    if json_mode and (content := response.choices[0].message.content):
        return content
    elif tool_calls := response.choices[0].message.tool_calls:
        return tool_calls[0].function.arguments
    else:
        raise ValueError("No tool call or JSON object found in response.")


def _handle_chunk(
    chunk: ChatCompletionChunk,
    current_tool_call: ChatCompletionMessageToolCall,
    current_tool_type: type[OpenAITool] | None,
    tool_types: list[type[OpenAITool]] | None,
) -> tuple[
    OpenAITool | None,
    ChatCompletionMessageToolCall,
    type[OpenAITool] | None,
]:
    """Handles a chunk of the stream."""
    if not tool_types or not (tool_calls := chunk.choices[0].delta.tool_calls):
        return None, current_tool_call, current_tool_type

    tool_call = tool_calls[0]
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
        for tool_type in tool_types:
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


def handle_stream(
    stream: Generator[ChatCompletionChunk, None, None],
    tool_types: list[type[OpenAITool]] | None,
) -> Generator[tuple[OpenAICallResponseChunk, OpenAITool | None], None, None]:
    """Iterates over the stream and constructs tools as they are streamed."""
    current_tool_call = ChatCompletionMessageToolCall(
        id="", function=Function(arguments="", name=""), type="function"
    )
    current_tool_type = None
    for chunk in stream:
        if not tool_types or not chunk.choices[0].delta.tool_calls:
            if current_tool_type:
                yield (
                    chunk,
                    current_tool_type.from_tool_call(current_tool_call),
                )
                current_tool_type = None
            else:
                yield chunk, None
        tool, current_tool_call, current_tool_type = _handle_chunk(
            chunk,
            current_tool_call,
            current_tool_type,
            tool_types,
        )
        if tool is not None:
            yield chunk, tool


async def handle_stream_async(
    stream: AsyncGenerator[ChatCompletionChunk, None],
    tool_types: list[type[OpenAITool]] | None,
):
    """Async iterates over the stream and constructs tools as they are streamed."""
    current_tool_call = ChatCompletionMessageToolCall(
        id="", function=Function(arguments="", name=""), type="function"
    )
    current_tool_type = None
    async for chunk in stream:
        if not tool_types or not chunk.choices[0].delta.tool_calls:
            if current_tool_type:
                yield (
                    chunk,
                    current_tool_type.from_tool_call(current_tool_call),
                )
                current_tool_type = None
            else:
                yield chunk, None
        tool, current_tool_call, current_tool_type = _handle_chunk(
            chunk,
            current_tool_call,
            current_tool_type,
            tool_types,
        )
        if tool is not None:
            yield chunk, tool


def openai_api_calculate_cost(
    response: ChatCompletion, model="gpt-3.5-turbo-16k"
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
    if (usage := response.usage) is None:
        return None
    try:
        model = response.model if response.model else model
        model_pricing = pricing[model]
    except KeyError:
        return None

    prompt_cost = usage.prompt_tokens * model_pricing["prompt"]
    completion_cost = usage.completion_tokens * model_pricing["completion"]
    total_cost = prompt_cost + completion_cost

    return total_cost
