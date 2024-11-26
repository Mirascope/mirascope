"""Tests the `mistral._utils.handle_stream` module."""

import pytest
from mistralai.models import (
    CompletionChunk,
    CompletionEvent,
    CompletionResponseStreamChoice,
    DeltaMessage,
    FunctionCall,
    ToolCall,
)

from mirascope.core.mistral._utils._handle_stream import (
    handle_stream,
    handle_stream_async,
)
from mirascope.core.mistral.tool import MistralTool


class FormatBook(MistralTool):
    """Returns the title and author nicely formatted."""

    title: str
    author: str

    def call(self) -> None:
        """Dummy call."""


@pytest.fixture()
def mock_chunks() -> list[CompletionChunk]:
    """Returns a list of mock `ChatCompletionStreamResponse` instances."""

    start_tool_call = ToolCall(
        id="call_id",
        function=FunctionCall(
            arguments="",
            name="FormatBook",
        ),
        type="function",
    )

    # Split the arguments into multiple chunks
    part1_tool_call = ToolCall(
        id="null",
        function=FunctionCall(
            arguments='{"title": "The Name',
            name="FormatBook",
        ),
        type="function",
    )

    part2_tool_call = ToolCall(
        id="null",
        function=FunctionCall(
            arguments=' of the Wind", "',
            name="FormatBook",
        ),
        type="function",
    )

    part3_tool_call = ToolCall(
        id="null",
        function=FunctionCall(
            arguments='author": "Patrick',
            name="FormatBook",
        ),
        type="function",
    )

    part4_tool_call = ToolCall(
        id="null",
        function=FunctionCall(
            arguments=' Rothfuss"}',
            name="FormatBook",
        ),
        type="function",
    )

    return [
        CompletionChunk(
            id="chunk_id",
            choices=[
                CompletionResponseStreamChoice(
                    index=0,
                    delta=DeltaMessage(
                        content=None,
                        tool_calls=[start_tool_call],
                    ),
                    finish_reason=None,
                )
            ],
            created=0,
            model="mistral-large-latest",
            object="chat.completion.chunk",
        ),
        CompletionChunk(
            id="chunk_id",
            choices=[
                CompletionResponseStreamChoice(
                    index=0,
                    delta=DeltaMessage(
                        content=None,
                        tool_calls=[part1_tool_call],
                    ),
                    finish_reason=None,
                )
            ],
            created=0,
            model="mistral-large-latest",
            object="chat.completion.chunk",
        ),
        CompletionChunk(
            id="chunk_id",
            choices=[
                CompletionResponseStreamChoice(
                    index=0,
                    delta=DeltaMessage(
                        content=None,
                        tool_calls=[part2_tool_call],
                    ),
                    finish_reason=None,
                )
            ],
            created=0,
            model="mistral-large-latest",
            object="chat.completion.chunk",
        ),
        CompletionChunk(
            id="chunk_id",
            choices=[
                CompletionResponseStreamChoice(
                    index=0,
                    delta=DeltaMessage(
                        content=None,
                        tool_calls=[part3_tool_call],
                    ),
                    finish_reason=None,
                )
            ],
            created=0,
            model="mistral-large-latest",
            object="chat.completion.chunk",
        ),
        CompletionChunk(
            id="chunk_id",
            choices=[
                CompletionResponseStreamChoice(
                    index=0,
                    delta=DeltaMessage(
                        content=None,
                        tool_calls=[part4_tool_call],
                    ),
                    finish_reason=None,
                )
            ],
            created=0,
            model="mistral-large-latest",
            object="chat.completion.chunk",
        ),
        CompletionChunk(
            id="chunk_id",
            choices=[
                CompletionResponseStreamChoice(
                    index=0,
                    delta=DeltaMessage(content=None, tool_calls=None),
                    finish_reason="tool_calls",
                )
            ],
            created=0,
            model="mistral-large-latest",
            object="chat.completion.chunk",
        ),
    ]


