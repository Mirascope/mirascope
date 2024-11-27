"""Handles the stream of completion chunks."""

from collections.abc import AsyncGenerator, Generator
from typing import cast

from mistralai.models import (
    CompletionEvent,
    FunctionCall,
    ToolCall,
)

from ..call_response_chunk import MistralCallResponseChunk
from ..tool import MistralTool


def _handle_chunk(
    chunk: CompletionEvent,
    current_tool_call: ToolCall,
    current_tool_type: type[MistralTool] | None,
    tool_types: list[type[MistralTool]] | None,
) -> tuple[
    MistralTool | None,
    ToolCall,
    type[MistralTool] | None,
]:
    """Handles a chunk of the stream."""
    if not tool_types or not (tool_calls := chunk.data.choices[0].delta.tool_calls):
        return None, current_tool_call, current_tool_type

    tool_call = tool_calls[0]
    # Reset on new tool
    if tool_call.id != "null" and tool_call.function is not None:
        previous_tool_call = current_tool_call.model_copy()
        previous_tool_type = current_tool_type
        current_tool_call = ToolCall(
            id=tool_call.id,
            function=FunctionCall(
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
            )  # pragma: no cover
        if previous_tool_call.id and previous_tool_type is not None:
            return (
                previous_tool_type.from_tool_call(previous_tool_call),
                current_tool_call,
                current_tool_type,
            )

    # Update arguments with each chunk
    if tool_call.function and tool_call.function.arguments:
        current_tool_call.function.arguments += cast(str, tool_call.function.arguments)  # pyright: ignore [reportOperatorIssue]

    return None, current_tool_call, current_tool_type


def handle_stream(
    stream: Generator[CompletionEvent, None, None],
    tool_types: list[type[MistralTool]] | None,
    partial_tools: bool = False,
) -> Generator[tuple[MistralCallResponseChunk, MistralTool | None], None, None]:
    """Iterator over the stream and constructs tools as they are streamed."""
    current_tool_call = ToolCall(
        id="", function=FunctionCall(arguments="", name=""), type="function"
    )
    current_tool_type = None
    last_chuk_data = None
    for chunk in stream:
        if not tool_types or not chunk.data.choices[0].delta.tool_calls:
            if current_tool_type:
                yield (
                    MistralCallResponseChunk(chunk=chunk.data),
                    current_tool_type.from_tool_call(current_tool_call),
                )
                current_tool_type = None
            else:
                yield MistralCallResponseChunk(chunk=chunk.data), None
        tool, current_tool_call, current_tool_type = _handle_chunk(
            chunk,
            current_tool_call,
            current_tool_type,
            tool_types,
        )
        if tool is not None:
            yield MistralCallResponseChunk(chunk=chunk.data), tool
        else:
            last_chuk_data = chunk.data
    if current_tool_type and last_chuk_data:
        yield (
            MistralCallResponseChunk(chunk=last_chuk_data),
            current_tool_type.from_tool_call(current_tool_call),
        )


async def handle_stream_async(
    stream: AsyncGenerator[CompletionEvent, None],
    tool_types: list[type[MistralTool]] | None,
    partial_tools: bool = False,
) -> AsyncGenerator[tuple[MistralCallResponseChunk, MistralTool | None], None]:
    """Async iterator over the stream and constructs tools as they are streamed."""
    current_tool_call = ToolCall(
        id="", function=FunctionCall(arguments="", name=""), type="function"
    )
    current_tool_type = None
    last_chuk_data = None
    async for chunk in stream:
        if not tool_types or not chunk.data.choices[0].delta.tool_calls:
            if current_tool_type:
                yield (
                    MistralCallResponseChunk(chunk=chunk.data),
                    current_tool_type.from_tool_call(current_tool_call),
                )
                current_tool_type = None
            else:
                yield MistralCallResponseChunk(chunk=chunk.data), None
        tool, current_tool_call, current_tool_type = _handle_chunk(
            chunk,
            current_tool_call,
            current_tool_type,
            tool_types,
        )
        if tool is not None:
            yield MistralCallResponseChunk(chunk=chunk.data), tool
        else:
            last_chuk_data = chunk.data
    if current_tool_type and last_chuk_data:
        yield (
            MistralCallResponseChunk(chunk=last_chuk_data),
            current_tool_type.from_tool_call(current_tool_call),
        )
