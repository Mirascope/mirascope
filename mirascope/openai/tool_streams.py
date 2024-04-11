"""A module for convenience around streaming tools with OpenAI."""
from typing import AsyncGenerator, Generator, Literal, Optional, Type, overload

from openai.types.chat.chat_completion_message_tool_call import (
    ChatCompletionMessageToolCall,
    Function,
)
from openai.types.chat.completion_create_params import ResponseFormat

from ..base.tool_streams import BaseToolStream
from ..partial import partial
from .tools import OpenAITool
from .types import OpenAICallResponseChunk


def _handle_chunk(
    chunk: OpenAICallResponseChunk,
    current_tool_call: ChatCompletionMessageToolCall,
    current_tool_type: Optional[Type[OpenAITool]],
    allow_partial: bool,
) -> tuple[
    Optional[OpenAITool],
    ChatCompletionMessageToolCall,
    Optional[Type[OpenAITool]],
    bool,
]:
    """Handles a chunk of the stream."""
    if not chunk.tool_types:
        return None, current_tool_call, current_tool_type, False

    if chunk.response_format == ResponseFormat(type="json_object"):
        # Note: we only handle single tool calls in JSON mode.
        current_tool_type = chunk.tool_types[0]
        if chunk.content:
            current_tool_call.function.arguments += chunk.content
            if allow_partial:
                return (
                    partial(current_tool_type).from_tool_call(
                        ChatCompletionMessageToolCall(
                            id="id",
                            function=Function(
                                name=current_tool_type.__name__,
                                arguments=current_tool_call.function.arguments,
                            ),
                            type="function",
                        ),
                        allow_partial=allow_partial,
                    ),
                    current_tool_call,
                    current_tool_type,
                    False,
                )
        return None, current_tool_call, current_tool_type, False

    if not chunk.tool_calls:
        return None, current_tool_call, current_tool_type, False

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
                previous_tool_type.from_tool_call(
                    previous_tool_call, allow_partial=allow_partial
                ),
                current_tool_call,
                current_tool_type,
                True,
            )

    # Update arguments with each chunk
    if tool_call.function and tool_call.function.arguments:
        current_tool_call.function.arguments += tool_call.function.arguments

        if allow_partial and current_tool_type:
            return (
                partial(current_tool_type).from_tool_call(
                    current_tool_call, allow_partial=True
                ),
                current_tool_call,
                current_tool_type,
                False,
            )

    return None, current_tool_call, current_tool_type, False


class OpenAIToolStream(BaseToolStream[OpenAICallResponseChunk, OpenAITool]):
    """A base class for streaming tools from response chunks."""

    @classmethod
    @overload
    def from_stream(
        cls,
        stream: Generator[OpenAICallResponseChunk, None, None],
        allow_partial: Literal[True],
    ) -> Generator[Optional[OpenAITool], None, None]:
        yield ...  # type: ignore  # pragma: no cover

    @classmethod
    @overload
    def from_stream(
        cls,
        stream: Generator[OpenAICallResponseChunk, None, None],
        allow_partial: Literal[False],
    ) -> Generator[OpenAITool, None, None]:
        yield ...  # type: ignore  # pragma: no cover

    @classmethod
    @overload
    def from_stream(
        cls,
        stream: Generator[OpenAICallResponseChunk, None, None],
        allow_partial: bool = False,
    ) -> Generator[Optional[OpenAITool], None, None]:
        yield ...  # type: ignore  # pragma: no cover

    @classmethod
    def from_stream(cls, stream, allow_partial=False):
        """Yields partial tools from the given stream of chunks.

        Args:
            stream: The generator of chunks from which to stream tools.
            allow_partial: Whether to allow partial tools.

        Raises:
            RuntimeError: if a tool in the stream is of an unknown type.
        """
        cls._check_version_for_partial(allow_partial)
        current_tool_call = ChatCompletionMessageToolCall(
            id="", function=Function(arguments="", name=""), type="function"
        )
        current_tool_type = None
        for chunk in stream:
            tool, current_tool_call, current_tool_type, starting_new = _handle_chunk(
                chunk, current_tool_call, current_tool_type, allow_partial
            )
            if tool is not None:
                yield tool
            if starting_new:
                yield None
        if current_tool_type:
            yield current_tool_type.from_tool_call(current_tool_call)

    @classmethod
    @overload
    async def from_async_stream(
        cls,
        stream: AsyncGenerator[OpenAICallResponseChunk, None],
        allow_partial: Literal[True],
    ) -> AsyncGenerator[Optional[OpenAITool], None]:
        yield ...  # type: ignore  # pragma: no cover

    @classmethod
    @overload
    async def from_async_stream(
        cls,
        stream: AsyncGenerator[OpenAICallResponseChunk, None],
        allow_partial: Literal[False],
    ) -> AsyncGenerator[OpenAITool, None]:
        yield ...  # type: ignore  # pragma: no cover

    @classmethod
    @overload
    async def from_async_stream(
        cls,
        stream: AsyncGenerator[OpenAICallResponseChunk, None],
        allow_partial: bool = False,
    ) -> AsyncGenerator[Optional[OpenAITool], None]:
        yield ...  # type: ignore  # pragma: no cover

    @classmethod
    async def from_async_stream(cls, async_stream, allow_partial=False):
        """Yields partial tools from the given stream of chunks asynchronously.

        Args:
            stream: The async generator of chunks from which to stream tools.
            allow_partial: Whether to allow partial tools.

        Raises:
            RuntimeError: if a tool in the stream is of an unknown type.
        """
        cls._check_version_for_partial(allow_partial)
        current_tool_call = ChatCompletionMessageToolCall(
            id="", function=Function(arguments="", name=""), type="function"
        )
        current_tool_type = None
        async for chunk in async_stream:
            tool, current_tool_call, current_tool_type, starting_new = _handle_chunk(
                chunk, current_tool_call, current_tool_type, allow_partial
            )
            if tool is not None:
                yield tool
            if starting_new:
                yield None
        if current_tool_type:
            yield current_tool_type.from_tool_call(current_tool_call)
