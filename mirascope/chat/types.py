"""Classes for responses when interacting with a Chat API."""
from typing import Optional, Type

from openai.types.chat import (
    ChatCompletion,
    ChatCompletionChunk,
    ChatCompletionMessageToolCall,
)
from openai.types.chat.chat_completion import Choice
from openai.types.chat.chat_completion_chunk import Choice as ChunkChoice
from openai.types.chat.chat_completion_chunk import ChoiceDelta, ChoiceDeltaToolCall
from openai.types.chat.chat_completion_message import ChatCompletionMessage
from pydantic import BaseModel

from .tools import OpenAITool


class OpenAIChatCompletion(BaseModel):
    """Convenience wrapper around chat completions."""

    completion: ChatCompletion
    tool_types: Optional[list[Type[OpenAITool]]] = None

    @property
    def choices(self) -> list[Choice]:
        """Returns the array of chat completion choices."""
        return self.completion.choices

    @property
    def choice(self) -> Choice:
        """Returns the 0th choice."""
        return self.completion.choices[0]

    @property
    def message(self) -> ChatCompletionMessage:
        """Returns the message of the chat completion for the 0th choice."""
        return self.completion.choices[0].message

    @property
    def content(self) -> Optional[str]:
        """Returns the content of the chat completion for the 0th choice."""
        return self.completion.choices[0].message.content

    @property
    def tool_calls(self) -> Optional[list[ChatCompletionMessageToolCall]]:
        """Returns the tool calls for the 0th choice message."""
        return self.message.tool_calls

    @property
    def tools(self) -> Optional[list[OpenAITool]]:
        """Returns the tools for the 0th choice message.

        Raises:
            ValidationError: if a tool call doesn't match the tool's schema.
        """
        if not self.tool_types or not self.tool_calls:
            return None

        extracted_tools = []
        for tool_call in self.tool_calls:
            for tool_type in self.tool_types:
                if tool_call.function.name == tool_type.__name__:
                    extracted_tools.append(tool_type.from_tool_call(tool_call))
                    break

        return extracted_tools

    @property
    def tool(self) -> Optional[OpenAITool]:
        """Returns the 0th tool for the 0th choice message.

        Raises:
            ValidationError: if the tool call doesn't match the tool's schema.
        """
        if not self.tool_types or not self.tool_calls or len(self.tool_calls) == 0:
            return None

        tool_call = self.tool_calls[0]
        for tool_type in self.tool_types:
            if self.tool_calls[0].function.name == tool_type.__name__:
                return tool_type.from_tool_call(tool_call)

        return None

    def __str__(self):
        """Returns the contained string content for the 0th choice."""
        return self.content if self.content is not None else ""


class OpenAIChatCompletionChunk(BaseModel):
    """Convenience wrapper around chat completion streaming chunks."""

    chunk: ChatCompletionChunk
    tool_types: Optional[list[Type[OpenAITool]]] = None

    @property
    def choices(self) -> list[ChunkChoice]:
        """Returns the array of chat completion choices."""
        return self.chunk.choices

    @property
    def choice(self) -> ChunkChoice:
        """Returns the 0th choice."""
        return self.chunk.choices[0]

    @property
    def delta(self) -> ChoiceDelta:
        """Returns the delta for the 0th choice."""
        return self.choices[0].delta

    @property
    def content(self) -> Optional[str]:
        """Returns the content for the 0th choice delta."""
        return self.delta.content

    @property
    def tool_calls(self) -> Optional[list[ChoiceDeltaToolCall]]:
        """Returns the partial tool calls for the 0th choice message.

        The first and last `list[ChoiceDeltaToolCall]` will be None indicating start
        and end of stream respectively. The next `list[ChoiceDeltaToolCall]` will
        contain the name of the tool and index and subsequent
        `list[ChoiceDeltaToolCall]`s will contain the arguments which will be strings
        that need to be concatenated with future `list[ChoiceDeltaToolCall]`s to form a
        complete JSON tool calls.
        """
        return self.delta.tool_calls

    def __str__(self) -> str:
        """Returns the chunk content for the 0th choice."""
        return self.content if self.content is not None else ""
