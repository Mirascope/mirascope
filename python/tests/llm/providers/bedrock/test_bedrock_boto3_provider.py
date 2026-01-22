"""Tests for BedrockBoto3Provider."""

from __future__ import annotations

import base64
import builtins
import importlib
import json
import sys
from collections.abc import Iterator
from types import ModuleType
from typing import Any, cast
from unittest.mock import MagicMock, patch

import pytest
from botocore.exceptions import BotoCoreError, ClientError
from inline_snapshot import snapshot
from pydantic import BaseModel

from mirascope import llm
from mirascope.llm.providers.bedrock.boto3 import (
    BedrockBoto3Provider,
    BedrockBoto3RoutedProvider,
)

EMPTY_TOOLKIT = llm.Toolkit(None)
EMPTY_CONTEXT_TOOLKIT = llm.ContextToolkit(None)
EMPTY_ASYNC_TOOLKIT = llm.AsyncToolkit(None)
EMPTY_ASYNC_CONTEXT_TOOLKIT = llm.AsyncContextToolkit(None)


@llm.tool(strict=True)
def strict_tool() -> str:
    """A strict test tool."""

    return "result"


@llm.tool(strict=False)
def non_strict_tool() -> str:
    """A non-strict test tool."""

    return "result"


def _basic_converse_response(
    *,
    content: list[dict[str, Any]] | None = None,
    stop_reason: str = "end_turn",
    input_tokens: int = 1,
    output_tokens: int = 1,
) -> dict[str, Any]:
    if content is None:
        content = [{"text": "ok"}]
    return {
        "output": {"message": {"role": "assistant", "content": content}},
        "stopReason": stop_reason,
        "usage": {"inputTokens": input_tokens, "outputTokens": output_tokens},
    }


def _make_provider(
    mock_session_cls: MagicMock,
) -> tuple[BedrockBoto3Provider, MagicMock]:
    mock_client = MagicMock()
    mock_session = MagicMock()
    mock_session.client.return_value = mock_client
    mock_session_cls.return_value = mock_session
    provider = BedrockBoto3Provider()
    return provider, mock_client


def _call_provider(
    provider: BedrockBoto3Provider,
    mock_client: MagicMock,
    *,
    response: dict[str, Any] | None = None,
    **call_kwargs: Any,  # noqa: ANN401
) -> tuple[llm.Response, dict[str, Any]]:
    mock_client.converse.return_value = response or _basic_converse_response()
    toolkit = call_kwargs.pop("toolkit", None)
    tools = call_kwargs.pop("tools", None)
    if toolkit is None:
        toolkit = tools if isinstance(tools, llm.Toolkit) else llm.Toolkit(tools)
    call_kwargs["toolkit"] = toolkit
    result = provider.call(**call_kwargs)
    kwargs = mock_client.converse.call_args.kwargs
    return result, kwargs


def _stream_response(events: list[dict[str, Any]]) -> dict[str, Any]:
    return {"stream": iter(events)}


@patch("boto3.Session")
def test_bedrock_boto3_provider_initialization(mock_session_cls: MagicMock) -> None:
    """Test BedrockBoto3Provider initialization with default settings."""
    mock_client = MagicMock()
    mock_session = MagicMock()
    mock_session.client.return_value = mock_client
    mock_session_cls.return_value = mock_session

    provider = BedrockBoto3Provider()
    assert provider.id == "bedrock:boto3"
    assert provider.client is mock_client
    mock_session.client.assert_called_once_with("bedrock-runtime")


@patch("boto3.Session")
def test_bedrock_boto3_provider_initialization_with_credentials(
    mock_session_cls: MagicMock,
) -> None:
    """Test BedrockBoto3Provider initialization with AWS credentials."""
    mock_client = MagicMock()
    mock_session = MagicMock()
    mock_session.client.return_value = mock_client
    mock_session_cls.return_value = mock_session

    provider = BedrockBoto3Provider(
        aws_region="us-east-1",
        aws_access_key="test-access-key",
        aws_secret_key="test-secret-key",
        aws_session_token="test-session-token",
        aws_profile="test-profile",
    )
    assert provider.client is mock_client
    mock_session_cls.assert_called_once_with(
        region_name="us-east-1",
        profile_name="test-profile",
    )
    mock_session.client.assert_called_once_with(
        "bedrock-runtime",
        aws_access_key_id="test-access-key",
        aws_secret_access_key="test-secret-key",
        aws_session_token="test-session-token",
    )


