"""Tests for AnthropicBedrockClient."""

import pytest

from mirascope import llm


def test_context_manager() -> None:
    """Test nested context manager behavior and get_client() integration."""
    global_client = llm.get_client("anthropic-bedrock")

    client1 = llm.client("anthropic-bedrock", aws_region="us-west-2")
    client2 = llm.client("anthropic-bedrock", aws_region="us-east-1")

    assert llm.get_client("anthropic-bedrock") is global_client

    with client1 as ctx1:
        assert ctx1 is client1
        assert llm.get_client("anthropic-bedrock") is client1

        with client2 as ctx2:
            assert ctx2 is client2
            assert llm.get_client("anthropic-bedrock") is client2

        assert llm.get_client("anthropic-bedrock") is client1

    assert llm.get_client("anthropic-bedrock") is global_client


def test_client_caching() -> None:
    """Test that client() returns cached instances for identical parameters."""
    client1 = llm.client("anthropic-bedrock", aws_region="us-west-2")
    client2 = llm.client("anthropic-bedrock", aws_region="us-west-2")
    assert client1 is client2

    client3 = llm.client("anthropic-bedrock", aws_region="us-east-1")
    assert client1 is not client3

    client4 = llm.client("anthropic-bedrock", aws_access_key="key1")
    client5 = llm.client("anthropic-bedrock", aws_access_key="key2")
    assert client4 is not client5

    client6 = llm.client("anthropic-bedrock", aws_profile="profile1")
    client7 = llm.client("anthropic-bedrock", aws_profile="profile2")
    assert client6 is not client7

    client8 = llm.client("anthropic-bedrock", base_url="https://custom.example.com")
    client9 = llm.client("anthropic-bedrock", base_url="https://different.example.com")
    assert client8 is not client9

    client10 = llm.client("anthropic-bedrock")
    client11 = llm.get_client("anthropic-bedrock")
    assert client10 is client11


def test_client_env_var_fallback(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test that client() falls back to environment variables."""
    monkeypatch.setenv("AWS_REGION", "eu-west-1")
    bedrock_client = llm.client("anthropic-bedrock")
    assert bedrock_client.client.aws_region == "eu-west-1"

    monkeypatch.setenv("AWS_PROFILE", "test-profile")
    bedrock_client2 = llm.client("anthropic-bedrock", aws_region="us-west-2")
    assert bedrock_client2.client.aws_profile == "test-profile"

    monkeypatch.setenv("AWS_ACCESS_KEY_ID", "test-access-key")
    bedrock_client3 = llm.client("anthropic-bedrock")
    assert bedrock_client3.client.aws_access_key == "test-access-key"

    monkeypatch.setenv("AWS_SECRET_ACCESS_KEY", "test-secret-key")
    bedrock_client4 = llm.client("anthropic-bedrock")
    assert bedrock_client4.client.aws_secret_key == "test-secret-key"
