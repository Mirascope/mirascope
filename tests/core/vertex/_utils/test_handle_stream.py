"""Tests the `vertex._utils.handle_stream` module."""

import pytest
from vertexai.generative_models import (
    Candidate,
    Content,
    Part,
)
from vertexai.generative_models import (
    GenerationResponse as GenerateContentResponse,
)

from mirascope.core.vertex._utils._handle_stream import (
    handle_stream,
    handle_stream_async,
)


@pytest.fixture()
def mock_chunks() -> list[GenerateContentResponse]:
    """Returns a list of mock `GenerateContentResponse` instances."""
    return [
        GenerateContentResponse.from_dict(
            {
                "candidates": [
                    Candidate.from_dict(
                        {
                            "finish_reason": 1,
                            "content": Content(
                                parts=[Part.from_text("The author is ")],
                                role="model",
                            ).to_dict(),
                        }
                    ).to_dict()
                ]
            }
        ),
        GenerateContentResponse.from_dict(
            {
                "candidates": [
                    Candidate.from_dict(
                        {
                            "finish_reason": 1,
                            "content": Content(
                                parts=[Part.from_text("Patrick Rothfuss")], role="model"
                            ).to_dict(),
                        }
                    ).to_dict()
                ]
            }
        ),
    ]


def test_handle_stream(mock_chunks: list[GenerateContentResponse]) -> None:
    """Tests the `handle_stream` function."""
    result = list(handle_stream((chunk for chunk in mock_chunks), tool_types=None))
    assert len(result) == 2
    assert result[0][0].content == "The author is "
    assert result[0][1] is None
    assert result[1][0].content == "Patrick Rothfuss"
    assert result[1][1] is None


@pytest.mark.asyncio
async def test_handle_stream_async(
    mock_chunks: list[GenerateContentResponse],
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