@patch("boto3.Session")
def test_bedrock_boto3_provider_default_scope(mock_session_cls: MagicMock) -> None:
    """Test BedrockBoto3Provider has correct default scope."""
    mock_client = MagicMock()
    mock_session = MagicMock()
    mock_session.client.return_value = mock_client
    mock_session_cls.return_value = mock_session

    provider = BedrockBoto3Provider()
    assert provider.default_scope == "bedrock/"


@patch("boto3.Session")
def test_bedrock_boto3_provider_get_error_status(mock_session_cls: MagicMock) -> None:
    """Test BedrockBoto3Provider get_error_status returns status code."""
    mock_client = MagicMock()
    mock_session = MagicMock()
    mock_session.client.return_value = mock_client
    mock_session_cls.return_value = mock_session

    provider = BedrockBoto3Provider()

    class DummyError(Exception):
        response = {"ResponseMetadata": {"HTTPStatusCode": 418}}

    assert provider.get_error_status(DummyError()) == 418


@patch("boto3.Session")
def test_bedrock_boto3_provider_get_error_status_no_response(
    mock_session_cls: MagicMock,
) -> None:
    """Test BedrockBoto3Provider get_error_status returns None for non-response errors."""
    mock_client = MagicMock()
    mock_session = MagicMock()
    mock_session.client.return_value = mock_client
    mock_session_cls.return_value = mock_session

    provider = BedrockBoto3Provider()

    class DummyError(Exception):
        pass

    assert provider.get_error_status(DummyError()) is None


@patch("boto3.Session")
def test_bedrock_boto3_routed_provider_id(mock_session_cls: MagicMock) -> None:
    """Test BedrockBoto3RoutedProvider uses 'bedrock' as provider id."""
    mock_client = MagicMock()
    mock_session = MagicMock()
    mock_session.client.return_value = mock_client
    mock_session_cls.return_value = mock_session

    provider = BedrockBoto3RoutedProvider()
    assert provider.id == "bedrock"


@patch("boto3.Session")
def test_bedrock_boto3_provider_initialization_with_base_url(
    mock_session_cls: MagicMock,
) -> None:
    """Test BedrockBoto3Provider initialization with base_url."""
    mock_client = MagicMock()
    mock_session = MagicMock()
    mock_session.client.return_value = mock_client
    mock_session_cls.return_value = mock_session

    provider = BedrockBoto3Provider(
        aws_region="us-gov-west-1",
        base_url="https://bedrock-runtime.us-gov-west-1.amazonaws.com",
    )
    assert provider.client is mock_client
    mock_session_cls.assert_called_once_with(region_name="us-gov-west-1")
    mock_session.client.assert_called_once_with(
        "bedrock-runtime",
        endpoint_url="https://bedrock-runtime.us-gov-west-1.amazonaws.com",
    )


@patch("boto3.Session")
def test_call_encodes_basic_request(mock_session_cls: MagicMock) -> None:
    provider, mock_client = _make_provider(mock_session_cls)
    _, kwargs = _call_provider(
        provider,
        mock_client,
        model_id="bedrock/amazon.titan-text-express-v1",
        messages=[llm.messages.user("hello")],
    )

    assert kwargs == snapshot(
        {
            "modelId": "amazon.titan-text-express-v1",
            "messages": [{"role": "user", "content": [{"text": "hello"}]}],
            "inferenceConfig": {"maxTokens": 4096},
        }
    )


@patch("boto3.Session")
def test_call_encodes_system_message(mock_session_cls: MagicMock) -> None:
    provider, mock_client = _make_provider(mock_session_cls)
    _, kwargs = _call_provider(
        provider,
        mock_client,
        model_id="bedrock/amazon.titan-text-express-v1",
        messages=[
            llm.messages.system("You are helpful"),
            llm.messages.user("hello"),
        ],
    )

    assert kwargs["system"] == [{"text": "You are helpful"}]
    assert kwargs["messages"] == snapshot(
        [{"role": "user", "content": [{"text": "hello"}]}]
    )


