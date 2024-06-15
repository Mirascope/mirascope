"""Tests for Mirascope's Anthropic types module."""

from typing import Type

import pytest
from anthropic.lib.streaming import ContentBlockStopEvent
from anthropic.types import (
    ContentBlockDeltaEvent,
    ContentBlockStartEvent,
    Message,
    MessageStartEvent,
    TextBlock,
    Usage,
)

from mirascope.anthropic.tools import AnthropicTool
from mirascope.anthropic.types import (
    AnthropicAsyncStream,
    AnthropicCallResponse,
    AnthropicCallResponseChunk,
    AnthropicStream,
    AnthropicToolStream,
)


def test_anthropic_call_response(fixture_anthropic_message: Message):
    """Tests the `AnthropicCallResponse` class."""
    response = AnthropicCallResponse(
        response=fixture_anthropic_message, start_time=0, end_time=1
    )
    assert response.content == "test"
    assert response.message_param == {
        "content": [{"text": "test", "type": "text"}],
        "role": "assistant",
    }
    assert response.tools is None
    assert response.tool is None
    assert response.usage is not None
    assert response.output_tokens is not None
    assert response.input_tokens is not None
    assert response.model == fixture_anthropic_message.model
    assert response.id == fixture_anthropic_message.id
    assert response.finish_reasons == [fixture_anthropic_message.stop_reason]
    assert response.dump() == {
        "start_time": 0,
        "end_time": 1,
        "output": fixture_anthropic_message.model_dump(),
    }


def test_anthropic_call_response_json_mode_tool(
    fixture_anthropic_message_with_json_tool: Message,
    fixture_anthropic_book_tool: type[AnthropicTool],
):
    """Tests the `AnthropicCallResponse` class with a json mode tool."""
    response = AnthropicCallResponse(
        response=fixture_anthropic_message_with_json_tool,
        response_format="json",
        start_time=0,
        end_time=0,
        tool_types=[fixture_anthropic_book_tool],
    )
    assert response.tools is not None
    assert response.tools[0].args == {
        "title": "The Name of the Wind",
        "author": "Patrick Rothfuss",
    }
    output = "The Name of the Wind by Patrick Rothfuss"
    assert response.tool_message_params([(response.tools[0], output)]) == [
        {
            "role": "user",
            "content": [
                {
                    "tool_use_id": "id",
                    "type": "tool_result",
                    "content": [{"text": output, "type": "text"}],
                }
            ],
        }
    ]


def test_anthropic_call_response_with_tools_bad_stop_reason(
    fixture_anthropic_message_with_tools_bad_stop_reason: Message,
    fixture_anthropic_book_tool: Type[AnthropicTool],
):
    """Tests the `AnthropicCallResponse` class with a tool and bad stop reason."""
    response = AnthropicCallResponse(
        response=fixture_anthropic_message_with_tools_bad_stop_reason,
        tool_types=[fixture_anthropic_book_tool],
        start_time=0,
        end_time=1,
    )
    with pytest.raises(RuntimeError):
        response.tool


def test_anthropic_call_response_chunk(
    fixture_anthropic_message_chunk: ContentBlockDeltaEvent,
):
    """Tests the `AnthropicCallResponseChunk` class."""
    chunk = AnthropicCallResponseChunk(chunk=fixture_anthropic_message_chunk)
    assert chunk.content == "test"

    chunk = AnthropicCallResponseChunk(
        chunk=ContentBlockStartEvent(
            content_block=TextBlock(text="test_start", type="text"),
            index=0,
            type="content_block_start",
        )
    )
    assert chunk.content == "test_start"
    assert chunk.type == "content_block_start"

    chunk = AnthropicCallResponseChunk(
        chunk=ContentBlockStopEvent(
            index=2,
            type="content_block_stop",
            content_block=TextBlock(text="", type="text"),
        )
    )
    assert chunk.content == ""
    assert chunk.type == "content_block_stop"

    chunk = AnthropicCallResponseChunk(
        chunk=MessageStartEvent(
            message=Message(
                id="test_id",
                model="test_model",
                role="assistant",
                type="message",
                content=[TextBlock(text="test", type="text")],
                stop_reason="end_turn",
                usage=Usage(input_tokens=1, output_tokens=1),
            ),
            type="message_start",
        )
    )
    assert chunk.usage is not None
    assert chunk.output_tokens == 1
    assert chunk.input_tokens == 1
    assert chunk.model == "test_model"
    assert chunk.id == "test_id"
    assert chunk.finish_reasons == ["end_turn"]


