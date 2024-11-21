"""Handles the stream of completion chunks."""

from collections.abc import AsyncGenerator, Generator

from openai.types.chat import ChatCompletionChunk, ChatCompletionMessageToolCall
from openai.types.chat.chat_completion_message_tool_call import Function

from mirascope.core.base.tool_call_response_chunk import SimpleToolCallResponseChunk

from ..call_response_chunk import OpenAICallResponseChunk
from ..tool import OpenAITool


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
    if (
        not tool_types
        or not chunk.choices
        or not (tool_calls := chunk.choices[0].delta.tool_calls)
    ):
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
            )  # pragma: no cover
        if (
            previous_tool_call.id
            and previous_tool_call.function.arguments
            and previous_tool_type is not None
        ):
            return (
                previous_tool_type.from_tool_call(previous_tool_call),
                current_tool_call,
                current_tool_type,
                SimpleToolCallResponseChunk(
                    type="name", delta=tool_call.function.name
                ),
            )

    # Update arguments with each chunk
    if tool_call.function and tool_call.function.arguments:
        current_tool_call.function.arguments += tool_call.function.arguments

    return (
        None,
        current_tool_call,
        current_tool_type,
        SimpleToolCallResponseChunk(
            type="arguments", delta=tool_call.function.arguments
        ),
    )


def handle_stream(
    stream: Generator[ChatCompletionChunk, None, None],
    tool_types: list[type[OpenAITool]] | None,
) -> Generator[tuple[OpenAICallResponseChunk, OpenAITool | None], None, None]:
    """Iterator over the stream and constructs tools as they are streamed."""
    current_tool_call = ChatCompletionMessageToolCall(
        id="", function=Function(arguments="", name=""), type="function"
    )
    current_tool_type = None
    for chunk in stream:
        if not tool_types or not chunk.choices or not chunk.choices[0].delta.tool_calls:
            if current_tool_type:
                yield (
                    OpenAICallResponseChunk(chunk=chunk),
                    current_tool_type.from_tool_call(current_tool_call),
                )
                current_tool_type = None
            else:
                yield OpenAICallResponseChunk(chunk=chunk), None
        tool, current_tool_call, current_tool_type = _handle_chunk(
            chunk,
            current_tool_call,
            current_tool_type,
            tool_types,
        )
        if tool is not None:
            yield OpenAICallResponseChunk(chunk=chunk), tool
        else:
            yield OpenAICallResponseChunk(chunk=chunk), None


async def handle_stream_async(
    stream: AsyncGenerator[ChatCompletionChunk, None],
    tool_types: list[type[OpenAITool]] | None,
) -> AsyncGenerator[tuple[OpenAICallResponseChunk, OpenAITool | None], None]:
    """Async iterator over the stream and constructs tools as they are streamed."""
    current_tool_call = ChatCompletionMessageToolCall(
        id="", function=Function(arguments="", name=""), type="function"
    )
    current_tool_type = None
    async for chunk in stream:
        if not tool_types or not chunk.choices[0].delta.tool_calls:
            if current_tool_type:
                yield (
                    OpenAICallResponseChunk(chunk=chunk),
                    current_tool_type.from_tool_call(current_tool_call),
                )
                current_tool_type = None
            else:
                yield OpenAICallResponseChunk(chunk=chunk), None
        tool, current_tool_call, current_tool_type = _handle_chunk(
            chunk,
            current_tool_call,
            current_tool_type,
            tool_types,
        )
        if tool is not None:
            yield OpenAICallResponseChunk(chunk=chunk), tool
