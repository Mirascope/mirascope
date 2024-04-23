"""Fixtures for Mirascope's Cohere module tests."""
from typing import Type

import pytest
from cohere import ApiMetaBilledUnits
from cohere.types import (
    ApiMeta,
    ChatCitation,
    ChatSearchQuery,
    ChatSearchResult,
    ChatSearchResultConnector,
    EmbedByTypeResponseEmbeddings,
    EmbedResponse_EmbeddingsByType,
    EmbedResponse_EmbeddingsFloats,
    NonStreamedChatResponse,
    StreamedChatResponse_TextGeneration,
    ToolCall,
)

from mirascope.cohere.embedders import CohereEmbedder
from mirascope.cohere.tools import CohereTool
from mirascope.cohere.types import CohereEmbeddingParams


@pytest.fixture()
def fixture_chat_search_query() -> ChatSearchQuery:
    """Returns a Cohere chat search query."""
    return ChatSearchQuery(text="test query", generation_id="id")


@pytest.fixture()
def fixture_chat_search_result(
    fixture_chat_search_query: ChatSearchQuery,
) -> ChatSearchResult:
    """Returns a Cohere chat search result."""
    return ChatSearchResult(
        search_query=fixture_chat_search_query,
        connector=ChatSearchResultConnector(id="id"),
        document_ids=["test_id"],
    )


@pytest.fixture()
def fixture_chat_document() -> dict[str, str]:
    """Returns a Cohere chat document."""
    return {"id": "test_doc_id", "text": "test doc"}


@pytest.fixture()
def fixture_chat_citation() -> ChatCitation:
    """Returns a Cohere chat citation."""
    return ChatCitation(start=0, end=0, text="", document_ids=["test_cite_id"])


class BookTool(CohereTool):
    title: str
    author: str


@pytest.fixture()
def fixture_book_tool() -> Type[BookTool]:
    """Returns the `BookTool` type definition."""
    return BookTool


@pytest.fixture()
def fixture_tool_call() -> ToolCall:
    """Returns a Cohere tool call."""
    return ToolCall(
        name="BookTool",
        parameters={"title": "The Name of the Wind", "author": "Patrick Rothfuss"},
    )


@pytest.fixture()
def fixture_non_streamed_response(
    fixture_chat_search_query: ChatSearchQuery,
    fixture_chat_search_result: ChatSearchResult,
    fixture_chat_document: dict[str, str],
    fixture_chat_citation: ChatCitation,
    fixture_tool_call: ToolCall,
) -> NonStreamedChatResponse:
    """Returns a Cohere chat response."""
    return NonStreamedChatResponse(
        text="Test response",
        search_queries=[fixture_chat_search_query],
        search_results=[fixture_chat_search_result],
        documents=[fixture_chat_document],
        citations=[fixture_chat_citation],
        tool_calls=[fixture_tool_call],
        meta=ApiMeta(billed_units=ApiMetaBilledUnits(input_tokens=1, output_tokens=1)),
    )


@pytest.fixture()
def fixture_cohere_response_with_tools() -> NonStreamedChatResponse:
    """Returns a Cohere chat response with tools in the response"""
    return NonStreamedChatResponse(
        text="test",
        search_queries=None,
        search_results=None,
        documents=None,
        citations=None,
        tool_calls=[
            ToolCall(
                name="BookTool",
                parameters={
                    "title": "The Name of the Wind",
                    "author": "Patrick Rothfuss",
                },
            )
        ],
        meta=ApiMeta(billed_units=ApiMetaBilledUnits(input_tokens=1, output_tokens=1)),
    )


@pytest.fixture()
def fixture_cohere_response_chunk():
    """Returns a Cohere chat response chunk."""
    return StreamedChatResponse_TextGeneration(
        event_type="text-generation",
        text="test",
        search_queries=None,
        search_results=None,
        documents=None,
        citations=None,
        tool_calls=None,
        response=None,
    )


@pytest.fixture()
def fixture_cohere_response_chunks(
    fixture_cohere_response_chunk: StreamedChatResponse_TextGeneration,
):
    """Returns a context managed stream."""
    return [fixture_cohere_response_chunk] * 3


@pytest.fixture()
def fixture_cohere_async_response_chunks(
    fixture_cohere_response_chunk: StreamedChatResponse_TextGeneration,
):
    """Returns a context managed async stream"""

    async def generator():
        yield fixture_cohere_response_chunk

    return generator()


