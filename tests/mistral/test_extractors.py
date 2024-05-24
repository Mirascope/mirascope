"""Tests for the `MistralExtractor` class."""

from typing import Type
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from mistralai.models.chat_completion import ChatCompletionResponse

from mirascope.mistral.extractors import MistralExtractor
from mirascope.mistral.tools import MistralTool


@patch("mistralai.client.MistralClient.chat", new_callable=MagicMock)
def test_mistral_extractor_extract_tool(
    mock_generate_content: MagicMock,
    fixture_book_tool: Type[MistralTool],
    fixture_chat_completion_response_with_tools: ChatCompletionResponse,
) -> None:
    """Tests that the `MistralExtractor` class returns the expected model."""
    mock_generate_content.return_value = fixture_chat_completion_response_with_tools

    class TempExtractor(MistralExtractor[Type[MistralTool]]):
        extract_schema: Type[MistralTool] = fixture_book_tool

    tool = TempExtractor().extract()

    assert isinstance(tool, fixture_book_tool)
    assert tool.title == "The Name of the Wind"
    assert tool.author == "Patrick Rothfuss"


@patch("mistralai.async_client.MistralAsyncClient.chat", new_callable=AsyncMock)
@pytest.mark.asyncio
async def test_mistral_extractor_extract_async_tool(
    mock_generate_content: AsyncMock,
    fixture_book_tool: Type[MistralTool],
    fixture_chat_completion_response_with_tools: ChatCompletionResponse,
) -> None:
    """Tests that the `MistralExtractor` class returns the expected model."""
    mock_generate_content.return_value = fixture_chat_completion_response_with_tools

    class TempExtractor(MistralExtractor[Type[MistralTool]]):
        extract_schema: Type[MistralTool] = fixture_book_tool

    tool = await TempExtractor().extract_async()

    assert isinstance(tool, fixture_book_tool)
    assert tool.title == "The Name of the Wind"
    assert tool.author == "Patrick Rothfuss"
