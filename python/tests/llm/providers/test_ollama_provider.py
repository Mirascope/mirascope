"""Tests for OllamaProvider."""

import os

from mirascope.llm.providers.ollama.provider import OllamaProvider


def test_ollama_provider_initialization() -> None:
    """Test OllamaProvider initialization."""
    provider = OllamaProvider()
    assert provider.id == "ollama"
    assert provider.default_scope == "ollama/"


def test_ollama_provider_default_api_key() -> None:
    """Test OllamaProvider uses default 'ollama' api_key."""
    original_key = os.environ.pop("OLLAMA_API_KEY", None)
    try:
        provider = OllamaProvider()
        assert provider.client.api_key == "ollama"
    finally:
        if original_key is not None:
            os.environ["OLLAMA_API_KEY"] = original_key


def test_ollama_provider_api_key_from_env() -> None:
    """Test OllamaProvider uses OLLAMA_API_KEY from environment."""
    original_key = os.environ.get("OLLAMA_API_KEY")
    os.environ["OLLAMA_API_KEY"] = "env-test-key"
    try:
        provider = OllamaProvider()
        assert provider.client.api_key == "env-test-key"
    finally:
        if original_key is not None:
            os.environ["OLLAMA_API_KEY"] = original_key
        else:
            os.environ.pop("OLLAMA_API_KEY", None)


def test_ollama_provider_custom_base_url() -> None:
    """Test OllamaProvider with custom base_url."""
    provider = OllamaProvider(base_url="http://custom.ollama.local:11434/v1/")
    assert provider.id == "ollama"
    assert str(provider.client.base_url) == "http://custom.ollama.local:11434/v1/"


def test_ollama_provider_base_url_from_env() -> None:
    """Test OllamaProvider uses OLLAMA_BASE_URL from environment."""
    original_url = os.environ.get("OLLAMA_BASE_URL")
    os.environ["OLLAMA_BASE_URL"] = "http://remote-ollama:11434/v1/"
    try:
        provider = OllamaProvider()
        assert provider.id == "ollama"
        assert str(provider.client.base_url) == "http://remote-ollama:11434/v1/"
    finally:
        if original_url is not None:
            os.environ["OLLAMA_BASE_URL"] = original_url
        else:
            os.environ.pop("OLLAMA_BASE_URL", None)


def test_ollama_provider_default_base_url() -> None:
    """Test OllamaProvider uses default base_url."""
    original_url = os.environ.pop("OLLAMA_BASE_URL", None)
    try:
        provider = OllamaProvider()
        assert str(provider.client.base_url) == "http://localhost:11434/v1/"
    finally:
        if original_url is not None:
            os.environ["OLLAMA_BASE_URL"] = original_url


def test_ollama_provider_model_name() -> None:
    """Test OllamaProvider strips 'ollama/' prefix from model_id."""
    provider = OllamaProvider()
    assert provider._model_name("ollama/gemma3:4b") == "gemma3:4b"  # pyright: ignore[reportPrivateUsage]
    assert provider._model_name("gemma3:4b") == "gemma3:4b"  # pyright: ignore[reportPrivateUsage]
