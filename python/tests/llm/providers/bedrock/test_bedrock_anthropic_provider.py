"""Tests for BedrockAnthropicProvider."""

import pytest
from anthropic import types

from mirascope.llm.messages import user
from mirascope.llm.providers.bedrock.anthropic import (
    BedrockAnthropicProvider,
    BedrockAnthropicRoutedProvider,
)
from mirascope.llm.providers.bedrock.anthropic._utils import (
    bedrock_anthropic_model_name,
    decode_response,
    encode_request,
)
from mirascope.llm.providers.bedrock.anthropic.provider import (
    AsyncBedrockAnthropicApiKeyClient,
    BedrockAnthropicApiKeyClient,
)


def test_bedrock_anthropic_provider_initialization() -> None:
    """Test BedrockAnthropicProvider initialization with default settings."""
    provider = BedrockAnthropicProvider()
    assert provider.id == "bedrock:anthropic"
    assert provider.client is not None
    assert provider.async_client is not None


def test_bedrock_anthropic_provider_initialization_with_credentials() -> None:
    """Test BedrockAnthropicProvider initialization with AWS credentials."""
    provider = BedrockAnthropicProvider(
        aws_region="us-east-1",
        aws_access_key="test-access-key",
        aws_secret_key="test-secret-key",
        aws_session_token="test-session-token",
    )
    assert provider.client is not None
    assert provider.async_client is not None


def test_bedrock_anthropic_provider_default_scope() -> None:
    """Test BedrockAnthropicProvider has correct default scopes."""
    provider = BedrockAnthropicProvider()
    assert "bedrock/anthropic." in provider.default_scope
    assert "bedrock/us.anthropic." in provider.default_scope


def test_bedrock_anthropic_provider_get_error_status() -> None:
    """Test BedrockAnthropicProvider get_error_status returns status code."""
    provider = BedrockAnthropicProvider()

    class DummyError(Exception):
        status_code = 418

    assert provider.get_error_status(DummyError()) == 418


def test_bedrock_anthropic_provider_model_name() -> None:
    """Test BedrockAnthropicProvider _model_name strips prefix."""
    provider = BedrockAnthropicProvider()
    assert (
        provider._model_name("bedrock/anthropic.claude-3-5-sonnet-20241022-v1:0")  # pyright: ignore[reportPrivateUsage]
        == "anthropic.claude-3-5-sonnet-20241022-v1:0"
    )


def test_bedrock_anthropic_routed_provider_id() -> None:
    """Test BedrockAnthropicRoutedProvider uses 'bedrock' as provider id."""
    provider = BedrockAnthropicRoutedProvider()
    assert provider.id == "bedrock"


def test_bedrock_anthropic_model_name_strips_prefix() -> None:
    """Test bedrock_anthropic_model_name strips 'bedrock/' prefix."""
    assert (
        bedrock_anthropic_model_name(
            "bedrock/anthropic.claude-3-5-sonnet-20241022-v1:0"
        )
        == "anthropic.claude-3-5-sonnet-20241022-v1:0"
    )


def test_bedrock_anthropic_model_name_preserves_inference_profile() -> None:
    """Test bedrock_anthropic_model_name handles inference profile IDs."""
    assert (
        bedrock_anthropic_model_name(
            "bedrock/us.anthropic.claude-3-5-sonnet-20241022-v1:0"
        )
        == "us.anthropic.claude-3-5-sonnet-20241022-v1:0"
    )


def test_bedrock_anthropic_encode_request_sets_model() -> None:
    """Test encode_request uses the Bedrock model ID."""
    _, _, kwargs = encode_request(
        model_id="bedrock/anthropic.claude-3-5-sonnet-20241022-v1:0",
        messages=[user("hello")],
        tools=None,
        format=None,
        params={},
    )
    assert kwargs["model"] == "anthropic.claude-3-5-sonnet-20241022-v1:0"


def test_bedrock_anthropic_encode_request_handles_inference_profile() -> None:
    """Test encode_request uses inference profile IDs correctly."""
    _, _, kwargs = encode_request(
        model_id="bedrock/us.anthropic.claude-3-5-sonnet-20241022-v1:0",
        messages=[user("hello")],
        tools=None,
        format=None,
        params={},
    )
    assert kwargs["model"] == "us.anthropic.claude-3-5-sonnet-20241022-v1:0"


def test_bedrock_anthropic_decode_response_sets_provider_id() -> None:
    """Test decode_response sets correct provider_id."""
    response = types.Message.model_validate(
        {
            "id": "msg_123",
            "type": "message",
            "role": "assistant",
            "content": [{"type": "text", "text": "hello"}],
            "model": "anthropic.claude-3-5-sonnet-20241022-v1:0",
            "stop_reason": "end_turn",
            "stop_sequence": None,
            "usage": {"input_tokens": 1, "output_tokens": 2},
        }
    )
    assistant_message, _, _ = decode_response(
        response,
        "bedrock/anthropic.claude-3-5-sonnet-20241022-v1:0",
        include_thoughts=False,
        provider_id="bedrock:anthropic",
    )
    assert assistant_message.provider_id == "bedrock:anthropic"


