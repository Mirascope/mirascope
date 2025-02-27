"""Tests the `bedrock.call_response_chunk` module."""

from mypy_boto3_bedrock_runtime.type_defs import TokenUsageTypeDef

from mirascope.core.base.types import CostMetadata
from mirascope.core.bedrock._types import StreamOutputChunk
from mirascope.core.bedrock.call_response_chunk import BedrockCallResponseChunk


def test_bedrock_call_response_chunk() -> None:
    """Tests the `BedrockCallResponseChunk` class."""
    usage = TokenUsageTypeDef(inputTokens=1, outputTokens=1)  # pyright: ignore [reportCallIssue]
    chunks = [
        StreamOutputChunk(
            messageStart={},  # pyright: ignore [reportArgumentType]
            responseMetadata={"RequestId": "id"},  # pyright: ignore [reportArgumentType]
            model="anthropic.claude-3-haiku-20240307-v1:0",
        ),
        StreamOutputChunk(
            contentBlockDelta={
                "contentBlockIndex": 0,
                "delta": {"text": "content"},
            },
            responseMetadata={"RequestId": "id"},  # pyright: ignore [reportArgumentType]
            model="anthropic.claude-3-haiku-20240307-v1:0",
        ),
        StreamOutputChunk(
            messageStop={"stopReason": "end_turn"},
            responseMetadata={"RequestId": "id"},  # pyright: ignore [reportArgumentType]
            model="anthropic.claude-3-haiku-20240307-v1:0",
            metadata={"usage": usage},  # pyright: ignore [reportArgumentType]
        ),
    ]

    call_response_chunk_0 = BedrockCallResponseChunk(chunk=chunks[0])
    call_response_chunk_1 = BedrockCallResponseChunk(chunk=chunks[1])
    call_response_chunk_2 = BedrockCallResponseChunk(chunk=chunks[2])

    # Test chunk 0 (message start)
    assert call_response_chunk_0.content == ""
    assert call_response_chunk_0.finish_reasons == []
    assert call_response_chunk_0.model == "anthropic.claude-3-haiku-20240307-v1:0"
    assert call_response_chunk_0.id == "id"
    assert call_response_chunk_0.usage is None
    assert call_response_chunk_0.input_tokens is None
    assert call_response_chunk_0.output_tokens is None
    assert call_response_chunk_0.cost_metadata == CostMetadata()

    # Test chunk 1 (content delta)
    assert call_response_chunk_1.content == "content"
    assert call_response_chunk_1.finish_reasons == []
    assert call_response_chunk_1.model == "anthropic.claude-3-haiku-20240307-v1:0"
    assert call_response_chunk_1.id == "id"
    assert call_response_chunk_1.usage is None
    assert call_response_chunk_1.input_tokens is None
    assert call_response_chunk_1.output_tokens is None
    assert call_response_chunk_1.cost_metadata == CostMetadata()

    # Test chunk 2 (message stop)
    assert call_response_chunk_2.content == ""
    assert call_response_chunk_2.finish_reasons == ["end_turn"]
    assert call_response_chunk_2.model == "anthropic.claude-3-haiku-20240307-v1:0"
    assert call_response_chunk_2.id == "id"
    assert call_response_chunk_2.usage == usage
    assert call_response_chunk_2.input_tokens == 1
    assert call_response_chunk_2.output_tokens == 1
    assert call_response_chunk_2.common_finish_reasons == ["stop"]
    assert call_response_chunk_2.cost_metadata == CostMetadata(
        input_tokens=1, output_tokens=1
    )
