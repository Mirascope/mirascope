"""Handles the stream of completion chunks."""

import json
from collections.abc import AsyncGenerator, Generator

from mypy_boto3_bedrock_runtime.type_defs import (
    ToolUseBlockOutputTypeDef,
)
from typing_extensions import TypedDict

from .._types import (
    AsyncStreamOutputChunk,
    StreamOutputChunk,
    ToolUseBlockContentTypeDef,
)
from ..call_response_chunk import BedrockCallResponseChunk
from ..tool import BedrockTool


class ToolUseChunk(TypedDict):
    tool_use_id: str
    input_chunk: str
    name: str
    stop: bool


def _handle_chunk(
    chunk: StreamOutputChunk | AsyncStreamOutputChunk,
    current_tool_use_chunk: ToolUseChunk | None,
    tool_types: list[type[BedrockTool]] | None,
) -> tuple[
    BedrockCallResponseChunk | None,
    BedrockTool | None,
    ToolUseChunk | None,
]:
    """Handles a chunk of the stream."""
    if not tool_types:
        return BedrockCallResponseChunk(chunk=chunk), None, None
    elif (content_block_start := chunk.get("contentBlockStart")) and (
        tool_use := content_block_start["start"].get("toolUse")
    ):
        current_tool_use_chunk = ToolUseChunk(
            tool_use_id=tool_use["toolUseId"],
            input_chunk="",
            name=tool_use["name"],
            stop=False,
        )
    elif (
        (content_block_delta := chunk.get("contentBlockDelta"))
        and (tool_use := content_block_delta["delta"].get("toolUse"))
        and current_tool_use_chunk
        and not current_tool_use_chunk["stop"]
    ):
        current_tool_use_chunk["input_chunk"] += tool_use["input"]
        return None, None, current_tool_use_chunk
    elif "contentBlockStop" in chunk and current_tool_use_chunk:
        current_tool_use_chunk["stop"] = True
        return None, None, current_tool_use_chunk
    elif current_tool_use_chunk and current_tool_use_chunk["stop"]:
        for tool_type in tool_types:
            if current_tool_use_chunk["name"] == tool_type._name():
                current_tool_use = ToolUseBlockContentTypeDef(
                    toolUse=ToolUseBlockOutputTypeDef(
                        toolUseId=current_tool_use_chunk["tool_use_id"],
                        input=json.loads(current_tool_use_chunk["input_chunk"]),
                        name=current_tool_use_chunk["name"],
                    )
                )
                return (
                    BedrockCallResponseChunk(chunk=chunk),
                    tool_type.from_tool_call(current_tool_use),
                    None,
                )
    return BedrockCallResponseChunk(chunk=chunk), None, current_tool_use_chunk


def handle_stream(
    stream: Generator[StreamOutputChunk, None, None],
    tool_types: list[type[BedrockTool]] | None,
    partial_tools: bool = False,
) -> Generator[tuple[BedrockCallResponseChunk, BedrockTool | None], None, None]:
    """Iterator over the stream and constructs tools as they are streamed."""
    current_tool_use_chunk = None
    for chunk in stream:
        call_response, tool, current_tool_use_chunk = _handle_chunk(
            chunk, current_tool_use_chunk, tool_types
        )
        if call_response:
            yield call_response, tool


async def handle_stream_async(
    stream: AsyncGenerator[AsyncStreamOutputChunk, None],
    tool_types: list[type[BedrockTool]] | None,
    partial_tools: bool = False,
) -> AsyncGenerator[tuple[BedrockCallResponseChunk, BedrockTool | None], None]:
    """Async iterator over the stream and constructs tools as they are streamed."""
    current_tool_use_chunk = None
    async for chunk in stream:
        call_response, tool, current_tool_use_chunk = _handle_chunk(
            chunk, current_tool_use_chunk, tool_types
        )
        if call_response:
            yield call_response, tool
