"""Utilities for the Mirascope Core Anthropic module."""

import inspect
import json
from collections.abc import AsyncGenerator, Generator
from typing import Any, Awaitable, Callable

from anthropic import Anthropic, AsyncAnthropic
from anthropic._base_client import BaseClient
from anthropic.types import (
    Message,
    MessageParam,
    MessageStreamEvent,
    TextBlock,
    ToolUseBlock,
)

from ..base import BaseTool, _utils
from .call_params import AnthropicCallParams
from .call_response_chunk import AnthropicCallResponseChunk
from .dynamic_config import AnthropicDynamicConfig
from .tool import AnthropicTool


def setup_call(
    *,
    model: str,
    client: BaseClient | None,
    fn: Callable[..., AnthropicDynamicConfig | Awaitable[AnthropicDynamicConfig]],
    fn_args: dict[str, any],
    dynamic_config: AnthropicDynamicConfig,
    tools: list[type[BaseTool] | Callable] | None,
    json_mode: bool,
    call_params: AnthropicCallParams,
    extract: bool,
) -> tuple[
    Callable[..., Message],
    str,
    list[dict[str, MessageParam]],
    list[type[AnthropicTool]],
    dict[str, Any],
]:
    prompt_template, messages, tool_types, call_kwargs = _utils.setup_call(
        fn, fn_args, dynamic_config, tools, AnthropicTool, call_params
    )
    if messages[0]["role"] == "system":
        call_kwargs["system"] = messages.pop(0)["content"]
    if client is None:
        client = AsyncAnthropic() if inspect.iscoroutinefunction(fn) else Anthropic()
    create = client.messages.create
    call_kwargs |= {"model": model, "messages": messages}

    if json_mode:
        messages[-1]["content"] += _utils.json_mode_content(
            tool_types[0] if tools else None
        )
        call_kwargs.pop("tools", None)
    elif extract:
        call_kwargs["tool_choice"] = {"type": "tool", "name": tool_types[0]._name()}

    return create, prompt_template, messages, tool_types, call_kwargs


def get_json_output(response: Message, json_mode: bool):
    """Get the JSON output from a completion response."""
    block = response.content[0]
    if json_mode and block.type == "text":
        json_start = block.text.index("{")
        json_end = block.text.rfind("}")
        return block.text[json_start : json_end + 1]
    elif block.type == "tool_use":
        return block.input
    else:
        raise ValueError("No tool call or JSON object found in response.")


def _handle_chunk(
    buffer: str,
    chunk: MessageStreamEvent,
    current_tool_call: ToolUseBlock,
    current_tool_type: type[AnthropicTool] | None,
    tool_types: list[type[AnthropicTool]] | None,
) -> tuple[
    str,
    AnthropicTool | None,
    ToolUseBlock,
    type[AnthropicTool] | None,
]:
    """Handles a chunk of the stream."""
    if not tool_types:
        return buffer, None, current_tool_call, current_tool_type

    if chunk.type == "content_block_stop" and current_tool_type and buffer:
        current_tool_call.input = json.loads(buffer)
        return (
            "",
            current_tool_type.from_tool_call(current_tool_call),
            ToolUseBlock(id="", input={}, name="", type="tool_use"),
            None,
        )

    if chunk.type == "content_block_start" and isinstance(
        chunk.content_block, ToolUseBlock
    ):
        content_block = chunk.content_block
        current_tool_type = None
        for tool_type in tool_types:
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

    if chunk.type == "content_block_delta" and chunk.delta.type == "input_json_delta":
        buffer += chunk.delta.partial_json

    return buffer, None, current_tool_call, current_tool_type


def handle_stream(
    stream: Generator[MessageStreamEvent, None, None],
    tool_types: list[type[AnthropicTool] | Callable],
):
    """Iterator over the stream and constructs tools as they are streamed."""
    current_text_block = TextBlock(id="", text="", type="text")
    current_tool_call = ToolUseBlock(id="", input={}, name="", type="tool_use")
    current_tool_type, content, buffer = None, [], ""
    for chunk in stream:
        buffer, tool, current_tool_call, current_tool_type = _handle_chunk(
            buffer, chunk, current_tool_call, current_tool_type, tool_types
        )
        if tool is not None:
            yield chunk, tool
            if current_text_block.text:
                content.append(current_text_block)
                current_text_block = TextBlock(id="", text="", type="text")
            content.append(tool.tool_call)
        else:
            yield chunk, None
            if hasattr(chunk, "content_block") and hasattr(chunk.content_block, "text"):
                current_text_block.text += chunk.content_block.text


async def handle_stream_async(
    stream: AsyncGenerator[MessageStreamEvent, None],
    tool_types: list[type[AnthropicTool] | Callable],
):
    """Async iterator over the stream and constructs tools as they are streamed."""
    current_text_block = TextBlock(id="", text="", type="text")
    current_tool_call = ToolUseBlock(id="", input={}, name="", type="tool_use")
    current_tool_type, content, buffer = None, [], ""
    async for chunk in stream:
        buffer, tool, current_tool_call, current_tool_type = _handle_chunk(
            buffer, chunk, current_tool_call, current_tool_type, tool_types
        )
        if tool is not None:
            yield chunk, tool
            if current_text_block.text:
                content.append(current_text_block)
                current_text_block = TextBlock(id="", text="", type="text")
            content.append(tool.tool_call)
        else:
            yield chunk, None
            if hasattr(chunk, "content_block") and hasattr(chunk.content_block, "text"):
                current_text_block.text += chunk.content_block.text


def anthropic_api_calculate_cost(
    response: Message, model="claude-3-haiku-20240229"
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
        model = response.model if response.model else model
        model_pricing = pricing[model]
    except KeyError:
        return None

    prompt_cost = response.usage.input_tokens * model_pricing["prompt"]
    completion_cost = response.usage.output_tokens * model_pricing["completion"]
    total_cost = prompt_cost + completion_cost

    return total_cost
