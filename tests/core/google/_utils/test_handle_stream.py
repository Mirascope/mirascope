"""Tests the `google._utils.handle_stream` module."""

import pytest
from google.genai.types import (
    Candidate,
    Content,
    FunctionCall,
    GenerateContentResponse,
    Part,
)
from google.genai.types import (
    FinishReason as GoogleFinishReason,
)

from mirascope.core.google._utils._handle_stream import (
    handle_stream,
    handle_stream_async,
)
from mirascope.core.google.tool import GoogleTool


class FormatBook(GoogleTool):
    """Returns the title and author nicely formatted."""

    title: str
    author: str

    def call(self) -> None:
        """Dummy call."""


@pytest.fixture()
def mock_chunks() -> list[GenerateContentResponse]:
    """Returns a list of mock `GenerateContentResponse` instances."""
    return [
        GenerateContentResponse(
            candidates=[
                Candidate(
                    finish_reason=GoogleFinishReason.STOP,
                    content=Content(
                        parts=[Part(text="The author is ")],
                        role="model",
                    ),
                )
            ]
        ),
        GenerateContentResponse(
            candidates=[
                Candidate(
                    finish_reason=GoogleFinishReason.STOP,
                    content=Content(
                        parts=[Part(text="Patrick Rothfuss")],
                        role="model",
                    ),
                )
            ]
        ),
        GenerateContentResponse(
            candidates=[
                Candidate(
                    finish_reason=GoogleFinishReason.STOP,
                    content=Content(
                        parts=[
                            Part(
                                function_call=FunctionCall(
                                    name="FormatBook",
                                    args={
                                        "title": "The Name of the Wind",
                                        "author": "Patrick Rothfuss",
                                    },
                                )
                            )
                        ],
                        role="model",
                    ),
                )
            ]
        ),
        GenerateContentResponse(
            candidates=[
                Candidate(
                    finish_reason=GoogleFinishReason.STOP,
                    content=Content(
                        parts=[
                            Part(
                                function_call=FunctionCall(
                                    name="FormatBook",
                                    args={
                                        "title": "The Name of the Wind",
                                        "author": "Patrick Rothfuss",
                                    },
                                )
                            ),
                            Part(
                                function_call=FunctionCall(
                                    name="FormatBook",
                                    args={
                                        "title": "Mistborn: The Final Empire",
                                        "author": "Brandon Sanderson",
                                    },
                                )
                            ),
                        ],
                        role="model",
                    ),
                )
            ]
        ),
    ]


def test_handle_stream(mock_chunks: list[GenerateContentResponse]) -> None:
    """Tests the `handle_stream` function."""
    result = list(
        handle_stream((chunk for chunk in mock_chunks), tool_types=[FormatBook])
    )

    assert len(result) == 5
    assert result[0][0].content == "The author is "
    assert result[0][1] is None
    assert result[1][0].content == "Patrick Rothfuss"
    assert result[1][1] is None
    assert (tool := result[2][1]) is not None
    assert isinstance(tool, FormatBook)
    assert tool.model_dump(exclude={"tool_call", "delta"}) == {
        "author": "Patrick Rothfuss",
        "title": "The Name of the Wind",
    }
    assert (tool := result[3][1]) is not None
    assert isinstance(tool, FormatBook)
    assert tool.model_dump(exclude={"tool_call", "delta"}) == {
        "author": "Patrick Rothfuss",
        "title": "The Name of the Wind",
    }
    assert (tool := result[4][1]) is not None
    assert isinstance(tool, FormatBook)
    assert tool.model_dump(exclude={"tool_call", "delta"}) == {
        "author": "Brandon Sanderson",
        "title": "Mistborn: The Final Empire",
    }


@pytest.mark.asyncio
async def test_handle_stream_async(
    mock_chunks: list[GenerateContentResponse],
) -> None:
    """Tests the `handle_stream_async` function."""
    result = []

    async def generator():
        for chunk in mock_chunks:
            yield chunk

    async for chunk, tool in handle_stream_async(generator(), tool_types=[FormatBook]):
        result.append((chunk, tool))

    assert len(result) == 5
    assert result[0][0].content == "The author is "
    assert result[0][1] is None
    assert result[1][0].content == "Patrick Rothfuss"
    assert result[1][1] is None
    assert (tool := result[2][1]) is not None
    assert isinstance(tool, FormatBook)
    assert tool.model_dump(exclude={"tool_call", "delta"}) == {
        "author": "Patrick Rothfuss",
        "title": "The Name of the Wind",
    }
    assert (tool := result[3][1]) is not None
    assert isinstance(tool, FormatBook)
    assert tool.model_dump(exclude={"tool_call", "delta"}) == {
        "author": "Patrick Rothfuss",
        "title": "The Name of the Wind",
    }
    assert (tool := result[4][1]) is not None
    assert isinstance(tool, FormatBook)
    assert tool.model_dump(exclude={"tool_call", "delta"}) == {
        "author": "Brandon Sanderson",
        "title": "Mistborn: The Final Empire",
    }
