"""Tests the `anthropic.call_response_chunk` module."""

from anthropic.types import (
    Message,
    RawContentBlockDeltaEvent,
    RawMessageStartEvent,
    TextBlock,
    TextDelta,
    Usage,
)

from mirascope.core.anthropic.call_response_chunk import AnthropicCallResponseChunk
from mirascope.core.base.types import CostMetadata


def test_anthropic_call_response_chunk() -> None:
    """Tests the `AnthropicCallResponseChunk` class."""
    usage = Usage(input_tokens=1, output_tokens=1)
    chunks = [
        RawMessageStartEvent(
            message=Message(
                id="id",
                content=[TextBlock(text="content", type="text")],
                model="claude-3-5-sonnet-20240620",
                role="assistant",
                stop_reason="end_turn",
                stop_sequence=None,
                type="message",
                usage=usage,
            ),
            type="message_start",
        ),
        RawContentBlockDeltaEvent(
            index=0,
            delta=TextDelta(text="content", type="text_delta"),
            type="content_block_delta",
        ),
    ]
    call_response_chunk_0 = AnthropicCallResponseChunk(chunk=chunks[0])
    call_response_chunk_1 = AnthropicCallResponseChunk(chunk=chunks[1])
    assert call_response_chunk_0.finish_reasons == ["end_turn"]
    assert call_response_chunk_0.model == "claude-3-5-sonnet-20240620"
    assert call_response_chunk_0.id == "id"
    assert call_response_chunk_0.usage == usage
    assert call_response_chunk_0.input_tokens == 1
    assert call_response_chunk_0.output_tokens == 1
    assert call_response_chunk_1.content == "content"
    assert call_response_chunk_1.finish_reasons is None
    assert call_response_chunk_1.model is None
    assert call_response_chunk_1.id is None
    assert call_response_chunk_1.usage is None
    assert call_response_chunk_1.input_tokens is None
    assert call_response_chunk_1.output_tokens is None
    assert call_response_chunk_1.common_finish_reasons is None
    assert call_response_chunk_1.cost_metadata == CostMetadata()
