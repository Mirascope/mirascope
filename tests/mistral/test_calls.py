"""Tests for the `mirascope.mistral.calls` module"""
from typing import Type
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from mistralai.models.chat_completion import (
    ChatCompletionResponse,
    ChatCompletionStreamResponse,
)

from mirascope.mistral import (
    MistralCall,
    MistralCallParams,
    MistralCallResponse,
    MistralTool,
)


@patch("mistralai.client.MistralClient.chat", new_callable=MagicMock)
def test_mistral_call_call(
    mock_chat_completion: MagicMock,
    fixture_chat_completion_response: ChatCompletionResponse,
) -> None:
    """Tests that `MistralCall.call` returns the expected response."""
    mock_chat_completion.return_value = fixture_chat_completion_response

    class TempCall(MistralCall):
        prompt_template = ""

    response = TempCall().call()
    assert isinstance(response, MistralCallResponse)
    assert response.content == "test content"


@patch("mistralai.client.MistralClient.chat", new_callable=MagicMock)
def test_mistral_call_call_with_tools(
    mock_chat_completion: MagicMock,
    fixture_book_tool: Type[MistralTool],
    fixture_expected_book_tool_instance: MistralTool,
    fixture_generate_content_response_with_tools: ChatCompletionResponse,
) -> None:
    """Tests that `MistralCall.call` works with tools."""
    mock_chat_completion.return_value = fixture_generate_content_response_with_tools

    class TempCall(MistralCall):
        prompt_template = ""

        call_params = MistralCallParams(tools=[fixture_book_tool])

    response = TempCall().call()
    assert response.tool == fixture_expected_book_tool_instance


@patch("mistralai.async_client.MistralAsyncClient.chat", new_callable=AsyncMock)
@pytest.mark.asyncio
async def test_mistral_call_call_async(
    mock_chat_completion: AsyncMock,
    fixture_chat_completion_response: ChatCompletionResponse,
) -> None:
    """Tests that `MistralCall.call_async` returns the expected response."""
    mock_chat_completion.return_value = fixture_chat_completion_response

    class TempCall(MistralCall):
        prompt_template = ""

    response = await TempCall().call_async()
    assert isinstance(response, MistralCallResponse)
    assert response.content == "test content"


@patch("mistralai.client.MistralClient.chat_stream", new_callable=MagicMock)
def test_mistral_call_stream(
    mock_chat_completion: MagicMock,
    fixture_generate_content_chunks: list[ChatCompletionStreamResponse],
) -> None:
    """Tests that `MistralCall.stream` returns the expected response."""
    mock_chat_completion.return_value = fixture_generate_content_chunks

    class TempCall(MistralCall):
        prompt_template = ""

    chunks = [chunk for chunk in TempCall().stream()]
    assert len(chunks) == 2
    assert chunks[0].content == "A"
    assert chunks[1].content == "B"