@patch("boto3.Session")
def test_call_encodes_inference_params(mock_session_cls: MagicMock) -> None:
    provider, mock_client = _make_provider(mock_session_cls)
    _, kwargs = _call_provider(
        provider,
        mock_client,
        model_id="bedrock/amazon.titan-text-express-v1",
        messages=[llm.messages.user("hello")],
        max_tokens=1000,
        temperature=0.7,
        top_p=0.9,
        stop_sequences=["STOP", "END"],
    )

    assert kwargs["inferenceConfig"] == snapshot(
        {
            "maxTokens": 1000,
            "temperature": 0.7,
            "topP": 0.9,
            "stopSequences": ["STOP", "END"],
        }
    )


@patch("boto3.Session")
def test_call_raises_for_strict_tools(mock_session_cls: MagicMock) -> None:
    provider, _ = _make_provider(mock_session_cls)

    with pytest.raises(llm.FeatureNotSupportedError, match="strict tools"):
        provider.call(
            model_id="bedrock/amazon.nova-micro-v1:0",
            messages=[llm.messages.user("hello")],
            toolkit=llm.Toolkit([strict_tool]),
        )


@patch("boto3.Session")
def test_call_raises_for_strict_format(mock_session_cls: MagicMock) -> None:
    provider, _ = _make_provider(mock_session_cls)

    class TestFormat(BaseModel):
        value: str

    strict_format = llm.format(TestFormat, mode="strict")

    with pytest.raises(llm.FeatureNotSupportedError, match="strict"):
        provider.call(
            model_id="bedrock/amazon.nova-micro-v1:0",
            messages=[llm.messages.user("hello")],
            toolkit=EMPTY_TOOLKIT,
            format=strict_format,
        )


@patch("boto3.Session")
def test_call_encodes_format_tool_mode(mock_session_cls: MagicMock) -> None:
    provider, mock_client = _make_provider(mock_session_cls)

    class TestResponse(BaseModel):
        answer: str

    format_spec = llm.format(TestResponse, mode="tool")

    _, kwargs = _call_provider(
        provider,
        mock_client,
        model_id="bedrock/amazon.titan-text-express-v1",
        messages=[llm.messages.user("hello")],
        format=format_spec,
    )

    tool_config = kwargs["toolConfig"]
    assert len(tool_config["tools"]) == 1
    assert (
        tool_config["toolChoice"]["tool"]["name"]
        == tool_config["tools"][0]["toolSpec"]["name"]
    )
    assert format_spec is not None
    assert kwargs["system"][0]["text"] == format_spec.formatting_instructions


@patch("boto3.Session")
def test_call_encodes_format_with_tools(mock_session_cls: MagicMock) -> None:
    provider, mock_client = _make_provider(mock_session_cls)

    class TestResponse(BaseModel):
        answer: str

    format_spec = llm.format(TestResponse, mode="tool")

    _, kwargs = _call_provider(
        provider,
        mock_client,
        model_id="bedrock/amazon.titan-text-express-v1",
        messages=[llm.messages.user("hello")],
        tools=[non_strict_tool],
        format=format_spec,
    )

    tool_config = kwargs["toolConfig"]
    assert len(tool_config["tools"]) == 2
    assert tool_config["toolChoice"] == {"any": {}}


@patch("boto3.Session")
def test_call_encodes_tools_without_format(mock_session_cls: MagicMock) -> None:
    provider, mock_client = _make_provider(mock_session_cls)

    _, kwargs = _call_provider(
        provider,
        mock_client,
        model_id="bedrock/amazon.titan-text-express-v1",
        messages=[llm.messages.user("hello")],
        tools=[non_strict_tool],
        format=None,
    )

    tool_config = kwargs["toolConfig"]
    assert len(tool_config["tools"]) == 1
    assert "toolChoice" not in tool_config


