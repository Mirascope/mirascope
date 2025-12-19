"""Tests for AzureOpenAIProvider and AzureProvider."""

import os

import pytest

from mirascope.llm.providers.azure import AzureProvider
from mirascope.llm.providers.azure.openai.provider import AzureOpenAIProvider


def test_azure_provider_initialization() -> None:
    """Test AzureProvider initialization with api_key and base_url."""
    provider = AzureProvider(
        api_key="test-api-key",
        base_url="https://test-resource.openai.azure.com/",
    )
    assert provider.id == "azure"
    assert provider.default_scope == "azure/"


def test_azure_openai_provider_initialization() -> None:
    """Test AzureOpenAIProvider initialization with api_key and base_url."""
    provider = AzureOpenAIProvider(
        api_key="test-api-key",
        base_url="https://test-resource.openai.azure.com/",
    )
    assert provider.id == "azure:openai"
    assert provider.default_scope == "azure/"


def test_azure_openai_provider_missing_api_key() -> None:
    """Test AzureOpenAIProvider raises error when API key is missing."""
    original_key = os.environ.pop("AZURE_OPENAI_API_KEY", None)
    original_endpoint = os.environ.pop("AZURE_OPENAI_ENDPOINT", None)
    try:
        with pytest.raises(ValueError) as exc_info:
            AzureOpenAIProvider(base_url="https://test.openai.azure.com/")
        assert "Azure OpenAI API key is required" in str(exc_info.value)
        assert "AZURE_OPENAI_API_KEY" in str(exc_info.value)
    finally:
        if original_key is not None:
            os.environ["AZURE_OPENAI_API_KEY"] = original_key
        if original_endpoint is not None:
            os.environ["AZURE_OPENAI_ENDPOINT"] = original_endpoint


def test_azure_openai_provider_missing_base_url() -> None:
    """Test AzureOpenAIProvider raises error when base_url is missing."""
    original_key = os.environ.pop("AZURE_OPENAI_API_KEY", None)
    original_endpoint = os.environ.pop("AZURE_OPENAI_ENDPOINT", None)
    try:
        with pytest.raises(ValueError) as exc_info:
            AzureOpenAIProvider(api_key="test-api-key")
        assert "Azure OpenAI endpoint is required" in str(exc_info.value)
        assert "AZURE_OPENAI_ENDPOINT" in str(exc_info.value)
    finally:
        if original_key is not None:
            os.environ["AZURE_OPENAI_API_KEY"] = original_key
        if original_endpoint is not None:
            os.environ["AZURE_OPENAI_ENDPOINT"] = original_endpoint


def test_azure_openai_provider_uses_env_vars() -> None:
    """Test AzureOpenAIProvider uses environment variables."""
    original_key = os.environ.get("AZURE_OPENAI_API_KEY")
    original_endpoint = os.environ.get("AZURE_OPENAI_ENDPOINT")
    os.environ["AZURE_OPENAI_API_KEY"] = "env-test-key"
    os.environ["AZURE_OPENAI_ENDPOINT"] = "https://env-resource.openai.azure.com/"
    try:
        provider = AzureOpenAIProvider()
        assert provider.id == "azure:openai"
        assert provider.client.api_key == "env-test-key"
    finally:
        if original_key is not None:
            os.environ["AZURE_OPENAI_API_KEY"] = original_key
        else:
            os.environ.pop("AZURE_OPENAI_API_KEY", None)
        if original_endpoint is not None:
            os.environ["AZURE_OPENAI_ENDPOINT"] = original_endpoint
        else:
            os.environ.pop("AZURE_OPENAI_ENDPOINT", None)


def test_azure_openai_provider_base_url_normalization() -> None:
    """Test AzureOpenAIProvider normalizes base_url to include /openai/v1/."""
    provider = AzureOpenAIProvider(
        api_key="test-key",
        base_url="https://test-resource.openai.azure.com/",
    )
    assert (
        str(provider.client.base_url)
        == "https://test-resource.openai.azure.com/openai/v1/"
    )


def test_azure_openai_provider_base_url_already_normalized() -> None:
    """Test AzureOpenAIProvider preserves already normalized base_url."""
    provider = AzureOpenAIProvider(
        api_key="test-key",
        base_url="https://test-resource.openai.azure.com/openai/v1/",
    )
    assert (
        str(provider.client.base_url)
        == "https://test-resource.openai.azure.com/openai/v1/"
    )


def test_azure_openai_provider_base_url_openai_v1_without_trailing_slash() -> None:
    """Test AzureOpenAIProvider adds trailing slash to /openai/v1 suffix."""
    provider = AzureOpenAIProvider(
        api_key="test-key",
        base_url="https://test-resource.openai.azure.com/openai/v1",
    )
    assert (
        str(provider.client.base_url)
        == "https://test-resource.openai.azure.com/openai/v1/"
    )


def test_azure_openai_provider_base_url_without_trailing_slash() -> None:
    """Test AzureOpenAIProvider handles base_url without trailing slash."""
    provider = AzureOpenAIProvider(
        api_key="test-key",
        base_url="https://test-resource.openai.azure.com",
    )
    assert (
        str(provider.client.base_url)
        == "https://test-resource.openai.azure.com/openai/v1/"
    )


def test_azure_openai_provider_model_name() -> None:
    """Test AzureOpenAIProvider strips 'azure/' prefix from model_id."""
    provider = AzureOpenAIProvider(
        api_key="test-key",
        base_url="https://test-resource.openai.azure.com/",
    )
    assert provider._model_name("azure/gpt-4o") == "gpt-4o"  # pyright: ignore[reportPrivateUsage]
    assert provider._model_name("gpt-4o") == "gpt-4o"  # pyright: ignore[reportPrivateUsage]
