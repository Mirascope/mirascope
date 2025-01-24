"""Tests the `gemini._utils.handle_stream` module."""

import pytest
from google.ai.generativelanguage import (
    Candidate,
    Content,
    GenerateContentResponse,
    Part,
)
from google.generativeai.types import (  # type: ignore
    GenerateContentResponse as GenerateContentResponseType,
)

from mirascope.core.gemini._utils._handle_stream import (
    handle_stream,
    handle_stream_async,
)


@pytest.fixture()
def mock_chunks() -> list[GenerateContentResponseType]:
    """Returns a list of mock `GenerateContentResponse` instances."""
    return [
        GenerateContentResponseType.from_response(
            GenerateContentResponse(
                candidates=[
                    Candidate(
                        finish_reason=1,
                        content=Content(
                            parts=[Part(text="The author is ")],
                            role="model",
                        ),
                    )
                ]
            )
        ),
        GenerateContentResponseType.from_response(
            GenerateContentResponse(
                candidates=[
                    Candidate(
                        finish_reason=1,
                        content=Content(
                            parts=[Part(text="Patrick Rothfuss")],
                            role="model",
                        ),
                    )
                ]
            )
        ),
    ]


def test_handle_stream(mock_chunks: list[GenerateContentResponseType]) -> None:
    """Tests the `handle_stream` function."""
    result = list(handle_stream((chunk for chunk in mock_chunks), tool_types=None))
    assert len(result) == 2
    assert result[0][0].content == "The author is "
    assert result[0][1] is None
    assert result[1][0].content == "Patrick Rothfuss"
    assert result[1][1] is None


@pytest.mark.asyncio
async def test_handle_stream_async(
    mock_chunks: list[GenerateContentResponseType],
) -> None:
    """Tests the `handle_stream_async` function."""
    result = []

    async def generator():
        for chunk in mock_chunks:
            yield chunk

    async for chunk, tool in handle_stream_async(generator(), tool_types=None):
        result.append((chunk, tool))

    assert len(result) == 2
    assert result[0][0].content == "The author is "
    assert result[0][1] is None
    assert result[1][0].content == "Patrick Rothfuss"
    assert result[1][1] is None
