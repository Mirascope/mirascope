"""Utility functions for using OpenAIToolParser."""
from typing import TYPE_CHECKING, Union

from openai.types.chat.chat_completion_chunk import ChoiceDeltaToolCall
from openai.types.chat.chat_completion_message_tool_call import (
    ChatCompletionMessageToolCall,
    Function,
)

from ..utils import convert_tools_list_to_openai_tools

if TYPE_CHECKING:
    from .openai_parsers import OpenAIToolStreamParser
    from .openai_parsers_async import AsyncOpenAIToolStreamParser


def handle_new_index(
    self: Union["OpenAIToolStreamParser", "AsyncOpenAIToolStreamParser"],
    tool_call_chunk: ChoiceDeltaToolCall,
) -> None:
    """Instantiate new tool call when index changes and reset tool type."""
    if len(self.tool_calls) <= tool_call_chunk.index:
        self.tool_calls.append(
            ChatCompletionMessageToolCall(
                id="",
                type="function",
                function=Function(name="", arguments=""),
            )
        )
        self._current_tool_type = None


def handle_new_id(
    self: Union["OpenAIToolStreamParser", "AsyncOpenAIToolStreamParser"],
    tool_call_chunk: ChoiceDeltaToolCall,
) -> None:
    """Build tool call from tool call chunks."""
    tool_call = self.tool_calls[tool_call_chunk.index]
    if tool_call_chunk.id:
        tool_call.id = tool_call_chunk.id


def handle_new_function(
    self: Union["OpenAIToolStreamParser", "AsyncOpenAIToolStreamParser"],
    tool_call_chunk: ChoiceDeltaToolCall,
) -> None:
    """Build tool call function from tool call chunks and set tool based on name."""
    openai_tools = convert_tools_list_to_openai_tools(self.tools)
    tool_call = self.tool_calls[tool_call_chunk.index]
    if tool_call_chunk.function and tool_call_chunk.function.name and openai_tools:
        tool_call.function.name += tool_call_chunk.function.name
        for tool_class in openai_tools:
            if tool_class.__name__ == tool_call.function.name:
                self._current_tool_type = tool_class


def handle_new_arguments(
    self: Union["OpenAIToolStreamParser", "AsyncOpenAIToolStreamParser"],
    tool_call_chunk: ChoiceDeltaToolCall,
) -> None:
    """Build tool call function arguments from tool call chunks."""
    tool_call = self.tool_calls[tool_call_chunk.index]
    if tool_call_chunk.function and tool_call_chunk.function.arguments:
        tool_call.function.arguments += tool_call_chunk.function.arguments
