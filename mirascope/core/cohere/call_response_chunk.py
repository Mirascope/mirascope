"""This module contains the `CohereCallResponseChunk` class."""

from cohere import StreamedChatResponse_StreamEnd, StreamedChatResponse_StreamStart
from cohere.types import (
    ApiMetaBilledUnits,
    ChatStreamEndEventFinishReason,
    StreamedChatResponse,
    StreamedChatResponse_TextGeneration,
)
from pydantic import SkipValidation

from ..base import BaseCallResponseChunk


class CohereCallResponseChunk(
    BaseCallResponseChunk[
        SkipValidation[StreamedChatResponse], ChatStreamEndEventFinishReason
    ]
):
    '''A convenience wrapper around the Cohere `ChatCompletionChunk` streamed chunks.

    When calling the Cohere API using a function decorated with `cohere_call` and
    `stream` set to `True`, the stream will contain `CohereResponseChunk` instances with
    properties that allow for more convenient access to commonly used attributes.

    Example:

    ```python
    from mirascope.core.cohere import cohere_call

    @cohere_call(model="gpt-4o", stream=True)
    def recommend_book(genre: str):
        """Recommend a {genre} book."""

    stream = recommend_book("fantasy")  # response is an `CohereStream`
    for chunk in stream:
        print(chunk.content, end="", flush=True)
    #> Sure! I would recommend...
    ```
    '''

    @property
    def content(self) -> str:
        """Returns the content for the 0th choice delta."""
        if isinstance(self.chunk, StreamedChatResponse_TextGeneration):
            return self.chunk.text
        return ""

    @property
    def finish_reasons(self) -> list[ChatStreamEndEventFinishReason] | None:
        """Returns the finish reasons of the response."""
        if isinstance(self.chunk, StreamedChatResponse_StreamEnd):
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
        if isinstance(self.chunk, StreamedChatResponse_StreamStart):
            return self.chunk.generation_id
        elif isinstance(self.chunk, StreamedChatResponse_StreamEnd):
            return self.chunk.response.generation_id
        return None

    @property
    def usage(self) -> ApiMetaBilledUnits | None:
        """Returns the usage of the response."""
        if isinstance(self.chunk, StreamedChatResponse_StreamEnd):
            if self.chunk.response.meta:
                return self.chunk.response.meta.billed_units
        return None

    @property
    def input_tokens(self) -> float | None:
        """Returns the number of input tokens."""
        if self.usage:
            return self.usage.input_tokens
        return None

    @property
    def output_tokens(self) -> float | None:
        """Returns the number of output tokens."""
        if self.usage:
            return self.usage.output_tokens
        return None
