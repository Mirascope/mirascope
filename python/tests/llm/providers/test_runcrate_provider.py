"""Tests for RuncrateProvider."""

import logging
import os

import pytest

from mirascope import llm
from mirascope.llm.providers.openai.completions._utils import (
    CompletionsModelFeatureInfo,
    encode_request,
)
from mirascope.llm.providers.runcrate.provider import RuncrateProvider
from mirascope.llm.tools import Toolkit


class _InspectableRuncrateProvider(RuncrateProvider):
    def model_name(self, model_id: str) -> str:
        return self._model_name(model_id)

    def model_feature_info(self, model_id: str) -> CompletionsModelFeatureInfo:
        return self._model_feature_info(model_id)


def test_runcrate_provider_initialization() -> None:
    """Test RuncrateProvider initialization with api_key."""
    provider = _InspectableRuncrateProvider(api_key="test-api-key")
    assert provider.id == "runcrate"
    assert provider.default_scope == []


def test_runcrate_provider_missing_api_key() -> None:
    """Test RuncrateProvider raises error when API key is missing."""
    original_key = os.environ.pop("RUNCRATE_API_KEY", None)
    try:
        with pytest.raises(ValueError) as exc_info:
            RuncrateProvider()
        assert "Runcrate API key is required" in str(exc_info.value)
        assert "RUNCRATE_API_KEY" in str(exc_info.value)
    finally:
        if original_key is not None:
            os.environ["RUNCRATE_API_KEY"] = original_key


def test_runcrate_provider_uses_env_var() -> None:
    """Test RuncrateProvider uses RUNCRATE_API_KEY from environment."""
    original_key = os.environ.get("RUNCRATE_API_KEY")
    os.environ["RUNCRATE_API_KEY"] = "env-test-key"
    try:
        provider = _InspectableRuncrateProvider()
        assert provider.client.api_key == "env-test-key"
    finally:
        if original_key is not None:
            os.environ["RUNCRATE_API_KEY"] = original_key
        else:
            os.environ.pop("RUNCRATE_API_KEY", None)


def test_runcrate_provider_default_base_url() -> None:
    """Test RuncrateProvider uses the Runcrate API by default."""
    provider = _InspectableRuncrateProvider(api_key="test-key")
    assert str(provider.client.base_url) == "https://api.runcrate.ai/v1/"
    assert str(provider.async_client.base_url) == "https://api.runcrate.ai/v1/"


def test_runcrate_provider_custom_base_url() -> None:
    """Test RuncrateProvider with custom base_url."""
    provider = _InspectableRuncrateProvider(
        api_key="test-key", base_url="https://example.com/v1"
    )
    assert str(provider.client.base_url) == "https://example.com/v1/"


def test_runcrate_provider_model_name() -> None:
    """Test RuncrateProvider strips only the 'runcrate/' prefix from model_id."""
    provider = _InspectableRuncrateProvider(api_key="test-key")
    assert (
        provider.model_name("runcrate/deepseek-ai/DeepSeek-V4.1-Flash")
        == "deepseek-ai/DeepSeek-V4.1-Flash"
    )
    assert provider.model_name("runcrate/openai/gpt-oss-120b") == "openai/gpt-oss-120b"
    assert provider.model_name("zai-org/GLM-5.3") == "zai-org/GLM-5.3"


def test_runcrate_provider_model_feature_info_is_empty_for_open_models() -> None:
    """Test open-weight IDs never pick up OpenAI API feature info."""
    provider = _InspectableRuncrateProvider(api_key="test-key")
    for model_id in (
        "runcrate/openai/gpt-oss-120b",
        "runcrate/deepseek-ai/DeepSeek-V4.1-Flash",
        "zai-org/GLM-5.3",
    ):
        assert provider.model_feature_info(model_id) == CompletionsModelFeatureInfo()


def test_runcrate_model_accepts_temperature(caplog: pytest.LogCaptureFixture) -> None:
    """Test that temperature is sent for Runcrate models, including gpt-oss.

    This is a unit test that calls encode_request directly to avoid network calls.
    """
    provider = _InspectableRuncrateProvider(api_key="test-key")
    model_id = "runcrate/openai/gpt-oss-120b"

    with caplog.at_level(logging.WARNING):
        encode_request(
            model_id=model_id,
            messages=[llm.messages.user("Say hello")],
            tools=Toolkit([]),
            format=None,
            params={"temperature": 0.5},
            feature_info=provider.model_feature_info(model_id),
            provider_id="runcrate",
        )

    assert "Skipping unsupported parameter: temperature" not in caplog.text
