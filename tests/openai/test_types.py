"""Tests for types for working with OpenAI with Mirascope."""

from collections.abc import Generator
from typing import Type
from unittest.mock import MagicMock, patch

import pytest
from openai.types.chat import (
    ChatCompletion,
    ChatCompletionChunk,
    ChatCompletionMessageToolCall,
)
from openai.types.chat.chat_completion_message_tool_call import Function
from openai.types.chat.completion_create_params import ResponseFormat
from pydantic import ValidationError

from mirascope.openai.calls import OpenAICall
from mirascope.openai.tools import OpenAITool
from mirascope.openai.types import (
    OpenAIAsyncStream,
    OpenAICallParams,
    OpenAICallResponse,
    OpenAICallResponseChunk,
    OpenAIStream,
    OpenAIToolStream,
)


def test_openai_call_params_kwargs():
    """Tests the `kwargs` function of `OpenAICallParams`."""
    call_params = OpenAICallParams(model="model")
    assert call_params.kwargs() == {"model": "model"}


def test_openai_call_response(fixture_chat_completion: ChatCompletion):
    """Tests that `OpenAICallResponse` can be initialized properly."""
    response = OpenAICallResponse(
        response=fixture_chat_completion, start_time=0, end_time=0
    )
    choices = fixture_chat_completion.choices
    assert response.message_param == {
        "role": "assistant",
        "content": choices[0].message.content,
        "tool_calls": None,
        "refusal": None,
    }
    assert response.choices == choices
    assert response.choice == choices[0]
    assert response.message == choices[0].message
    assert response.content == choices[0].message.content
    assert response.model == fixture_chat_completion.model
    assert response.finish_reasons == ["stop", "stop"]
    assert response.id == fixture_chat_completion.id
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
    assert response.tool_message_params([(response.tools[0], "output")]) == [
        {
            "role": "tool",
            "content": "output",
            "tool_call_id": "id",
            "name": "my_openai_tool",
        }
    ]


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
    assert openai_chat_completion_chunk.model == fixture_chat_completion_chunk.model
    assert openai_chat_completion_chunk.id == fixture_chat_completion_chunk.id
    assert openai_chat_completion_chunk.finish_reasons == ["stop"]


def test_openai_chat_completion_last_chunk(
    fixture_chat_completion_last_chunk: ChatCompletionChunk,
):
    """Tests that `OpenAICallResponseChunk` can be initialized properly."""
    openai_chat_completion_chunk = OpenAICallResponseChunk(
        chunk=fixture_chat_completion_last_chunk
    )
    usage = fixture_chat_completion_last_chunk.usage
    assert openai_chat_completion_chunk.usage == usage
    assert openai_chat_completion_chunk.input_tokens == (
        usage.prompt_tokens if usage else None
    )
    assert openai_chat_completion_chunk.output_tokens == (
        usage.completion_tokens if usage else None
    )


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


def test_openai_chat_completion_last_chunk_with_tools(
    fixture_chat_completion_last_chunk_with_tools: ChatCompletionChunk,
    fixture_my_openai_tool: Type[OpenAITool],
):
    """Tests that `OpenAICallResponseChunk` can be initialized properly with tools."""
    openai_chat_completion_chunk = OpenAICallResponseChunk(
        chunk=fixture_chat_completion_last_chunk_with_tools,
        tool_types=[fixture_my_openai_tool],
    )
    usage = fixture_chat_completion_last_chunk_with_tools.usage
    assert openai_chat_completion_chunk.usage == usage
    assert openai_chat_completion_chunk.input_tokens == (
        usage.prompt_tokens if usage else None
    )
    assert openai_chat_completion_chunk.output_tokens == (
        usage.completion_tokens if usage else None
    )


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


