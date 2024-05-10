"""Types for interacting with Cohere chat models using Mirascope."""
from typing import Any, Callable, Literal, Optional, Sequence, Type, Union

from cohere import (
    AsyncClient,
    Client,
    StreamedChatResponse_CitationGeneration,
    StreamedChatResponse_SearchQueriesGeneration,
    StreamedChatResponse_SearchResults,
    StreamedChatResponse_StreamEnd,
    StreamedChatResponse_ToolCallsGeneration,
)
from cohere.types import (
    ApiMetaBilledUnits,
    ChatCitation,
    ChatConnector,
    ChatDocument,
    ChatMessage,
    ChatRequestPromptTruncation,
    ChatRequestToolResultsItem,
    ChatSearchQuery,
    ChatSearchResult,
    EmbedByTypeResponseEmbeddings,
    EmbedResponse,
    NonStreamedChatResponse,
    StreamedChatResponse,
    StreamedChatResponse_TextGeneration,
    ToolCall,
)
from pydantic import ConfigDict, SkipValidation
from typing_extensions import NotRequired, TypedDict

from ..base import BaseCallParams, BaseCallResponse, BaseCallResponseChunk
from ..rag.types import BaseEmbeddingParams, BaseEmbeddingResponse
from .tools import CohereTool


class RequestOptions(TypedDict):
    """Redefining their class to use `typing_extensions.TypedDict` for Pydantic."""

    timeout_in_seconds: NotRequired[int]
    max_retries: NotRequired[int]
    additional_headers: NotRequired[dict[str, Any]]
    additional_query_parameters: NotRequired[dict[str, Any]]
    additional_body_parameters: NotRequired[dict[str, Any]]


class CohereCallParams(BaseCallParams[CohereTool]):
    """The parameters to use when calling the Cohere chat API."""

    model: str = "command-r-plus"
    preamble: Optional[str] = None
    chat_history: Optional[Sequence[ChatMessage]] = None
    conversation_id: Optional[str] = None
    prompt_truncation: Optional[ChatRequestPromptTruncation] = None
    connectors: Optional[Sequence[ChatConnector]] = None
    search_queries_only: Optional[bool] = None
    documents: Optional[Sequence[ChatDocument]] = None
    temperature: Optional[float] = None
    max_tokens: Optional[int] = None
    max_input_tokens: Optional[int] = None
    k: Optional[int] = None
    p: Optional[float] = None
    seed: Optional[float] = None
    stop_sequences: Optional[Sequence[str]] = None
    frequency_penalty: Optional[float] = None
    presence_penalty: Optional[float] = None
    raw_prompting: Optional[bool] = None
    tool_results: Optional[Sequence[ChatRequestToolResultsItem]] = None
    request_options: Optional[RequestOptions] = None

    wrapper: Optional[Callable[[Client], Client]] = None
    wrapper_async: Optional[Callable[[AsyncClient], AsyncClient]] = None

    model_config = ConfigDict(arbitrary_types_allowed=True)

    def kwargs(
        self,
        tool_type: Optional[Type[CohereTool]] = CohereTool,
        exclude: Optional[set[str]] = None,
    ) -> dict[str, Any]:
        """Returns the keyword argument call parameters."""
        extra_exclude = {"wrapper", "wrapper_async"}
        exclude = extra_exclude if exclude is None else exclude.union(extra_exclude)
        return super().kwargs(tool_type, exclude)


class CohereCallResponse(BaseCallResponse[NonStreamedChatResponse, CohereTool]):
    """A convenience wrapper around the Cohere `NonStreamedChatResponse` response.

    When using Mirascope's convenience wrappers to interact with Cohere chat models via
    `CohereCall`, responses using `CohereCall.call()` will return a `CohereCallResponse`
    whereby the implemented properties allow for simpler syntax and a convenient
    developer experience.

    Example:

    ```python
    from mirascope.cohere import CohereCall


    class BookRecommender(CohereCall):
        prompt_template = "Please recommend a {genre} book"

        genre: str


    response = Bookrecommender(genre="fantasy").call()
    print(response.content)
    #> The Name of the Wind

    print(response.message)
    #> ...

    print(response.choices)
    #> ...
    ```
    """

    # We need to skip validation since it's a pydantic_v1 model and breaks validation.
    response: SkipValidation[NonStreamedChatResponse]

    @property
    def content(self) -> str:
        """Returns the content of the chat completion for the 0th choice."""
        return self.response.text

    @property
    def search_queries(self) -> Optional[list[ChatSearchQuery]]:
        """Returns the search queries for the 0th choice message."""
        return self.response.search_queries

    @property
    def search_results(self) -> Optional[list[ChatSearchResult]]:
        """Returns the search results for the 0th choice message."""
        return self.response.search_results

    @property
    def documents(self) -> Optional[list[ChatDocument]]:
        """Returns the documents for the 0th choice message."""
        return self.response.documents

    @property
    def citations(self) -> Optional[list[ChatCitation]]:
        """Returns the citations for the 0th choice message."""
        return self.response.citations

    @property
    def tool_calls(self) -> Optional[list[ToolCall]]:
        """Returns the tool calls for the 0th choice message."""
        return self.response.tool_calls

    @property
    def tools(self) -> Optional[list[CohereTool]]:
        """Returns the tools for the 0th choice message.

        Raises:
            ValidationError: if a tool call doesn't match the tool's schema.
        """
        if not self.tool_types or not self.tool_calls:
            return None

        if self.response.finish_reason == "MAX_TOKENS":
            raise RuntimeError(
                "Generation stopped with MAX_TOKENS finish reason. This means that the "
                "response hit the token limit before completion, "
            )

        extracted_tools = []
        for tool_call in self.tool_calls:
            for tool_type in self.tool_types:
                if tool_call.name == tool_type.__name__:
                    extracted_tools.append(tool_type.from_tool_call(tool_call))
                    break

        return extracted_tools

    @property
    def tool(self) -> Optional[CohereTool]:
        """Returns the 0th tool for the 0th choice message.

        Raises:
            ValidationError: if the tool call doesn't match the tool's schema.
        """
        tools = self.tools
        if tools:
            return tools[0]
        return None

    @property
    def usage(self) -> Optional[ApiMetaBilledUnits]:
        """Returns the usage of the response."""
        if self.response.meta:
            return self.response.meta.billed_units
        return None

    @property
    def input_tokens(self) -> Optional[float]:
        """Returns the number of input tokens."""
        if self.usage:
            return self.usage.input_tokens
        return None

    @property
    def output_tokens(self) -> Optional[float]:
        """Returns the number of output tokens."""
        if self.usage:
            return self.usage.output_tokens
        return None

    def dump(self) -> dict[str, Any]:
        """Dumps the response to a dictionary."""
        return {
            "start_time": self.start_time,
            "end_time": self.end_time,
            "output": self.response.dict(),
            "cost": self.cost,
        }


