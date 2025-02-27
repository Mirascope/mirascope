"""Tests the `cohere.call_response_chunk` module."""

from cohere.types import (
    ApiMeta,
    ApiMetaBilledUnits,
    NonStreamedChatResponse,
    StreamEndStreamedChatResponse,
    StreamStartStreamedChatResponse,
    TextGenerationStreamedChatResponse,
)

from mirascope.core.base.types import CostMetadata
from mirascope.core.cohere.call_response_chunk import CohereCallResponseChunk


def test_cohere_call_response_chunk() -> None:
    """Tests the `CohereCallResponseChunk` class."""
    usage = ApiMetaBilledUnits(input_tokens=1, output_tokens=1)
    chunk_start = StreamStartStreamedChatResponse(generation_id="id")
    chunk = TextGenerationStreamedChatResponse(
        text="content",
    )
    chunk_finish = StreamEndStreamedChatResponse(
        finish_reason="COMPLETE",
        response=NonStreamedChatResponse(
            generation_id="id",
            text="content",
            meta=ApiMeta(billed_units=usage),
        ),
    )
    call_response_chunk_start = CohereCallResponseChunk(chunk=chunk_start)
    call_response_chunk = CohereCallResponseChunk(chunk=chunk)
    call_response_chunk_finish = CohereCallResponseChunk(chunk=chunk_finish)
    assert call_response_chunk_start.id == "id"
    assert call_response_chunk.content == "content"
    assert call_response_chunk.finish_reasons is None
    assert call_response_chunk.model is None
    assert call_response_chunk.id is None
    assert call_response_chunk.usage is None
    assert call_response_chunk.input_tokens is None
    assert call_response_chunk.output_tokens is None
    assert call_response_chunk_finish.content == ""
    assert call_response_chunk_finish.id == "id"
    assert call_response_chunk_finish.usage == usage
    assert call_response_chunk_finish.input_tokens == 1
    assert call_response_chunk_finish.output_tokens == 1
    assert call_response_chunk_finish.finish_reasons == ["COMPLETE"]
    assert call_response_chunk_finish.common_finish_reasons == ["stop"]
    assert call_response_chunk_finish.cost_metadata == CostMetadata(
        input_tokens=1.0, output_tokens=1.0
    )
