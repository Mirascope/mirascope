"""Tests for RequestyProvider."""

import logging
import os

import pytest

from mirascope import llm
from mirascope.llm.providers.openai.completions._utils import (
    CompletionsModelFeatureInfo,
    encode_request,
)
from mirascope.llm.providers.requesty.provider import RequestyProvider
from mirascope.llm.tools import Toolkit


def test_requesty_provider_initialization() -> None:
    """Test RequestyProvider initialization with api_key."""
    provider = RequestyProvider(api_key="test-api-key")
    assert provider.id == "requesty"
    assert provider.default_scope == []


def test_requesty_provider_missing_api_key() -> None:
    """Test RequestyProvider raises error when API key is missing."""
    original_key = os.environ.pop("REQUESTY_API_KEY", None)
    try:
        with pytest.raises(ValueError) as exc_info:
            RequestyProvider()
        assert "Requesty API key is required" in str(exc_info.value)
        assert "REQUESTY_API_KEY" in str(exc_info.value)
    finally:
        if original_key is not None:
            os.environ["REQUESTY_API_KEY"] = original_key


def test_requesty_provider_uses_env_var() -> None:
    """Test RequestyProvider uses REQUESTY_API_KEY from environment."""
    original_key = os.environ.get("REQUESTY_API_KEY")
    os.environ["REQUESTY_API_KEY"] = "env-test-key"
    try:
        provider = RequestyProvider()
        assert provider.id == "requesty"
    finally:
        if original_key is not None:
            os.environ["REQUESTY_API_KEY"] = original_key
        else:
            os.environ.pop("REQUESTY_API_KEY", None)


def test_requesty_provider_default_base_url() -> None:
    """Test RequestyProvider uses the Requesty router by default."""
    provider = RequestyProvider(api_key="test-key")
    assert str(provider.client.base_url) == "https://router.requesty.ai/v1/"
    assert str(provider.async_client.base_url) == "https://router.requesty.ai/v1/"


def test_requesty_provider_custom_base_url() -> None:
    """Test RequestyProvider with custom base_url."""
    provider = RequestyProvider(
        api_key="test-key", base_url="https://router.eu.requesty.ai/v1"
    )
    assert provider.id == "requesty"
    assert str(provider.client.base_url) == "https://router.eu.requesty.ai/v1/"


def test_requesty_provider_model_name() -> None:
    """Test RequestyProvider strips 'requesty/' prefix from model_id."""
    provider = RequestyProvider(api_key="test-key")
    assert provider._model_name("requesty/openai/gpt-4o-mini") == "openai/gpt-4o-mini"  # pyright: ignore[reportPrivateUsage]
    assert provider._model_name("openai/gpt-4o-mini") == "openai/gpt-4o-mini"  # pyright: ignore[reportPrivateUsage]
    assert (
        provider._model_name("anthropic/claude-sonnet-4-5")  # pyright: ignore[reportPrivateUsage]
        == "anthropic/claude-sonnet-4-5"
    )
    assert provider._model_name("requesty/claude-sonnet-4-5") == "claude-sonnet-4-5"  # pyright: ignore[reportPrivateUsage]


def test_requesty_provider_model_feature_info_openai_models() -> None:
    """Test _model_feature_info returns OpenAI feature info for openai/ models."""
    provider = RequestyProvider(api_key="test-key")
    # gpt-4o-2024-05-13 doesn't support strict
    info = provider._model_feature_info("openai/gpt-4o-2024-05-13")  # pyright: ignore[reportPrivateUsage]
    assert (
        info.strict_support is False
    )  # gpt-4o-2024-05-13 is in MODELS_WITHOUT_JSON_SCHEMA_SUPPORT
    assert (
        info.is_reasoning_model is False
    )  # gpt-4o-2024-05-13 is in NON_REASONING_MODELS

    # gpt-4o supports strict
    info = provider._model_feature_info("requesty/openai/gpt-4o")  # pyright: ignore[reportPrivateUsage]
    assert info.strict_support is True
    assert info.is_reasoning_model is False

    # o1 is a reasoning model
    info = provider._model_feature_info("openai/o1")  # pyright: ignore[reportPrivateUsage]
    assert info.is_reasoning_model is True


