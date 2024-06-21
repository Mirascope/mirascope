"""This module contains classes for streaming responses from OpenAI's API."""

from collections.abc import AsyncGenerator, Generator

from openai.types.chat import (
    ChatCompletionAssistantMessageParam,
    ChatCompletionMessageToolCall,
    ChatCompletionUserMessageParam,
)
from openai.types.chat.chat_completion_message_tool_call import Function

from ..base import BaseAsyncStream, BaseStream
from ..base._partial import partial
from .call_response import OpenAICallResponse
from .call_response_chunk import OpenAICallResponseChunk
from .tools import OpenAITool


def _handle_chunk(
    chunk: OpenAICallResponseChunk,
    current_tool_call: ChatCompletionMessageToolCall,
    current_tool_type: type[OpenAITool] | None,
    allow_partial: bool,
) -> tuple[
    OpenAITool | None,
    ChatCompletionMessageToolCall,
    type[OpenAITool] | None,
    bool,
]:
    """Handles a chunk of the stream."""
    if not chunk.tool_types or not chunk.tool_calls:
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
            if tool_type._name() == tool_call.function.name:
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


class OpenAIStream(
    BaseStream[
        OpenAICallResponseChunk,
        ChatCompletionUserMessageParam,
        ChatCompletionAssistantMessageParam,
        OpenAITool,
    ]
):
    """A class for streaming responses from OpenAI's API."""

    def __init__(self, stream: Generator[OpenAICallResponseChunk, None, None]):
        """Initializes an instance of `OpenAIStream`."""
        super().__init__(stream, ChatCompletionAssistantMessageParam)

    def __iter__(
        self,
    ) -> Generator[tuple[OpenAICallResponseChunk, OpenAITool | None], None, None]:
        """Iterator over the stream and constructs tools as they are streamed."""
        current_tool_call = ChatCompletionMessageToolCall(
            id="", function=Function(arguments="", name=""), type="function"
        )
        current_tool_type, tool_calls = None, []
        for chunk, _ in super().__iter__():
            if not chunk.tool_types or not chunk.tool_calls:
                if current_tool_type:
                    yield chunk, current_tool_type.from_tool_call(current_tool_call)
                    tool_calls.append(current_tool_call)
                    current_tool_type = None
                else:
                    yield chunk, None
            tool, current_tool_call, current_tool_type, _ = _handle_chunk(
                chunk, current_tool_call, current_tool_type, False
            )
            if tool is not None:
                yield chunk, tool
                tool_calls.append(tool.tool_call)
        if tool_calls:
            self.message_param["tool_calls"] = tool_calls  # type: ignore

    @classmethod
    def tool_message_params(cls, tools_and_outputs):
        """Returns the tool message parameters for tool call results."""
        return OpenAICallResponse.tool_message_params(tools_and_outputs)


class OpenAIAsyncStream(
    BaseAsyncStream[
        OpenAICallResponseChunk,
        ChatCompletionUserMessageParam,
        ChatCompletionAssistantMessageParam,
        OpenAITool,
    ]
):
    """A class for streaming responses from OpenAI's API."""

    def __init__(self, stream: AsyncGenerator[OpenAICallResponseChunk, None]):
        """Initializes an instance of `OpenAIAsyncStream`."""
        super().__init__(stream, ChatCompletionAssistantMessageParam)

    def __aiter__(
        self,
    ) -> AsyncGenerator[tuple[OpenAICallResponseChunk, OpenAITool | None], None]:
        """Iterator over the stream and constructs tools as they are streamed."""
        stream = super().__aiter__()

        async def generator():
            current_tool_call = ChatCompletionMessageToolCall(
                id="", function=Function(arguments="", name=""), type="function"
            )
            current_tool_type, tool_calls = None, []
            async for chunk, _ in stream:
                if not chunk.tool_types or not chunk.tool_calls:
                    if current_tool_type:
                        yield chunk, current_tool_type.from_tool_call(current_tool_call)
                        tool_calls.append(current_tool_call)
                        current_tool_type = None
                    else:
                        yield chunk, None
                (
                    tool,
                    current_tool_call,
                    current_tool_type,
                    _,
                ) = _handle_chunk(chunk, current_tool_call, current_tool_type, False)
                if tool is not None:
                    yield chunk, tool
                    tool_calls.append(tool.tool_call)
            if tool_calls:
                self.message_param["tool_calls"] = tool_calls  # type: ignore

        return generator()

    @classmethod
    def tool_message_params(cls, tools_and_outputs):
        """Returns the tool message parameters for tool call results."""
        return OpenAICallResponse.tool_message_params(tools_and_outputs)
