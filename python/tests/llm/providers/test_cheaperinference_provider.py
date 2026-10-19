"""Tests for CheaperInferenceProvider."""

import logging
import os

import pytest

from mirascope import llm
from mirascope.llm.providers.cheaperinference.provider import CheaperInferenceProvider
from mirascope.llm.providers.openai.completions._utils import (
    CompletionsModelFeatureInfo,
    encode_request,
)
from mirascope.llm.tools import Toolkit


def test_cheaperinference_provider_initialization() -> None:
    """Test CheaperInferenceProvider initialization with api_key."""
    provider = CheaperInferenceProvider(api_key="test-api-key")
    assert provider.id == "cheaperinference"
    assert provider.default_scope == []


def test_cheaperinference_provider_missing_api_key() -> None:
    """Test CheaperInferenceProvider raises error when API key is missing."""
    original_key = os.environ.pop("CHEAPER_INFERENCE_API_KEY", None)
    try:
        with pytest.raises(ValueError) as exc_info:
            CheaperInferenceProvider()
        assert "Cheaper Inference API key is required" in str(exc_info.value)
        assert "CHEAPER_INFERENCE_API_KEY" in str(exc_info.value)
    finally:
        if original_key is not None:
            os.environ["CHEAPER_INFERENCE_API_KEY"] = original_key


def test_cheaperinference_provider_uses_env_var() -> None:
    """Test CheaperInferenceProvider uses CHEAPER_INFERENCE_API_KEY from environment."""
    original_key = os.environ.get("CHEAPER_INFERENCE_API_KEY")
    os.environ["CHEAPER_INFERENCE_API_KEY"] = "env-test-key"
    try:
        provider = CheaperInferenceProvider()
        assert provider.id == "cheaperinference"
    finally:
        if original_key is not None:
            os.environ["CHEAPER_INFERENCE_API_KEY"] = original_key
        else:
            os.environ.pop("CHEAPER_INFERENCE_API_KEY", None)


def test_cheaperinference_provider_default_base_url() -> None:
    """Test CheaperInferenceProvider uses the Cheaper Inference API by default."""
    provider = CheaperInferenceProvider(api_key="test-key")
    assert str(provider.client.base_url) == "https://api.cheaperinference.com/v1/"
    assert str(provider.async_client.base_url) == "https://api.cheaperinference.com/v1/"


def test_cheaperinference_provider_custom_base_url() -> None:
    """Test CheaperInferenceProvider with custom base_url."""
    provider = CheaperInferenceProvider(
        api_key="test-key", base_url="https://example.com/v1"
    )
    assert provider.id == "cheaperinference"
    assert str(provider.client.base_url) == "https://example.com/v1/"


def test_cheaperinference_provider_model_name() -> None:
    """Test CheaperInferenceProvider strips 'cheaperinference/' prefix from model_id."""
    provider = CheaperInferenceProvider(api_key="test-key")
    assert provider._model_name("cheaperinference/gpt-5.4-mini") == "gpt-5.4-mini"  # pyright: ignore[reportPrivateUsage]
    assert provider._model_name("gpt-5.4-mini") == "gpt-5.4-mini"  # pyright: ignore[reportPrivateUsage]
    assert (
        provider._model_name("cheaperinference/claude-sonnet-5")  # pyright: ignore[reportPrivateUsage]
        == "claude-sonnet-5"
    )


def test_cheaperinference_provider_model_feature_info_openai_models() -> None:
    """Test _model_feature_info returns OpenAI feature info for OpenAI models."""
    provider = CheaperInferenceProvider(api_key="test-key")
    # gpt-4o-2024-05-13 doesn't support strict
    info = provider._model_feature_info("cheaperinference/gpt-4o-2024-05-13")  # pyright: ignore[reportPrivateUsage]
    assert (
        info.strict_support is False
    )  # gpt-4o-2024-05-13 is in MODELS_WITHOUT_JSON_SCHEMA_SUPPORT
    assert (
        info.is_reasoning_model is False
    )  # gpt-4o-2024-05-13 is in NON_REASONING_MODELS

    # gpt-4o supports strict
    info = provider._model_feature_info("cheaperinference/gpt-4o")  # pyright: ignore[reportPrivateUsage]
    assert info.strict_support is True
    assert info.is_reasoning_model is False

    # o1 is a reasoning model
    info = provider._model_feature_info("cheaperinference/o1")  # pyright: ignore[reportPrivateUsage]
    assert info.is_reasoning_model is True


def test_cheaperinference_provider_model_feature_info_non_openai_models() -> None:
    """Test _model_feature_info returns empty info for non-OpenAI models."""
    provider = CheaperInferenceProvider(api_key="test-key")
    info = provider._model_feature_info("cheaperinference/claude-sonnet-5")  # pyright: ignore[reportPrivateUsage]
    assert info == CompletionsModelFeatureInfo()

    info = provider._model_feature_info("cheaperinference/deepseek-v4-flash")  # pyright: ignore[reportPrivateUsage]
    assert info == CompletionsModelFeatureInfo()

    info = provider._model_feature_info("gemini-3.1-pro")  # pyright: ignore[reportPrivateUsage]
    assert info == CompletionsModelFeatureInfo()


def test_cheaperinference_reasoning_model_temperature_warning(
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Test that reasoning models via Cheaper Inference skip temperature with warning.

    o1 is not in NON_REASONING_MODELS, so it's treated as a reasoning model.
    When accessed via Cheaper Inference, _model_feature_info returns info with
    is_reasoning_model=True. Temperature should be skipped with a warning.

    This is a unit test that calls encode_request directly to avoid network calls.
    """
    provider = CheaperInferenceProvider(api_key="test-key")
    model_id = "cheaperinference/o1"

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
            provider_id="cheaperinference",
        )

    assert "Skipping unsupported parameter: temperature" in caplog.text


def test_cheaperinference_non_reasoning_model_accepts_temperature(
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Test that non-reasoning OpenAI models via Cheaper Inference accept temperature.

    gpt-4o is in NON_REASONING_MODELS, so temperature should be accepted without warning.
    """
    provider = CheaperInferenceProvider(api_key="test-key")
    model_id = "cheaperinference/gpt-4o"

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
            provider_id="cheaperinference",
        )

    assert "Skipping unsupported parameter: temperature" not in caplog.text


def test_cheaperinference_anthropic_model_accepts_temperature(
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Test that Anthropic models via Cheaper Inference accept temperature.

    Non-OpenAI models use empty CompletionsModelFeatureInfo, which sets
    is_reasoning_model=None (treated as False), so temperature should be
    accepted without warning.
    """
    provider = CheaperInferenceProvider(api_key="test-key")
    model_id = "cheaperinference/claude-sonnet-5"

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
            provider_id="cheaperinference",
        )

    assert "Skipping unsupported parameter: temperature" not in caplog.text
