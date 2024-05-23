"""Tests for the `mirascope.gemini.calls` module."""

from typing import Type
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from google.generativeai.types import GenerateContentResponse  # type: ignore

from mirascope.gemini.calls import GeminiCall
from mirascope.gemini.tools import GeminiTool
from mirascope.gemini.types import GeminiCallParams, GeminiCallResponse


@patch("google.generativeai.GenerativeModel.generate_content", new_callable=MagicMock)
def test_gemini_call_call(
    mock_generate_content: MagicMock,
    fixture_generate_content_response: GenerateContentResponse,
) -> None:
    """Tests that `GeminiClass.call` returns the expected response."""
    mock_generate_content.return_value = fixture_generate_content_response

    class TempCall(GeminiCall):
        prompt_template = ""

    response = TempCall().call()
    assert isinstance(response, GeminiCallResponse)
    assert response.usage is None
    assert response.content == "Who is the author?"


@patch("google.generativeai.GenerativeModel.generate_content", new_callable=MagicMock)
def test_gemini_call_call_with_tools(
    mock_generate_content: MagicMock,
    fixture_book_tool: Type[GeminiTool],
    fixture_expected_book_tool_instance: GeminiTool,
    fixture_generate_content_response_with_tools: GenerateContentResponse,
) -> None:
    """Tests that `GeminiCall.call` works with tools."""
    mock_generate_content.return_value = fixture_generate_content_response_with_tools

    class TempCall(GeminiCall):
        prompt_template = ""

        call_params = GeminiCallParams(tools=[fixture_book_tool])

    response = TempCall().call()
    assert response.tool == fixture_expected_book_tool_instance


@patch(
    "google.generativeai.GenerativeModel.generate_content_async", new_callable=AsyncMock
)
@pytest.mark.asyncio
async def test_gemini_call_call_async(
    mock_generate_content: MagicMock,
    fixture_generate_content_response: GenerateContentResponse,
) -> None:
    """Tests that the `GeminiPrompt` class returns the expected completion."""
    mock_generate_content.return_value = fixture_generate_content_response

    class TempCall(GeminiCall):
        prompt_template = ""

    response = await TempCall().call_async()
    assert isinstance(response, GeminiCallResponse)
    assert response.content == "Who is the author?"


@patch("google.generativeai.GenerativeModel.generate_content", new_callable=MagicMock)
def test_gemini_call_stream(
    mock_generate_content: MagicMock,
    fixture_generate_content_chunks: GenerateContentResponse,
) -> None:
    """Tests that the `GeminiPrompt` class returns the expected completion."""
    mock_generate_content.return_value = fixture_generate_content_chunks

    class TempCall(GeminiCall):
        prompt_template = ""

    chunks = [chunk for chunk in TempCall().stream()]
    assert len(chunks) == 2
    assert chunks[0].content == "first"
    assert chunks[1].content == "second"


@patch(
    "google.generativeai.GenerativeModel.generate_content_async", new_callable=AsyncMock
)
@pytest.mark.asyncio
async def test_gemini_call_stream_async(
    mock_generate_content: AsyncMock,
    fixture_generate_content_chunks: GenerateContentResponse,
) -> None:
    """Tests that the `GeminiPrompt` class returns the expected completion."""
    mock_generate_content.return_value.__aiter__.return_value = (
        fixture_generate_content_chunks
    )

    class TempCall(GeminiCall):
        prompt_template = ""

    chunks = [chunk async for chunk in TempCall().stream_async()]
    assert len(chunks) == 2
    assert chunks[0].content == "first"
    assert chunks[1].content == "second"
