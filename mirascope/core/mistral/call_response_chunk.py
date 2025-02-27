"""This module contains the `MistralCallResponseChunk` class.

usage docs: learn/streams.md#handling-streamed-responses
"""

from typing import cast

from mistralai.models import CompletionChunk, FinishReason, UsageInfo

from ..base import BaseCallResponseChunk, types
from ..base.types import CostMetadata
from ._utils._convert_finish_reason_to_common_finish_reasons import (
    _convert_finish_reasons_to_common_finish_reasons,
)


class MistralCallResponseChunk(BaseCallResponseChunk[CompletionChunk, FinishReason]):
    """A convenience wrapper around the Mistral `ChatCompletionChunk` streamed chunks.

    When calling the Mistral API using a function decorated with `mistral_call` and
    `stream` set to `True`, the stream will contain `MistralResponseChunk` instances with
    properties that allow for more convenient access to commonly used attributes.

    Example:

    ```python
    from mirascope.core import prompt_template
    from mirascope.core.mistral import mistral_call


    @mistral_call("mistral-large-latest", stream=True)
    def recommend_book(genre: str) -> str:
        return f"Recommend a {genre} book"


    stream = recommend_book("fantasy")  # response is an `MistralStream`
    for chunk, _ in stream:
        print(chunk.content, end="", flush=True)
    ```
    """

    @property
    def content(self) -> str:
        """Returns the content of the delta."""
        delta = None
        if self.chunk.choices:
            delta = self.chunk.choices[0].delta

        if delta is not None and isinstance(delta.content, str):
            return delta.content
        return ""

    @property
    def finish_reasons(self) -> list[FinishReason]:
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
    def usage(self) -> UsageInfo | None:
        """Returns the usage of the chat completion."""
        return self.chunk.usage

    @property
    def input_tokens(self) -> int | None:
        """Returns the number of input tokens."""
        if self.usage:
            return self.usage.prompt_tokens
        return None

    @property
    def cached_tokens(self) -> int:
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
    def common_finish_reasons(self) -> list[types.FinishReason] | None:
        return _convert_finish_reasons_to_common_finish_reasons(
            cast(list[str], self.finish_reasons)
        )