def test_openai_tool_stream_from_stream(
    fixture_my_openai_tool: Type[OpenAITool],
    fixture_chat_completion_chunks_with_tools: list[ChatCompletionChunk],
) -> None:
    """Tests streaming tools from chunks."""

    def generator():
        stream = fixture_chat_completion_chunks_with_tools[:-1] * 2
        stream.append(fixture_chat_completion_chunks_with_tools[-1])
        for chunk in stream:
            yield OpenAICallResponseChunk(
                chunk=chunk, tool_types=[fixture_my_openai_tool]
            )

    complete_tool = {
        "param": "param",
        "optional": 0,
    }
    incomplete_tool = {
        "param": "param",
        "optional": None,
    }

    def tool_assertions(tools):
        assert len(tools) == 7
        assert tools[0] is not None and tools[0].args == incomplete_tool
        assert tools[1] is not None and tools[1].args == complete_tool
        assert tools[2] is not None and tools[2].args == complete_tool
        assert tools[3] is None
        assert tools[4] is not None and tools[4].args == incomplete_tool
        assert tools[5] is not None and tools[5].args == complete_tool
        assert tools[6] is not None and tools[6].args == complete_tool

    tools = list(OpenAIToolStream.from_stream(generator(), allow_partial=True))
    tool_assertions(tools)

    stream = OpenAIStream(generator(), allow_partial=True)
    tools = [tool for _, tool in stream]
    tool_assertions(tools)
    assert stream.message_param == {
        "role": "assistant",
        "content": "",
        "tool_calls": [
            ChatCompletionMessageToolCall(
                id="id0",
                function=Function(
                    arguments='{\n "param": "param",\n "optional": 0\n}',
                    name="my_openai_tool",
                ),
                type="function",
            ),
            ChatCompletionMessageToolCall(
                id="id0",
                function=Function(
                    arguments='{\n "param": "param",\n "optional": 0\n}',
                    name="my_openai_tool",
                ),
                type="function",
            ),
        ],
    }
    assert stream.tool_message_params([(tools[0], "output")]) == [
        {
            "role": "tool",
            "content": "output",
            "tool_call_id": "id0",
            "name": "my_openai_tool",
        }
    ]


def test_openai_tool_stream_bad_tool_name(
    fixture_my_openai_tool: Type[OpenAITool],
    fixture_chat_completion_chunk_with_tools: ChatCompletionChunk,
) -> None:
    """Tests that a runtime error is thrown when a tool has a bad name."""

    def generator():
        chunk_copy = fixture_chat_completion_chunk_with_tools.model_copy()
        chunk_copy.choices[0].delta.tool_calls[0].function.name = "BadToolName"
        yield OpenAICallResponseChunk(
            chunk=chunk_copy, tool_types=[fixture_my_openai_tool]
        )

    with pytest.raises(RuntimeError):
        list(OpenAIToolStream.from_stream(generator(), allow_partial=True))


@pytest.mark.asyncio
async def test_openai_tool_stream_from_async_stream(
    fixture_my_openai_tool: Type[OpenAITool],
    fixture_chat_completion_chunks_with_tools: list[ChatCompletionChunk],
) -> None:
    """Tests streaming tools from chunks."""

    async def async_generator():
        stream = fixture_chat_completion_chunks_with_tools[:-1] * 2
        stream.append(fixture_chat_completion_chunks_with_tools[-1])
        for chunk in stream:
            yield OpenAICallResponseChunk(
                chunk=chunk, tool_types=[fixture_my_openai_tool]
            )

    def tool_assertions(tools):
        assert len(tools) == 7
        assert tools[0] is not None and tools[0].args == {
            "param": "param",
            "optional": None,
        }
        assert tools[1] is not None and tools[1].args == {
            "param": "param",
            "optional": 0,
        }
        assert tools[2] is not None and tools[2].args == {
            "param": "param",
            "optional": 0,
        }
        assert tools[3] is None
        assert tools[4] is not None and tools[4].args == {
            "param": "param",
            "optional": None,
        }
        assert tools[5] is not None and tools[5].args == {
            "param": "param",
            "optional": 0,
        }
        assert tools[6] is not None and tools[6].args == {
            "param": "param",
            "optional": 0,
        }

    tools = []
    async for tool in OpenAIToolStream.from_async_stream(
        async_generator(), allow_partial=True
    ):
        tools.append(tool)
    tool_assertions(tools)

    tools = []
    stream = OpenAIAsyncStream(async_generator(), allow_partial=True)
    async for _, tool in stream:
        tools.append(tool)
    tool_assertions(tools)
    assert stream.message_param == {
        "role": "assistant",
        "content": "",
        "tool_calls": [
            ChatCompletionMessageToolCall(
                id="id0",
                function=Function(
                    arguments='{\n "param": "param",\n "optional": 0\n}',
                    name="my_openai_tool",
                ),
                type="function",
            ),
            ChatCompletionMessageToolCall(
                id="id0",
                function=Function(
                    arguments='{\n "param": "param",\n "optional": 0\n}',
                    name="my_openai_tool",
                ),
                type="function",
            ),
        ],
    }
    assert stream.tool_message_params([(tools[0], "output")]) == [
        {
            "role": "tool",
            "content": "output",
            "tool_call_id": "id0",
            "name": "my_openai_tool",
        }
    ]


def test_openai_tool_stream_no_tool_types(
    fixture_chat_completion_chunk_with_tools: ChatCompletionChunk,
) -> None:
    """Tests that None is returned when chunk.tool_types is not set."""

    def generator() -> Generator[OpenAICallResponseChunk, None, None]:
        yield OpenAICallResponseChunk(
            chunk=fixture_chat_completion_chunk_with_tools,
            tool_types=None,
            response_format={"type": "json_object"},
        )

    tools = list(OpenAIToolStream.from_stream(generator(), allow_partial=True))
    assert len(tools) == 0
