"""Tests for CloudGPUProvider."""

import logging
import os

import pytest

from mirascope import llm
from mirascope.llm.providers.cloudgpu.provider import CloudGPUProvider
from mirascope.llm.providers.openai.completions._utils import (
    CompletionsModelFeatureInfo,
    encode_request,
)
from mirascope.llm.tools import Toolkit


class _InspectableCloudGPUProvider(CloudGPUProvider):
    def model_name(self, model_id: str) -> str:
        return self._model_name(model_id)

    def model_feature_info(self, model_id: str) -> CompletionsModelFeatureInfo:
        return self._model_feature_info(model_id)


def test_cloudgpu_provider_initialization() -> None:
    """Test CloudGPUProvider initialization with api_key."""
    provider = _InspectableCloudGPUProvider(api_key="test-api-key")
    assert provider.id == "cloudgpu"
    assert provider.default_scope == []


def test_cloudgpu_provider_missing_api_key() -> None:
    """Test CloudGPUProvider raises error when API key is missing."""
    original_key = os.environ.pop("CLOUDGPU_API_KEY", None)
    try:
        with pytest.raises(ValueError) as exc_info:
            CloudGPUProvider()
        assert "CloudGPU API key is required" in str(exc_info.value)
        assert "CLOUDGPU_API_KEY" in str(exc_info.value)
    finally:
        if original_key is not None:
            os.environ["CLOUDGPU_API_KEY"] = original_key


def test_cloudgpu_provider_uses_env_var() -> None:
    """Test CloudGPUProvider uses CLOUDGPU_API_KEY from environment."""
    original_key = os.environ.get("CLOUDGPU_API_KEY")
    os.environ["CLOUDGPU_API_KEY"] = "env-test-key"
    try:
        provider = _InspectableCloudGPUProvider()
        assert provider.client.api_key == "env-test-key"
    finally:
        if original_key is not None:
            os.environ["CLOUDGPU_API_KEY"] = original_key
        else:
            os.environ.pop("CLOUDGPU_API_KEY", None)


def test_cloudgpu_provider_default_base_url() -> None:
    """Test CloudGPUProvider uses the CloudGPU API by default."""
    provider = _InspectableCloudGPUProvider(api_key="test-key")
    assert str(provider.client.base_url) == "https://cloudgpu.app/v1/"
    assert str(provider.async_client.base_url) == "https://cloudgpu.app/v1/"


def test_cloudgpu_provider_custom_base_url() -> None:
    """Test CloudGPUProvider with custom base_url."""
    provider = _InspectableCloudGPUProvider(
        api_key="test-key", base_url="https://example.com/v1"
    )
    assert provider.id == "cloudgpu"
    assert str(provider.client.base_url) == "https://example.com/v1/"


def test_cloudgpu_provider_model_name() -> None:
    """Test CloudGPUProvider strips only the 'cloudgpu/' prefix from model_id."""
    provider = _InspectableCloudGPUProvider(api_key="test-key")
    assert provider.model_name("cloudgpu/deepseek-v4-flash") == "deepseek-v4-flash"
    assert provider.model_name("cloudgpu/kimi-k2.6") == "kimi-k2.6"
    assert provider.model_name("glm-5.3") == "glm-5.3"


def test_cloudgpu_provider_model_feature_info_is_empty() -> None:
    """Test CloudGPU model IDs never pick up OpenAI API feature info."""
    provider = _InspectableCloudGPUProvider(api_key="test-key")
    for model_id in (
        "cloudgpu/deepseek-v4-flash",
        "cloudgpu/qwen3-coder-480b",
        "glm-5.3",
    ):
        assert provider.model_feature_info(model_id) == CompletionsModelFeatureInfo()


def test_cloudgpu_model_accepts_temperature(caplog: pytest.LogCaptureFixture) -> None:
    """Test that temperature is sent for CloudGPU models.

    This is a unit test that calls encode_request directly to avoid network calls.
    """
    provider = _InspectableCloudGPUProvider(api_key="test-key")
    model_id = "cloudgpu/deepseek-v4-flash"

    with caplog.at_level(logging.WARNING):
        encode_request(
            model_id=model_id,
            messages=[llm.messages.user("Say hello")],
            tools=Toolkit([]),
            format=None,
            params={"temperature": 0.5},
            feature_info=provider.model_feature_info(model_id),
            provider_id="cloudgpu",
        )

    assert "Skipping unsupported parameter: temperature" not in caplog.text
