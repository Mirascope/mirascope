"""Classes for using parsers with Chat APIs."""
from typing import Callable, Generator, Optional, Type, Union

from openai.types.chat.chat_completion_message_tool_call import (
    ChatCompletionMessageToolCall,
)
from pydantic import BaseModel

from ..tools import OpenAITool
from ..types import OpenAIChatCompletionChunk
from .utils import (
    append_tool_call_arguments,
    append_tool_call_function_name,
    created_new_tool_call,
    find_tool_class,
)


class OpenAIToolStreamParser(BaseModel):
    """A utility class to parse `OpenAIChatCompletionChunk`s into `OpenAITools`."""

    tool_calls: list[ChatCompletionMessageToolCall] = []
    tools: list[Union[Callable, Type[OpenAITool]]] = []

    def from_stream(
        self, stream: Generator[OpenAIChatCompletionChunk, None, None]
    ) -> Generator[OpenAITool, None, None]:
        """Parses a stream of `OpenAIChatCompletionChunk`s into `OpenAITools`."""
        current_tool_type: Optional[Type[OpenAITool]] = None
        for chunk in stream:
            # Chunks start and end with None so we skip
            if not chunk.tool_calls:
                continue
            # We are making what we think is a reasonable assumption here that
            # tool_calls is never longer than 1. If it is, this will be updated.
            tool_call_chunk = chunk.tool_calls[0]

            if created_new_tool_call(self.tool_calls, tool_call_chunk):
                current_tool_type = None

            tool_call = self.tool_calls[tool_call_chunk.index]
            if tool_call_chunk.id:
                tool_call.id = tool_call_chunk.id

            if append_tool_call_function_name(self.tool_calls, tool_call_chunk):
                tool_class = find_tool_class(
                    self.tool_calls, tool_call_chunk, self.tools
                )
                if tool_class:
                    current_tool_type = tool_class

            append_tool_call_arguments(self.tool_calls, tool_call_chunk)

            try:
                if current_tool_type:
                    tool_call = self.tool_calls[tool_call_chunk.index]
                    yield current_tool_type.from_tool_call(tool_call)
            except ValueError:
                continue