@patch("boto3.Session")
def test_call_encodes_tool_call_and_tool_output_messages(
    mock_session_cls: MagicMock,
) -> None:
    provider, mock_client = _make_provider(mock_session_cls)

    messages = [
        llm.messages.user("What's the weather in SF?"),
        llm.messages.assistant(
            content=[
                llm.ToolCall(
                    id="tool-123", name="get_weather", args='{"location": "SF"}'
                )
            ],
            model_id="bedrock/test",
            provider_id="bedrock",
            provider_model_name="test",
            raw_message=None,
        ),
        llm.messages.user(
            content=[
                llm.ToolOutput(id="tool-123", name="get_weather", result="Sunny, 72F")
            ]
        ),
    ]

    _, kwargs = _call_provider(
        provider,
        mock_client,
        model_id="bedrock/amazon.titan-text-express-v1",
        messages=messages,
    )

    encoded_messages = kwargs["messages"]
    assert encoded_messages[1]["content"][0]["toolUse"] == snapshot(
        {
            "toolUseId": "tool-123",
            "name": "get_weather",
            "input": {"location": "SF"},
        }
    )
    assert encoded_messages[2]["content"][0]["toolResult"] == snapshot(
        {"toolUseId": "tool-123", "content": [{"text": "Sunny, 72F"}]}
    )


@patch("boto3.Session")
def test_call_encodes_thought_content(mock_session_cls: MagicMock) -> None:
    provider, mock_client = _make_provider(mock_session_cls)

    messages = [
        llm.messages.user("Hello"),
        llm.messages.assistant(
            content=[
                llm.Thought(thought="Let me think about this..."),
                llm.Text(text="Here's my response"),
            ],
            model_id="bedrock/test",
            provider_id="bedrock",
            provider_model_name="test",
            raw_message=None,
        ),
        llm.messages.user("Thanks"),
    ]

    _, kwargs = _call_provider(
        provider,
        mock_client,
        model_id="bedrock/amazon.nova-micro-v1:0",
        messages=messages,
    )

    assistant_content = kwargs["messages"][1]["content"]
    assert assistant_content[0]["text"] == "**Thinking:** Let me think about this..."
    assert assistant_content[1]["text"] == "Here's my response"


@patch("boto3.Session")
def test_call_encodes_base64_image_and_fallback_format(
    mock_session_cls: MagicMock,
) -> None:
    provider, mock_client = _make_provider(mock_session_cls)

    png_bytes = bytes([0x89, 0x50, 0x4E, 0x47, 0x0D, 0x0A, 0x1A, 0x0A])
    png_data = base64.b64encode(png_bytes).decode("ascii")

    image = llm.Image(
        source=llm.Base64ImageSource(
            type="base64_image_source",
            mime_type="image/png",
            data=png_data,
        )
    )
    unknown_image = llm.Image(
        source=llm.Base64ImageSource(
            type="base64_image_source",
            mime_type=cast(Any, "image/unknown"),
            data=png_data,
        )
    )

    _, kwargs = _call_provider(
        provider,
        mock_client,
        model_id="bedrock/amazon.nova-micro-v1:0",
        messages=[llm.messages.user(["describe", image, unknown_image])],
    )

    content = kwargs["messages"][0]["content"]
    assert content[0] == {"text": "describe"}
    assert content[1]["image"]["format"] == "png"
    assert content[1]["image"]["source"]["bytes"] == png_bytes
    assert content[2]["image"]["format"] == "jpeg"


@patch("boto3.Session")
def test_call_raises_for_url_image(mock_session_cls: MagicMock) -> None:
    provider, _ = _make_provider(mock_session_cls)
    image = llm.Image(
        source=llm.URLImageSource(
            type="url_image_source",
            url="https://example.com/image.png",
        )
    )

    with pytest.raises(llm.FeatureNotSupportedError, match="URL image sources"):
        provider.call(
            model_id="bedrock/amazon.nova-micro-v1:0",
            messages=[llm.messages.user([image])],
            toolkit=EMPTY_TOOLKIT,
        )


