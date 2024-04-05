"""Tests for `AnthropicExtractor`."""
from typing import Type
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from anthropic.types import Message

from mirascope.anthropic.extractors import AnthropicExtractor
from mirascope.anthropic.tools import AnthropicTool


@patch(
    "anthropic.resources.beta.tools.messages.Messages.create",
    new_callable=MagicMock,
)
def test_anthropic_extractor_extract_tool(
    mock_create: MagicMock,
    fixture_anthropic_book_tool: Type[AnthropicTool],
    fixture_anthropic_message_with_tools: Message,
) -> None:
    """Tests that the `AnthropicExtractor` class returns the expected model."""
    mock_create.return_value = fixture_anthropic_message_with_tools

    class TempExtractor(AnthropicExtractor[Type[AnthropicTool]]):
        extract_schema: Type[AnthropicTool] = fixture_anthropic_book_tool
        prompt_template = "test"

    tool = TempExtractor().extract()

    assert isinstance(tool, fixture_anthropic_book_tool)
    assert tool.title == "The Name of the Wind"
    assert tool.author == "Patrick Rothfuss"


@patch(
    "anthropic.resources.beta.tools.messages.AsyncMessages.create",
    new_callable=AsyncMock,
)
@pytest.mark.asyncio
async def test_anthropic_extractor_extract_async_tool(
    mock_create: AsyncMock,
    fixture_anthropic_book_tool: Type[AnthropicTool],
    fixture_anthropic_message_with_tools: Message,
) -> None:
    """Tests that the `AnthropicExtractor` class returns the expected model."""
    mock_create.return_value = fixture_anthropic_message_with_tools

    class TempExtractor(AnthropicExtractor[Type[AnthropicTool]]):
        extract_schema: Type[AnthropicTool] = fixture_anthropic_book_tool
        prompt_template = "test"

    tool = await TempExtractor().extract_async()

    assert isinstance(tool, fixture_anthropic_book_tool)
    assert tool.title == "The Name of the Wind"
    assert tool.author == "Patrick Rothfuss"
