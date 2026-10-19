"""Tests for AtlasCloudProvider."""

import logging
import os

import pytest

from mirascope import llm
from mirascope.llm.providers.atlascloud.provider import AtlasCloudProvider
from mirascope.llm.providers.openai.completions._utils import (
    CompletionsModelFeatureInfo,
    encode_request,
)
from mirascope.llm.tools import Toolkit


def test_atlascloud_provider_initialization() -> None:
    """Test AtlasCloudProvider initialization with api_key."""
    provider = AtlasCloudProvider(api_key="test-api-key")
    assert provider.id == "atlascloud"
    assert provider.default_scope == []


def test_atlascloud_provider_missing_api_key() -> None:
    """Test AtlasCloudProvider raises error when API key is missing."""
    original_key = os.environ.pop("ATLASCLOUD_API_KEY", None)
    try:
        with pytest.raises(ValueError) as exc_info:
            AtlasCloudProvider()
        assert "Atlas Cloud API key is required" in str(exc_info.value)
        assert "ATLASCLOUD_API_KEY" in str(exc_info.value)
    finally:
        if original_key is not None:
            os.environ["ATLASCLOUD_API_KEY"] = original_key


def test_atlascloud_provider_uses_env_var() -> None:
    """Test AtlasCloudProvider uses ATLASCLOUD_API_KEY from environment."""
    original_key = os.environ.get("ATLASCLOUD_API_KEY")
    os.environ["ATLASCLOUD_API_KEY"] = "env-test-key"
    try:
        provider = AtlasCloudProvider()
        assert provider.id == "atlascloud"
    finally:
        if original_key is not None:
            os.environ["ATLASCLOUD_API_KEY"] = original_key
        else:
            os.environ.pop("ATLASCLOUD_API_KEY", None)


def test_atlascloud_provider_default_base_url() -> None:
    """Test AtlasCloudProvider uses the Atlas Cloud API by default."""
    provider = AtlasCloudProvider(api_key="test-key")
    assert str(provider.client.base_url) == "https://api.atlascloud.ai/v1/"
    assert str(provider.async_client.base_url) == "https://api.atlascloud.ai/v1/"


def test_atlascloud_provider_custom_base_url() -> None:
    """Test AtlasCloudProvider with custom base_url."""
    provider = AtlasCloudProvider(api_key="test-key", base_url="https://example.com/v1")
    assert provider.id == "atlascloud"
    assert str(provider.client.base_url) == "https://example.com/v1/"


def test_atlascloud_provider_model_name() -> None:
    """Test AtlasCloudProvider strips 'atlascloud/' prefix from model_id."""
    provider = AtlasCloudProvider(api_key="test-key")
    assert (
        provider._model_name("atlascloud/openai/gpt-4.1-mini")  # pyright: ignore[reportPrivateUsage]
        == "openai/gpt-4.1-mini"
    )
    assert provider._model_name("openai/gpt-4.1-mini") == "openai/gpt-4.1-mini"  # pyright: ignore[reportPrivateUsage]
    assert (
        provider._model_name("anthropic/claude-sonnet-4.6")  # pyright: ignore[reportPrivateUsage]
        == "anthropic/claude-sonnet-4.6"
    )
    assert provider._model_name("atlascloud/claude-sonnet-4.6") == "claude-sonnet-4.6"  # pyright: ignore[reportPrivateUsage]


def test_atlascloud_provider_model_feature_info_openai_models() -> None:
    """Test _model_feature_info returns OpenAI feature info for openai/ models."""
    provider = AtlasCloudProvider(api_key="test-key")
    # gpt-4o-2024-05-13 doesn't support strict
    info = provider._model_feature_info("openai/gpt-4o-2024-05-13")  # pyright: ignore[reportPrivateUsage]
    assert (
        info.strict_support is False
    )  # gpt-4o-2024-05-13 is in MODELS_WITHOUT_JSON_SCHEMA_SUPPORT
    assert (
        info.is_reasoning_model is False
    )  # gpt-4o-2024-05-13 is in NON_REASONING_MODELS

    # gpt-4o supports strict
    info = provider._model_feature_info("atlascloud/openai/gpt-4o")  # pyright: ignore[reportPrivateUsage]
    assert info.strict_support is True
    assert info.is_reasoning_model is False

    # o1 is a reasoning model
    info = provider._model_feature_info("openai/o1")  # pyright: ignore[reportPrivateUsage]
    assert info.is_reasoning_model is True


def test_atlascloud_provider_model_feature_info_non_openai_models() -> None:
    """Test _model_feature_info returns empty info for non-openai/ models."""
    provider = AtlasCloudProvider(api_key="test-key")
    info = provider._model_feature_info("anthropic/claude-sonnet-4.6")  # pyright: ignore[reportPrivateUsage]
    assert info == CompletionsModelFeatureInfo()

    info = provider._model_feature_info("atlascloud/anthropic/claude-sonnet-4.6")  # pyright: ignore[reportPrivateUsage]
    assert info == CompletionsModelFeatureInfo()

    info = provider._model_feature_info("claude-sonnet-4.6")  # pyright: ignore[reportPrivateUsage]
    assert info == CompletionsModelFeatureInfo()


def test_atlascloud_reasoning_model_temperature_warning(
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Test that reasoning models via Atlas Cloud skip temperature with warning.

    o1 is not in NON_REASONING_MODELS, so it's treated as a reasoning model.
    When accessed via Atlas Cloud, _model_feature_info returns info with
    is_reasoning_model=True. Temperature should be skipped with a warning.

    This is a unit test that calls encode_request directly to avoid network calls.
    """
    provider = AtlasCloudProvider(api_key="test-key")
    model_id = "atlascloud/openai/o1"

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
            provider_id="atlascloud",
        )

    assert "Skipping unsupported parameter: temperature" in caplog.text


def test_atlascloud_non_reasoning_model_accepts_temperature(
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Test that non-reasoning OpenAI models via Atlas Cloud accept temperature.

    gpt-4o is in NON_REASONING_MODELS, so temperature should be accepted without warning.
    """
    provider = AtlasCloudProvider(api_key="test-key")
    model_id = "atlascloud/openai/gpt-4o"

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
            provider_id="atlascloud",
        )

    assert "Skipping unsupported parameter: temperature" not in caplog.text


def test_atlascloud_anthropic_model_accepts_temperature(
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Test that Anthropic models via Atlas Cloud accept temperature.

    Non-OpenAI models use empty CompletionsModelFeatureInfo, which sets
    is_reasoning_model=None (treated as False), so temperature should be
    accepted without warning.
    """
    provider = AtlasCloudProvider(api_key="test-key")
    model_id = "atlascloud/anthropic/claude-sonnet-4.6"

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
            provider_id="atlascloud",
        )

    assert "Skipping unsupported parameter: temperature" not in caplog.text