def test_requesty_provider_model_feature_info_non_openai_models() -> None:
    """Test _model_feature_info returns empty info for non-openai/ models."""
    provider = RequestyProvider(api_key="test-key")
    info = provider._model_feature_info("anthropic/claude-sonnet-4-5")  # pyright: ignore[reportPrivateUsage]
    assert info == CompletionsModelFeatureInfo()

    info = provider._model_feature_info("requesty/anthropic/claude-sonnet-4-5")  # pyright: ignore[reportPrivateUsage]
    assert info == CompletionsModelFeatureInfo()

    info = provider._model_feature_info("claude-sonnet-4-5")  # pyright: ignore[reportPrivateUsage]
    assert info == CompletionsModelFeatureInfo()


def test_requesty_reasoning_model_temperature_warning(
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Test that reasoning models via Requesty skip temperature with warning.

    o1 is not in NON_REASONING_MODELS, so it's treated as a reasoning model.
    When accessed via Requesty, _model_feature_info returns info with
    is_reasoning_model=True. Temperature should be skipped with a warning.

    This is a unit test that calls encode_request directly to avoid network calls.
    """
    provider = RequestyProvider(api_key="test-key")
    model_id = "requesty/openai/o1"

    # Get the feature_info that would be used
    feature_info = provider._model_feature_info(model_id)  # pyright: ignore[reportPrivateUsage]
    assert (
        feature_info.is_reasoning_model is True
    )  # Verify it's detected as reasoning model

    messages = [llm.messages.user("What is 2+2?")]
    toolkit = Toolkit([])

    with caplog.at_level(logging.WARNING):
        encode_request(
            model_id=model_id,
            messages=messages,
            tools=toolkit,
            format=None,
            params={"temperature": 0.5},
            feature_info=feature_info,
            provider_id="requesty",
        )

    assert "Skipping unsupported parameter: temperature" in caplog.text


def test_requesty_non_reasoning_model_accepts_temperature(
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Test that non-reasoning OpenAI models via Requesty accept temperature.

    gpt-4o is in NON_REASONING_MODELS, so temperature should be accepted without warning.
    """
    provider = RequestyProvider(api_key="test-key")
    model_id = "requesty/openai/gpt-4o"

    feature_info = provider._model_feature_info(model_id)  # pyright: ignore[reportPrivateUsage]
    assert feature_info.is_reasoning_model is False

    messages = [llm.messages.user("Say hello")]
    toolkit = Toolkit([])

    with caplog.at_level(logging.WARNING):
        encode_request(
            model_id=model_id,
            messages=messages,
            tools=toolkit,
            format=None,
            params={"temperature": 0.5},
            feature_info=feature_info,
            provider_id="requesty",
        )

    assert "Skipping unsupported parameter: temperature" not in caplog.text


def test_requesty_anthropic_model_accepts_temperature(
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Test that Anthropic models via Requesty accept temperature.

    Non-OpenAI models use empty CompletionsModelFeatureInfo, which sets
    is_reasoning_model=None (treated as False), so temperature should be
    accepted without warning.
    """
    provider = RequestyProvider(api_key="test-key")
    model_id = "requesty/anthropic/claude-sonnet-4-5"

    feature_info = provider._model_feature_info(model_id)  # pyright: ignore[reportPrivateUsage]
    assert feature_info == CompletionsModelFeatureInfo()

    messages = [llm.messages.user("Say hello")]
    toolkit = Toolkit([])

    with caplog.at_level(logging.WARNING):
        encode_request(
            model_id=model_id,
            messages=messages,
            tools=toolkit,
            format=None,
            params={"temperature": 0.5},
            feature_info=feature_info,
            provider_id="requesty",
        )

    assert "Skipping unsupported parameter: temperature" not in caplog.text
