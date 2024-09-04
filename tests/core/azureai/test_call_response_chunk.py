"""Tests the `azureai.call_response_chunk` module."""

from datetime import datetime

from azure.ai.inference.models import (
    CompletionsFinishReason,
    CompletionsUsage,
    FunctionCall,
    StreamingChatChoiceUpdate,
    StreamingChatCompletionsUpdate,
    StreamingChatResponseMessageUpdate,
    StreamingChatResponseToolCallUpdate,
)

from mirascope.core.azureai.call_response_chunk import AzureAICallResponseChunk


def test_azureai_call_response_chunk() -> None:
    """Tests the `AzureAICallResponseChunk` class."""
    tool_call = StreamingChatResponseToolCallUpdate(
        id="id",
        function=FunctionCall(arguments='{"key": "value"}', name="function"),
    )
    choices = [
        StreamingChatChoiceUpdate(
            delta=StreamingChatResponseMessageUpdate(
                content="content", tool_calls=[tool_call]
            ),
            index=0,
            finish_reason=CompletionsFinishReason("stop"),
        )
    ]
    usage = CompletionsUsage(completion_tokens=1, prompt_tokens=1, total_tokens=2)
    chunk = StreamingChatCompletionsUpdate(
        id="id",
        choices=choices,
        created=datetime.fromtimestamp(0),
        model="gpt-4o",
        usage=usage,
    )
    call_response_chunk = AzureAICallResponseChunk(chunk=chunk)
    assert call_response_chunk.content == "content"
    assert call_response_chunk.finish_reasons == ["stop"]
    assert call_response_chunk.model == "gpt-4o"
    assert call_response_chunk.id == "id"
    assert call_response_chunk.usage == usage
    assert call_response_chunk.input_tokens == 1
    assert call_response_chunk.output_tokens == 1


def test_azureai_call_response_chunk_no_choices_or_usage() -> None:
    """Tests the `AzureAICallResponseChunk` class with None values."""
    chunk = StreamingChatCompletionsUpdate(
        id="id",
        choices=[],
        created=datetime.fromtimestamp(0),
        model="gpt-4o",
        usage=CompletionsUsage(completion_tokens=0, prompt_tokens=0, total_tokens=0),
    )
    call_response_chunk = AzureAICallResponseChunk(chunk=chunk)
    assert call_response_chunk.content == ""
    assert call_response_chunk.usage == {
        "completion_tokens": 0,
        "prompt_tokens": 0,
        "total_tokens": 0,
    }
    assert call_response_chunk.input_tokens == 0
    assert call_response_chunk.output_tokens == 0
