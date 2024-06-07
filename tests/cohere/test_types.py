from typing import Type

import pytest
from cohere.types import (
    ChatCitation,
    ChatDocument,
    ChatMessage,
    ChatSearchQuery,
    ChatSearchResult,
    NonStreamedChatResponse,
    StreamedChatResponse_CitationGeneration,
    StreamedChatResponse_SearchQueriesGeneration,
    StreamedChatResponse_SearchResults,
    StreamedChatResponse_StreamEnd,
    StreamedChatResponse_TextGeneration,
    StreamedChatResponse_ToolCallsGeneration,
    ToolCall,
)

from mirascope.cohere.tools import CohereTool
from mirascope.cohere.types import (
    CohereCallParams,
    CohereCallResponse,
    CohereCallResponseChunk,
)


def test_cohere_call_params_kwargs():
    params = CohereCallParams(temperature=0.5)
    kwargs = params.kwargs()
    assert kwargs["temperature"] == 0.5


def test_cohere_call_response_properties(
    fixture_non_streamed_response: NonStreamedChatResponse,
    fixture_chat_search_query: ChatSearchQuery,
    fixture_chat_search_result: ChatSearchResult,
    fixture_chat_document: ChatDocument,
    fixture_chat_citation: ChatCitation,
    fixture_tool_call: ToolCall,
):
    call_response = CohereCallResponse(
        response=fixture_non_streamed_response, start_time=0, end_time=0, cost=1
    )

    assert isinstance(call_response.message_param, ChatMessage)
    assert call_response.message_param == ChatMessage(
        message="Test response", tool_calls=[fixture_tool_call], role="assistant"
    )  # type: ignore

    assert call_response.content == "Test response"
    assert call_response.search_queries == [fixture_chat_search_query]
    assert call_response.search_results == [fixture_chat_search_result]
    assert call_response.documents == [fixture_chat_document]
    assert call_response.citations == [fixture_chat_citation]
    assert call_response.tool_calls == [fixture_tool_call]
    assert call_response.dump() == {
        "start_time": 0,
        "end_time": 0,
        "output": fixture_non_streamed_response.dict(),
        "cost": 1,
    }


def test_cohere_call_response_properties_no_usage(
    fixture_non_streamed_response_no_usage: NonStreamedChatResponse,
):
    """Test that when meta is None, usage is None."""
    call_response = CohereCallResponse(
        response=fixture_non_streamed_response_no_usage,
        start_time=0,
        end_time=0,
        cost=1,
    )

    assert call_response.usage is None
    assert call_response.input_tokens is None
    assert call_response.output_tokens is None


def test_cohere_call_response_tools(
    fixture_non_streamed_response: NonStreamedChatResponse,
    fixture_book_tool: Type[CohereTool],
):
    call_response = CohereCallResponse(
        response=fixture_non_streamed_response,
        tool_types=[fixture_book_tool],
        start_time=0,
        end_time=0,
        cost=None,
    )

    assert call_response.tools is not None
    assert isinstance(call_response.tools[0], fixture_book_tool)
    expected_tool_args = {
        "title": "The Name of the Wind",
        "author": "Patrick Rothfuss",
    }
    assert call_response.tools[0].args == expected_tool_args
    assert call_response.tool is not None
    assert call_response.tool.args == expected_tool_args

    call_response.response = fixture_non_streamed_response.copy(
        update={"tool_calls": None}
    )
    assert call_response.tool is None

    with pytest.raises(RuntimeError):
        call_response.response = fixture_non_streamed_response.copy(
            update={"finish_reason": "MAX_TOKENS"}
        )
        _ = call_response.tools


def test_cohere_call_response_chunk_properties(
    fixture_non_streamed_response: NonStreamedChatResponse,
    fixture_chat_search_query: ChatSearchQuery,
    fixture_chat_search_result: ChatSearchResult,
    fixture_chat_document: ChatDocument,
    fixture_chat_citation: ChatCitation,
    fixture_tool_call: ToolCall,
    fixture_book_tool: Type[CohereTool],
):
    chunk = StreamedChatResponse_TextGeneration(
        event_type="text-generation",
        **fixture_non_streamed_response.dict(exclude={"event_type"}),
    )
    call_chunk = CohereCallResponseChunk(chunk=chunk, tool_types=[fixture_book_tool])

    assert call_chunk.event_type == "text-generation"
    assert call_chunk.content == "Test response"
    assert call_chunk.response is None

    call_chunk.chunk = StreamedChatResponse_SearchQueriesGeneration(
        event_type="search-queries-generation",
        **chunk.dict(exclude={"event_type"}),
    )
    assert call_chunk.search_queries == [fixture_chat_search_query]
    assert call_chunk.search_results is None
    assert call_chunk.documents is None
    assert call_chunk.citations is None
    assert call_chunk.tool_calls is None
    assert call_chunk.content == ""

    call_chunk.chunk = StreamedChatResponse_SearchResults(
        event_type="search-results",
        **fixture_non_streamed_response.dict(exclude={"event_type"}),
    )
    assert call_chunk.search_results == [fixture_chat_search_result]
    assert call_chunk.documents == [fixture_chat_document]
    assert call_chunk.search_queries is None
    assert call_chunk.citations is None
    assert call_chunk.content == ""

    call_chunk.chunk = StreamedChatResponse_CitationGeneration(
        event_type="citation-generation",
        **fixture_non_streamed_response.dict(exclude={"event_type"}),
    )
    assert call_chunk.citations == [fixture_chat_citation]
    assert call_chunk.search_queries is None
    assert call_chunk.search_results is None
    assert call_chunk.documents is None
    assert call_chunk.content == ""

    call_chunk.chunk = StreamedChatResponse_ToolCallsGeneration(
        event_type="tool-calls-generation",
        **fixture_non_streamed_response.dict(exclude={"event_type"}),
    )
    assert call_chunk.tool_calls == [fixture_tool_call]
    assert call_chunk.search_queries is None
    assert call_chunk.search_results is None
    assert call_chunk.documents is None
    assert call_chunk.citations is None
    assert call_chunk.content == ""

    call_chunk.chunk = StreamedChatResponse_StreamEnd(
        event_type="stream-end",
        response=fixture_non_streamed_response,
        finish_reason="COMPLETE",
    )
    assert isinstance(call_chunk.response, NonStreamedChatResponse)
    assert call_chunk.search_queries is None
    assert call_chunk.search_results is None
    assert call_chunk.documents is None
    assert call_chunk.citations is None
    assert call_chunk.content == ""