@pytest.fixture()
def mock_chunks_onetime_tools() -> list[CompletionChunk]:
    """Returns a list of mock `ChatCompletionStreamResponse` instances with partial tool calls."""
    start_tool_call = ToolCall(
        id="call_id",
        function=FunctionCall(
            arguments="",
            name="FormatBook",
        ),
        type="function",
    )

    # Split the arguments into multiple chunks
    part1_tool_call = ToolCall(
        id="null",
        function=FunctionCall(
            arguments='{"title": "The Name',
            name="FormatBook",
        ),
        type="function",
    )

    part2_tool_call = ToolCall(
        id="null",
        function=FunctionCall(
            arguments=' of the Wind", "',
            name="FormatBook",
        ),
        type="function",
    )

    part3_tool_call = ToolCall(
        id="null",
        function=FunctionCall(
            arguments='author": "Patrick',
            name="FormatBook",
        ),
        type="function",
    )

    part4_tool_call = ToolCall(
        id="null",
        function=FunctionCall(
            arguments=' Rothfuss"}',
            name="FormatBook",
        ),
        type="function",
    )

    return [
        CompletionChunk(
            id="id",
            choices=[
                CompletionResponseStreamChoice(
                    index=0,
                    delta=DeltaMessage(content="content", tool_calls=None),
                    finish_reason=None,
                )
            ],
            created=0,
            model="mistral-large-latest",
            object="chat.completion.chunk",
        ),
        CompletionChunk(
            id="id",
            choices=[
                CompletionResponseStreamChoice(
                    index=0,
                    delta=DeltaMessage(
                        content=None,
                        tool_calls=[start_tool_call],
                    ),
                    finish_reason=None,
                )
            ],
            created=0,
            model="mistral-large-latest",
            object="chat.completion.chunk",
        ),
        CompletionChunk(
            id="id",
            choices=[
                CompletionResponseStreamChoice(
                    index=0,
                    delta=DeltaMessage(
                        content=None,
                        tool_calls=[part1_tool_call],
                    ),
                    finish_reason=None,
                )
            ],
            created=0,
            model="mistral-large-latest",
            object="chat.completion.chunk",
        ),
        CompletionChunk(
            id="id",
            choices=[
                CompletionResponseStreamChoice(
                    index=0,
                    delta=DeltaMessage(
                        content=None,
                        tool_calls=[part2_tool_call],
                    ),
                    finish_reason=None,
                )
            ],
            created=0,
            model="mistral-large-latest",
            object="chat.completion.chunk",
        ),
        CompletionChunk(
            id="id",
            choices=[
                CompletionResponseStreamChoice(
                    index=0,
                    delta=DeltaMessage(
                        content=None,
                        tool_calls=[part3_tool_call],
                    ),
                    finish_reason=None,
                )
            ],
            created=0,
            model="mistral-large-latest",
            object="chat.completion.chunk",
        ),
        CompletionChunk(
            id="id",
            choices=[
                CompletionResponseStreamChoice(
                    index=0,
                    delta=DeltaMessage(
                        content=None,
                        tool_calls=[part4_tool_call],
                    ),
                    finish_reason=None,
                )
            ],
            created=0,
            model="mistral-large-latest",
            object="chat.completion.chunk",
        ),
        CompletionChunk(
            id="id",
            choices=[
                CompletionResponseStreamChoice(
                    index=0,
                    delta=DeltaMessage(content=None, tool_calls=None),
                    finish_reason="tool_calls",
                )
            ],
            created=0,
            model="mistral-large-latest",
            object="chat.completion.chunk",
        ),
    ]


def test_handle_stream(mock_chunks: list[CompletionChunk]) -> None:
    """Tests the `handle_stream` function."""

    result = list(
        handle_stream(
            (CompletionEvent(data=c) for c in mock_chunks), tool_types=[FormatBook]
        )
    )
    # Check we get three tuples back.
    # (chunk, None), (chunk, FormatBook), (chunk, FormatBook)
    assert len(result) == 3
    assert result[0][1] is None
    assert (
        (tool := result[1][1]) is not None
        and isinstance(tool, FormatBook)
        and tool.model_dump(exclude={"tool_call"})
        == {"title": "The Name of the Wind", "author": "Patrick Rothfuss"}
    )
    assert (
        (tool := result[2][1]) is not None
        and isinstance(tool, FormatBook)
        and tool.model_dump(exclude={"tool_call"})
        == {"title": "The Name of the Wind", "author": "Patrick Rothfuss"}
    )


