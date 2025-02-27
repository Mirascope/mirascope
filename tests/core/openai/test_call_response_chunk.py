"""Tests the `openai.call_response_chunk` module."""

import base64

from openai.types.chat import ChatCompletionChunk
from openai.types.chat.chat_completion_chunk import (
    Choice,
    ChoiceDelta,
    ChoiceDeltaToolCall,
    ChoiceDeltaToolCallFunction,
)
from openai.types.completion_usage import CompletionUsage

from mirascope.core.base.types import CostMetadata
from mirascope.core.openai.call_response_chunk import OpenAICallResponseChunk


def test_openai_call_response_chunk() -> None:
    """Tests the `OpenAICallResponseChunk` class."""
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
        model="gpt-4o",
        object="chat.completion.chunk",
        usage=usage,
    )
    call_response_chunk = OpenAICallResponseChunk(chunk=chunk)
    assert call_response_chunk.content == "content"
    assert call_response_chunk.finish_reasons == ["stop"]
    assert call_response_chunk.model == "gpt-4o"
    assert call_response_chunk.id == "id"
    assert call_response_chunk.usage == usage
    assert call_response_chunk.input_tokens == 1
    assert call_response_chunk.output_tokens == 1
    assert call_response_chunk.common_finish_reasons == ["stop"]
    assert call_response_chunk.cost_metadata == CostMetadata(
        input_tokens=1,
        output_tokens=1,
    )


def test_openai_call_response_chunk_no_choices_or_usage() -> None:
    """Tests the `OpenAICallResponseChunk` class with None values."""
    chunk = ChatCompletionChunk(
        id="id",
        choices=[],
        created=0,
        model="gpt-4o",
        object="chat.completion.chunk",
        usage=None,
    )
    call_response_chunk = OpenAICallResponseChunk(chunk=chunk)
    assert call_response_chunk.content == ""
    assert call_response_chunk.usage is None
    assert call_response_chunk.input_tokens is None
    assert call_response_chunk.output_tokens is None
    assert call_response_chunk.common_finish_reasons == []


def test_openai_call_response_chunk_with_audio() -> None:
    """Tests the `OpenAICallResponseChunk` class with audio content."""
    audio_data = b"test audio data"
    audio_base64 = base64.b64encode(audio_data).decode()
    transcript = "This is a test transcript"

    choices = [
        Choice(
            delta=ChoiceDelta(
                content="content",
                audio={"data": audio_base64, "transcript": transcript},  # pyright: ignore [reportCallIssue]
            ),
            index=0,
            finish_reason="stop",
        )
    ]
    chunk = ChatCompletionChunk(
        id="id",
        choices=choices,
        created=0,
        model="gpt-4o",
        object="chat.completion.chunk",
    )
    call_response_chunk = OpenAICallResponseChunk(chunk=chunk)
    assert call_response_chunk.audio == audio_data
    assert call_response_chunk.audio_transcript == transcript


def test_openai_call_response_chunk_with_partial_audio() -> None:
    """Tests the `OpenAICallResponseChunk` class with partial audio content."""
    choices = [
        Choice(
            delta=ChoiceDelta(
                content="content",
                audio={"transcript": "transcript only"},  # pyright: ignore [reportCallIssue]
            ),
            index=0,
            finish_reason="stop",
        )
    ]
    chunk = ChatCompletionChunk(
        id="id",
        choices=choices,
        created=0,
        model="gpt-4o",
        object="chat.completion.chunk",
    )
    call_response_chunk = OpenAICallResponseChunk(chunk=chunk)
    assert call_response_chunk.audio is None
    assert call_response_chunk.audio_transcript == "transcript only"


def test_openai_call_response_chunk_without_audio() -> None:
    """Tests the `OpenAICallResponseChunk` class without audio content."""
    choices = [
        Choice(
            delta=ChoiceDelta(content="content"),  # no audio field
            index=0,
            finish_reason="stop",
        )
    ]
    chunk = ChatCompletionChunk(
        id="id",
        choices=choices,
        created=0,
        model="gpt-4o",
        object="chat.completion.chunk",
    )
    call_response_chunk = OpenAICallResponseChunk(chunk=chunk)
    assert call_response_chunk.audio is None
    assert call_response_chunk.audio_transcript is None
