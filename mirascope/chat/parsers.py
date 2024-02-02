"""Classes for using parsers with Chat APIs."""
import json
from typing import Callable, Generator, Optional, Type, Union

from openai.types.chat.chat_completion_message_tool_call import (
    ChatCompletionMessageToolCall,
    Function,
)
from pydantic import BaseModel

from .tools import OpenAITool
from .types import OpenAIChatCompletionChunk
from .utils import convert_tools_list_to_openai_tools


class OpenAIToolStreamParser(BaseModel):
    """A utility class to parse `OpenAIChatCompletionChunk`s into `OpenAITools`."""

    tool_calls: list[ChatCompletionMessageToolCall] = []
    tools: list[Union[Callable, Type[OpenAITool]]] = []

    def from_stream(
        self, stream: Generator[OpenAIChatCompletionChunk, None, None]
    ) -> Generator[OpenAITool, None, None]:
        """Parses a stream of `OpenAIChatCompletionChunk`s into `OpenAITools`."""
        openai_tools = convert_tools_list_to_openai_tools(self.tools)
        tool_type: Optional[Type[OpenAITool]] = None

        for chunk in stream:
            # Chunks start and end with None so we skip
            if not chunk.tool_calls:
                continue
            # We are making what we think is a reasonable assumption here that
            # tool_calls is never longer than 1. If it is, this will be updated.
            tool_call_chunk = chunk.tool_calls[0]

            # Instantiate new tool call when index changes and reset tool type
            if len(self.tool_calls) <= tool_call_chunk.index:
                self.tool_calls.append(
                    ChatCompletionMessageToolCall(
                        id="",
                        type="function",
                        function=Function(name="", arguments=""),
                    )
                )
                tool_type = None

            tool_call = self.tool_calls[tool_call_chunk.index]

            # Build tool call from tool call chunks
            if tool_call_chunk.id:
                tool_call.id = tool_call_chunk.id

            # Build tool call function from tool call chunks and set tool based on name
            if (
                tool_call_chunk.function
                and tool_call_chunk.function.name
                and openai_tools
            ):
                tool_call.function.name += tool_call_chunk.function.name
                for tool_class in openai_tools:
                    if tool_class.__name__ == tool_call.function.name:
                        tool_type = tool_class

            # Build tool call function arguments from tool call chunks and return
            # the OpenAITool if arguments are validated
            if tool_call_chunk.function and tool_call_chunk.function.arguments:
                try:
                    tool_call.function.arguments += tool_call_chunk.function.arguments
                    parsed_json = json.loads(tool_call.function.arguments)
                    if tool_type:
                        yield tool_type(**parsed_json)
                except json.JSONDecodeError:
                    continue