@pytest.mark.asyncio
async def test_handle_stream_async(
    mock_chunks: list[CompletionChunk],
) -> None:
    """Tests the `handle_stream_async` function."""

    async def generator():
        for chunk in mock_chunks:
            yield CompletionEvent(data=chunk)

    result = []
    async for t in handle_stream_async(generator(), tool_types=[FormatBook]):
        result.append(t)
    # Check we get three tuples back.
    # (chunk, None), (chunk, FormatBook), (chunk, FormatBook)
    assert len(result) == 3
    assert result[0][1] is None
    assert (
        (tool := result[1][1]) is not None
        and isinstance(tool, FormatBook)
        and tool.model_dump(exclude={"tool_call"})
        == {"title": "The Name of the Wind", "author": "Patrick Rothfuss"}
    )
    assert (
        (tool := result[2][1]) is not None
        and isinstance(tool, FormatBook)
        and tool.model_dump(exclude={"tool_call"})
        == {"title": "The Name of the Wind", "author": "Patrick Rothfuss"}
    )


def test_handle_stream_onetime_tools(mock_chunks_onetime_tools) -> None:
    """Tests the `handle_stream` function."""

    result = list(
        handle_stream(
            (CompletionEvent(data=c) for c in mock_chunks_onetime_tools),
            tool_types=[FormatBook],
            allow_partial_tool=True,
        )
    )
    # Check we get three tuples back.
    # (chunk, None), (chunk, FormatBook), (chunk, FormatBook)
    assert len(result) == 5
    assert result[0][1] is None
    assert (
        (tool := result[1][1]) is not None
        and isinstance(tool, FormatBook)
        and tool.model_dump(exclude={"tool_call"})
        == {"title": "The Name of the Wind", "author": "Patrick Rothfuss"}
    )


@pytest.mark.asyncio
async def test_handle_stream_async_onetime_tools(
    mock_chunks_onetime_tools,
) -> None:
    """Tests the `handle_stream_async` function."""

    async def generator():
        for chunk in mock_chunks_onetime_tools:
            yield CompletionEvent(data=chunk)

    result = []
    async for t in handle_stream_async(generator(), tool_types=[FormatBook]):
        result.append(t)
    # Check we get three tuples back.
    # (chunk, None), (chunk, FormatBook), (chunk, FormatBook)
    assert len(result) == 2
    assert result[0][1] is None
    assert (
        (tool := result[1][1]) is not None
        and isinstance(tool, FormatBook)
        and tool.model_dump(exclude={"tool_call"})
        == {"title": "The Name of the Wind", "author": "Patrick Rothfuss"}
    )


def test_handle_stream_with_partial_tools(mock_chunks: list[CompletionChunk]) -> None:
    """Tests the `handle_stream` function with partial tools enabled."""
    result = list(
        handle_stream(
            (CompletionEvent(data=c) for c in mock_chunks),
            tool_types=[FormatBook],
            allow_partial_tool=True,
        )
    )

    assert len(result) == 5

    # First partial response
    assert (
        (tool := result[0][1]) is not None
        and isinstance(tool, FormatBook)
        and tool.delta == '{"title": "The Name'
    )

    # Second partial response
    assert (
        (tool := result[1][1]) is not None
        and isinstance(tool, FormatBook)
        and tool.delta == ' of the Wind", "'
    )

    # Third partial response
    assert (
        (tool := result[2][1]) is not None
        and isinstance(tool, FormatBook)
        and tool.delta == 'author": "Patrick'
    )

    # Forth partial response
    assert (
        (tool := result[3][1]) is not None
        and isinstance(tool, FormatBook)
        and tool.delta == ' Rothfuss"}'
    )

    # Final complete tool
    assert (
        (tool := result[4][1]) is not None
        and isinstance(tool, FormatBook)
        and tool.model_dump(exclude={"tool_call"})
        == {"title": "The Name of the Wind", "author": "Patrick Rothfuss"}
        and tool.delta is None
    )


