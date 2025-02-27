"""This module contains the `AzureCallResponseChunk` class.

usage docs: learn/streams.md#handling-streamed-responses
"""

from typing import cast

from azure.ai.inference.models import (
    CompletionsFinishReason,
    CompletionsUsage,
    StreamingChatCompletionsUpdate,
)
from pydantic import SkipValidation

from ..base import BaseCallResponseChunk
from ..base.types import CostMetadata, FinishReason


class AzureCallResponseChunk(
    BaseCallResponseChunk[StreamingChatCompletionsUpdate, CompletionsFinishReason]
):
    """A convenience wrapper around the Azure `ChatCompletionChunk` streamed chunks.

    When calling the Azure API using a function decorated with `azure_call` and
    `stream` set to `True`, the stream will contain `AzureResponseChunk` instances with
    properties that allow for more convenient access to commonly used attributes.

    Example:

    ```python
    from mirascope.core import prompt_template
    from mirascope.core.azure import azure_call


    @azure_call("gpt-4o-mini", stream=True)
    def recommend_book(genre: str) -> str:
        return f"Recommend a {genre} book"


    stream = recommend_book("fantasy")  # response is an `AzureStream`
    for chunk, _ in stream:
        print(chunk.content, end="", flush=True)
    ```
    """

    chunk: SkipValidation[StreamingChatCompletionsUpdate]

    @property
    def content(self) -> str:
        """Returns the content for the 0th choice delta."""
        delta = None
        if self.chunk.choices:
            delta = self.chunk.choices[0].delta
        return delta.content if delta is not None and delta.content else ""

    @property
    def finish_reasons(self) -> list[CompletionsFinishReason]:
        """Returns the finish reasons of the response."""
        return [
            finish_reason
            if isinstance(finish_reason, CompletionsFinishReason)
            else CompletionsFinishReason(finish_reason)
            for choice in self.chunk.choices
            if (finish_reason := choice.finish_reason)
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
    def usage(self) -> CompletionsUsage:
        """Returns the usage of the chat completion."""
        return self.chunk.usage

    @property
    def input_tokens(self) -> int:
        """Returns the number of input tokens."""
        return self.usage.prompt_tokens

    @property
    def cached_tokens(self) -> int:
        """Returns the number of cached tokens."""
        return 0

    @property
    def output_tokens(self) -> int:
        """Returns the number of output tokens."""
        return self.usage.completion_tokens

    @property
    def cost_metadata(self) -> CostMetadata:
        """Returns the cost metadata."""
        return super().cost_metadata

    @property
    def common_finish_reasons(self) -> list[FinishReason] | None:
        """Provider-agnostic finish reasons."""
        return cast(list[FinishReason], self.finish_reasons)
