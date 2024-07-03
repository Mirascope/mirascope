"""This module contains the `CohereCallResponseChunk` class."""

from typing import Literal

from cohere import (
    StreamedChatResponse_CitationGeneration,
    StreamedChatResponse_SearchQueriesGeneration,
    StreamedChatResponse_SearchResults,
    StreamedChatResponse_StreamEnd,
    StreamedChatResponse_StreamStart,
    StreamedChatResponse_ToolCallsGeneration,
)
from cohere.types import (
    ApiMetaBilledUnits,
    ChatCitation,
    ChatDocument,
    ChatSearchQuery,
    ChatSearchResult,
    NonStreamedChatResponse,
    StreamedChatResponse,
    StreamedChatResponse_TextGeneration,
    ToolCall,
)
from pydantic import SkipValidation

from ..base import BaseCallResponseChunk


class CohereCallResponseChunk(
    BaseCallResponseChunk[SkipValidation[StreamedChatResponse]]
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
    def event_type(
        self,
    ) -> Literal[
        "stream-start",
        "search-queries-generation",
        "search-results",
        "text-generation",
        "citation-generation",
        "tool-calls-generation",
        "stream-end",
        "tool-calls-chunk",
    ]:
        """Returns the type of the chunk."""
        return self.chunk.event_type

    @property
    def content(self) -> str:
        """Returns the content for the 0th choice delta."""
        if isinstance(self.chunk, StreamedChatResponse_TextGeneration):
            return self.chunk.text
        return ""

    @property
    def search_queries(self) -> list[ChatSearchQuery] | None:
        """Returns the search queries for search-query event type else None."""
        if isinstance(self.chunk, StreamedChatResponse_SearchQueriesGeneration):
            return self.chunk.search_queries  # type: ignore
        return None

    @property
    def search_results(self) -> list[ChatSearchResult] | None:
        """Returns the search results for search-results event type else None."""
        if isinstance(self.chunk, StreamedChatResponse_SearchResults):
            return self.chunk.search_results
        return None

    @property
    def documents(self) -> list[ChatDocument] | None:
        """Returns the documents for search-results event type else None."""
        if isinstance(self.chunk, StreamedChatResponse_SearchResults):
            return self.chunk.documents
        return None

    @property
    def citations(self) -> list[ChatCitation] | None:
        """Returns the citations for citation-generation event type else None."""
        if isinstance(self.chunk, StreamedChatResponse_CitationGeneration):
            return self.chunk.citations
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
        return None

    @property
    def finish_reasons(self) -> list[str] | None:
        """Returns the finish reasons of the response."""
        if isinstance(self.chunk, StreamedChatResponse_StreamEnd):
            return [str(self.chunk.finish_reason)]
        return None

    @property
    def response(self) -> NonStreamedChatResponse | None:
        """Returns the full response for the stream-end event type else None."""
        if isinstance(self.chunk, StreamedChatResponse_StreamEnd):
            return self.chunk.response
        return None

    @property
    def tool_calls(self) -> list[ToolCall] | None:
        """Returns the partial tool calls for the 0th choice message."""
        if isinstance(self.chunk, StreamedChatResponse_ToolCallsGeneration):
            return self.chunk.tool_calls
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
