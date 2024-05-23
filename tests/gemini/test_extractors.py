"""Tests for the `GeminiExtractor` class."""

from typing import Type
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from google.generativeai.types import GenerateContentResponse  # type: ignore

from mirascope.gemini.extractors import GeminiExtractor
from mirascope.gemini.tools import GeminiTool


@patch("google.generativeai.GenerativeModel.generate_content", new_callable=MagicMock)
def test_gemini_extractor_extract_tool(
    mock_generate_content: MagicMock,
    fixture_book_tool: Type[GeminiTool],
    fixture_generate_content_response_with_tools: GenerateContentResponse,
) -> None:
    """Tests that the `GeminiExtractor` class returns the expected model."""
    mock_generate_content.return_value = fixture_generate_content_response_with_tools

    class TempExtractor(GeminiExtractor[Type[GeminiTool]]):
        extract_schema: Type[GeminiTool] = fixture_book_tool

    tool = TempExtractor().extract()

    assert isinstance(tool, fixture_book_tool)
    assert tool.title == "The Name of the Wind"
    assert tool.author == "Patrick Rothfuss"


@patch(
    "google.generativeai.GenerativeModel.generate_content_async", new_callable=AsyncMock
)
@pytest.mark.asyncio
async def test_gemini_extractor_extract_async_tool(
    mock_generate_content: AsyncMock,
    fixture_book_tool: Type[GeminiTool],
    fixture_generate_content_response_with_tools: GenerateContentResponse,
) -> None:
    """Tests that the `GeminiExtractor` class returns the expected model."""
    mock_generate_content.return_value = fixture_generate_content_response_with_tools

    class TempExtractor(GeminiExtractor[Type[GeminiTool]]):
        extract_schema: Type[GeminiTool] = fixture_book_tool

    tool = await TempExtractor().extract_async()

    assert isinstance(tool, fixture_book_tool)
    assert tool.title == "The Name of the Wind"
    assert tool.author == "Patrick Rothfuss"
