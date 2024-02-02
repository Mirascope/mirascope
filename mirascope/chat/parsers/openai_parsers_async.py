"""Asynchronous classes for using parsers with Chat APIs."""
from typing import AsyncGenerator, Callable, Optional, Type, Union

from openai.types.chat.chat_completion_message_tool_call import (
    ChatCompletionMessageToolCall,
)
from pydantic import BaseModel

from ..tools import OpenAITool
from ..types import OpenAIChatCompletionChunk
from .utils import (
    handle_new_arguments,
    handle_new_function,
    handle_new_id,
    handle_new_index,
)


class AsyncOpenAIToolStreamParser(BaseModel):
    """A utility class to parse `OpenAIChatCompletionChunk`s into `OpenAITools`.

    This is an async version of `OpenAIToolStreamParser`.
    """

    tool_calls: list[ChatCompletionMessageToolCall] = []
    tools: list[Union[Callable, Type[OpenAITool]]] = []
    _current_tool_type: Optional[Type[OpenAITool]] = None

    async def from_stream(
        self, stream: AsyncGenerator[OpenAIChatCompletionChunk, None]
    ) -> AsyncGenerator[OpenAITool, None]:
        """Parses a stream of `OpenAIChatCompletionChunk`s into `OpenAITools` async."""

        async for chunk in stream:
            # Chunks start and end with None so we skip
            if not chunk.tool_calls:
                continue
            # We are making what we think is a reasonable assumption here that
            # tool_calls is never longer than 1. If it is, this will be updated.
            tool_call_chunk = chunk.tool_calls[0]

            handle_new_index(self, tool_call_chunk)

            handle_new_id(self, tool_call_chunk)

            handle_new_function(self, tool_call_chunk)

            handle_new_arguments(self, tool_call_chunk)

            try:
                if self._current_tool_type:
                    tool_call = self.tool_calls[tool_call_chunk.index]
                    yield self._current_tool_type.from_tool_call(tool_call)
            except ValueError:
                continue
