"""This module contains the `GroqCallResponseChunk` class.

usage docs: learn/streams.md#handling-streamed-responses
"""

from typing import cast

from groq.types.chat import ChatCompletionChunk
from groq.types.chat.chat_completion import Choice
from groq.types.completion_usage import CompletionUsage

from ..base import BaseCallResponseChunk
from ..base.types import CostMetadata

FinishReason = Choice.__annotations__["finish_reason"]


class GroqCallResponseChunk(BaseCallResponseChunk[ChatCompletionChunk, FinishReason]):
    """A convenience wrapper around the Groq `ChatCompletionChunk` streamed chunks.

    When calling the Groq API using a function decorated with `groq_call` and
    `stream` set to `True`, the stream will contain `GroqResponseChunk` instances with
    properties that allow for more convenient access to commonly used attributes.

    Example:

    ```python
    from mirascope.core import prompt_template
    from mirascope.core.groq import groq_call


    @groq_call("llama-3.1-8b-instant", stream=True)
    def recommend_book(genre: str) -> str:
        return f"Recommend a {genre} book"

    stream = recommend_book("fantasy")  # response is an `GroqStream`
    for chunk, _ in stream:
        print(chunk.content, end="", flush=True)
    ```
    """

    @property
    def content(self) -> str:
        """Returns the content for the 0th choice delta."""
        delta = None
        if self.chunk.choices:
            delta = self.chunk.choices[0].delta
        return delta.content if delta is not None and delta.content else ""

    @property
    def finish_reasons(
        self,
    ) -> list[FinishReason]:
        """Returns the finish reasons of the response."""
        return [
            choice.finish_reason
            for choice in self.chunk.choices
            if choice.finish_reason
        ]

    @property
    def model(self) -> str:
        """Returns the name of the response model."""
        return self.chunk.model

    @property
    def id(self) -> str:
        """Returns the id of the response."""
        return self.chunk.id

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
    def cached_tokens(self) -> int | None:
        """Returns the number of cached tokens."""
        return 0

    @property
    def output_tokens(self) -> int | None:
        """Returns the number of output tokens."""
        if self.usage:
            return self.usage.completion_tokens
        return None

    @property
    def cost_metadata(self) -> CostMetadata:
        """Returns the cost metadata."""
        return super().cost_metadata

    @property
    def common_finish_reasons(self) -> list[FinishReason] | None:
        return cast(list[FinishReason], self.finish_reasons)