@pytest.fixture()
def fixture_cohere_book_tool() -> Type[BookTool]:
    """Returns the `BookTool` type definition."""

    return BookTool


@pytest.fixture()
def fixture_cohere_embeddings() -> EmbedResponse_EmbeddingsFloats:
    """Returns a Cohere embeddings response with embedding_types None."""
    return EmbedResponse_EmbeddingsFloats(
        id="test",
        embeddings=[
            [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0],
        ],
        texts=["test"],
        meta=ApiMeta(billed_units=ApiMetaBilledUnits(input_tokens=1, output_tokens=1)),
    )


@pytest.fixture()
def fixture_cohere_embeddings_by_type_float() -> EmbedResponse_EmbeddingsByType:
    """Returns a Cohere embeddings response with embedding_types float."""
    return EmbedResponse_EmbeddingsByType(
        id="test",
        embeddings=EmbedByTypeResponseEmbeddings(
            float_=[  # type: ignore
                [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0],
            ]
        ),
        texts=["test"],
        meta=ApiMeta(billed_units=ApiMetaBilledUnits(input_tokens=1, output_tokens=1)),
    )


@pytest.fixture()
def fixture_cohere_embeddings_by_type_int8() -> EmbedResponse_EmbeddingsByType:
    """Returns a Cohere embeddings response with embedding_types int8."""
    return EmbedResponse_EmbeddingsByType(
        id="test",
        embeddings=EmbedByTypeResponseEmbeddings(
            int8=[
                [-127, -126, -125, -124, -123, -122, -121, -120, -119],
            ]
        ),
        texts=["test"],
        meta=ApiMeta(billed_units=ApiMetaBilledUnits(input_tokens=1, output_tokens=1)),
    )


@pytest.fixture()
def fixture_cohere_embeddings_by_type_uint8() -> EmbedResponse_EmbeddingsByType:
    """Returns a Cohere embeddings response with embedding_types uint8."""
    return EmbedResponse_EmbeddingsByType(
        id="test",
        embeddings=EmbedByTypeResponseEmbeddings(
            uint8=[
                [1, 2, 3, 4, 5, 6, 7, 8, 9],
            ]
        ),
        texts=["test"],
        meta=ApiMeta(billed_units=ApiMetaBilledUnits(input_tokens=1, output_tokens=1)),
    )


@pytest.fixture()
def fixture_cohere_embeddings_by_type_binary() -> EmbedResponse_EmbeddingsByType:
    """Returns a Cohere embeddings response with embedding_types binary."""
    return EmbedResponse_EmbeddingsByType(
        id="test",
        embeddings=EmbedByTypeResponseEmbeddings(
            binary=[
                [-127, -126, -125, -124, -123, -122, -121, -120, -119],
            ]
        ),
        texts=["test"],
        meta=ApiMeta(billed_units=ApiMetaBilledUnits(input_tokens=1, output_tokens=1)),
    )


@pytest.fixture()
def fixture_cohere_embeddings_by_type_ubinary() -> EmbedResponse_EmbeddingsByType:
    """Returns a Cohere embeddings response with embedding_types ubinary."""
    return EmbedResponse_EmbeddingsByType(
        id="test",
        embeddings=EmbedByTypeResponseEmbeddings(
            ubinary=[
                [1, 2, 3, 4, 5, 6, 7, 8, 9],
            ]
        ),
        texts=["test"],
        meta=ApiMeta(billed_units=ApiMetaBilledUnits(input_tokens=1, output_tokens=1)),
    )


@pytest.fixture()
def fixture_cohere_embeddings_by_type_no_data() -> EmbedResponse_EmbeddingsByType:
    """Returns a Cohere embeddings response with embedding_type float with no data."""
    return EmbedResponse_EmbeddingsByType(
        id="test",
        embeddings=EmbedByTypeResponseEmbeddings(
            float_=None  # type: ignore
        ),
        texts=["test"],
        meta=ApiMeta(billed_units=ApiMetaBilledUnits(input_tokens=1, output_tokens=1)),
    )


@pytest.fixture()
def fixture_cohere_test_embedder():
    """Returns an `CohereEmbedding` instance."""

    class TestEmbedder(CohereEmbedder):
        api_key = "test"
        embedding_params = CohereEmbeddingParams(model="test_model")

    return TestEmbedder()
