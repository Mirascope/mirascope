"""Tests for mirascope chat types."""
import pytest
from pydantic import ValidationError

from mirascope.chat.types import OpenAIChatCompletion, OpenAIChatCompletionChunk


def test_openai_chat_completion(fixture_chat_completion):
    """Tests that `OpenAIChatCompletion` can be initialized properly."""
    openai_chat_completion = OpenAIChatCompletion(completion=fixture_chat_completion)
    choices = fixture_chat_completion.choices
    assert openai_chat_completion.choices == choices
    assert openai_chat_completion.choice == choices[0]
    assert openai_chat_completion.message == choices[0].message
    assert openai_chat_completion.content == choices[0].message.content
    assert str(openai_chat_completion) == openai_chat_completion.content
    assert openai_chat_completion.tools is None
    assert openai_chat_completion.tool is None


def test_openai_chat_completion_with_tools(
    fixture_chat_completion_with_tools, fixture_my_tool, fixture_my_tool_instance
):
    """Tests that `OpenAIChatCompletion` can be initialized properly with tools."""
    openai_chat_completion = OpenAIChatCompletion(
        completion=fixture_chat_completion_with_tools, tool_types=[fixture_my_tool]
    )
    choices = fixture_chat_completion_with_tools.choices
    assert openai_chat_completion.choices == choices
    assert openai_chat_completion.choice == choices[0]
    assert openai_chat_completion.message == choices[0].message
    assert openai_chat_completion.tool_calls == choices[0].message.tool_calls
    fixture_tool_model_dump = fixture_my_tool_instance.model_dump()
    completion_tool_model_dumps = [
        tool.model_dump() for tool in openai_chat_completion.tools or []
    ]
    assert completion_tool_model_dumps == [fixture_tool_model_dump]
    assert completion_tool_model_dumps[0] == fixture_tool_model_dump
    assert (
        openai_chat_completion.tools[0]._tool_call
        == fixture_my_tool_instance._tool_call
    )


def test_openai_chat_completion_with_bad_tools(
    fixture_chat_completion_with_bad_tools, fixture_my_tool
):
    """Tests that `OpenAIChatCompletion` raises a ValidationError with bad tools."""
    completion = OpenAIChatCompletion(
        completion=fixture_chat_completion_with_bad_tools,
        tool_types=[fixture_my_tool],
    )
    with pytest.raises(ValidationError):
        completion.tools

    with pytest.raises(ValidationError):
        completion.tool


def test_openai_chat_completion_chunk(fixture_chat_completion_chunk):
    """Tests that `OpenAIChatCompletionChunk` can be initialized properly."""
    openai_chat_completion_chunk = OpenAIChatCompletionChunk(
        chunk=fixture_chat_completion_chunk
    )
    choices = fixture_chat_completion_chunk.choices
    assert openai_chat_completion_chunk.choices == choices
    assert openai_chat_completion_chunk.delta == choices[0].delta
    assert openai_chat_completion_chunk.content == choices[0].delta.content
    assert str(openai_chat_completion_chunk) == openai_chat_completion_chunk.content


def test_openai_chat_completion_chunk_with_tools(
    fixture_chat_completion_chunk_with_tools, fixture_my_tool
):
    """Tests that `OpenAIChatCompletionChunk` can be initialized properly with tools."""
    openai_chat_completion_chunk = OpenAIChatCompletionChunk(
        chunk=fixture_chat_completion_chunk_with_tools, tool_types=[fixture_my_tool]
    )
    choices = fixture_chat_completion_chunk_with_tools.choices
    assert openai_chat_completion_chunk.choices == choices
    assert openai_chat_completion_chunk.delta == choices[0].delta
    assert openai_chat_completion_chunk.content == choices[0].delta.content
    assert openai_chat_completion_chunk.tool_calls == choices[0].delta.tool_calls
