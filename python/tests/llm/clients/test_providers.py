"""Tests for provider get_client functions."""

import os
import sys

import pytest

from mirascope import llm


def test_get_client_anthropic() -> None:
    """Test that get_client('anthropic') returns same instance on multiple calls."""
    client1 = llm.get_client("anthropic")
    client2 = llm.get_client("anthropic")

    assert isinstance(client1, llm.clients.AnthropicClient)
    assert client1 is client2
    assert client1.client.api_key == os.getenv("ANTHROPIC_API_KEY")


def test_get_client_google() -> None:
    """Test that get_client('google') returns same instance on multiple calls."""
    client1 = llm.get_client("google")
    client2 = llm.get_client("google")

    assert isinstance(client1, llm.clients.GoogleClient)
    assert client1 is client2
    assert client1.client._api_client.api_key == os.getenv("GOOGLE_API_KEY")  # pyright: ignore[reportPrivateUsage]


def test_get_client_openai() -> None:
    """Test that get_client('openai') returns same instance on multiple calls."""
    client1 = llm.get_client("openai")
    client2 = llm.get_client("openai")

    assert isinstance(client1, llm.clients.OpenAICompletionsClient)
    assert client1 is client2
    assert client1.client.api_key == os.getenv("OPENAI_API_KEY")


def test_get_client_openai_responses() -> None:
    """Test that get_client('openai:responses') returns same instance on multiple calls."""
    client1 = llm.get_client("openai:responses")
    client2 = llm.get_client("openai:responses")

    assert isinstance(client1, llm.clients.OpenAIResponsesClient)
    assert client1 is client2
    assert client1.client.api_key == os.getenv("OPENAI_API_KEY")


@pytest.mark.skipif(sys.platform != "darwin", reason="MLX is only available on macOS")
def test_get_client_mlx() -> None:
    """Test that get_client('mlx') returns same instance on multiple calls."""
    client1 = llm.get_client("mlx")
    client2 = llm.get_client("mlx")
    assert isinstance(client1, llm.clients.MLXClient)
    assert client1 is client2


def test_get_client_unknown_provider() -> None:
    """Test that get_client raises ValueError for unknown providers."""
    with pytest.raises(ValueError, match="Unknown provider: unknown"):
        llm.get_client("unknown")  # pyright: ignore[reportArgumentType, reportCallIssue]
