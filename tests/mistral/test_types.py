"""Tests for the `mirascope.mistral.types` module."""

from typing import Type

import pytest
from mistralai.models.chat_completion import (
    ChatCompletionResponse,
    ChatCompletionStreamResponse,
)

from mirascope.mistral import (
    MistralCallResponse,
    MistralCallResponseChunk,
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
    assert response.message_param == {
        "role": "assistant",
        "content": "test content",
        "name": None,
        "tool_call_id": None,
        "tool_calls": None,
    }
    assert response.content == "test content"
    assert response.tools is None
    assert response.tool is None
    assert response.usage is not None
    assert response.input_tokens is not None
    assert response.output_tokens is not None


def test_mistral_call_response_dump(
    fixture_chat_completion_response: ChatCompletionResponse,
):
    """Tests that `MistralCallResponse.dump` returns the expected dictionary."""
    response = MistralCallResponse(
        response=fixture_chat_completion_response, start_time=0, end_time=0
    )
    mistral_chat_completion_json = response.dump()
    assert (
        mistral_chat_completion_json["output"]["choices"][0]["message"]["content"]
        == response.content
    )


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


def test_mistral_call_response_with_tools_bad_stop_sequence(
    fixture_chat_completion_response_with_tools_bad_stop_sequence: ChatCompletionResponse,
    fixture_book_tool: Type[MistralTool],
    fixture_expected_book_tool_instance: MistralTool,
) -> None:
    """Tests the `MistralCallResponse` class with a tool."""
    response = MistralCallResponse(
        response=fixture_chat_completion_response_with_tools_bad_stop_sequence,
        tool_types=[fixture_book_tool],
        start_time=0,
        end_time=0,
    )

    with pytest.raises(RuntimeError):
        response.tool


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


def test_mistral_stream_response_with_tools(
    fixture_chat_completion_stream_response_with_tools: list[
        ChatCompletionStreamResponse
    ],
    fixture_book_tool: Type[MistralTool],
):
    """Tests that the streaming response `tool_calls` property works."""
    response = MistralCallResponseChunk(
        chunk=fixture_chat_completion_stream_response_with_tools[0],
        tool_types=[fixture_book_tool],
    )

    assert response.tool_calls is not None
    assert (
        response.tool_calls
        == fixture_chat_completion_stream_response_with_tools[0]
        .choices[0]
        .delta.tool_calls
    )