def test_bedrock_anthropic_decode_response_sets_model_name() -> None:
    """Test decode_response sets correct provider_model_name."""
    response = types.Message.model_validate(
        {
            "id": "msg_123",
            "type": "message",
            "role": "assistant",
            "content": [{"type": "text", "text": "hello"}],
            "model": "anthropic.claude-3-5-sonnet-20241022-v1:0",
            "stop_reason": "end_turn",
            "stop_sequence": None,
            "usage": {"input_tokens": 1, "output_tokens": 2},
        }
    )
    assistant_message, _, _ = decode_response(
        response,
        "bedrock/anthropic.claude-3-5-sonnet-20241022-v1:0",
        include_thoughts=False,
    )
    assert (
        assistant_message.provider_model_name
        == "anthropic.claude-3-5-sonnet-20241022-v1:0"
    )


def test_bedrock_anthropic_decode_response_with_routed_provider_id() -> None:
    """Test decode_response can use a different provider_id."""
    response = types.Message.model_validate(
        {
            "id": "msg_123",
            "type": "message",
            "role": "assistant",
            "content": [{"type": "text", "text": "hello"}],
            "model": "anthropic.claude-3-5-sonnet-20241022-v1:0",
            "stop_reason": "end_turn",
            "stop_sequence": None,
            "usage": {"input_tokens": 1, "output_tokens": 2},
        }
    )
    assistant_message, _, _ = decode_response(
        response,
        "bedrock/anthropic.claude-3-5-sonnet-20241022-v1:0",
        include_thoughts=False,
        provider_id="bedrock",
    )
    assert assistant_message.provider_id == "bedrock"
def test_bedrock_anthropic_provider_initialization_with_api_key() -> None:
    """Test BedrockAnthropicProvider initialization with API key."""
    provider = BedrockAnthropicProvider(
        api_key="test-api-key",
        aws_region="us-east-1",
    )
    assert isinstance(provider.client, BedrockAnthropicApiKeyClient)
    assert isinstance(provider.async_client, AsyncBedrockAnthropicApiKeyClient)


def test_bedrock_anthropic_provider_initialization_with_api_key_env(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test BedrockAnthropicProvider uses AWS_BEDROCK_ANTHROPIC_API_KEY env var."""
    monkeypatch.setenv("AWS_BEDROCK_ANTHROPIC_API_KEY", "env-api-key")
    monkeypatch.setenv("AWS_REGION", "us-west-2")
    provider = BedrockAnthropicProvider()
    assert isinstance(provider.client, BedrockAnthropicApiKeyClient)
    assert isinstance(provider.async_client, AsyncBedrockAnthropicApiKeyClient)


def test_bedrock_anthropic_provider_api_key_takes_priority(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test that explicit api_key takes priority over environment variable."""
    monkeypatch.setenv("AWS_BEDROCK_ANTHROPIC_API_KEY", "env-api-key")
    provider = BedrockAnthropicProvider(
        api_key="explicit-api-key",
        aws_region="us-east-1",
    )
    assert isinstance(provider.client, BedrockAnthropicApiKeyClient)
    assert provider.client._bearer_token == "explicit-api-key"  # pyright: ignore[reportPrivateUsage]


def test_bedrock_anthropic_provider_api_key_env_var_class_attribute() -> None:
    """Test BedrockAnthropicProvider has correct api_key_env_var."""
    assert BedrockAnthropicProvider.api_key_env_var == "AWS_BEDROCK_ANTHROPIC_API_KEY"


def test_bedrock_anthropic_provider_region_fallback(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test region resolution for API key auth uses correct fallback order."""
    monkeypatch.delenv("AWS_REGION", raising=False)
    monkeypatch.delenv("AWS_DEFAULT_REGION", raising=False)
    provider = BedrockAnthropicProvider(api_key="test-api-key")
    assert provider.client.aws_region == "us-east-1"


def test_bedrock_anthropic_provider_region_from_aws_region_env(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test region resolution prefers AWS_REGION environment variable."""
    monkeypatch.setenv("AWS_REGION", "eu-west-1")
    monkeypatch.setenv("AWS_DEFAULT_REGION", "ap-northeast-1")
    provider = BedrockAnthropicProvider(api_key="test-api-key")
    assert provider.client.aws_region == "eu-west-1"


def test_bedrock_anthropic_provider_region_from_aws_default_region_env(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test region resolution uses AWS_DEFAULT_REGION when AWS_REGION is not set."""
    monkeypatch.delenv("AWS_REGION", raising=False)
    monkeypatch.setenv("AWS_DEFAULT_REGION", "ap-northeast-1")
    provider = BedrockAnthropicProvider(api_key="test-api-key")
    assert provider.client.aws_region == "ap-northeast-1"


def test_bedrock_anthropic_api_key_client_prepare_request() -> None:
    """Test BedrockAnthropicApiKeyClient sets Bearer token in request."""
    import httpx

    client = BedrockAnthropicApiKeyClient(
        api_key="test-bearer-token",
        aws_region="us-east-1",
    )
    request = httpx.Request("POST", "https://example.com/messages")
    client._prepare_request(request)  # pyright: ignore[reportPrivateUsage]
    assert request.headers["Authorization"] == "Bearer test-bearer-token"


@pytest.mark.asyncio
async def test_async_bedrock_anthropic_api_key_client_prepare_request() -> None:
    """Test AsyncBedrockAnthropicApiKeyClient sets Bearer token in request."""
    import httpx

    client = AsyncBedrockAnthropicApiKeyClient(
        api_key="test-bearer-token",
        aws_region="us-east-1",
    )
    request = httpx.Request("POST", "https://example.com/messages")
    await client._prepare_request(request)  # pyright: ignore[reportPrivateUsage]
    assert request.headers["Authorization"] == "Bearer test-bearer-token"
