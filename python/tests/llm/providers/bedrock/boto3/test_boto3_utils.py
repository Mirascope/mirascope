"""Tests for Bedrock boto3 utilities.

Tests encode/decode utility functions directly (without mocking boto3.Session).
Full E2E tests for basic call/stream are in tests/e2e/input/test_openai_compatibility_providers.py.
"""

import base64
import json
from typing import Any, cast

import pytest

from mirascope import llm
from mirascope.llm.exceptions import FeatureNotSupportedError
from mirascope.llm.providers.bedrock.boto3._utils import (
    FORMAT_TOOL_NAME,
    ConverseResponse,
    ConverseStreamEvent,
    _encode_content_part,  # pyright: ignore[reportPrivateUsage]
    _encode_tool,  # pyright: ignore[reportPrivateUsage]
    _normalize_tool_name,  # pyright: ignore[reportPrivateUsage]
    decode_response,
    decode_stream,
    encode_request,
)
from mirascope.llm.tools import ProviderTool


def test_normalize_tool_name_regular_name() -> None:
    assert _normalize_tool_name("my_tool") == "my_tool"


def test_normalize_tool_name_format_tool_name() -> None:
    format_tool_token = FORMAT_TOOL_NAME.lstrip("_")
    assert _normalize_tool_name(format_tool_token) == FORMAT_TOOL_NAME
    assert _normalize_tool_name(f"_{format_tool_token}") == FORMAT_TOOL_NAME


def test_encode_tool_with_provider_tool_raises_error() -> None:
    provider_tool = ProviderTool(name="test_provider_tool")
    with pytest.raises(FeatureNotSupportedError, match="Provider tool"):
        _encode_tool(provider_tool)


def test_encode_content_part_text() -> None:
    part = llm.Text(text="hello")
    result = _encode_content_part(part)
    assert result == {"text": "hello"}


def test_encode_content_part_base64_image() -> None:
    png_bytes = bytes([0x89, 0x50, 0x4E, 0x47, 0x0D, 0x0A, 0x1A, 0x0A])
    png_data = base64.b64encode(png_bytes).decode("ascii")
    part = llm.Image(
        source=llm.Base64ImageSource(
            type="base64_image_source", mime_type="image/png", data=png_data
        )
    )
    result = _encode_content_part(part)
    result_dict = cast(dict[str, Any], result)
    assert result_dict["image"]["format"] == "png"
    assert result_dict["image"]["source"]["bytes"] == png_bytes


def test_encode_content_part_image_format_fallback() -> None:
    data = base64.b64encode(b"test").decode("ascii")
    part = llm.Image(
        source=llm.Base64ImageSource(
            type="base64_image_source",
            mime_type="image/unknown",  # type: ignore[arg-type]
            data=data,
        )
    )
    result = _encode_content_part(part)
    result_dict = cast(dict[str, Any], result)
    assert result_dict["image"]["format"] == "jpeg"


def test_encode_content_part_tool_output() -> None:
    part = llm.ToolOutput(id="tool-123", name="get_weather", result="Sunny")
    result = _encode_content_part(part)
    result_dict = cast(dict[str, Any], result)
    assert result_dict["toolResult"]["toolUseId"] == "tool-123"
    assert result_dict["toolResult"]["content"][0]["text"] == "Sunny"


def test_encode_content_part_tool_call() -> None:
    part = llm.ToolCall(id="tool-456", name="get_temp", args='{"city": "SF"}')
    result = _encode_content_part(part)
    result_dict = cast(dict[str, Any], result)
    assert result_dict["toolUse"]["toolUseId"] == "tool-456"
    assert result_dict["toolUse"]["name"] == "get_temp"
    assert result_dict["toolUse"]["input"] == {"city": "SF"}


def test_encode_content_part_thought() -> None:
    part = llm.Thought(thought="Let me think...")
    result = _encode_content_part(part)
    result_dict = cast(dict[str, Any], result)
    assert result_dict["text"] == "**Thinking:** Let me think..."


@llm.tool
def sample_tool(x: int) -> int:
    """A sample tool."""
    return x


def test_encode_tool_with_tool_schema() -> None:
    result = _encode_tool(sample_tool)
    result_dict = cast(dict[str, Any], result)
    assert "toolSpec" in result_dict
    assert result_dict["toolSpec"]["name"] == "sample_tool"


def test_encode_request_basic() -> None:
    messages = [llm.messages.user("hello")]
    _, _, kwargs = encode_request(
        model_id="bedrock/amazon.nova-micro-v1:0",
        messages=messages,
        toolkit=llm.Toolkit(None),
        format=None,
        params={},
    )
    kwargs_dict = cast(dict[str, Any], kwargs)
    assert kwargs_dict["modelId"] == "amazon.nova-micro-v1:0"
    assert len(kwargs_dict["messages"]) == 1


