"""Tests for provider get_client functions."""

import os

import pytest

from mirascope.llm.clients import (
    AnthropicClient,
    GoogleClient,
    OpenAIClient,
    get_client,
)


def test_get_client_anthropic() -> None:
    """Test that get_client('anthropic') returns same instance on multiple calls."""
    client1 = get_client("anthropic")
    client2 = get_client("anthropic")

    assert isinstance(client1, AnthropicClient)
    assert client1 is client2
    assert client1.client.api_key == os.getenv("ANTHROPIC_API_KEY")


def test_get_client_google() -> None:
    """Test that get_client('google') returns same instance on multiple calls."""
    client1 = get_client("google")
    client2 = get_client("google")

    assert isinstance(client1, GoogleClient)
    assert client1 is client2
    assert client1.client._api_client.api_key == os.getenv("GOOGLE_API_KEY")


def test_get_client_openai() -> None:
    """Test that get_client('openai') returns same instance on multiple calls."""
    client1 = get_client("openai")
    client2 = get_client("openai")

    assert isinstance(client1, OpenAIClient)
    assert client1 is client2
    assert client1.client.api_key == os.getenv("OPENAI_API_KEY")


def test_get_client_unknown_provider() -> None:
    """Test that get_client raises ValueError for unknown providers."""
    with pytest.raises(ValueError, match="Unknown provider: unknown"):
        get_client("unknown")  # type: ignore
