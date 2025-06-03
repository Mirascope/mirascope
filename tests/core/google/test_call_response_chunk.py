"""Tests the `google.call_response_chunk` module."""

from google.genai.types import (
    Candidate,
    Content,
    GenerateContentResponse,
    Part,
)
from google.genai.types import (
    FinishReason as GoogleFinishReason,
)

from mirascope.core.base.types import CostMetadata
from mirascope.core.google.call_response_chunk import GoogleCallResponseChunk


def test_google_call_response_chunk() -> None:
    """Tests the `GoogleCallResponseChunk` class."""
    chunk = GenerateContentResponse(
        candidates=[
            Candidate(
                finish_reason=GoogleFinishReason.STOP,
                content=Content(
                    parts=[Part(text="The author is Patrick Rothfuss")],
                    role="model",
                ),
            )
        ]
    )

    call_response_chunk = GoogleCallResponseChunk(chunk=chunk)
    assert call_response_chunk.content == "The author is Patrick Rothfuss"
    assert call_response_chunk.finish_reasons == [GoogleFinishReason.STOP]
    assert call_response_chunk.model is None
    assert call_response_chunk.id is None
    assert call_response_chunk.usage is None
    assert call_response_chunk.input_tokens is None
    assert call_response_chunk.output_tokens is None
    assert call_response_chunk.common_finish_reasons == ["stop"]
    assert call_response_chunk.cost_metadata == CostMetadata()

    call_response_chunk_no_candidates = GoogleCallResponseChunk(
        chunk=GenerateContentResponse(candidates=[])
    )
    assert call_response_chunk_no_candidates.content == ""


def test_google_call_response_chunk_thinking() -> None:
    """Tests the `GoogleCallResponseChunk` class with thinking parts."""
    # Test thinking part chunk
    thinking_chunk = GenerateContentResponse(
        candidates=[
            Candidate(
                finish_reason=GoogleFinishReason.STOP,
                content=Content(
                    parts=[
                        Part(text="Let me think about this problem...", thought=True)
                    ],
                    role="model",
                ),
            )
        ]
    )
    call_response_chunk = GoogleCallResponseChunk(chunk=thinking_chunk)
    assert call_response_chunk.thinking == "Let me think about this problem..."
    assert call_response_chunk.content == ""

    # Test regular text part chunk (should have empty thinking)
    text_chunk = GenerateContentResponse(
        candidates=[
            Candidate(
                finish_reason=GoogleFinishReason.STOP,
                content=Content(
                    parts=[Part(text="The answer is 42")],
                    role="model",
                ),
            )
        ]
    )
    call_response_chunk_text = GoogleCallResponseChunk(chunk=text_chunk)
    assert call_response_chunk_text.thinking == ""
    assert call_response_chunk_text.content == "The answer is 42"

    # Test mixed parts (thinking + text)
    mixed_chunk = GenerateContentResponse(
        candidates=[
            Candidate(
                finish_reason=GoogleFinishReason.STOP,
                content=Content(
                    parts=[
                        Part(text="First I need to think...", thought=True),
                        Part(text="The final answer"),
                    ],
                    role="model",
                ),
            )
        ]
    )
    call_response_chunk_mixed = GoogleCallResponseChunk(chunk=mixed_chunk)
    assert call_response_chunk_mixed.thinking == "First I need to think..."
    assert call_response_chunk_mixed.content == "The final answer"

    # Test chunk with no candidates
    empty_chunk = GenerateContentResponse(candidates=[])
    call_response_chunk_empty = GoogleCallResponseChunk(chunk=empty_chunk)
    assert call_response_chunk_empty.thinking == ""
    assert call_response_chunk_empty.content == ""