def test_encode_request_with_inference_params() -> None:
    messages = [llm.messages.user("hello")]
    _, _, kwargs = encode_request(
        model_id="bedrock/amazon.nova-micro-v1:0",
        messages=messages,
        toolkit=llm.Toolkit(None),
        format=None,
        params={"temperature": 0.7, "top_p": 0.9, "stop_sequences": ["STOP"]},
    )
    kwargs_dict = cast(dict[str, Any], kwargs)
    assert kwargs_dict["inferenceConfig"]["temperature"] == 0.7
    assert kwargs_dict["inferenceConfig"]["topP"] == 0.9
    assert kwargs_dict["inferenceConfig"]["stopSequences"] == ["STOP"]


def test_encode_request_with_max_tokens() -> None:
    messages = [llm.messages.user("hello")]
    _, _, kwargs = encode_request(
        model_id="bedrock/amazon.nova-micro-v1:0",
        messages=messages,
        toolkit=llm.Toolkit(None),
        format=None,
        params={"max_tokens": 500},
    )
    kwargs_dict = cast(dict[str, Any], kwargs)
    assert kwargs_dict["inferenceConfig"]["maxTokens"] == 500


def test_encode_request_with_system_message() -> None:
    messages = [llm.messages.system("You are helpful"), llm.messages.user("hello")]
    _, _, kwargs = encode_request(
        model_id="bedrock/amazon.nova-micro-v1:0",
        messages=messages,
        toolkit=llm.Toolkit(None),
        format=None,
        params={},
    )
    kwargs_dict = cast(dict[str, Any], kwargs)
    assert kwargs_dict["system"][0]["text"] == "You are helpful"
    assert len(kwargs_dict["messages"]) == 1


def test_encode_request_with_tools() -> None:
    messages = [llm.messages.user("hello")]
    _, _, kwargs = encode_request(
        model_id="bedrock/amazon.nova-micro-v1:0",
        messages=messages,
        toolkit=llm.Toolkit([sample_tool]),
        format=None,
        params={},
    )
    kwargs_dict = cast(dict[str, Any], kwargs)
    assert "toolConfig" in kwargs_dict
    assert len(kwargs_dict["toolConfig"]["tools"]) == 1


def test_encode_request_with_format_tool_mode() -> None:
    from pydantic import BaseModel

    class TestResponse(BaseModel):
        answer: str

    format_spec = llm.format(TestResponse, mode="tool")
    messages = [llm.messages.user("hello")]
    _, resolved_format, kwargs = encode_request(
        model_id="bedrock/amazon.nova-micro-v1:0",
        messages=messages,
        toolkit=llm.Toolkit(None),
        format=format_spec,
        params={},
    )
    kwargs_dict = cast(dict[str, Any], kwargs)
    assert resolved_format is not None
    assert "toolConfig" in kwargs_dict
    assert kwargs_dict["toolConfig"]["toolChoice"]["tool"]["name"] == FORMAT_TOOL_NAME


def test_encode_request_with_format_and_tools() -> None:
    from pydantic import BaseModel

    class TestResponse(BaseModel):
        answer: str

    format_spec = llm.format(TestResponse, mode="tool")
    messages = [llm.messages.user("hello")]
    _, _, kwargs = encode_request(
        model_id="bedrock/amazon.nova-micro-v1:0",
        messages=messages,
        toolkit=llm.Toolkit([sample_tool]),
        format=format_spec,
        params={},
    )
    kwargs_dict = cast(dict[str, Any], kwargs)
    assert kwargs_dict["toolConfig"]["toolChoice"] == {"any": {}}


def _basic_converse_response(
    *,
    content: list[dict[str, Any]] | None = None,
    stop_reason: str = "end_turn",
    input_tokens: int = 1,
    output_tokens: int = 1,
) -> ConverseResponse:
    if content is None:
        content = [{"text": "ok"}]
    return ConverseResponse(
        output={"message": {"role": "assistant", "content": content}},  # type: ignore[typeddict-item]
        stopReason=stop_reason,  # type: ignore[typeddict-item]
        usage={"inputTokens": input_tokens, "outputTokens": output_tokens},
    )


def test_decode_response_text() -> None:
    response = _basic_converse_response(content=[{"text": "Hello!"}])
    assistant_message, finish_reason, usage = decode_response(
        response, "bedrock/amazon.nova-micro-v1:0"
    )
    assert assistant_message.content[0].text == "Hello!"  # type: ignore[union-attr]
    assert finish_reason is None
    assert usage.input_tokens == 1


