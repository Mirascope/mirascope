"""Tests the `vertex.call_response_chunk` module."""

from vertexai.generative_models import (
    Candidate,
    Content,
    FinishReason,
    Part,
)
from vertexai.generative_models import (
    GenerationResponse as GenerateContentResponse,
)

from mirascope.core.base.types import CostMetadata
from mirascope.core.vertex.call_response_chunk import VertexCallResponseChunk


def test_vertex_call_response_chunk() -> None:
    """Tests the `VertexCallResponseChunk` class."""
    chunk = GenerateContentResponse.from_dict(
        {
            "candidates": [
                Candidate.from_dict(
                    {
                        "finish_reason": 1,
                        "content": Content(
                            parts=[Part.from_text("The author is Patrick Rothfuss")],
                            role="model",
                        ).to_dict(),
                    }
                ).to_dict()
            ]
        }
    )
    call_response_chunk = VertexCallResponseChunk(chunk=chunk)
    assert call_response_chunk.content == "The author is Patrick Rothfuss"
    assert call_response_chunk.finish_reasons == [FinishReason.STOP]
    assert call_response_chunk.model is None
    assert call_response_chunk.id is None
    assert call_response_chunk.usage is None
    assert call_response_chunk.input_tokens is None
    assert call_response_chunk.output_tokens is None
    assert call_response_chunk.common_finish_reasons == ["stop"]
    assert call_response_chunk.cost_metadata == CostMetadata()