@patch("boto3.Session")
def test_call_raises_for_audio(mock_session_cls: MagicMock) -> None:
    provider, _ = _make_provider(mock_session_cls)
    audio = llm.Audio(
        source=llm.Base64AudioSource(
            type="base64_audio_source",
            mime_type="audio/mp3",
            data="base64data",
        )
    )

    with pytest.raises(llm.FeatureNotSupportedError, match="audio input"):
        provider.call(
            model_id="bedrock/amazon.nova-micro-v1:0",
            messages=[llm.messages.user([audio])],
            toolkit=EMPTY_TOOLKIT,
        )


@patch("boto3.Session")
def test_call_raises_for_document(mock_session_cls: MagicMock) -> None:
    provider, _ = _make_provider(mock_session_cls)
    doc = llm.Document(
        source=llm.content.Base64DocumentSource(
            type="base64_document_source",
            data="dGVzdA==",
            media_type="application/pdf",
        )
    )

    with pytest.raises(
        llm.FeatureNotSupportedError, match="document support is not implemented"
    ):
        provider.call(
            model_id="bedrock/amazon.nova-micro-v1:0",
            messages=[llm.messages.user([doc])],
            toolkit=EMPTY_TOOLKIT,
        )


@patch("boto3.Session")
def test_call_decodes_text_response(mock_session_cls: MagicMock) -> None:
    provider, mock_client = _make_provider(mock_session_cls)
    mock_client.converse.return_value = _basic_converse_response(
        content=[{"text": "Hello, world!"}],
        stop_reason="end_turn",
        input_tokens=10,
        output_tokens=5,
    )

    response = provider.call(
        model_id="bedrock/amazon.titan-text-express-v1",
        messages=[llm.messages.user("hello")],
        toolkit=EMPTY_TOOLKIT,
    )

    assert response.texts[0].text == "Hello, world!"
    assert response.finish_reason is None
    assert response.usage is not None
    assert response.usage.input_tokens == 10
    assert response.usage.output_tokens == 5


@patch("boto3.Session")
def test_call_decodes_tool_use_response(mock_session_cls: MagicMock) -> None:
    provider, mock_client = _make_provider(mock_session_cls)
    mock_client.converse.return_value = _basic_converse_response(
        content=[
            {
                "toolUse": {
                    "toolUseId": "tool-123",
                    "name": "get_weather",
                    "input": {"location": "San Francisco"},
                }
            }
        ],
        stop_reason="tool_use",
        input_tokens=15,
        output_tokens=8,
    )

    response = provider.call(
        model_id="bedrock/amazon.titan-text-express-v1",
        messages=[llm.messages.user("hello")],
        toolkit=EMPTY_TOOLKIT,
    )

    assert len(response.tool_calls) == 1
    tool_call = response.tool_calls[0]
    assert tool_call.id == "tool-123"
    assert tool_call.name == "get_weather"
    assert json.loads(tool_call.args) == {"location": "San Francisco"}
    assert response.finish_reason is None


@patch("boto3.Session")
def test_call_decodes_empty_content_response(mock_session_cls: MagicMock) -> None:
    provider, mock_client = _make_provider(mock_session_cls)
    mock_client.converse.return_value = _basic_converse_response(content=[])

    response = provider.call(
        model_id="bedrock/amazon.titan-text-express-v1",
        messages=[llm.messages.user("hello")],
        toolkit=EMPTY_TOOLKIT,
    )

    assert response.texts[0].text == ""


@pytest.mark.parametrize(
    ("stop_reason", "expected"),
    [
        ("max_tokens", llm.FinishReason.MAX_TOKENS),
        ("content_filtered", llm.FinishReason.REFUSAL),
        ("guardrail_intervened", llm.FinishReason.REFUSAL),
    ],
)
@patch("boto3.Session")
def test_call_sets_finish_reason_from_stop_reason(
    mock_session_cls: MagicMock,
    stop_reason: str,
    expected: llm.FinishReason,
) -> None:
    provider, mock_client = _make_provider(mock_session_cls)
    mock_client.converse.return_value = _basic_converse_response(
        content=[{"text": "Hello"}],
        stop_reason=stop_reason,
    )

    response = provider.call(
        model_id="bedrock/amazon.titan-text-express-v1",
        messages=[llm.messages.user("hello")],
        toolkit=EMPTY_TOOLKIT,
    )

    assert response.finish_reason == expected


