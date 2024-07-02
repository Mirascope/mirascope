"""Utilities for handling a stream of messages."""

import json
from collections.abc import AsyncGenerator, Generator
from typing import Callable

from anthropic.types import MessageStreamEvent, TextBlock, ToolUseBlock

from ..tool import AnthropicTool


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
