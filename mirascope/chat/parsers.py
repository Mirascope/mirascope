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


class PartialToolParser(BaseModel):
    """A utility class to parse `OpenAIChatCompletionChunk`s into `PartialModels`."""

    tool_calls: list[ChatCompletionMessageToolCall] = []
    tools: list[Union[Callable, Type[OpenAITool]]] = []

    def from_stream(
        self, stream: Generator[OpenAIChatCompletionChunk, None, None]
    ) -> Generator[Partial, None, None]:
        """Parses a stream of `OpenAIChatCompletionChunk`s into `PartialTools`s."""
        openai_tools = convert_tools_list_to_openai_tools(self.tools)
        prompt: Optional[Type[OpenAITool]] = None
        for chunk in stream:
            tcchunklist = chunk.tool_calls
            if not tcchunklist:
                continue
            for tcchunk in tcchunklist:
                if len(self.tool_calls) <= tcchunk.index:
                    self.tool_calls.append(
                        ChatCompletionMessageToolCall(
                            id="",
                            type="function",
                            function=Function(name="", arguments=""),
                        )
                    )
                    prompt = None
                tc = self.tool_calls[tcchunk.index]
                if tcchunk.id:
                    tc.id += tcchunk.id
                if tcchunk.function and tcchunk.function.name and openai_tools:
                    # construct tool GetCurrentWeather
                    tc.function.name += tcchunk.function.name
                    for prompt_class in openai_tools:
                        if prompt_class.__name__ == tc.function.name:
                            prompt = prompt_class
                if tcchunk.function and tcchunk.function.arguments:
                    # construct json
                    try:
                        tc.function.arguments += tcchunk.function.arguments
                        parsed_json = json.loads(tc.function.arguments)
                        if prompt:
                            yield Partial[prompt](**parsed_json)
                    except json.JSONDecodeError:
                        continue
