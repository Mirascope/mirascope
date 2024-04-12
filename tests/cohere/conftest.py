"""Fixtures for Mirascope's Cohere module tests."""
from typing import Type

import pytest
from cohere.types import (
    ChatCitation,
    ChatSearchQuery,
    ChatSearchResult,
    ChatSearchResultConnector,
    NonStreamedChatResponse,
    StreamedChatResponse_TextGeneration,
    ToolCall,
)

from mirascope.cohere.tools import CohereTool


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
