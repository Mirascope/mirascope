"""Tests for the `mirascope.gemini.types` module."""
from typing import Type

import pytest
from google.generativeai.types import GenerateContentResponse  # type: ignore

from mirascope.gemini.tools import GeminiTool
from mirascope.gemini.types import GeminiCallResponse


def test_gemini_call_response(
    fixture_generate_content_response: GenerateContentResponse,
) -> None:
    """Tests the `GeminiCallResponse` class."""
    response = GeminiCallResponse(
        response=fixture_generate_content_response,
        start_time=0,
        end_time=0,
        cost=None,
    )
    assert response.content == "Who is the author?"
    assert response.tools is None
    assert response.tool is None
    assert response.dump() == {
        "start_time": 0,
        "end_time": 0,
        "output": str(fixture_generate_content_response),
        "cost": None,
    }


def test_gemini_call_response_with_tools(
    fixture_generate_content_response_with_tools: GenerateContentResponse,
    fixture_book_tool: Type[GeminiTool],
    fixture_expected_book_tool_instance: GeminiTool,
) -> None:
    """Tests the `GeminiCallResponse` class with a tool."""
    response = GeminiCallResponse(
        response=fixture_generate_content_response_with_tools,
        tool_types=[fixture_book_tool],
        start_time=0,
        end_time=0,
    )

    expected_tool = fixture_expected_book_tool_instance

    tools = response.tools
    assert tools is not None
    tools = [tool for tool in tools]
    assert response.tool == expected_tool
    assert len(tools) == 2
    assert tools[0] == expected_tool
    assert tools[1] == expected_tool


def test_gemini_call_response_with_tools_bad_stop_sequence(
    fixture_generate_content_response_with_tools_bad_stop_sequence: GenerateContentResponse,
    fixture_book_tool: Type[GeminiTool],
) -> None:
    """Tests the `GeminiCallResponse` class with a tool."""
    response = GeminiCallResponse(
        response=fixture_generate_content_response_with_tools_bad_stop_sequence,
        tool_types=[fixture_book_tool],
        start_time=0,
        end_time=0,
    )

    with pytest.raises(RuntimeError):
        response.tool


def test_gemini_call_response_with_no_matching_tools(
    fixture_generate_content_response_with_tools: GenerateContentResponse,
) -> None:
    """Tests that the `tools` and `tool` convenience functions work with no matches."""

    class NotBookTool(GeminiTool):
        title: str

    response = GeminiCallResponse(
        response=fixture_generate_content_response_with_tools,
        tool_types=[NotBookTool],
        start_time=0,
        end_time=0,
    )

    tools = response.tools
    assert tools == []
    assert response.tool is None


def test_gemini_call_response_with_no_tools(
    fixture_generate_content_response_with_tools: GenerateContentResponse,
) -> None:
    """Tests that the `tools` and `tool` convenience functions work with no tools."""
    response = GeminiCallResponse(
        response=fixture_generate_content_response_with_tools,
        start_time=0,
        end_time=0,
    )

    assert response.tools is None
    assert response.tool is None
