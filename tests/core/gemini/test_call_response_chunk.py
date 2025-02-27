"""Tests the `gemini.call_response_chunk` module."""

from google.ai.generativelanguage import (
    Candidate,
    Content,
    GenerateContentResponse,
    Part,
)
from google.generativeai.types import (  # type: ignore
    GenerateContentResponse as GenerateContentResponseType,
)

from mirascope.core.base.types import CostMetadata
from mirascope.core.gemini.call_response_chunk import GeminiCallResponseChunk


def test_gemini_call_response_chunk() -> None:
    """Tests the `GeminiCallResponseChunk` class."""
    chunk = GenerateContentResponseType.from_response(
        GenerateContentResponse(
            candidates=[
                Candidate(
                    finish_reason=1,
                    content=Content(
                        parts=[Part(text="The author is Patrick Rothfuss")],
                        role="model",
                    ),
                )
            ]
        )
    )
    call_response_chunk = GeminiCallResponseChunk(chunk=chunk)
    assert call_response_chunk.content == "The author is Patrick Rothfuss"
    assert call_response_chunk.finish_reasons == [Candidate.FinishReason.STOP]
    assert call_response_chunk.model is None
    assert call_response_chunk.id is None
    assert call_response_chunk.usage is None
    assert call_response_chunk.input_tokens is None
    assert call_response_chunk.output_tokens is None
    assert call_response_chunk.common_finish_reasons == ["stop"]
    assert call_response_chunk.cost_metadata == CostMetadata()
