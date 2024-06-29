"""This module contains the `OpenAICallResponseChunk` class."""

from openai.types.chat import ChatCompletionChunk
from openai.types.chat.chat_completion_chunk import (
    Choice,
    ChoiceDelta,
    ChoiceDeltaToolCall,
)
from openai.types.completion_usage import CompletionUsage

from ..base import BaseCallResponseChunk


class OpenAICallResponseChunk(BaseCallResponseChunk[ChatCompletionChunk]):
    '''A convenience wrapper around the OpenAI `ChatCompletionChunk` streamed chunks.

    When calling the OpenAI API using a function decorated with `openai_call` and
    `stream` set to `True`, the stream will contain `OpenAIResponseChunk` instances with
    properties that allow for more convenient access to commonly used attributes.

    Example:

    ```python
    from mirascope.core.openai import openai_call

    @openai_call(model="gpt-4o", stream=True)
    def recommend_book(genre: str):
        """Recommend a {genre} book."""

    stream = recommend_book("fantasy")  # response is an `OpenAIStream`
    for chunk in stream:
        print(chunk.content, end="", flush=True)
    #> Sure! I would recommend...
    ```
    '''

    @property
    def choices(self) -> list[Choice]:
        """Returns the array of chat completion choices."""
        return self.chunk.choices

    @property
    def choice(self) -> Choice:
        """Returns the 0th choice."""
        return self.chunk.choices[0]

    @property
    def delta(self) -> ChoiceDelta | None:
        """Returns the delta for the 0th choice."""
        if self.chunk.choices:
            return self.chunk.choices[0].delta
        return None

    @property
    def content(self) -> str:
        """Returns the content for the 0th choice delta."""
        return (
            self.delta.content if self.delta is not None and self.delta.content else ""
        )

    @property
    def model(self) -> str:
        """Returns the name of the response model."""
        return self.chunk.model

    @property
    def id(self) -> str:
        """Returns the id of the response."""
        return self.chunk.id

    @property
    def finish_reasons(self) -> list[str]:
        """Returns the finish reasons of the response."""
        return [str(choice.finish_reason) for choice in self.chunk.choices]

    @property
    def tool_calls(self) -> list[ChoiceDeltaToolCall] | None:
        """Returns the partial tool calls for the 0th choice message.

        The first `list[ChoiceDeltaToolCall]` will contain the name of the tool and
        index, and subsequent `list[ChoiceDeltaToolCall]`s will contain the arguments
        which will be strings that need to be concatenated with future
        `list[ChoiceDeltaToolCall]`s to form a complete JSON tool calls. The last
        `list[ChoiceDeltaToolCall]` will be None indicating end of stream.
        """
        if self.delta:
            return self.delta.tool_calls
        return None

    @property
    def usage(self) -> CompletionUsage | None:
        """Returns the usage of the chat completion."""
        if self.chunk.usage:
            return self.chunk.usage
        return None

    @property
    def input_tokens(self) -> int | None:
        """Returns the number of input tokens."""
        if self.usage:
            return self.usage.prompt_tokens
        return None

    @property
    def output_tokens(self) -> int | None:
        """Returns the number of output tokens."""
        if self.usage:
            return self.usage.completion_tokens
        return None