@patch("boto3.Session")
def test_call_uses_routed_provider_id(mock_session_cls: MagicMock) -> None:
    mock_client = MagicMock()
    mock_session = MagicMock()
    mock_session.client.return_value = mock_client
    mock_session_cls.return_value = mock_session

    provider = BedrockBoto3RoutedProvider()
    mock_client.converse.return_value = _basic_converse_response(
        content=[{"text": "Hello"}],
    )

    response = provider.call(
        model_id="bedrock/amazon.titan-text-express-v1",
        messages=[llm.messages.user("hello")],
        toolkit=EMPTY_TOOLKIT,
    )

    assert response.provider_id == "bedrock"


@pytest.mark.parametrize(
    ("code", "expected_error"),
    [
        ("ThrottlingException", llm.RateLimitError),
        ("AccessDeniedException", llm.PermissionError),
        ("ValidationException", llm.BadRequestError),
        ("ResourceNotFoundException", llm.NotFoundError),
        ("ServiceUnavailableException", llm.ServerError),
        ("ModelNotReadyException", llm.ServerError),
        ("InternalServerException", llm.ServerError),
    ],
)
@patch("boto3.Session")
def test_call_maps_client_errors(
    mock_session_cls: MagicMock,
    code: str,
    expected_error: type[llm.ProviderError],
) -> None:
    provider, mock_client = _make_provider(mock_session_cls)
    mock_client.converse.side_effect = ClientError(
        error_response={"Error": {"Code": code, "Message": "boom"}},
        operation_name="converse",
    )

    with pytest.raises(expected_error):
        provider.call(
            model_id="bedrock/amazon.titan-text-express-v1",
            messages=[llm.messages.user("hello")],
            toolkit=EMPTY_TOOLKIT,
        )


@patch("boto3.Session")
def test_call_maps_unknown_client_error(mock_session_cls: MagicMock) -> None:
    provider, mock_client = _make_provider(mock_session_cls)
    mock_client.converse.side_effect = ClientError(
        error_response={"Error": {"Code": "UnknownException", "Message": "boom"}},
        operation_name="converse",
    )

    with pytest.raises(llm.ProviderError):
        provider.call(
            model_id="bedrock/amazon.titan-text-express-v1",
            messages=[llm.messages.user("hello")],
            toolkit=EMPTY_TOOLKIT,
        )


@patch("boto3.Session")
def test_call_maps_botocore_error(mock_session_cls: MagicMock) -> None:
    provider, mock_client = _make_provider(mock_session_cls)
    mock_client.converse.side_effect = BotoCoreError()

    with pytest.raises(llm.ProviderError):
        provider.call(
            model_id="bedrock/amazon.titan-text-express-v1",
            messages=[llm.messages.user("hello")],
            toolkit=EMPTY_TOOLKIT,
        )


@patch("boto3.Session")
def test_stream_decodes_text_and_usage(mock_session_cls: MagicMock) -> None:
    provider, mock_client = _make_provider(mock_session_cls)
    events = [
        {"contentBlockStart": {"start": {}}},
        {"contentBlockDelta": {"delta": {"text": "Hello, "}}},
        {"contentBlockDelta": {"delta": {"text": "world!"}}},
        {"contentBlockStop": {}},
        {"messageStop": {"stopReason": "end_turn"}},
        {"metadata": {"usage": {"inputTokens": 10, "outputTokens": 5}}},
    ]
    mock_client.converse_stream.return_value = _stream_response(events)

    response = provider.stream(
        model_id="bedrock/amazon.titan-text-express-v1",
        messages=[llm.messages.user("hello")],
        toolkit=EMPTY_TOOLKIT,
    )
    chunks = list(response.chunk_stream())

    assert chunks[0].type == "text_start_chunk"
    assert chunks[1].type == "text_chunk"
    assert chunks[1].delta == "Hello, "
    assert chunks[2].type == "text_chunk"
    assert chunks[2].delta == "world!"
    assert chunks[3].type == "text_end_chunk"
    assert response.usage is not None
    assert response.usage.input_tokens == 10
    assert response.usage.output_tokens == 5


