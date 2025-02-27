"""Tests the `groq.call_response_chunk` module."""

from groq.types.chat import ChatCompletionChunk
from groq.types.chat.chat_completion_chunk import (
    Choice,
    ChoiceDelta,
    ChoiceDeltaToolCall,
    ChoiceDeltaToolCallFunction,
)
from groq.types.completion_usage import CompletionUsage

from mirascope.core.base.types import CostMetadata
from mirascope.core.groq.call_response_chunk import GroqCallResponseChunk


def test_groq_call_response_chunk() -> None:
    """Tests the `GroqCallResponseChunk` class."""
    tool_call = ChoiceDeltaToolCall(
        index=0,
        id="id",
        function=ChoiceDeltaToolCallFunction(
            arguments='{"key": "value"}', name="function"
        ),
        type="function",
    )
    choices = [
        Choice(
            delta=ChoiceDelta(content="content", tool_calls=[tool_call]),
            index=0,
            finish_reason="stop",
        )
    ]
    usage = CompletionUsage(completion_tokens=1, prompt_tokens=1, total_tokens=2)
    chunk = ChatCompletionChunk(
        id="id",
        choices=choices,
        created=0,
        model="llama3-70b-8192",
        object="chat.completion.chunk",
        usage=usage,
        x_groq=None,
    )
    call_response_chunk = GroqCallResponseChunk(chunk=chunk)
    assert call_response_chunk.content == "content"
    assert call_response_chunk.finish_reasons == ["stop"]
    assert call_response_chunk.model == "llama3-70b-8192"
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


def test_groq_call_response_chunk_no_choices_or_usage() -> None:
    """Tests the `GroqCallResponseChunk` class with None values."""
    chunk = ChatCompletionChunk(
        id="id",
        choices=[],
        created=0,
        model="llama3-70b-8192",
        object="chat.completion.chunk",
        usage=None,
        x_groq=None,
    )
    call_response_chunk = GroqCallResponseChunk(chunk=chunk)
    assert call_response_chunk.content == ""
    assert call_response_chunk.usage is None
    assert call_response_chunk.input_tokens is None
    assert call_response_chunk.output_tokens is None
    assert call_response_chunk.common_finish_reasons == []