class CohereCallResponseChunk(BaseCallResponseChunk[StreamedChatResponse, CohereTool]):
    """Convenience wrapper around chat completion streaming chunks.

    When using Mirascope's convenience wrappers to interact with Cohere models via
    `CohereCall.stream`, responses will return an `CohereCallResponseChunk`, whereby
    the implemented properties allow for simpler syntax and a convenient developer
    experience.

    Example:

    ```python
    from mirascope.cohere import CohereCall


    class Math(CohereCall):
        prompt_template = "What is 1 + 2?"


    for chunk in CohereCall().stream():
        print(chunk.content)

    #> 1
    #  +
    #  2
    #   equals
    #
    #  3
    #  .
    """

    chunk: SkipValidation[StreamedChatResponse]

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
    def search_queries(self) -> Optional[list[ChatSearchQuery]]:
        """Returns the search queries for search-query event type else None."""
        if isinstance(self.chunk, StreamedChatResponse_SearchQueriesGeneration):
            return self.chunk.search_queries  # type: ignore
        return None

    @property
    def search_results(self) -> Optional[list[ChatSearchResult]]:
        """Returns the search results for search-results event type else None."""
        if isinstance(self.chunk, StreamedChatResponse_SearchResults):
            return self.chunk.search_results
        return None

    @property
    def documents(self) -> Optional[list[ChatDocument]]:
        """Returns the documents for citation-generation event type else None."""
        if isinstance(self.chunk, StreamedChatResponse_SearchResults):
            return self.chunk.documents
        return None

    @property
    def citations(self) -> Optional[list[ChatCitation]]:
        """Returns the citations for citation-generation event type else None."""
        if isinstance(self.chunk, StreamedChatResponse_CitationGeneration):
            return self.chunk.citations
        return None

    @property
    def response(self) -> Optional[NonStreamedChatResponse]:
        """Returns the response for text-generation event type else None."""
        if isinstance(self.chunk, StreamedChatResponse_StreamEnd):
            return self.chunk.response
        return None

    @property
    def tool_calls(self) -> Optional[list[ToolCall]]:
        """Returns the partial tool calls for the 0th choice message."""
        if isinstance(self.chunk, StreamedChatResponse_ToolCallsGeneration):
            return self.chunk.tool_calls
        return None


class CohereEmbeddingResponse(BaseEmbeddingResponse[SkipValidation[EmbedResponse]]):
    """A convenience wrapper around the Cohere `EmbedResponse` response."""

    embedding_type: Optional[
        Literal["float", "int8", "uint8", "binary", "ubinary"]
    ] = None

    @property
    def embeddings(
        self,
    ) -> Optional[Union[list[list[float]], list[list[int]]]]:
        """Returns the embeddings"""
        if self.response.response_type == "embeddings_floats":
            return self.response.embeddings
        else:
            embedding_type = self.embedding_type
            if embedding_type == "float":
                embedding_type == "float_"

            # TODO: Update to model_dump when Cohere updates to Pydantic v2
            embeddings_by_type: EmbedByTypeResponseEmbeddings = self.response.embeddings
            embedding_dict = embeddings_by_type.dict()
            return embedding_dict.get(str(embedding_type), None)


class CohereEmbeddingParams(BaseEmbeddingParams):
    model: str = "embed-english-v3.0"
    input_type: Literal[
        "search_document", "search_query", "classification", "clustering"
    ] = "search_query"
    embedding_types: Optional[
        Sequence[Literal["float", "int8", "uint8", "binary", "ubinary"]]
    ] = None
    truncate: Optional[Literal["none", "end", "start"]] = "end"
    request_options: Optional[RequestOptions] = None
    batching: Optional[bool] = True