@patch("boto3.Session")
def test_stream_decodes_tool_use(mock_session_cls: MagicMock) -> None:
    provider, mock_client = _make_provider(mock_session_cls)
    tool_use_start = '{"loc'
    tool_use_end = 'ation": "SF"}'
    events = [
        {
            "contentBlockStart": {
                "start": {"toolUse": {"toolUseId": "tool-123", "name": "get_weather"}}
            }
        },
        {"contentBlockDelta": {"delta": {"toolUse": {"input": tool_use_start}}}},
        {"contentBlockDelta": {"delta": {"toolUse": {"input": tool_use_end}}}},
        {"contentBlockStop": {}},
        {"messageStop": {"stopReason": "tool_use"}},
    ]
    mock_client.converse_stream.return_value = _stream_response(events)

    response = provider.stream(
        model_id="bedrock/amazon.titan-text-express-v1",
        messages=[llm.messages.user("hello")],
        toolkit=EMPTY_TOOLKIT,
    )
    chunks = list(response.chunk_stream())

    assert chunks[0].type == "tool_call_start_chunk"
    assert chunks[0].id == "tool-123"
    assert chunks[0].name == "get_weather"
    assert chunks[1].type == "tool_call_chunk"
    assert chunks[1].delta == tool_use_start
    assert chunks[2].type == "tool_call_chunk"
    assert chunks[2].delta == tool_use_end
    assert chunks[3].type == "tool_call_end_chunk"


@patch("boto3.Session")
def test_stream_sets_finish_reason_for_max_tokens(
    mock_session_cls: MagicMock,
) -> None:
    provider, mock_client = _make_provider(mock_session_cls)
    events = [
        {"contentBlockStart": {"start": {}}},
        {"contentBlockDelta": {"delta": {"text": "Hello"}}},
        {"contentBlockStop": {}},
        {"messageStop": {"stopReason": "max_tokens"}},
    ]
    mock_client.converse_stream.return_value = _stream_response(events)

    response = provider.stream(
        model_id="bedrock/amazon.titan-text-express-v1",
        messages=[llm.messages.user("hello")],
        toolkit=EMPTY_TOOLKIT,
    )
    list(response.chunk_stream())

    assert response.finish_reason == llm.FinishReason.MAX_TOKENS


@patch("boto3.Session")
def test_stream_handles_text_delta_without_start(
    mock_session_cls: MagicMock,
) -> None:
    provider, mock_client = _make_provider(mock_session_cls)
    events = [
        {"contentBlockDelta": {"delta": {"text": "Hello"}}},
        {"contentBlockDelta": {"delta": {"text": " world!"}}},
        {"contentBlockStop": {}},
        {"messageStop": {"stopReason": "end_turn"}},
    ]
    mock_client.converse_stream.return_value = _stream_response(events)

    response = provider.stream(
        model_id="bedrock/amazon.nova-micro-v1:0",
        messages=[llm.messages.user("hello")],
        toolkit=EMPTY_TOOLKIT,
    )
    chunks = list(response.chunk_stream())

    assert chunks[0].type == "text_start_chunk"
    assert chunks[1].type == "text_chunk"
    assert chunks[1].delta == "Hello"
    assert chunks[2].type == "text_chunk"
    assert chunks[2].delta == " world!"


@patch("boto3.Session")
def test_context_call_and_stream(mock_session_cls: MagicMock) -> None:
    provider, mock_client = _make_provider(mock_session_cls)
    ctx = llm.Context(deps=None)

    mock_client.converse.return_value = _basic_converse_response(
        content=[{"text": "Hello"}],
    )
    response = provider.context_call(
        ctx=ctx,
        model_id="bedrock/amazon.titan-text-express-v1",
        messages=[llm.messages.user("hello")],
        toolkit=EMPTY_CONTEXT_TOOLKIT,
    )
    assert response.texts[0].text == "Hello"

    events = [
        {"contentBlockStart": {"start": {}}},
        {"contentBlockDelta": {"delta": {"text": "Hi"}}},
        {"contentBlockStop": {}},
        {"messageStop": {"stopReason": "end_turn"}},
    ]
    mock_client.converse_stream.return_value = _stream_response(events)
    stream = provider.context_stream(
        ctx=ctx,
        model_id="bedrock/amazon.titan-text-express-v1",
        messages=[llm.messages.user("hello")],
        toolkit=EMPTY_CONTEXT_TOOLKIT,
    )
    list(stream.chunk_stream())


