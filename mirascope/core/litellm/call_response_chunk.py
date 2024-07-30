"""This module contains the `LiteLLMCallResponseChunk` class."""

from typing import cast

from litellm.batches.main import ModelResponse
from openai.types.chat.chat_completion_chunk import Choice
from openai.types.completion_usage import CompletionUsage

from ..base import BaseCallResponseChunk


class LiteLLMCallResponseChunk(BaseCallResponseChunk[ModelResponse]):
    '''A convenience wrapper around the LiteLLM `ChatCompletionChunk` streamed chunks.

    When calling the LiteLLM API using a function decorated with `openai_call` and
    `stream` set to `True`, the stream will contain `LiteLLMResponseChunk` instances
    with properties that allow for more convenient access to commonly used attributes.

    Example:

    ```python
    from mirascope.core.openai import openai_call

    @openai_call(model="gpt-4o", stream=True)
    def recommend_book(genre: str):
        """Recommend a {genre} book."""

    stream = recommend_book("fantasy")  # response is an `LiteLLMStream`
    for chunk in stream:
        print(chunk.content, end="", flush=True)
    #> Sure! I would recommend...
    ```
    '''

    @property
    def content(self) -> str:
        """Returns the content for the 0th choice delta."""
        delta = None
        if self.chunk.choices:
            delta = cast(list[Choice], self.chunk.choices)[0].delta
        return delta.content if delta is not None and delta.content else ""

    @property
    def finish_reasons(self) -> list[str]:
        """Returns the finish reasons of the response."""
        return [str(choice.finish_reason) for choice in self.chunk.choices]

    @property
    def model(self) -> str | None:
        """Returns the name of the response model."""
        return self.chunk.model

    @property
    def id(self) -> str:
        """Returns the id of the response."""
        return self.chunk.id

    @property
    def usage(self) -> CompletionUsage | None:
        """Returns the usage of the chat completion."""
        if hasattr(self.chunk, "usage") and (usage := getattr(self.chunk, "usage")):
            return usage  # type: ignore
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
