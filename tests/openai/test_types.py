"""Tests for types for working with OpenAI with Mirascope."""
from typing import Type
from unittest.mock import MagicMock, patch

import pytest
from openai.types.chat import ChatCompletion, ChatCompletionChunk
from pydantic import ValidationError

from mirascope.openai.calls import OpenAICall
from mirascope.openai.tools import OpenAITool
from mirascope.openai.types import (
    OpenAICallParams,
    OpenAICallResponse,
    OpenAICallResponseChunk,
)


def test_openai_call_params_kwargs():
    """Tests the `kwargs` function of `OpenAICallParams`."""
    call_params = OpenAICallParams(model="model", wrapper=lambda x: x)
    assert call_params.kwargs() == {"model": "model"}


def test_openai_call_response(fixture_chat_completion: ChatCompletion):
    """Tests that `OpenAICallResponse` can be initialized properly."""
    response = OpenAICallResponse(
        response=fixture_chat_completion, start_time=0, end_time=0
    )
    choices = fixture_chat_completion.choices
    assert response.choices == choices
    assert response.choice == choices[0]
    assert response.message == choices[0].message
    assert response.content == choices[0].message.content
    assert response.tools is None
    assert response.tool is None


def test_openai_chat_completion_with_tools(
    fixture_chat_completion_with_tools: ChatCompletion,
    fixture_my_openai_tool: Type[OpenAITool],
    fixture_my_openai_tool_instance: OpenAITool,
):
    """Tests that `OpenAICallResponse` can be initialized properly with tools."""
    response = OpenAICallResponse(
        response=fixture_chat_completion_with_tools,
        tool_types=[fixture_my_openai_tool],
        start_time=0,
        end_time=0,
    )
    choices = fixture_chat_completion_with_tools.choices
    assert response.choices == choices
    assert response.choice == choices[0]
    assert response.message == choices[0].message
    assert response.tool_calls == choices[0].message.tool_calls
    fixture_tool_model_dump = fixture_my_openai_tool_instance.model_dump()
    completion_tool_model_dumps = [tool.model_dump() for tool in response.tools or []]
    assert completion_tool_model_dumps == [fixture_tool_model_dump]
    assert completion_tool_model_dumps[0] == fixture_tool_model_dump
    assert response.tools is not None
    assert response.tools[0].tool_call == fixture_my_openai_tool_instance.tool_call


def test_openai_chat_completion_with_assistant_message_tool(
    fixture_chat_completion_with_assistant_message_tool: ChatCompletion,
    fixture_my_openai_tool: Type[OpenAITool],
    fixture_my_openai_tool_instance: OpenAITool,
):
    """Tests that `OpenAICallResponse` returns a tool when it's an assistant message."""
    response = OpenAICallResponse(
        response=fixture_chat_completion_with_assistant_message_tool,
        tool_types=[fixture_my_openai_tool],
        start_time=0,
        end_time=0,
    )
    assert response.tools is not None
    assert response.tools[0].tool_call == fixture_my_openai_tool_instance.tool_call


def test_openai_call_response_dump(fixture_chat_completion: ChatCompletion):
    """Tests that `OpenAICallResponse.dump` returns the expected dictionary."""
    response = OpenAICallResponse(
        response=fixture_chat_completion, start_time=0, end_time=0
    )
    openai_chat_completion_json = response.dump()
    assert (
        openai_chat_completion_json["output"]["choices"][0]["message"]["content"]
        == response.content
    )


def test_openai_call_response_no_matching_tools(
    fixture_chat_completion_with_tools: ChatCompletion,
    fixture_empty_openai_tool: Type[OpenAITool],
):
    """Tests that `OpenAICallResponse` returns `None` if no tools match."""
    response = OpenAICallResponse(
        response=fixture_chat_completion_with_tools,
        tool_types=[fixture_empty_openai_tool],
        start_time=0,
        end_time=0,
    )
    assert not response.tools
    assert response.tool is None


def test_openai_chat_completion_with_bad_tools(
    fixture_chat_completion_with_bad_tools: ChatCompletion,
    fixture_my_openai_tool: Type[OpenAITool],
):
    """Tests that `OpenAICallResponse` raises a ValidationError with bad tools."""
    response = OpenAICallResponse(
        response=fixture_chat_completion_with_bad_tools,
        tool_types=[fixture_my_openai_tool],
        start_time=0,
        end_time=0,
    )
    with pytest.raises(ValidationError):
        response.tools

    with pytest.raises(ValidationError):
        response.tool


def test_openai_chat_completion_chunk(
    fixture_chat_completion_chunk: ChatCompletionChunk,
):
    """Tests that `OpenAICallResponseChunk` can be initialized properly."""
    openai_chat_completion_chunk = OpenAICallResponseChunk(
        chunk=fixture_chat_completion_chunk
    )
    choices = fixture_chat_completion_chunk.choices
    assert openai_chat_completion_chunk.choices == choices
    assert openai_chat_completion_chunk.choice == choices[0]
    assert openai_chat_completion_chunk.delta == choices[0].delta
    assert openai_chat_completion_chunk.content == choices[0].delta.content


def test_openai_chat_completion_chunk_with_tools(
    fixture_chat_completion_chunk_with_tools: ChatCompletionChunk,
    fixture_my_openai_tool: Type[OpenAITool],
):
    """Tests that `OpenAICallResponseChunk` can be initialized properly with tools."""
    openai_chat_completion_chunk = OpenAICallResponseChunk(
        chunk=fixture_chat_completion_chunk_with_tools,
        tool_types=[fixture_my_openai_tool],
    )
    choices = fixture_chat_completion_chunk_with_tools.choices
    assert openai_chat_completion_chunk.choices == choices
    assert openai_chat_completion_chunk.delta == choices[0].delta
    assert openai_chat_completion_chunk.content == ""
    assert openai_chat_completion_chunk.tool_calls == choices[0].delta.tool_calls


def test_openai_chat_completion_tools_wrong_stop_sequence(
    fixture_chat_completion_with_tools_bad_stop_sequence: ChatCompletion,
    fixture_my_openai_tool: Type[OpenAITool],
):
    """Tests that `OpenAICallResponse` raises a ValidationError with a wrong stop sequence."""
    response = OpenAICallResponse(
        response=fixture_chat_completion_with_tools_bad_stop_sequence,
        tool_types=[fixture_my_openai_tool],
        start_time=0,
        end_time=0,
    )
    with pytest.raises(RuntimeError):
        response.tool


@patch(
    "openai.resources.chat.completions.Completions.create",
    new_callable=MagicMock,
)
def test_openai_call_call_no_usage(
    mock_create: MagicMock,
    fixture_openai_test_call: OpenAICall,
    fixture_chat_completion_no_usage: ChatCompletion,
) -> None:
    """Tests `OpenAIPrompt.create` with no usage returns None for tokens and usage."""
    mock_create.return_value = fixture_chat_completion_no_usage
    response = fixture_openai_test_call.call(retries=1)
    assert response.usage is None
    assert response.input_tokens is None
    assert response.output_tokens is None
