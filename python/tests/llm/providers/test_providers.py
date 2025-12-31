"""Tests for provider client functions."""

import os
import sys

import pytest

from mirascope import llm


def test_register_provider_anthropic() -> None:
    """Test that register_provider('anthropic') returns same instance on multiple calls."""
    provider = llm.register_provider("anthropic")
    provider2 = llm.register_provider("anthropic")

    assert isinstance(provider, llm.providers.AnthropicProvider)
    assert provider is provider2
    assert provider.client.api_key == os.getenv("ANTHROPIC_API_KEY")


def test_register_provider_google() -> None:
    """Test that register_provider('google') returns same instance on multiple calls."""
    provider = llm.register_provider("google")
    provider2 = llm.register_provider("google")

    assert isinstance(provider, llm.providers.GoogleProvider)
    assert provider is provider2
    assert provider.client._api_client.api_key == os.getenv("GOOGLE_API_KEY")  # pyright: ignore[reportPrivateUsage]


def test_register_provider_openai() -> None:
    """Test that register_provider('openai') returns same instance on multiple calls."""
    provider = llm.register_provider("openai")
    provider2 = llm.register_provider("openai")

    assert isinstance(provider, llm.providers.OpenAIProvider)
    assert provider is provider2
    assert provider.client.api_key == os.getenv("OPENAI_API_KEY")


@pytest.mark.skipif(sys.platform != "darwin", reason="MLX is only available on macOS")
def test_get_register_provider_mlx() -> None:
    """Test that register_provider('mlx') returns same instance on multiple calls."""
    provider = llm.register_provider("mlx")
    provider2 = llm.register_provider("mlx")
    assert isinstance(provider, llm.providers.MLXProvider)
    assert provider is provider2


def test_register_provider_unknown_provider() -> None:
    """Test that register_provider raises ValueError for unknown providers."""
    with pytest.raises(ValueError, match="Unknown provider: 'unknown'"):
        llm.register_provider("unknown")
