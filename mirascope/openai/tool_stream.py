"""A module for convenience around streaming tools with OpenAI."""
from typing import AsyncGenerator, Generator, Literal, Optional, Type, Union, overload

from openai.types.chat.chat_completion_message_tool_call import (
    ChatCompletionMessageToolCall,
    Function,
)

from ..base.tool_stream import BaseToolStream
from ..partial import Partial
from .tools import OpenAITool
from .types import OpenAICallResponseChunk


def _handle_chunk(
    chunk: OpenAICallResponseChunk,
    current_tool_call: ChatCompletionMessageToolCall,
    current_tool_type: Optional[Type[OpenAITool]],
    partial: bool,
) -> tuple[
    Optional[OpenAITool], ChatCompletionMessageToolCall, Optional[Type[OpenAITool]]
]:
    """Handles a chunk of the stream."""
    if not chunk.tool_calls or not chunk.tool_types:
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
            if tool_type.__name__ == tool_call.function.name:
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

    # if partial:
    #     yield (
    #         Partial[current_tool_type].from_tool_call(current_tool_call),
    #         current_tool_call,
    #         current_tool_type,
    #     )

    return None, current_tool_call, current_tool_type


class OpenAIToolStream(BaseToolStream):
    """A base class for streaming tools from response chunks."""

    @classmethod
    @overload
    def from_stream(
        cls,
        stream: Generator[OpenAICallResponseChunk, None, None],
        partial: Literal[True],
    ) -> Generator[Optional[Partial[OpenAITool]], None, None]:
        ...  # pragma: no cover

    @classmethod
    @overload
    def from_stream(
        cls,
        stream: Generator[OpenAICallResponseChunk, None, None],
        partial: Literal[False],
    ) -> Generator[OpenAITool, None, None]:
        ...  # pragma: no cover

    @classmethod
    @overload
    def from_stream(
        cls,
        stream: Generator[OpenAICallResponseChunk, None, None],
        partial: bool,
    ) -> Generator[Union[OpenAITool, Optional[Partial[OpenAITool]]], None, None]:
        ...  # pragma: no cover

    @classmethod
    def from_stream(
        cls,
        stream,
        partial=False,
    ):
        """Yields partial tools from the given stream of chunks.

        Raises:
            RuntimeError: if a tool in the stream is of an unknown type.
        """
        cls._check_version_for_partial(partial)
        current_tool_call = ChatCompletionMessageToolCall(
            id="", function=Function(arguments="", name=""), type="function"
        )
        current_tool_type = None
        for chunk in stream:
            tool, current_tool_call, current_tool_type = _handle_chunk(
                chunk, current_tool_call, current_tool_type, partial
            )
            if tool is not None:
                yield tool
        yield current_tool_type.from_tool_call(current_tool_call)

    @classmethod
    @overload
    async def from_async_stream(
        cls,
        async_stream: AsyncGenerator[OpenAICallResponseChunk, None],
        partial: Literal[True],
    ) -> Generator[Optional[Partial[OpenAITool]], None, None]:
        ...  # pragma: no cover

    @classmethod
    @overload
    async def from_async_stream(
        cls,
        async_stream: AsyncGenerator[OpenAICallResponseChunk, None],
        partial: Literal[False],
    ) -> Generator[OpenAITool, None, None]:
        ...  # pragma: no cover

    @classmethod
    @overload
    async def from_async_stream(
        cls,
        async_stream: AsyncGenerator[OpenAICallResponseChunk, None],
        partial: bool,
    ) -> Generator[Union[OpenAITool, Optional[Partial[OpenAITool]]], None, None]:
        ...  # pragma: no cover

    @classmethod
    async def from_async_stream(cls, async_stream, partial=False):
        """Yields partial tools from the given stream of chunks asynchronously.

        Raises:
            RuntimeError: if a tool in the stream is of an unknown type.
        """
        cls._check_version_for_partial(partial)
        current_tool_call = ChatCompletionMessageToolCall(
            id="", function=Function(arguments="", name=""), type="function"
        )
        current_tool_type = None
        async for chunk in async_stream:
            tool, current_tool_call, current_tool_type = _handle_chunk(
                chunk, current_tool_call, current_tool_type, partial
            )
            if tool is not None:
                yield tool
        yield current_tool_type.from_tool_call(current_tool_call)