@pytest.mark.asyncio
async def test_handle_stream_async_with_partial_tools(
    mock_chunks: list[CompletionChunk],
) -> None:
    """Tests the `handle_stream_async` function with partial tools enabled."""

    async def generator():
        for chunk in mock_chunks:
            yield CompletionEvent(data=chunk)

    result = []
    async for t in handle_stream_async(
        generator(), tool_types=[FormatBook], allow_partial_tool=True
    ):
        result.append(t)

    assert len(result) == 5

    # First partial response
    assert (
        (tool := result[0][1]) is not None
        and isinstance(tool, FormatBook)
        and tool.delta == '{"title": "The Name'
    )

    # Second partial response
    assert (
        (tool := result[1][1]) is not None
        and isinstance(tool, FormatBook)
        and tool.delta == ' of the Wind", "'
    )

    # Third partial response
    assert (
        (tool := result[2][1]) is not None
        and isinstance(tool, FormatBook)
        and tool.delta == 'author": "Patrick'
    )

    # Forth partial response
    assert (
        (tool := result[3][1]) is not None
        and isinstance(tool, FormatBook)
        and tool.delta == ' Rothfuss"}'
    )

    # Final complete tool
    assert (
        (tool := result[4][1]) is not None
        and isinstance(tool, FormatBook)
        and tool.model_dump(exclude={"tool_call"})
        == {"title": "The Name of the Wind", "author": "Patrick Rothfuss"}
        and tool.delta is None
    )


def test_handle_stream_with_partial_tools_onetime(
    mock_chunks_onetime_tools: list[CompletionChunk],
) -> None:
    """Tests the `handle_stream` function with partial tools enabled for onetime tool calls."""
    result = list(
        handle_stream(
            (CompletionEvent(data=c) for c in mock_chunks_onetime_tools),
            tool_types=[FormatBook],
            allow_partial_tool=True,
        )
    )

    assert len(result) == 6
    assert result[0][1] is None

    # First part
    assert (
        (tool := result[1][1]) is not None
        and isinstance(tool, FormatBook)
        and tool.delta == '{"title": "The Name'
    )

    # Second part
    assert (
        (tool := result[2][1]) is not None
        and isinstance(tool, FormatBook)
        and tool.delta == ' of the Wind", "'
    )

    # Third part
    assert (
        (tool := result[3][1]) is not None
        and isinstance(tool, FormatBook)
        and tool.delta == 'author": "Patrick'
    )

    # Fourth part
    assert (
        (tool := result[4][1]) is not None
        and isinstance(tool, FormatBook)
        and tool.delta == ' Rothfuss"}'
    )

    # Final complete tool
    assert (
        (tool := result[5][1]) is not None
        and isinstance(tool, FormatBook)
        and tool.model_dump(exclude={"tool_call"})
        == {"title": "The Name of the Wind", "author": "Patrick Rothfuss"}
    )


@pytest.mark.asyncio
async def test_handle_stream_async_with_partial_tools_onetime(
    mock_chunks_onetime_tools: list[CompletionChunk],
) -> None:
    """Tests the `handle_stream_async` function with partial tools enabled for onetime tool calls."""

    async def generator():
        for chunk in mock_chunks_onetime_tools:
            yield CompletionEvent(data=chunk)

    result = []
    async for t in handle_stream_async(
        generator(), tool_types=[FormatBook], allow_partial_tool=True
    ):
        result.append(t)

    assert len(result) == 6
    assert result[0][1] is None

    # First part
    assert (
        (tool := result[1][1]) is not None
        and isinstance(tool, FormatBook)
        and tool.delta == '{"title": "The Name'
    )

    # Second part
    assert (
        (tool := result[2][1]) is not None
        and isinstance(tool, FormatBook)
        and tool.delta == ' of the Wind", "'
    )

    # Third part
    assert (
        (tool := result[3][1]) is not None
        and isinstance(tool, FormatBook)
        and tool.delta == 'author": "Patrick'
    )

    # Fourth part
    assert (
        (tool := result[4][1]) is not None
        and isinstance(tool, FormatBook)
        and tool.delta == ' Rothfuss"}'
    )

    # Final complete tool
    assert (
        (tool := result[5][1]) is not None
        and isinstance(tool, FormatBook)
        and tool.model_dump(exclude={"tool_call"})
        == {"title": "The Name of the Wind", "author": "Patrick Rothfuss"}
    )
