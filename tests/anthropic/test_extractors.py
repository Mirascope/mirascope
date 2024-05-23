"""Tests for `AnthropicExtractor`."""

from typing import Type
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from anthropic.types import Message

from mirascope.anthropic.extractors import AnthropicExtractor
from mirascope.anthropic.tools import AnthropicTool
from mirascope.anthropic.types import AnthropicCallParams, AnthropicCallResponseChunk


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


@patch(
    "mirascope.anthropic.calls.AnthropicCall.stream",
    new_callable=MagicMock,
)
def test_anthropic_extractor_stream_tool(
    mock_stream: MagicMock,
    fixture_anthropic_book_tool: Type[AnthropicTool],
    fixture_anthropic_call_response_chunks_with_tools: list[AnthropicCallResponseChunk],
) -> None:
    """Tests that the `AnthropicExtractor` class streams the expected model."""
    mock_stream.return_value = fixture_anthropic_call_response_chunks_with_tools

    class TempExtractor(AnthropicExtractor[Type[AnthropicTool]]):
        extract_schema: Type[AnthropicTool] = fixture_anthropic_book_tool
        prompt_template = "test"
        api_key = "test"
        call_params = AnthropicCallParams(response_format="json")

    tools = list(TempExtractor().stream())

    assert len(tools) == 2
    assert tools[0].args == {"title": "The Name of the Wind", "author": None}
    assert tools[1].args == {
        "title": "The Name of the Wind",
        "author": "Patrick Rothfuss",
    }


@patch(
    "mirascope.anthropic.calls.AnthropicCall.stream_async",
    new_callable=MagicMock,
)
@pytest.mark.asyncio
async def test_anthropic_extractor_stream_async_tool(
    mock_stream: MagicMock,
    fixture_anthropic_book_tool: Type[AnthropicTool],
    fixture_anthropic_call_response_chunks_with_tools: list[AnthropicCallResponseChunk],
) -> None:
    """Tests that the `AnthropicExtractor` class streams the expected model."""
    mock_stream.return_value.__aiter__.return_value = (
        fixture_anthropic_call_response_chunks_with_tools
    )

    class TempExtractor(AnthropicExtractor[Type[AnthropicTool]]):
        extract_schema: Type[AnthropicTool] = fixture_anthropic_book_tool
        prompt_template = "test"
        api_key = "test"
        call_params = AnthropicCallParams(response_format="json")

    tools = [tool async for tool in TempExtractor().stream_async()]

    assert len(tools) == 2
    assert tools[0].args == {"title": "The Name of the Wind", "author": None}
    assert tools[1].args == {
        "title": "The Name of the Wind",
        "author": "Patrick Rothfuss",
    }
