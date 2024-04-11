"""Tests for the `mirascope.cohere.calls` module"""
from typing import Type
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from cohere import AsyncClient, Client
from cohere.types import (
    ChatDocument,
    NonStreamedChatResponse,
    StreamedChatResponse,
    StreamedChatResponse_TextGeneration,
)

from mirascope.base import Message
from mirascope.cohere import (
    CohereCall,
    CohereCallParams,
    CohereCallResponse,
    CohereCallResponseChunk,
    CohereTool,
)


@patch("cohere.Client.chat", new_callable=MagicMock)
def test_cohere_call_call(
    mock_chat: MagicMock,
    fixture_non_streamed_response: NonStreamedChatResponse,
    fixture_chat_document: ChatDocument,
) -> None:
    """Tests that `CohereCall.call` returns the expected response."""
    mock_chat.return_value = fixture_non_streamed_response
    wrapper = MagicMock()
    wrapper.return_value = Client()

    class TempCall(CohereCall):
        prompt_template = """
        SYSTEM:
        System message
        MESSAGES:
        {history}

        USER:
        User message
        """
        api_key = "test"
        history: list[Message] = [{"role": "user", "content": "text"}]
        documents: list[ChatDocument] = [fixture_chat_document]
        call_params = CohereCallParams(preamble="test", wrapper=wrapper)

    response = TempCall().call()
    assert isinstance(response, CohereCallResponse)
    assert response.content == "Test response"
    wrapper.assert_called_once()


@patch("cohere.Client.chat", new_callable=MagicMock)
def test_cohere_call_call_with_tools(
    mock_chat: MagicMock,
    fixture_cohere_book_tool: Type[CohereTool],
    fixture_cohere_response_with_tools: NonStreamedChatResponse,
) -> None:
    """Tests that `CohereCall.call` works with tools."""
    mock_chat.return_value = fixture_cohere_response_with_tools

    class TempCall(CohereCall):
        prompt_template = ""
        api_key = "test"

        call_params = CohereCallParams(tools=[fixture_cohere_book_tool])

    response = TempCall().call()
    assert response.tool is not None
    assert response.tool.args == {
        "title": "The Name of the Wind",
        "author": "Patrick Rothfuss",
    }


@patch("cohere.AsyncClient.chat", new_callable=AsyncMock)
@pytest.mark.asyncio
async def test_cohere_call_call_async(
    mock_chat: AsyncMock,
    fixture_non_streamed_response: NonStreamedChatResponse,
) -> None:
    """Tests that `CohereCall.call_async` returns the expected response."""
    mock_chat.return_value = fixture_non_streamed_response
    wrapper_async = MagicMock()
    wrapper_async.return_value = AsyncClient()

    class TempCall(CohereCall):
        prompt_template = ""
        api_key = "test"

        call_params = CohereCallParams(wrapper_async=wrapper_async)

    response = await TempCall().call_async()
    assert isinstance(response, CohereCallResponse)
    assert response.content == "Test response"
    wrapper_async.assert_called_once()


@patch("cohere.Client.chat_stream", new_callable=MagicMock)
def test_cohere_call_stream(
    mock_chat_stream: MagicMock,
    fixture_cohere_response_chunks: list[StreamedChatResponse],
) -> None:
    """Tests that `CohereCall.stream` returns the expected response."""
    mock_chat_stream.return_value = fixture_cohere_response_chunks
    wrapper = MagicMock()
    wrapper.return_value = Client()

    class TempCall(CohereCall):
        prompt_template = ""
        api_key = "test"

        call_params = CohereCallParams(wrapper=wrapper)

    chunks = [chunk for chunk in TempCall().stream()]
    assert len(chunks) == 3
    assert all(chunk.content == "test" for chunk in chunks)
    wrapper.assert_called_once()


@patch("cohere.AsyncClient.chat_stream", new_callable=MagicMock)
@pytest.mark.asyncio
async def test_cohere_call_stream_async(
    mock_chat_stream: MagicMock,
    fixture_cohere_async_response_chunks,
):
    """Tests `CohereCall.stream_async` returns expected response."""
    wrapper_async = MagicMock()
    wrapper_async.return_value = AsyncClient()

    class TempCall(CohereCall):
        prompt_template = ""
        api_key = "test"

        call_params = CohereCallParams(wrapper_async=wrapper_async)

    mock_chat_stream.return_value = fixture_cohere_async_response_chunks
    temp_call = TempCall()
    stream = temp_call.stream_async()

    async for chunk in stream:
        assert isinstance(chunk, CohereCallResponseChunk)
        assert isinstance(chunk.chunk, StreamedChatResponse_TextGeneration)
        assert chunk.chunk.text == "test"

    mock_chat_stream.assert_called_once_with(
        message="", model=temp_call.call_params.model
    )
    wrapper_async.assert_called_once()