def test_decode_response_tool_use() -> None:
    response = _basic_converse_response(
        content=[
            {
                "toolUse": {
                    "toolUseId": "tool-123",
                    "name": "get_weather",
                    "input": {"location": "SF"},
                }
            }
        ],
        stop_reason="tool_use",
    )
    assistant_message, _, _ = decode_response(
        response, "bedrock/amazon.nova-micro-v1:0"
    )
    tool_call = assistant_message.content[0]
    assert tool_call.id == "tool-123"  # type: ignore[union-attr]
    assert tool_call.name == "get_weather"  # type: ignore[union-attr]
    assert json.loads(tool_call.args) == {"location": "SF"}  # type: ignore[union-attr]


def test_decode_response_empty_content() -> None:
    response = _basic_converse_response(content=[])
    assistant_message, _, _ = decode_response(
        response, "bedrock/amazon.nova-micro-v1:0"
    )
    assert assistant_message.content[0].text == ""  # type: ignore[union-attr]


def test_decode_response_finish_reason_max_tokens() -> None:
    response = _basic_converse_response(stop_reason="max_tokens")
    _, finish_reason, _ = decode_response(response, "bedrock/amazon.nova-micro-v1:0")
    assert finish_reason == llm.FinishReason.MAX_TOKENS


def test_decode_response_finish_reason_content_filtered() -> None:
    response = _basic_converse_response(stop_reason="content_filtered")
    _, finish_reason, _ = decode_response(response, "bedrock/amazon.nova-micro-v1:0")
    assert finish_reason == llm.FinishReason.REFUSAL


def test_decode_response_finish_reason_guardrail() -> None:
    response = _basic_converse_response(stop_reason="guardrail_intervened")
    _, finish_reason, _ = decode_response(response, "bedrock/amazon.nova-micro-v1:0")
    assert finish_reason == llm.FinishReason.REFUSAL


def test_decode_stream_text_block() -> None:
    events: list[ConverseStreamEvent] = [
        {"contentBlockStart": {"start": {}}},
        {"contentBlockDelta": {"delta": {"text": "Hello"}}},
        {"contentBlockStop": {}},
    ]
    chunks = list(decode_stream(iter(events)))
    assert len(chunks) == 3
    assert chunks[0].type == "text_start_chunk"
    assert chunks[1].type == "text_chunk"
    assert chunks[1].delta == "Hello"
    assert chunks[2].type == "text_end_chunk"


def test_decode_stream_text_delta_without_start() -> None:
    events: list[ConverseStreamEvent] = [
        {"contentBlockDelta": {"delta": {"text": "Hello"}}},
        {"contentBlockStop": {}},
    ]
    chunks = list(decode_stream(iter(events)))
    assert len(chunks) == 3
    assert chunks[0].type == "text_start_chunk"
    assert chunks[1].type == "text_chunk"
    assert chunks[2].type == "text_end_chunk"


def test_decode_stream_tool_block() -> None:
    events: list[ConverseStreamEvent] = [
        {
            "contentBlockStart": {
                "start": {"toolUse": {"toolUseId": "tool-123", "name": "get_weather"}}
            }
        },
        {"contentBlockDelta": {"delta": {"toolUse": {"input": '{"loc'}}}},
        {"contentBlockStop": {}},
    ]
    chunks = list(decode_stream(iter(events)))
    assert len(chunks) == 3
    assert chunks[0].type == "tool_call_start_chunk"
    assert chunks[0].id == "tool-123"
    assert chunks[0].name == "get_weather"
    assert chunks[1].type == "tool_call_chunk"
    assert chunks[1].delta == '{"loc'
    assert chunks[2].type == "tool_call_end_chunk"


def test_decode_stream_message_stop_end_turn() -> None:
    events: list[ConverseStreamEvent] = [
        {"messageStop": {"stopReason": "end_turn"}},
    ]
    chunks = list(decode_stream(iter(events)))
    assert len(chunks) == 0


def test_decode_stream_message_stop_max_tokens() -> None:
    events: list[ConverseStreamEvent] = [
        {"messageStop": {"stopReason": "max_tokens"}},
    ]
    chunks = list(decode_stream(iter(events)))
    assert len(chunks) == 1
    assert chunks[0].type == "finish_reason_chunk"
    assert chunks[0].finish_reason == llm.FinishReason.MAX_TOKENS


def test_decode_stream_metadata() -> None:
    events: list[ConverseStreamEvent] = [
        {"metadata": {"usage": {"inputTokens": 10, "outputTokens": 5}}},
    ]
    chunks = list(decode_stream(iter(events)))
    assert len(chunks) == 1
    assert chunks[0].type == "usage_delta_chunk"
    assert chunks[0].input_tokens == 10
    assert chunks[0].output_tokens == 5