@pytest.mark.asyncio
@patch("boto3.Session")
async def test_call_async_and_context_async(mock_session_cls: MagicMock) -> None:
    provider, mock_client = _make_provider(mock_session_cls)
    ctx = llm.Context(deps=None)

    mock_client.converse.return_value = _basic_converse_response(
        content=[{"text": "Hello"}],
    )
    response = await provider.call_async(
        model_id="bedrock/amazon.titan-text-express-v1",
        messages=[llm.messages.user("hello")],
        toolkit=EMPTY_ASYNC_TOOLKIT,
    )
    assert response.texts[0].text == "Hello"

    response = await provider.context_call_async(
        ctx=ctx,
        model_id="bedrock/amazon.titan-text-express-v1",
        messages=[llm.messages.user("hello")],
        toolkit=EMPTY_ASYNC_CONTEXT_TOOLKIT,
    )
    assert response.texts[0].text == "Hello"


@pytest.mark.asyncio
@patch("boto3.Session")
async def test_context_stream_async(mock_session_cls: MagicMock) -> None:
    provider, mock_client = _make_provider(mock_session_cls)
    ctx = llm.Context(deps=None)

    events = [
        {"contentBlockStart": {"start": {}}},
        {"contentBlockDelta": {"delta": {"text": "Hi"}}},
        {"contentBlockStop": {}},
        {"messageStop": {"stopReason": "end_turn"}},
    ]
    mock_client.converse_stream.return_value = _stream_response(events)

    stream = await provider.context_stream_async(
        ctx=ctx,
        model_id="bedrock/amazon.titan-text-express-v1",
        messages=[llm.messages.user("hello")],
        toolkit=EMPTY_ASYNC_CONTEXT_TOOLKIT,
    )
    await stream.finish()


@pytest.mark.asyncio
@patch("boto3.Session")
async def test_stream_async_exception_propagation(
    mock_session_cls: MagicMock,
) -> None:
    provider, mock_client = _make_provider(mock_session_cls)

    def event_iterator() -> Iterator[dict[str, Any]]:
        yield {"contentBlockStart": {"start": {}}}
        raise ValueError("Stream error during iteration")

    mock_client.converse_stream.return_value = {"stream": event_iterator()}

    response = await provider.stream_async(
        model_id="bedrock/amazon.titan-text-express-v1",
        messages=[llm.messages.user("hello")],
        toolkit=EMPTY_ASYNC_TOOLKIT,
    )

    with pytest.raises(ValueError, match="Stream error during iteration"):
        await response.finish()


# ==========================================================================
# ImportError tests
# ==========================================================================


def test_boto3_import_error(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test BedrockBoto3Provider raises ImportError when boto3 is unavailable."""
    modules_to_remove = [
        "mirascope.llm.providers.bedrock.boto3.provider",
        "mirascope.llm.providers.bedrock.boto3",
    ]
    original_modules = {name: sys.modules.get(name) for name in modules_to_remove}
    for name in modules_to_remove:
        sys.modules.pop(name, None)

    original_import = builtins.__import__

    def mock_import(name: str, *args: Any, **kwargs: Any) -> ModuleType:  # noqa: ANN401
        if name == "boto3" or name.startswith("boto3."):
            raise ImportError(f"No module named '{name}'")
        return original_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", mock_import)

    try:
        provider_module = importlib.import_module(
            "mirascope.llm.providers.bedrock.boto3.provider"
        )

        with pytest.raises(ImportError, match="bedrock"):
            provider_module.BedrockBoto3Provider()
    finally:
        for name, module in original_modules.items():
            if module is None:
                sys.modules.pop(name, None)
            else:
                sys.modules[name] = module
