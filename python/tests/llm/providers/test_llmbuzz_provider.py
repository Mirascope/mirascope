"""Tests for LLMBuzzProvider."""

import logging
import os

import pytest

from mirascope import llm
from mirascope.llm.providers.llmbuzz.provider import LLMBuzzProvider
from mirascope.llm.providers.openai.completions._utils import (
    CompletionsModelFeatureInfo,
    encode_request,
)
from mirascope.llm.tools import Toolkit


class _InspectableLLMBuzzProvider(LLMBuzzProvider):
    def model_name(self, model_id: str) -> str:
        return self._model_name(model_id)

    def model_feature_info(self, model_id: str) -> CompletionsModelFeatureInfo:
        return self._model_feature_info(model_id)


def test_llmbuzz_provider_initialization() -> None:
    """Test LLMBuzzProvider initialization with api_key."""
    provider = _InspectableLLMBuzzProvider(api_key="test-api-key")
    assert provider.id == "llmbuzz"
    assert provider.default_scope == []


def test_llmbuzz_provider_missing_api_key() -> None:
    """Test LLMBuzzProvider raises error when API key is missing."""
    original_key = os.environ.pop("LLM_BUZZ_API_KEY", None)
    try:
        with pytest.raises(ValueError) as exc_info:
            LLMBuzzProvider()
        assert "llm.buzz API key is required" in str(exc_info.value)
        assert "LLM_BUZZ_API_KEY" in str(exc_info.value)
    finally:
        if original_key is not None:
            os.environ["LLM_BUZZ_API_KEY"] = original_key


def test_llmbuzz_provider_uses_env_var() -> None:
    """Test LLMBuzzProvider uses LLM_BUZZ_API_KEY from environment."""
    original_key = os.environ.get("LLM_BUZZ_API_KEY")
    os.environ["LLM_BUZZ_API_KEY"] = "env-test-key"
    try:
        provider = _InspectableLLMBuzzProvider()
        assert provider.id == "llmbuzz"
    finally:
        if original_key is not None:
            os.environ["LLM_BUZZ_API_KEY"] = original_key
        else:
            os.environ.pop("LLM_BUZZ_API_KEY", None)


def test_llmbuzz_provider_default_base_url() -> None:
    """Test LLMBuzzProvider uses the llm.buzz API by default."""
    provider = _InspectableLLMBuzzProvider(api_key="test-key")
    assert str(provider.client.base_url) == "https://api.llm.buzz/api/v1/"
    assert str(provider.async_client.base_url) == "https://api.llm.buzz/api/v1/"


def test_llmbuzz_provider_custom_base_url() -> None:
    """Test LLMBuzzProvider with custom base_url."""
    provider = _InspectableLLMBuzzProvider(
        api_key="test-key", base_url="https://example.com/v1"
    )
    assert provider.id == "llmbuzz"
    assert str(provider.client.base_url) == "https://example.com/v1/"


def test_llmbuzz_provider_model_name() -> None:
    """Test LLMBuzzProvider strips 'llmbuzz/' prefix from model_id."""
    provider = _InspectableLLMBuzzProvider(api_key="test-key")
    assert (
        provider.model_name("llmbuzz/openai/gpt-4.1-mini") == "openai/gpt-4.1-mini"
    )
    assert provider.model_name("openai/gpt-4.1-mini") == "openai/gpt-4.1-mini"
    assert (
        provider.model_name("anthropic/claude-sonnet-4.6")
        == "anthropic/claude-sonnet-4.6"
    )
    assert provider.model_name("llmbuzz/claude-sonnet-4.6") == "claude-sonnet-4.6"


def test_llmbuzz_provider_model_feature_info_openai_models() -> None:
    """Test _model_feature_info returns OpenAI feature info for openai/ models."""
    provider = _InspectableLLMBuzzProvider(api_key="test-key")
    # gpt-4o-2024-05-13 doesn't support strict
    info = provider.model_feature_info("openai/gpt-4o-2024-05-13")
    assert (
        info.strict_support is False
    )  # gpt-4o-2024-05-13 is in MODELS_WITHOUT_JSON_SCHEMA_SUPPORT
    assert (
        info.is_reasoning_model is False
    )  # gpt-4o-2024-05-13 is in NON_REASONING_MODELS

    # gpt-4o supports strict
    info = provider.model_feature_info("llmbuzz/openai/gpt-4o")
    assert info.strict_support is True
    assert info.is_reasoning_model is False

    # o1 is a reasoning model
    info = provider.model_feature_info("openai/o1")
    assert info.is_reasoning_model is True


def test_llmbuzz_provider_model_feature_info_non_openai_models() -> None:
    """Test _model_feature_info returns empty info for non-openai/ models."""
    provider = _InspectableLLMBuzzProvider(api_key="test-key")
    info = provider.model_feature_info("anthropic/claude-sonnet-4.6")
    assert info == CompletionsModelFeatureInfo()

    info = provider.model_feature_info("llmbuzz/anthropic/claude-sonnet-4.6")
    assert info == CompletionsModelFeatureInfo()

    info = provider.model_feature_info("claude-sonnet-4.6")
    assert info == CompletionsModelFeatureInfo()


def test_llmbuzz_reasoning_model_temperature_warning(
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Test that reasoning models via llm.buzz skip temperature with warning.

    o1 is not in NON_REASONING_MODELS, so it's treated as a reasoning model.
    When accessed via llm.buzz, _model_feature_info returns info with
    is_reasoning_model=True. Temperature should be skipped with a warning.

    This is a unit test that calls encode_request directly to avoid network calls.
    """
    provider = _InspectableLLMBuzzProvider(api_key="test-key")
    model_id = "llmbuzz/openai/o1"

    # Get the feature_info that would be used
    feature_info = provider.model_feature_info(model_id)
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
            provider_id="llmbuzz",
        )

    assert "Skipping unsupported parameter: temperature" in caplog.text


def test_llmbuzz_non_reasoning_model_accepts_temperature(
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Test that non-reasoning OpenAI models via llm.buzz accept temperature.

    gpt-4o is in NON_REASONING_MODELS, so temperature should be accepted without warning.
    """
    provider = _InspectableLLMBuzzProvider(api_key="test-key")
    model_id = "llmbuzz/openai/gpt-4o"

    feature_info = provider.model_feature_info(model_id)
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
            provider_id="llmbuzz",
        )

    assert "Skipping unsupported parameter: temperature" not in caplog.text


def test_llmbuzz_anthropic_model_accepts_temperature(
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Test that Anthropic models via llm.buzz accept temperature.

    Non-OpenAI models use empty CompletionsModelFeatureInfo, which sets
    is_reasoning_model=None (treated as False), so temperature should be
    accepted without warning.
    """
    provider = _InspectableLLMBuzzProvider(api_key="test-key")
    model_id = "llmbuzz/anthropic/claude-sonnet-4.6"

    feature_info = provider.model_feature_info(model_id)
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
            provider_id="llmbuzz",
        )

    assert "Skipping unsupported parameter: temperature" not in caplog.text