def test_anthropic_tool_stream_from_stream(
    fixture_anthropic_call_response_chunks_with_tools: list[AnthropicCallResponseChunk],
) -> None:
    """Tests streaming tools from chunks."""

    def generator():
        for chunk in fixture_anthropic_call_response_chunks_with_tools:
            yield chunk

    def tool_assertions(tools):
        assert len(tools) == 7
        assert tools[0] is not None and tools[0].args == {
            "title": "The Name of the Wind",
            "author": None,
        }
        assert tools[1] is not None and tools[1].args == {
            "title": "The Name of the Wind",
            "author": "Patrick Rothfuss",
        }
        assert tools[2] is not None and tools[2].args == {
            "title": "The Name of the Wind",
            "author": "Patrick Rothfuss",
        }
        assert tools[3] is None
        assert tools[4] is not None and tools[4].args == {
            "title": "The Name of the Wind",
            "author": None,
        }
        assert tools[5] is not None and tools[5].args == {
            "title": "The Name of the Wind",
            "author": "Patrick Rothfuss",
        }
        assert tools[6] is not None and tools[6].args == {
            "title": "The Name of the Wind",
            "author": "Patrick Rothfuss",
        }

    tools = list(AnthropicToolStream.from_stream(generator(), allow_partial=True))
    tool_assertions(tools)

    tools = list(AnthropicToolStream.from_stream(generator(), allow_partial=False))
    assert len(tools) == 2

    tools = [tool for _, tool in AnthropicStream(generator(), allow_partial=True)]
    tool_assertions(tools[1:])

    stream = AnthropicStream(generator())
    tools = [tool for _, tool in stream]
    assert len(tools[1:]) == 2
    assert stream.message_param == {
        "role": "assistant",
        "content": [
            {
                "id": "test_id",
                "type": "tool_use",
                "name": "AnthropicBookTool",
                "input": {
                    "title": "The Name of the Wind",
                    "author": "Patrick Rothfuss",
                },
            },
            {
                "id": "test_id",
                "type": "tool_use",
                "name": "AnthropicBookTool",
                "input": {
                    "title": "The Name of the Wind",
                    "author": "Patrick Rothfuss",
                },
            },
        ],
    }
    tool = tools[-1]
    assert tool is not None
    assert stream.tool_message_params([(tool, "output")]) == [
        {
            "role": "user",
            "content": [
                {
                    "tool_use_id": "test_id",
                    "content": [{"text": "output", "type": "text"}],
                    "type": "tool_result",
                }
            ],
        }
    ]


def test_anthropic_tool_stream_bad_tool_name(
    fixture_anthropic_call_response_chunk_with_bad_tool: AnthropicCallResponseChunk,
) -> None:
    """Tests that a runtime error is thrown when a tool has a bad name."""

    def generator_partial():
        yield fixture_anthropic_call_response_chunk_with_bad_tool

    with pytest.raises(RuntimeError):
        list(AnthropicToolStream.from_stream(generator_partial(), allow_partial=True))

    def generator():
        yield fixture_anthropic_call_response_chunk_with_bad_tool

    with pytest.raises(RuntimeError):
        list(AnthropicToolStream.from_stream(generator(), allow_partial=False))


def test_anthropic_tool_stream_missing_tool_name(
    fixture_anthropic_call_response_chunk_with_bad_tool: AnthropicCallResponseChunk,
) -> None:
    """Tests that a runtime error is thrown when a tool has a bad name."""

    def generator():
        yield fixture_anthropic_call_response_chunk_with_bad_tool

    with pytest.raises(RuntimeError):
        list(AnthropicToolStream.from_stream(generator()))


def test_anthropic_tool_stream_no_tool_types(
    fixture_anthropic_call_response_chunks_with_tools: list[AnthropicCallResponseChunk],
) -> None:
    """Tests a runtime error is thrown when not using json mode for a tool stream."""

    def generator():
        for chunk in fixture_anthropic_call_response_chunks_with_tools:
            chunk.tool_types = None
            yield chunk

    tools = list(AnthropicToolStream.from_stream(generator()))
    assert len(tools) == 0


@pytest.mark.asyncio
async def test_anthropic_tool_stream_from_async_stream(
    fixture_anthropic_call_response_chunks_with_tools: list[AnthropicCallResponseChunk],
) -> None:
    """Tests streaming tools from chunks."""

    async def generator():
        for chunk in fixture_anthropic_call_response_chunks_with_tools:
            yield chunk

    def tool_assertions(tools):
        assert len(tools) == 7
        assert tools[0] is not None and tools[0].args == {
            "title": "The Name of the Wind",
            "author": None,
        }
        assert tools[1] is not None and tools[1].args == {
            "title": "The Name of the Wind",
            "author": "Patrick Rothfuss",
        }
        assert tools[2] is not None and tools[2].args == {
            "title": "The Name of the Wind",
            "author": "Patrick Rothfuss",
        }
        assert tools[3] is None
        assert tools[4] is not None and tools[4].args == {
            "title": "The Name of the Wind",
            "author": None,
        }
        assert tools[5] is not None and tools[5].args == {
            "title": "The Name of the Wind",
            "author": "Patrick Rothfuss",
        }
        assert tools[6] is not None and tools[6].args == {
            "title": "The Name of the Wind",
            "author": "Patrick Rothfuss",
        }

    tools = [
        tool
        async for tool in AnthropicToolStream.from_async_stream(
            generator(), allow_partial=True
        )
    ]
    tool_assertions(tools)

    stream = AnthropicAsyncStream(generator(), allow_partial=True)
    tools = [tool async for _, tool in stream]
    tool_assertions(tools[1:])
    assert stream.message_param == {
        "role": "assistant",
        "content": [
            {
                "id": "test_id",
                "type": "tool_use",
                "name": "AnthropicBookTool",
                "input": {
                    "title": "The Name of the Wind",
                    "author": "Patrick Rothfuss",
                },
            },
            {
                "id": "test_id",
                "type": "tool_use",
                "name": "AnthropicBookTool",
                "input": {
                    "title": "The Name of the Wind",
                    "author": "Patrick Rothfuss",
                },
            },
        ],
    }
    tool = tools[-1]
    assert tool is not None
    assert stream.tool_message_params([(tool, "output")]) == [
        {
            "role": "user",
            "content": [
                {
                    "tool_use_id": "test_id",
                    "content": [{"text": "output", "type": "text"}],
                    "type": "tool_result",
                }
            ],
        }
    ]
