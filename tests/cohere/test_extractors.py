"""Tests for the `CohereExtractor` class."""

from typing import Type
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from cohere.types import NonStreamedChatResponse
from pydantic import BaseModel

from mirascope.cohere.extractors import CohereExtractor
from mirascope.cohere.tools import CohereTool
from mirascope.cohere.types import CohereCallParams, CohereCallResponse


@patch("cohere.Client.chat", new_callable=MagicMock)
def test_cohere_extractor_extract_tool(
    mock_chat: MagicMock,
    fixture_book_tool: Type[CohereTool],
    fixture_non_streamed_response: NonStreamedChatResponse,
) -> None:
    """Tests that the `CohereExtractor` class returns the expected model."""
    mock_chat.return_value = fixture_non_streamed_response
    mock_chat.__name__ = "chat"

    class TempExtractor(CohereExtractor[Type[CohereTool]]):
        extract_schema: Type[CohereTool] = fixture_book_tool
        api_key = "test"

    tool = TempExtractor().extract()

    assert isinstance(tool, fixture_book_tool)
    assert tool.title == "The Name of the Wind"
    assert tool.author == "Patrick Rothfuss"


@patch("cohere.AsyncClient.chat", new_callable=AsyncMock)
@pytest.mark.asyncio
async def test_cohere_extractor_extract_async_tool(
    mock_chat: AsyncMock,
    fixture_book_tool: Type[CohereTool],
    fixture_non_streamed_response: NonStreamedChatResponse,
) -> None:
    """Tests that the `CohereExtractor` class returns the expected model."""
    mock_chat.return_value = fixture_non_streamed_response

    class TempExtractor(CohereExtractor[Type[CohereTool]]):
        extract_schema: Type[CohereTool] = fixture_book_tool
        api_key = "test"

    tool = await TempExtractor().extract_async()

    assert isinstance(tool, fixture_book_tool)
    assert tool.title == "The Name of the Wind"
    assert tool.author == "Patrick Rothfuss"


@patch("mirascope.cohere.calls.CohereCall.call", new_callable=MagicMock)
def test_cohere_extractor_extract_with_no_tools(
    mock_call: MagicMock,
    fixture_non_streamed_response: NonStreamedChatResponse,
    fixture_book_tool: Type[CohereTool],
):
    """Tests that `CohereCall` raises a `ValueError` when no tools are provided."""
    mock_call.return_value = CohereCallResponse(
        response=fixture_non_streamed_response.copy(update={"tool_calls": None}),
        tool_types=[fixture_book_tool],
        start_time=0,
        end_time=0,
    )

    class TempExtractor(CohereExtractor[BaseModel]):
        prompt_template = "test"
        api_key = "test"

        extract_schema: Type[BaseModel] = fixture_book_tool

        call_params = CohereCallParams(model="command-r")

    with pytest.raises(AttributeError):
        TempExtractor().extract()
