"""Tests the `mistral.call_response_chunk` module."""

from mistralai.models import (
    CompletionChunk,
    CompletionResponseStreamChoice,
    DeltaMessage,
    FunctionCall,
    ToolCall,
    UsageInfo,
)

from mirascope.core.base.types import CostMetadata
from mirascope.core.mistral.call_response_chunk import MistralCallResponseChunk


def test_mistral_call_response_chunk() -> None:
    """Tests the `MistralCallResponseChunk` class."""
    tool_call = ToolCall(
        id="id",
        function=FunctionCall(name="function", arguments='{"key": "value"}'),
        type="function",
    )
    choices = [
        CompletionResponseStreamChoice(
            index=0,
            delta=DeltaMessage(content="content", tool_calls=[tool_call]),
            finish_reason="stop",
        )
    ]
    usage = UsageInfo(prompt_tokens=1, completion_tokens=1, total_tokens=2)
    chunk = CompletionChunk(
        id="id",
        choices=choices,
        created=0,
        model="mistral-large-latest",
        object="",
        usage=usage,
    )
    call_response_chunk = MistralCallResponseChunk(chunk=chunk)
    assert call_response_chunk.content == "content"
    assert call_response_chunk.finish_reasons == ["stop"]
    assert call_response_chunk.model == "mistral-large-latest"
    assert call_response_chunk.id == "id"
    assert call_response_chunk.usage == usage
    assert call_response_chunk.input_tokens == 1
    assert call_response_chunk.output_tokens == 1
    assert call_response_chunk.common_finish_reasons == ["stop"]
    assert call_response_chunk.cost_metadata == CostMetadata(
        input_tokens=1,
        output_tokens=1,
        cached_tokens=0,
    )


def test_mistral_call_response_chunk_no_choices_or_usage() -> None:
    """Tests the `MistralCallResponseChunk` class with None values."""
    chunk = CompletionChunk(
        id="id",
        choices=[],
        created=0,
        model="mistral-large-latest",
        object="chat.completion.chunk",
        usage=None,
    )
    call_response_chunk = MistralCallResponseChunk(chunk=chunk)
    assert call_response_chunk.content == ""
    assert call_response_chunk.usage is None
    assert call_response_chunk.input_tokens is None
    assert call_response_chunk.output_tokens is None
    assert call_response_chunk.common_finish_reasons is None
