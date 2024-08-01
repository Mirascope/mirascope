"""Handles the stream of completion chunks."""

from collections.abc import AsyncGenerator, Generator

from mistralai.models.chat_completion import (
    ChatCompletionStreamResponse,
    FunctionCall,
    ToolCall,
    ToolType,
)

from ..call_response_chunk import MistralCallResponseChunk
from ..tool import MistralTool


def _handle_chunk(
    chunk: ChatCompletionStreamResponse,
    current_tool_call: ToolCall,
    current_tool_type: type[MistralTool] | None,
    tool_types: list[type[MistralTool]] | None,
) -> tuple[
    MistralTool | None,
    ToolCall,
    type[MistralTool] | None,
]:
    """Handles a chunk of the stream."""
    if not tool_types or not (tool_calls := chunk.choices[0].delta.tool_calls):
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
            type=ToolType.function,
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
        current_tool_call.function.arguments += tool_call.function.arguments

    return None, current_tool_call, current_tool_type


def handle_stream(
    stream: Generator[ChatCompletionStreamResponse, None, None],
    tool_types: list[type[MistralTool]] | None,
) -> Generator[tuple[MistralCallResponseChunk, MistralTool | None], None, None]:
    """Iterator over the stream and constructs tools as they are streamed."""
    current_tool_call = ToolCall(
        id="", function=FunctionCall(arguments="", name=""), type=ToolType.function
    )
    current_tool_type = None
    for chunk in stream:
        if not tool_types or not chunk.choices[0].delta.tool_calls:
            if current_tool_type:
                yield (
                    MistralCallResponseChunk(chunk=chunk),
                    current_tool_type.from_tool_call(current_tool_call),
                )
                current_tool_type = None
            else:
                yield MistralCallResponseChunk(chunk=chunk), None
        tool, current_tool_call, current_tool_type = _handle_chunk(
            chunk,
            current_tool_call,
            current_tool_type,
            tool_types,
        )
        if tool is not None:
            yield MistralCallResponseChunk(chunk=chunk), tool


async def handle_stream_async(
    stream: AsyncGenerator[ChatCompletionStreamResponse, None],
    tool_types: list[type[MistralTool]] | None,
) -> AsyncGenerator[tuple[MistralCallResponseChunk, MistralTool | None], None]:
    """Async iterator over the stream and constructs tools as they are streamed."""
    current_tool_call = ToolCall(
        id="", function=FunctionCall(arguments="", name=""), type=ToolType.function
    )
    current_tool_type = None
    async for chunk in stream:
        if not tool_types or not chunk.choices[0].delta.tool_calls:
            if current_tool_type:
                yield (
                    MistralCallResponseChunk(chunk=chunk),
                    current_tool_type.from_tool_call(current_tool_call),
                )
                current_tool_type = None
            else:
                yield MistralCallResponseChunk(chunk=chunk), None
        tool, current_tool_call, current_tool_type = _handle_chunk(
            chunk,
            current_tool_call,
            current_tool_type,
            tool_types,
        )
        if tool is not None:
            yield MistralCallResponseChunk(chunk=chunk), tool
