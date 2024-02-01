"""Classes for using parsers with Chat APIs."""
import json
from typing import Callable, Generator, Optional, Type, Union

from openai.types.chat.chat_completion_message_tool_call import (
    ChatCompletionMessageToolCall,
    Function,
)
from pydantic import BaseModel

from ..partial import Partial
from .tools import OpenAITool
from .types import OpenAIChatCompletionChunk
from .utils import convert_tools_list_to_openai_tools


class PartialOpenAIToolParser(BaseModel):
    """A utility class to parse `OpenAIChatCompletionChunk`s into `PartialModels`."""

    tool_calls: list[ChatCompletionMessageToolCall] = []
    tools: list[Union[Callable, Type[OpenAITool]]] = []

    def from_stream(
        self, stream: Generator[OpenAIChatCompletionChunk, None, None]
    ) -> Generator[Partial, None, None]:
        """Parses a stream of `OpenAIChatCompletionChunk`s into `PartialTools`s."""
        openai_tools = convert_tools_list_to_openai_tools(self.tools)
        tool_type: Optional[Type[OpenAITool]] = None
        for chunk in stream:
            if not chunk.tool_calls:
                continue
            for tool_call_chunk in chunk.tool_calls:
                if len(self.tool_calls) <= tool_call_chunk.index:
                    self.tool_calls.append(
                        ChatCompletionMessageToolCall(
                            id="",
                            type="function",
                            function=Function(name="", arguments=""),
                        )
                    )
                    # reset tool type for following chunks
                    tool_type = None
                tool_call = self.tool_calls[tool_call_chunk.index]
                if tool_call_chunk.id:
                    tool_call.id += tool_call_chunk.id
                if (
                    tool_call_chunk.function
                    and tool_call_chunk.function.name
                    and openai_tools
                ):
                    # set tool type for the next iterations
                    tool_call.function.name += tool_call_chunk.function.name
                    for tool_class in openai_tools:
                        if tool_class.__name__ == tool_call.function.name:
                            tool_type = tool_class
                if tool_call_chunk.function and tool_call_chunk.function.arguments:
                    # construct json
                    # return completed partial tool
                    try:
                        tool_call.function.arguments += (
                            tool_call_chunk.function.arguments
                        )
                        parsed_json = json.loads(tool_call.function.arguments)
                        if tool_type:
                            # mypy cannot handle any dynamically created types
                            yield Partial[tool_type](**parsed_json)  # type: ignore
                    except json.JSONDecodeError:
                        continue
