"""Tests for TogetherProvider."""

import os

import pytest

from mirascope.llm.providers.together.provider import TogetherProvider


def test_together_provider_initialization() -> None:
    """Test TogetherProvider initialization with api_key."""
    provider = TogetherProvider(api_key="test-api-key")
    assert provider.id == "together"
    assert provider.default_scope == []


def test_together_provider_missing_api_key() -> None:
    """Test TogetherProvider raises error when API key is missing."""
    original_key = os.environ.pop("TOGETHER_API_KEY", None)
    try:
        with pytest.raises(ValueError) as exc_info:
            TogetherProvider()
        assert "Together API key is required" in str(exc_info.value)
        assert "TOGETHER_API_KEY" in str(exc_info.value)
    finally:
        if original_key is not None:
            os.environ["TOGETHER_API_KEY"] = original_key


def test_together_provider_uses_env_var() -> None:
    """Test TogetherProvider uses TOGETHER_API_KEY from environment."""
    original_key = os.environ.get("TOGETHER_API_KEY")
    os.environ["TOGETHER_API_KEY"] = "env-test-key"
    try:
        provider = TogetherProvider()
        assert provider.id == "together"
    finally:
        if original_key is not None:
            os.environ["TOGETHER_API_KEY"] = original_key
        else:
            os.environ.pop("TOGETHER_API_KEY", None)


def test_together_provider_custom_base_url() -> None:
    """Test TogetherProvider with custom base_url."""
    provider = TogetherProvider(
        api_key="test-key", base_url="https://custom.together.xyz/v1"
    )
    assert provider.id == "together"
