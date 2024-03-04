"""Utility functions for using OpenAIToolParser."""
from typing import Callable, Optional, Type, Union

from openai.types.chat.chat_completion_chunk import ChoiceDeltaToolCall
from openai.types.chat.chat_completion_message_tool_call import (
    ChatCompletionMessageToolCall,
    Function,
)

from ..tools import OpenAITool
from ..utils import convert_tools_list_to_openai_tools


def created_new_tool_call(
    tool_calls: list[ChatCompletionMessageToolCall],
    tool_call_chunk: ChoiceDeltaToolCall,
) -> bool:
    """Handles creating a new tool call if `tool_call_chunk` starts a new tool call.

    Args:
        tool_calls: The current list of tool calls being built in the stream parser.
        tool_call_chunk: The current chunk in the stream to be parsed.

    Returns:
        `True` if a new tool call was created and added to `tool_calls`.
    """
    if len(tool_calls) <= tool_call_chunk.index:
        tool_calls.append(
            ChatCompletionMessageToolCall(
                id="",
                type="function",
                function=Function(name="", arguments=""),
            )
        )
        return True
    return False


def append_tool_call_function_name(
    tool_calls: list[ChatCompletionMessageToolCall],
    tool_call_chunk: ChoiceDeltaToolCall,
) -> bool:
    """Build tool call function from tool call chunks.

    Args:
        tool_calls: The current list of tool calls being built in the stream parser.
        tool_call_chunk: The current chunk in the stream to be parsed.

    Returns:
        `True` if a new tool call function name was added to `tool_calls`.
    """
    tool_call = tool_calls[tool_call_chunk.index]
    if tool_call_chunk.function and tool_call_chunk.function.name:
        tool_call.function.name += tool_call_chunk.function.name
        return True
    return False


def find_tool_class(
    tool_calls: list[ChatCompletionMessageToolCall],
    tool_call_chunk: ChoiceDeltaToolCall,
    tools: list[Union[Callable, Type[OpenAITool]]],
) -> Optional[Type[OpenAITool]]:
    """Build tool call function from tool call chunks and set tool based on name.

    Args:
        tool_calls: The current list of tool calls being built in the stream parser.
        tool_call_chunk: The current chunk in the stream to be parsed.
        tools: The list of tools to be used in the stream parser.

    Returns:
        `Type[OpenAITool]` if the chunk contains the name of a valid tool.

    """
    openai_tools = convert_tools_list_to_openai_tools(tools)
    if openai_tools is None:
        openai_tools = []
    tool_call = tool_calls[tool_call_chunk.index]
    for tool_class in openai_tools:
        if tool_class.__name__ == tool_call.function.name:
            return tool_class
    return None


def append_tool_call_arguments(
    tool_calls: list[ChatCompletionMessageToolCall],
    tool_call_chunk: ChoiceDeltaToolCall,
) -> bool:
    """Build tool call function arguments from tool call chunks.

    Args:
        tool_calls: The current list of tool calls being built in the stream parser.
        tool_call_chunk: The current chunk in the stream to be parsed.

    Returns:
        `True` if a new tool call function argument was added to `tool_calls`.
    """
    tool_call = tool_calls[tool_call_chunk.index]
    if tool_call_chunk.function and tool_call_chunk.function.arguments:
        tool_call.function.arguments += tool_call_chunk.function.arguments
        return True
    return False
