"""Tests for the `mirascope.groq.types` module."""

from typing import Type

import pytest
from groq.types.chat.chat_completion import ChatCompletion
from groq.types.chat.chat_completion_chunk import ChatCompletionChunk

from mirascope.groq import (
    GroqCallResponse,
    GroqCallResponseChunk,
    GroqTool,
)


def test_groq_call_response(
    fixture_chat_completion_response: ChatCompletion,
) -> None:
    """Tests the `GroqCallResponse` class."""
    response = GroqCallResponse(
        response=fixture_chat_completion_response,
        start_time=0,
        end_time=0,
    )
    assert response.message_param == {
        "role": "assistant",
        "content": "test content",
        "tool_calls": [],
    }
    assert response.content == "test content"
    assert response.tools is None
    assert response.tool is None
    assert response.model == fixture_chat_completion_response.model
    assert response.id == fixture_chat_completion_response.id
    assert response.finish_reasons == [
        fixture_chat_completion_response.choices[0].finish_reason
    ]
    assert response.usage is not None
    assert response.input_tokens is not None
    assert response.output_tokens is not None


def test_groq_call_response_no_usage(
    fixture_chat_completion_response_no_usage: ChatCompletion,
) -> None:
    """Tests the `GroqCallResponse` class."""
    response = GroqCallResponse(
        response=fixture_chat_completion_response_no_usage,
        start_time=0,
        end_time=0,
    )
    assert response.usage is None
    assert response.input_tokens is None
    assert response.output_tokens is None


def test_groq_call_response_dump(
    fixture_chat_completion_response: ChatCompletion,
):
    """Tests that `GroqCallResponse.dump` returns the expected dictionary."""
    response = GroqCallResponse(
        response=fixture_chat_completion_response, start_time=0, end_time=0
    )
    groq_chat_completion_json = response.dump()
    assert (
        groq_chat_completion_json["output"]["choices"][0]["message"]["content"]
        == response.content
    )


def test_groq_call_response_with_tools(
    fixture_chat_completion_response_with_tools: ChatCompletion,
    fixture_book_tool: Type[GroqTool],
    fixture_expected_book_tool_instance: GroqTool,
) -> None:
    """Tests the `GroqCallResponse` class with a tool."""
    response = GroqCallResponse(
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
    assert response.tool_message_params([(tools[0], "output")]) == [
        {"role": "tool", "content": "output", "tool_call_id": "id"}
    ]


def test_groq_call_response_with_assistant_message_tool(
    fixture_chat_completion_response_with_assistant_message_tool: ChatCompletion,
    fixture_book_tool: Type[GroqTool],
    fixture_expected_book_tool_instance: GroqTool,
):
    """Tests that `OpenAICallResponse` returns a tool when it's an assistant message."""
    response = GroqCallResponse(
        response=fixture_chat_completion_response_with_assistant_message_tool,
        tool_types=[fixture_book_tool],
        start_time=0,
        end_time=0,
    )
    assert response.tools is not None
    assert response.tools[0].tool_call == fixture_expected_book_tool_instance.tool_call


def test_groq_call_response_with_tools_bad_stop_sequence(
    fixture_chat_completion_response_with_tools_bad_stop_sequence: ChatCompletion,
    fixture_book_tool: Type[GroqTool],
) -> None:
    """Tests the `GroqCallResponse` class with a tool and bad stop sequence."""
    response = GroqCallResponse(
        response=fixture_chat_completion_response_with_tools_bad_stop_sequence,
        tool_types=[fixture_book_tool],
        start_time=0,
        end_time=0,
    )

    with pytest.raises(RuntimeError):
        response.tool


def test_groq_call_response_with_no_matching_tools(
    fixture_chat_completion_response_with_tools: ChatCompletion,
) -> None:
    """Tests that the `tools` and `tool` convenience functions work with no matches."""

    class NotBookTool(GroqTool):
        title: str

    response = GroqCallResponse(
        response=fixture_chat_completion_response_with_tools,
        tool_types=[NotBookTool],
        start_time=0,
        end_time=0,
    )

    tools = response.tools
    assert tools == []
    assert response.tool is None


def test_groq_call_response_with_no_tools(
    fixture_chat_completion_response_with_tools: ChatCompletion,
) -> None:
    """Tests that the `tools` and `tool` convenience functions work with no tools."""
    response = GroqCallResponse(
        response=fixture_chat_completion_response_with_tools, start_time=0, end_time=0
    )

    assert response.tools is None
    assert response.tool is None


def test_groq_stream_response_with_tools(
    fixture_chat_completion_stream_response_with_tools: list[ChatCompletionChunk],
    fixture_book_tool: Type[GroqTool],
):
    """Tests that the streaming response `tool_calls` property works."""
    response = GroqCallResponseChunk(
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
    assert response.model == fixture_chat_completion_stream_response_with_tools[0].model
    assert response.id == fixture_chat_completion_stream_response_with_tools[0].id
    assert response.finish_reasons == [
        fixture_chat_completion_stream_response_with_tools[0].choices[0].finish_reason
    ]
    assert response.usage is not None
    assert response.input_tokens == 1
    assert response.output_tokens == 1

    response = GroqCallResponseChunk(
        chunk=fixture_chat_completion_stream_response_with_tools[1],
        tool_types=[fixture_book_tool],
    )
    assert response.usage is None
    assert response.input_tokens is None
    assert response.output_tokens is None
