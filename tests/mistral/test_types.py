"""Tests for the `mirascope.mistral.types` module."""
from typing import Type

from mistralai.models.chat_completion import (
    ChatCompletionResponse,
)

from mirascope.mistral import (
    MistralCallResponse,
    MistralTool,
)


def test_mistral_call_response(
    fixture_chat_completion_response: ChatCompletionResponse,
) -> None:
    """Tests the `MistralCallResponse` class."""
    response = MistralCallResponse(
        response=fixture_chat_completion_response,
        start_time=0,
        end_time=0,
    )
    assert response.content == "test content"
    assert response.tools is None
    assert response.tool is None


def test_mistral_call_response_with_tools(
    fixture_chat_completion_response_with_tools: ChatCompletionResponse,
    fixture_book_tool: Type[MistralTool],
    fixture_expected_book_tool_instance: MistralTool,
) -> None:
    """Tests the `MistralCallResponse` class with a tool."""
    response = MistralCallResponse(
        response=fixture_chat_completion_response_with_tools,
        tool_types=[fixture_book_tool],
        start_time=0,
        end_time=0,
    )

    expected_tool = fixture_expected_book_tool_instance

    tools = response.tools
    assert tools is not None
    tools = [tool for tool in tools]
    assert response.tool == expected_tool
    assert len(tools) == 1
    assert tools[0] == expected_tool


def test_mistral_call_response_with_no_matching_tools(
    fixture_chat_completion_response_with_tools: ChatCompletionResponse,
) -> None:
    """Tests that the `tools` and `tool` convenience functions work with no matches."""

    class NotBookTool(MistralTool):
        title: str

    response = MistralCallResponse(
        response=fixture_chat_completion_response_with_tools,
        tool_types=[NotBookTool],
        start_time=0,
        end_time=0,
    )

    tools = response.tools
    assert tools == []
    assert response.tool is None


def test_mistral_call_response_with_no_tools(
    fixture_chat_completion_response_with_tools: ChatCompletionResponse,
) -> None:
    """Tests that the `tools` and `tool` convenience functions work with no tools."""
    response = MistralCallResponse(
        response=fixture_chat_completion_response_with_tools, start_time=0, end_time=0
    )

    assert response.tools is None
    assert response.tool is None
