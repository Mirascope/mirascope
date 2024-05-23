"""Tests for the `GroqExtractor` class."""

from typing import Type
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from groq.types.chat.chat_completion import ChatCompletion
from pydantic import BaseModel

from mirascope.groq.extractors import GroqExtractor
from mirascope.groq.tools import GroqTool
from mirascope.groq.types import GroqCallParams, GroqCallResponse


@patch("groq.resources.chat.completions.Completions.create", new_callable=MagicMock)
def test_groq_extractor_extract_tool(
    mock_create: MagicMock,
    fixture_book_tool: Type[GroqTool],
    fixture_chat_completion_response_with_tools: ChatCompletion,
) -> None:
    """Tests that the `GroqExtractor` class returns the expected model."""
    mock_create.return_value = fixture_chat_completion_response_with_tools

    class TempExtractor(GroqExtractor[Type[GroqTool]]):
        extract_schema: Type[GroqTool] = fixture_book_tool
        api_key = "test"

    tool = TempExtractor().extract()

    assert isinstance(tool, fixture_book_tool)
    assert tool.title == "The Name of the Wind"
    assert tool.author == "Patrick Rothfuss"


@patch(
    "groq.resources.chat.completions.AsyncCompletions.create", new_callable=AsyncMock
)
@pytest.mark.asyncio
async def test_groq_extractor_extract_async_tool(
    mock_create: AsyncMock,
    fixture_book_tool: Type[GroqTool],
    fixture_chat_completion_response_with_tools: ChatCompletion,
) -> None:
    """Tests that the `GroqExtractor` class returns the expected model."""
    mock_create.return_value = fixture_chat_completion_response_with_tools

    class TempExtractor(GroqExtractor[Type[GroqTool]]):
        extract_schema: Type[GroqTool] = fixture_book_tool
        api_key = "test"

    tool = await TempExtractor().extract_async()

    assert isinstance(tool, fixture_book_tool)
    assert tool.title == "The Name of the Wind"
    assert tool.author == "Patrick Rothfuss"


@patch("mirascope.groq.calls.GroqCall.call", new_callable=MagicMock)
def test_groq_extractor_extract_with_no_tools(
    mock_call: MagicMock,
    fixture_chat_completion_response: ChatCompletion,
    fixture_book_tool: Type[GroqTool],
):
    """Tests that `GroqCall` raises a `ValueError` when no tools are provided."""
    mock_call.return_value = GroqCallResponse(
        response=fixture_chat_completion_response,
        tool_types=[fixture_book_tool],
        start_time=0,
        end_time=0,
    )

    class TempExtractor(GroqExtractor[BaseModel]):
        prompt_template = "test"
        api_key = "test"

        extract_schema: Type[BaseModel] = fixture_book_tool

        call_params = GroqCallParams(model="llama2-70b-4096")

    with pytest.raises(AttributeError):
        TempExtractor().extract()
