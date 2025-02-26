"""Tests the `bedrock.stream` module."""

from collections.abc import Generator

import pytest
from mypy_boto3_bedrock_runtime.type_defs import (
    ConverseStreamMetadataEventTypeDef,
    ResponseMetadataTypeDef,
    ToolTypeDef,
)

from mirascope.core.base.types import CostMetadata
from mirascope.core.bedrock.call_params import BedrockCallParams
from mirascope.core.bedrock.call_response import BedrockCallResponse
from mirascope.core.bedrock.call_response_chunk import BedrockCallResponseChunk
from mirascope.core.bedrock.stream import BedrockStream
from mirascope.core.bedrock.tool import BedrockTool


class MockTool(BedrockTool):
    name: str

    def call(self) -> str: ...


def test_bedrock_stream_init():
    stream = BedrockStream(
        stream=iter([]),
        metadata={},
        tool_types=None,
        call_response_type=BedrockCallResponse,
        model="anthropic.claude-v2",
        prompt_template="",
        fn_args={},
        dynamic_config=None,
        messages=[],
        call_params=BedrockCallParams(),
        call_kwargs={},
    )
    assert stream._provider == "bedrock"
    assert stream._metadata is None
    assert stream._response_metadata == {
        "RequestId": "",
        "HTTPStatusCode": 500,
        "HTTPHeaders": {},
        "RetryAttempts": 0,
    }
    assert stream.cost is None
    assert stream.cost_metadata == CostMetadata()


def test_bedrock_stream_construct_message_param():
    stream = BedrockStream(
        stream=iter([]),
        metadata={},
        tool_types=None,
        call_response_type=BedrockCallResponse,
        model="anthropic.claude-v2",
        prompt_template="",
        fn_args={},
        dynamic_config=None,
        messages=[],
        call_params=BedrockCallParams(),
        call_kwargs={},
    )

    # Test with content only
    message_param = stream._construct_message_param(content="Test content")
    assert message_param == {"role": "assistant", "content": [{"text": "Test content"}]}

    # Test with tool calls only
    tool_calls = [ToolTypeDef(toolUseId="1", name="TestTool", input={})]  # pyright: ignore [reportCallIssue]
    message_param = stream._construct_message_param(tool_calls=tool_calls)  # pyright: ignore [reportArgumentType]
    assert message_param == {
        "role": "assistant",
        "content": [{"toolUse": tool_calls[0]}],
    }

    # Test with both content and tool calls
    message_param = stream._construct_message_param(
        content="Test content",
        tool_calls=tool_calls,  # pyright: ignore [reportArgumentType]
    )
    assert message_param == {
        "role": "assistant",
        "content": [{"text": "Test content"}, {"toolUse": tool_calls[0]}],
    }


def test_bedrock_stream_update_properties():
    stream = BedrockStream(
        stream=iter([]),
        metadata={},
        tool_types=None,
        call_response_type=BedrockCallResponse,
        model="anthropic.claude-v2",
        prompt_template="",
        fn_args={},
        dynamic_config=None,
        messages=[],
        call_params=BedrockCallParams(),
        call_kwargs={},
    )

    chunk = BedrockCallResponseChunk(
        chunk={  # pyright: ignore [reportArgumentType]
            "model": "anthropic.claude-v2",
            "metadata": ConverseStreamMetadataEventTypeDef(  # pyright: ignore [reportCallIssue]
                usage={"inputTokens": 10, "outputTokens": 20}
            ),
            "responseMetadata": ResponseMetadataTypeDef(
                RequestId="test-id", HTTPStatusCode=200, HTTPHeaders={}, RetryAttempts=0
            ),
        }
    )

    stream._update_properties(chunk)
    assert stream._metadata == chunk.chunk["metadata"]  # pyright: ignore [reportTypedDictNotRequiredAccess]
    assert stream._response_metadata == chunk.chunk["responseMetadata"]


def test_bedrock_stream_construct_call_response():
    stream = BedrockStream(
        stream=iter([]),
        metadata={},
        tool_types=[MockTool],
        call_response_type=BedrockCallResponse,
        model="anthropic.claude-v2",
        prompt_template="Test prompt",
        fn_args={"arg": "value"},
        dynamic_config=None,
        messages=[],
        call_params=BedrockCallParams(),
        call_kwargs={},
    )

    stream.message_param = {"role": "assistant", "content": [{"text": "Test content"}]}
    stream.finish_reasons = ["end_turn"]
    stream._metadata = ConverseStreamMetadataEventTypeDef(
        usage={"inputTokens": 10, "outputTokens": 20},  # pyright: ignore [reportArgumentType]
        metrics={"latencyMs": 100},
        trace={"id": "trace-id"},  # pyright: ignore [reportArgumentType]
    )
    stream._response_metadata = ResponseMetadataTypeDef(
        RequestId="test-id", HTTPStatusCode=200, HTTPHeaders={}, RetryAttempts=0
    )
    stream.start_time = 0
    stream.end_time = 1

    response = stream.construct_call_response()
    assert isinstance(response, BedrockCallResponse)
    assert response.content == "Test content"
    assert response.finish_reasons == ["end_turn"]
    assert response.tool_types == [MockTool]
    assert response.prompt_template == "Test prompt"
    assert response.fn_args == {"arg": "value"}


def test_bedrock_stream_construct_call_response_error():
    stream = BedrockStream(
        stream=iter([]),
        metadata={},
        tool_types=None,
        call_response_type=BedrockCallResponse,
        model="anthropic.claude-v2",
        prompt_template="",
        fn_args={},
        dynamic_config=None,
        messages=[],
        call_params=BedrockCallParams(),
        call_kwargs={},
    )

    with pytest.raises(
        ValueError, match="No stream response, check if the stream has been consumed."
    ):
        stream.construct_call_response()


def test_bedrock_stream_iteration():
    response_metadata = ResponseMetadataTypeDef(
        RequestId="test-id", HTTPStatusCode=200, HTTPHeaders={}, RetryAttempts=0
    )
    chunks = [
        BedrockCallResponseChunk(
            chunk={  # pyright: ignore [reportArgumentType]
                "model": "anthropic.claude-v2",
                "responseMetadata": response_metadata,
                "contentBlockDelta": {"delta": {"text": "Hello"}},
            }
        ),
        BedrockCallResponseChunk(
            chunk={  # pyright: ignore [reportArgumentType]
                "model": "anthropic.claude-v2",
                "responseMetadata": response_metadata,
                "contentBlockDelta": {"delta": {"text": " world"}},
            }
        ),
        BedrockCallResponseChunk(
            chunk={
                "model": "anthropic.claude-v2",
                "responseMetadata": response_metadata,
                "messageStop": {"stopReason": "end_turn"},
            }
        ),
    ]

    def chunk_generator() -> Generator[
        tuple[BedrockCallResponseChunk, None], None, None
    ]:
        for chunk in chunks:
            yield chunk, None

    stream = BedrockStream(
        stream=chunk_generator(),
        metadata={},
        tool_types=None,
        call_response_type=BedrockCallResponse,
        model="anthropic.claude-v2",
        prompt_template="",
        fn_args={},
        dynamic_config=None,
        messages=[],
        call_params=BedrockCallParams(),
        call_kwargs={},
    )

    collected_chunks = list(stream)
    assert len(collected_chunks) == 3
    assert collected_chunks[0][0].content == "Hello"
    assert collected_chunks[1][0].content == " world"
    assert collected_chunks[2][0].finish_reasons == ["end_turn"]
    assert stream.message_param == {
        "role": "assistant",
        "content": [{"text": "Hello world"}],
    }
