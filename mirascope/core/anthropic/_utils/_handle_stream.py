"""Utilities for handling a stream of messages."""

from collections.abc import AsyncGenerator, Generator

import jiter
from anthropic.types import MessageStreamEvent, ToolUseBlock

from ..call_response_chunk import AnthropicCallResponseChunk
from ..tool import AnthropicTool


def _handle_chunk(
    buffer: str,
    chunk: MessageStreamEvent,
    current_tool_call: ToolUseBlock,
    current_tool_type: type[AnthropicTool] | None,
    tool_types: list[type[AnthropicTool]] | None,
    partial_tools: bool = False,
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
        current_tool_call.input = jiter.from_json(buffer.encode())
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
            raise RuntimeError(
                f"Unknown tool type in stream: {content_block.name}."
            )  # pragma: no cover
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

        # Return partial tool if enabled
        if partial_tools and current_tool_type:
            partial_tool_call = ToolUseBlock(
                id=current_tool_call.id,
                input=buffer,
                name=current_tool_call.name,
                type="tool_use",
            )
            partial_tool = current_tool_type.from_tool_call(partial_tool_call, True)
            partial_tool.delta = chunk.delta.partial_json
            return buffer, partial_tool, current_tool_call, current_tool_type
    return buffer, None, current_tool_call, current_tool_type


def handle_stream(
    stream: Generator[MessageStreamEvent, None, None],
    tool_types: list[type[AnthropicTool]] | None,
    partial_tools: bool = False,
) -> Generator[tuple[AnthropicCallResponseChunk, AnthropicTool | None], None, None]:
    """Iterator over the stream and constructs tools as they are streamed."""
    current_tool_call = ToolUseBlock(id="", input={}, name="", type="tool_use")
    current_tool_type, buffer = None, ""
    for chunk in stream:
        buffer, tool, current_tool_call, current_tool_type = _handle_chunk(
            buffer,
            chunk,
            current_tool_call,
            current_tool_type,
            tool_types,
            partial_tools,
        )
        yield AnthropicCallResponseChunk(chunk=chunk), tool


async def handle_stream_async(
    stream: AsyncGenerator[MessageStreamEvent, None],
    tool_types: list[type[AnthropicTool]] | None,
    partial_tools: bool = False,
) -> AsyncGenerator[tuple[AnthropicCallResponseChunk, AnthropicTool | None], None]:
    current_tool_call = ToolUseBlock(id="", input={}, name="", type="tool_use")
    current_tool_type, buffer = None, ""
    async for chunk in stream:
        buffer, tool, current_tool_call, current_tool_type = _handle_chunk(
            buffer,
            chunk,
            current_tool_call,
            current_tool_type,
            tool_types,
            partial_tools,
        )
        yield AnthropicCallResponseChunk(chunk=chunk), tool
