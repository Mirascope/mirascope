"""Tests for XAIProvider."""

import os

import pytest

from mirascope.llm.providers.xai.provider import XAIProvider


def test_xai_provider_initialization_with_api_key() -> None:
    """`api_key` kwarg should populate both clients without touching the env."""
    provider = XAIProvider(api_key="test-api-key")
    assert provider.id == "xai"
    assert provider.default_scope == "xai/"
    assert provider.client.api_key == "test-api-key"
    assert provider.async_client.api_key == "test-api-key"


def test_xai_provider_missing_api_key() -> None:
    """No api_key, no XAI_API_KEY -> a clear ValueError naming the env var."""
    original_key = os.environ.pop("XAI_API_KEY", None)
    try:
        with pytest.raises(ValueError) as exc_info:
            XAIProvider()
        assert "xAI API key is required" in str(exc_info.value)
        assert "XAI_API_KEY" in str(exc_info.value)
    finally:
        if original_key is not None:
            os.environ["XAI_API_KEY"] = original_key


def test_xai_provider_uses_env_var() -> None:
    """`XAI_API_KEY` should be picked up when no explicit api_key is passed."""
    original_key = os.environ.get("XAI_API_KEY")
    os.environ["XAI_API_KEY"] = "env-test-key"
    try:
        provider = XAIProvider()
        assert provider.client.api_key == "env-test-key"
        assert provider.async_client.api_key == "env-test-key"
    finally:
        if original_key is not None:
            os.environ["XAI_API_KEY"] = original_key
        else:
            os.environ.pop("XAI_API_KEY", None)


def test_xai_provider_default_base_url() -> None:
    """Without an explicit base_url the xAI default should be used."""
    provider = XAIProvider(api_key="test-key")
    assert str(provider.client.base_url) == "https://api.x.ai/v1/"
    assert str(provider.async_client.base_url) == "https://api.x.ai/v1/"


def test_xai_provider_custom_base_url() -> None:
    """An explicit base_url should override the default for both clients."""
    provider = XAIProvider(api_key="test-key", base_url="https://custom.x.ai/v2")
    assert str(provider.client.base_url) == "https://custom.x.ai/v2/"
    assert str(provider.async_client.base_url) == "https://custom.x.ai/v2/"
