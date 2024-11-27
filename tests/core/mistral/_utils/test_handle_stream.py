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

    new_tool_call = ToolCall(
        id="id",
        function=FunctionCall(
            arguments="",
            name="FormatBook",
        ),
        type="function",
    )
    tool_call = ToolCall(
        id="null",
        function=FunctionCall(
            arguments='{"title": "The Name of the Wind", "author": "Patrick Rothfuss"}',
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
                        tool_calls=[new_tool_call],
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
                        tool_calls=[tool_call],
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
                        tool_calls=[new_tool_call],
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
                        tool_calls=[tool_call],
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


@pytest.fixture()
def mock_chunks_onetime_tools() -> list[CompletionChunk]:
    """Returns a list of mock `ChatCompletionStreamResponse` instances."""

    tool_call = ToolCall(
        id="id",
        function=FunctionCall(
            arguments='{"title": "The Name of the Wind", "author": "Patrick Rothfuss"}',
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
                        tool_calls=[tool_call],
                    ),
                    finish_reason=None,
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
        and tool.model_dump(exclude={"tool_call", "delta"})
        == {"title": "The Name of the Wind", "author": "Patrick Rothfuss"}
    )
    assert (
        (tool := result[2][1]) is not None
        and isinstance(tool, FormatBook)
        and tool.model_dump(exclude={"tool_call", "delta"})
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
        and tool.model_dump(exclude={"tool_call", "delta"})
        == {"title": "The Name of the Wind", "author": "Patrick Rothfuss"}
    )
    assert (
        (tool := result[2][1]) is not None
        and isinstance(tool, FormatBook)
        and tool.model_dump(exclude={"tool_call", "delta"})
        == {"title": "The Name of the Wind", "author": "Patrick Rothfuss"}
    )


def test_handle_stream_onetime_tools(mock_chunks_onetime_tools) -> None:
    """Tests the `handle_stream` function."""

    result = list(
        handle_stream(
            (CompletionEvent(data=c) for c in mock_chunks_onetime_tools),
            tool_types=[FormatBook],
        )
    )
    # Check we get three tuples back.
    # (chunk, None), (chunk, FormatBook), (chunk, FormatBook)
    assert len(result) == 2
    assert result[0][1] is None
    assert (
        (tool := result[1][1]) is not None
        and isinstance(tool, FormatBook)
        and tool.model_dump(exclude={"tool_call", "delta"})
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
        and tool.model_dump(exclude={"tool_call", "delta"})
        == {"title": "The Name of the Wind", "author": "Patrick Rothfuss"}
    )
