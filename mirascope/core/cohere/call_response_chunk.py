"""This module contains the `CohereCallResponseChunk` class.

usage docs: learn/streams.md#handling-streamed-responses
"""

from typing import cast

from cohere.types import (
    ApiMetaBilledUnits,
    ChatStreamEndEventFinishReason,
    StreamedChatResponse,
)
from pydantic import SkipValidation

from ..base import BaseCallResponseChunk, types
from ..base.types import CostMetadata
from ._types import (
    StreamEndStreamedChatResponse,
    StreamStartStreamedChatResponse,
    TextGenerationStreamedChatResponse,
)
from ._utils._convert_finish_reason_to_common_finish_reasons import (
    _convert_finish_reasons_to_common_finish_reasons,
)


class CohereCallResponseChunk(
    BaseCallResponseChunk[
        SkipValidation[StreamedChatResponse], ChatStreamEndEventFinishReason
    ]
):
    """A convenience wrapper around the Cohere `ChatCompletionChunk` streamed chunks.

    When calling the Cohere API using a function decorated with `cohere_call` and
    `stream` set to `True`, the stream will contain `CohereResponseChunk` instances with
    properties that allow for more convenient access to commonly used attributes.

    Example:

    ```python
    from mirascope.core import prompt_template
    from mirascope.core.cohere import cohere_call


    @cohere_call("command-r-plus", stream=True)
    def recommend_book(genre: str) -> str:
        return f"Recommend a {genre} book"


    stream = recommend_book("fantasy")  # response is an `CohereStream`
    for chunk, _ in stream:
        print(chunk.content, end="", flush=True)
    ```
    """

    @property
    def content(self) -> str:
        """Returns the content for the 0th choice delta."""
        if isinstance(self.chunk, TextGenerationStreamedChatResponse):
            return self.chunk.text
        return ""

    @property
    def finish_reasons(self) -> list[ChatStreamEndEventFinishReason] | None:
        """Returns the finish reasons of the response."""
        if isinstance(self.chunk, StreamEndStreamedChatResponse):
            return [self.chunk.finish_reason]
        return None

    @property
    def model(self) -> str | None:
        """Returns the name of the response model.

        Cohere does not return model, so we return None
        """
        return None

    @property
    def id(self) -> str | None:
        """Returns the id of the response."""
        if isinstance(self.chunk, StreamStartStreamedChatResponse):
            return self.chunk.generation_id
        elif isinstance(self.chunk, StreamEndStreamedChatResponse):
            return self.chunk.response.generation_id
        return None

    @property
    def usage(self) -> ApiMetaBilledUnits | None:
        """Returns the usage of the response."""
        if (
            isinstance(self.chunk, StreamEndStreamedChatResponse)
            and self.chunk.response.meta
        ):
            return self.chunk.response.meta.billed_units
        return None

    @property
    def input_tokens(self) -> float | None:
        """Returns the number of input tokens."""
        if self.usage:
            return self.usage.input_tokens
        return None

    @property
    def cached_tokens(self) -> float | None:
        """Returns the number of cached tokens."""
        return None

    @property
    def output_tokens(self) -> float | None:
        """Returns the number of output tokens."""
        if self.usage:
            return self.usage.output_tokens
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
