"""Tests for MiniMaxProvider."""

import os

import pytest

from mirascope.llm.providers.minimax import MiniMaxModelId, MiniMaxProvider
from mirascope.llm.providers.minimax.model_id import (
    MINIMAX_KNOWN_MODELS,
    model_name,
)


def test_minimax_provider_initialization() -> None:
    """Test MiniMaxProvider initialization with api_key."""
    provider = MiniMaxProvider(api_key="test-api-key")
    assert provider.id == "minimax"
    assert provider.default_scope == "minimax/"


def test_minimax_provider_missing_api_key() -> None:
    """Test MiniMaxProvider raises error when API key is missing."""
    original_key = os.environ.pop("MINIMAX_API_KEY", None)
    try:
        with pytest.raises(ValueError) as exc_info:
            MiniMaxProvider()
        assert "MiniMax API key is required" in str(exc_info.value)
        assert "MINIMAX_API_KEY" in str(exc_info.value)
    finally:
        if original_key is not None:
            os.environ["MINIMAX_API_KEY"] = original_key


def test_minimax_provider_uses_env_var() -> None:
    """Test MiniMaxProvider uses MINIMAX_API_KEY from environment."""
    original_key = os.environ.get("MINIMAX_API_KEY")
    os.environ["MINIMAX_API_KEY"] = "env-test-key"
    try:
        provider = MiniMaxProvider()
        assert provider.id == "minimax"
    finally:
        if original_key is not None:
            os.environ["MINIMAX_API_KEY"] = original_key
        else:
            os.environ.pop("MINIMAX_API_KEY", None)


def test_minimax_provider_custom_base_url() -> None:
    """Test MiniMaxProvider with custom base_url."""
    provider = MiniMaxProvider(
        api_key="test-key", base_url="https://custom.minimax.io/v1"
    )
    assert provider.id == "minimax"


def test_minimax_provider_default_base_url() -> None:
    """Test MiniMaxProvider uses MiniMax API endpoint by default."""
    assert MiniMaxProvider.default_base_url == "https://api.minimax.io/v1"


def test_minimax_provider_model_name_strips_prefix() -> None:
    """Test _model_name strips 'minimax/' prefix."""
    provider = MiniMaxProvider(api_key="test-key")
    assert provider._model_name("minimax/MiniMax-M2.7") == "MiniMax-M2.7"
    assert (
        provider._model_name("minimax/MiniMax-M2.7-highspeed")
        == "MiniMax-M2.7-highspeed"
    )


def test_minimax_provider_model_name_no_prefix() -> None:
    """Test _model_name handles model IDs without prefix."""
    provider = MiniMaxProvider(api_key="test-key")
    assert provider._model_name("MiniMax-M2.7") == "MiniMax-M2.7"


def test_minimax_provider_api_key_required() -> None:
    """Test that api_key_required is True."""
    assert MiniMaxProvider.api_key_required is True


def test_minimax_provider_api_key_env_var() -> None:
    """Test that api_key_env_var is set correctly."""
    assert MiniMaxProvider.api_key_env_var == "MINIMAX_API_KEY"


def test_minimax_provider_name() -> None:
    """Test that provider_name is 'MiniMax'."""
    assert MiniMaxProvider.provider_name == "MiniMax"


def test_minimax_known_models_includes_flagship() -> None:
    """Test that MINIMAX_KNOWN_MODELS exposes the registered model strings."""
    assert "minimax/MiniMax-M3" in MINIMAX_KNOWN_MODELS
    assert "minimax/MiniMax-M2.7" in MINIMAX_KNOWN_MODELS
    assert "minimax/MiniMax-M2.7-highspeed" in MINIMAX_KNOWN_MODELS


def test_minimax_model_name_helper_strips_prefix() -> None:
    """Test that model_name helper strips the 'minimax/' prefix."""
    assert model_name("minimax/MiniMax-M3") == "MiniMax-M3"
    assert model_name("minimax/MiniMax-M2.7") == "MiniMax-M2.7"


def test_minimax_model_name_helper_no_prefix() -> None:
    """Test that model_name helper passes through IDs without the prefix."""
    assert model_name("MiniMax-M3") == "MiniMax-M3"


def test_minimax_model_id_accepts_arbitrary_string() -> None:
    """Test that MiniMaxModelId accepts arbitrary strings (as `str` fallback)."""
    custom: MiniMaxModelId = "minimax/custom-future-model"
    assert custom == "minimax/custom-future-model"
