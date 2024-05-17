"""Tests for the `mirascope.groq.calls` module"""
from typing import Type
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from groq import AsyncGroq, Groq
from groq.lib.chat_completion_chunk import ChatCompletionChunk
from groq.types.chat.chat_completion import ChatCompletion
from groq.types.chat.completion_create_params import Message, ResponseFormat

from mirascope.base.types import BaseConfig
from mirascope.groq import (
    GroqCall,
    GroqCallParams,
    GroqCallResponse,
    GroqCallResponseChunk,
    GroqTool,
)
from mirascope.groq.calls import _json_mode_content


@patch("groq.resources.chat.completions.Completions.create", new_callable=MagicMock)
def test_groq_call_call(
    mock_create: MagicMock,
    fixture_chat_completion_response: ChatCompletion,
) -> None:
    """Tests that `GroqCall.call` returns the expected response."""
    mock_create.return_value = fixture_chat_completion_response
    wrapper = MagicMock()
    wrapper.return_value = Groq(api_key="test")

    class TempCall(GroqCall):
        prompt_template = ""
        api_key = "test"

        configuration = BaseConfig(client_wrappers=[wrapper])

    response = TempCall().call()
    assert isinstance(response, GroqCallResponse)
    assert response.content == "test content"
    wrapper.assert_called_once()


@patch("groq.resources.chat.completions.Completions.create", new_callable=MagicMock)
def test_groq_call_call_with_tools(
    mock_chat_completion: MagicMock,
    fixture_book_tool: Type[GroqTool],
    fixture_expected_book_tool_instance: GroqTool,
    fixture_chat_completion_response_with_tools: ChatCompletion,
) -> None:
    """Tests that `GroqCall.call` works with tools."""
    mock_chat_completion.return_value = fixture_chat_completion_response_with_tools

    class TempCall(GroqCall):
        prompt_template = ""
        api_key = "test"

        call_params = GroqCallParams(tools=[fixture_book_tool])

    response = TempCall().call()
    assert response.tool == fixture_expected_book_tool_instance


@patch(
    "groq.resources.chat.completions.AsyncCompletions.create", new_callable=AsyncMock
)
@pytest.mark.asyncio
async def test_groq_call_call_async(
    mock_create: AsyncMock,
    fixture_chat_completion_response: ChatCompletion,
) -> None:
    """Tests that `GroqCall.call_async` returns the expected response."""
    mock_create.return_value = fixture_chat_completion_response
    wrapper_async = MagicMock()
    wrapper_async.return_value = AsyncGroq(api_key="test")

    class TempCall(GroqCall):
        prompt_template = ""
        api_key = "test"

        configuration = BaseConfig(client_wrappers=[wrapper_async])

    response = await TempCall().call_async()
    assert isinstance(response, GroqCallResponse)
    assert response.content == "test content"


@patch("groq.resources.chat.completions.Completions.create", new_callable=MagicMock)
def test_groq_call_stream(
    mock_create: MagicMock,
    fixture_chat_completion_stream_response: list[ChatCompletionChunk],
) -> None:
    """Tests that `GroqCall.stream` returns the expected response."""
    mock_create.return_value = fixture_chat_completion_stream_response
    wrapper = MagicMock()
    wrapper.return_value = Groq(api_key="test")

    class TempCall(GroqCall):
        prompt_template = ""
        api_key = "test"

        configuration = BaseConfig(client_wrappers=[wrapper])

    chunks = [chunk for chunk in TempCall().stream()]
    assert len(chunks) == 2
    assert chunks[0].content == "A"
    assert chunks[1].content == "B"
    wrapper.assert_called_once()


@patch(
    "groq.resources.chat.completions.AsyncCompletions.create", new_callable=AsyncMock
)
@pytest.mark.asyncio
async def test_groq_call_stream_async(
    mock_create: AsyncMock,
    fixture_chat_completion_stream_response: list[ChatCompletionChunk],
):
    """Tests `GroqCall.stream_async` returns expected response."""
    wrapper_async = MagicMock()
    wrapper_async.return_value = AsyncGroq(api_key="test")

    class TempCall(GroqCall):
        prompt_template = ""
        api_key = "test"

        configuration = BaseConfig(client_wrappers=[wrapper_async])

    mock_create.return_value.__aiter__.return_value = (
        fixture_chat_completion_stream_response
    )
    temp_call = TempCall()
    stream = temp_call.stream_async()

    i = 0
    async for chunk in stream:
        assert isinstance(chunk, GroqCallResponseChunk)
        assert chunk.chunk == fixture_chat_completion_stream_response[i]
        i += 1

    mock_create.assert_called_once_with(
        messages=temp_call.messages(), stream=True, model=temp_call.call_params.model
    )
    wrapper_async.assert_called_once()


@patch("groq.resources.chat.completions.Completions.create", new_callable=MagicMock)
def test_groq_call_call_with_tools_json_mode(
    mock_create: MagicMock,
    fixture_book_tool: Type[GroqTool],
    fixture_book_tool_instance: GroqTool,
    fixture_chat_completion_with_tools_json_mode: ChatCompletion,
) -> None:
    """Tests that tools are properly passed to the create call."""
    mock_create.return_value = fixture_chat_completion_with_tools_json_mode

    class CallWithTools(GroqCall):
        prompt_template = "test"

        api_key = "test"
        call_params = GroqCallParams(
            model="llama2-70b-4096",
            tools=[fixture_book_tool],
            response_format=ResponseFormat(type="json_object"),
        )

    call_with_tools = CallWithTools()
    response = call_with_tools.call()
    mock_create.assert_called_once_with(
        model="llama2-70b-4096",
        messages=call_with_tools.messages()
        + [
            Message(
                role="user",
                content=_json_mode_content(tool_type=fixture_book_tool),
            )
        ],
        response_format=ResponseFormat(type="json_object"),
        stream=False,
    )
    assert response.tool_types == [fixture_book_tool]
    tool = response.tool
    assert tool is not None
    assert tool.model_dump() == fixture_book_tool_instance.model_dump()
