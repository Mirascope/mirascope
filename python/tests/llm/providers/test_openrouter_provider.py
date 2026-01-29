"""Tests for OpenRouterProvider."""

import logging
import os

import pytest

from mirascope import llm
from mirascope.llm.providers.openai.completions._utils import encode_request
from mirascope.llm.providers.openai.completions._utils.constants import (
    SKIP_MODEL_FEATURES,
)
from mirascope.llm.providers.openrouter.provider import OpenRouterProvider
from mirascope.llm.tools import Toolkit


def test_openrouter_provider_initialization() -> None:
    """Test OpenRouterProvider initialization with api_key."""
    provider = OpenRouterProvider(api_key="test-api-key")
    assert provider.id == "openrouter"
    assert provider.default_scope == []


def test_openrouter_provider_missing_api_key() -> None:
    """Test OpenRouterProvider raises error when API key is missing."""
    original_key = os.environ.pop("OPENROUTER_API_KEY", None)
    try:
        with pytest.raises(ValueError) as exc_info:
            OpenRouterProvider()
        assert "OpenRouter API key is required" in str(exc_info.value)
        assert "OPENROUTER_API_KEY" in str(exc_info.value)
    finally:
        if original_key is not None:
            os.environ["OPENROUTER_API_KEY"] = original_key


def test_openrouter_provider_uses_env_var() -> None:
    """Test OpenRouterProvider uses OPENROUTER_API_KEY from environment."""
    original_key = os.environ.get("OPENROUTER_API_KEY")
    os.environ["OPENROUTER_API_KEY"] = "env-test-key"
    try:
        provider = OpenRouterProvider()
        assert provider.id == "openrouter"
    finally:
        if original_key is not None:
            os.environ["OPENROUTER_API_KEY"] = original_key
        else:
            os.environ.pop("OPENROUTER_API_KEY", None)


def test_openrouter_provider_custom_base_url() -> None:
    """Test OpenRouterProvider with custom base_url."""
    provider = OpenRouterProvider(
        api_key="test-key", base_url="https://custom.openrouter.ai/v1"
    )
    assert provider.id == "openrouter"


def test_openrouter_provider_model_name() -> None:
    """Test OpenRouterProvider strips 'openrouter/' prefix from model_id."""
    provider = OpenRouterProvider(api_key="test-key")
    assert provider._model_name("openrouter/openai/gpt-4") == "openai/gpt-4"  # pyright: ignore[reportPrivateUsage]
    assert provider._model_name("openai/gpt-4") == "openai/gpt-4"  # pyright: ignore[reportPrivateUsage]
    assert provider._model_name("anthropic/claude-3-opus") == "anthropic/claude-3-opus"  # pyright: ignore[reportPrivateUsage]


def test_openrouter_provider_model_features_name_openai_models() -> None:
    """Test _model_features_name returns OpenAI model name for openai/ models."""
    provider = OpenRouterProvider(api_key="test-key")
    assert provider._model_features_name("openai/gpt-4") == "gpt-4"  # pyright: ignore[reportPrivateUsage]
    assert provider._model_features_name("openrouter/openai/gpt-4o") == "gpt-4o"  # pyright: ignore[reportPrivateUsage]
    assert provider._model_features_name("openai/o1") == "o1"  # pyright: ignore[reportPrivateUsage]


def test_openrouter_provider_model_features_name_non_openai_models() -> None:
    """Test _model_features_name returns SKIP_MODEL_FEATURES for non-openai/ models."""
    provider = OpenRouterProvider(api_key="test-key")
    assert (
        provider._model_features_name("anthropic/claude-3-opus")  # pyright: ignore[reportPrivateUsage]
        is SKIP_MODEL_FEATURES
    )
    assert (
        provider._model_features_name("openrouter/anthropic/claude-3-opus")  # pyright: ignore[reportPrivateUsage]
        is SKIP_MODEL_FEATURES
    )
    assert (
        provider._model_features_name("meta-llama/Llama-3.3-70B")  # pyright: ignore[reportPrivateUsage]
        is SKIP_MODEL_FEATURES
    )


def test_openrouter_reasoning_model_temperature_warning(
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Test that reasoning models via OpenRouter skip temperature with warning.

    o1 is not in NON_REASONING_MODELS, so it's treated as a reasoning model.
    When accessed via OpenRouter, _model_features_name returns "o1", which triggers
    reasoning model detection. Temperature should be skipped with a warning.

    This is a unit test that calls encode_request directly to avoid network calls.
    """
    provider = OpenRouterProvider(api_key="test-key")
    model_id = "openrouter/openai/o1"

    # Get the model_features_name that would be used
    features_name = provider._model_features_name(model_id)  # pyright: ignore[reportPrivateUsage]
    assert features_name == "o1"  # Verify it's detected as reasoning model

    messages = [llm.messages.user("What is 2+2?")]
    toolkit = Toolkit([])

    with caplog.at_level(logging.WARNING):
        encode_request(
            model_id=model_id,
            messages=messages,
            tools=toolkit,
            format=None,
            params={"temperature": 0.5},
            model_features_name=features_name,
        )

    assert "Skipping unsupported parameter: temperature" in caplog.text


def test_openrouter_non_reasoning_model_accepts_temperature(
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Test that non-reasoning OpenAI models via OpenRouter accept temperature.

    gpt-4o is in NON_REASONING_MODELS, so temperature should be accepted without warning.
    """
    provider = OpenRouterProvider(api_key="test-key")
    model_id = "openrouter/openai/gpt-4o"

    features_name = provider._model_features_name(model_id)  # pyright: ignore[reportPrivateUsage]
    assert features_name == "gpt-4o"

    messages = [llm.messages.user("Say hello")]
    toolkit = Toolkit([])

    with caplog.at_level(logging.WARNING):
        encode_request(
            model_id=model_id,
            messages=messages,
            tools=toolkit,
            format=None,
            params={"temperature": 0.5},
            model_features_name=features_name,
        )

    assert "Skipping unsupported parameter: temperature" not in caplog.text


def test_openrouter_anthropic_model_accepts_temperature(
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Test that Anthropic models via OpenRouter accept temperature.

    Non-OpenAI models use SKIP_MODEL_FEATURES, which sets is_reasoning_model=False,
    so temperature should be accepted without warning.
    """
    provider = OpenRouterProvider(api_key="test-key")
    model_id = "openrouter/anthropic/claude-3-5-sonnet"

    features_name = provider._model_features_name(model_id)  # pyright: ignore[reportPrivateUsage]
    assert features_name is SKIP_MODEL_FEATURES

    messages = [llm.messages.user("Say hello")]
    toolkit = Toolkit([])

    with caplog.at_level(logging.WARNING):
        encode_request(
            model_id=model_id,
            messages=messages,
            tools=toolkit,
            format=None,
            params={"temperature": 0.5},
            model_features_name=features_name,
        )

    assert "Skipping unsupported parameter: temperature" not in caplog.text
