"""Tests for AzureAnthropicProvider."""

import os

import pytest

from mirascope.llm.providers.azure import AzureAnthropicProvider
from mirascope.llm.providers.azure.anthropic import (
    AzureAnthropicBetaProvider,
    AzureRoutedAnthropicBetaProvider,
    AzureRoutedAnthropicProvider,
)


def test_azure_anthropic_provider_initialization() -> None:
    """Test AzureAnthropicProvider initialization with api_key and base_url."""
    provider = AzureAnthropicProvider(
        api_key="test-api-key",
        base_url="https://test-resource.services.ai.azure.com/anthropic/",
    )
    assert provider.id == "azure:anthropic"
    assert provider.default_scope == "azure/claude-"


def test_azure_anthropic_provider_missing_api_key() -> None:
    """Test AzureAnthropicProvider raises error when API key is missing."""
    original_key = os.environ.pop("AZURE_ANTHROPIC_API_KEY", None)
    original_endpoint = os.environ.pop("AZURE_AI_ANTHROPIC_ENDPOINT", None)
    try:
        with pytest.raises(ValueError) as exc_info:
            AzureAnthropicProvider(
                base_url="https://test.services.ai.azure.com/anthropic/"
            )
        assert "Azure Anthropic API key is required" in str(exc_info.value)
        assert "AZURE_ANTHROPIC_API_KEY" in str(exc_info.value)
    finally:
        if original_key is not None:
            os.environ["AZURE_ANTHROPIC_API_KEY"] = original_key
        if original_endpoint is not None:
            os.environ["AZURE_AI_ANTHROPIC_ENDPOINT"] = original_endpoint


def test_azure_anthropic_provider_missing_base_url() -> None:
    """Test AzureAnthropicProvider raises error when base_url is missing."""
    original_key = os.environ.pop("AZURE_ANTHROPIC_API_KEY", None)
    original_endpoint = os.environ.pop("AZURE_AI_ANTHROPIC_ENDPOINT", None)
    try:
        with pytest.raises(ValueError) as exc_info:
            AzureAnthropicProvider(api_key="test-api-key")
        assert "Azure Anthropic endpoint is required" in str(exc_info.value)
        assert "AZURE_AI_ANTHROPIC_ENDPOINT" in str(exc_info.value)
    finally:
        if original_key is not None:
            os.environ["AZURE_ANTHROPIC_API_KEY"] = original_key
        if original_endpoint is not None:
            os.environ["AZURE_AI_ANTHROPIC_ENDPOINT"] = original_endpoint


def test_azure_anthropic_provider_uses_env_vars() -> None:
    """Test AzureAnthropicProvider uses environment variables."""
    original_key = os.environ.get("AZURE_ANTHROPIC_API_KEY")
    original_endpoint = os.environ.get("AZURE_AI_ANTHROPIC_ENDPOINT")
    os.environ["AZURE_ANTHROPIC_API_KEY"] = "env-test-key"
    os.environ["AZURE_AI_ANTHROPIC_ENDPOINT"] = (
        "https://env-resource.services.ai.azure.com/anthropic/"
    )
    try:
        provider = AzureAnthropicProvider()
        assert provider.id == "azure:anthropic"
        assert provider.client.api_key == "env-test-key"
    finally:
        if original_key is not None:
            os.environ["AZURE_ANTHROPIC_API_KEY"] = original_key
        else:
            os.environ.pop("AZURE_ANTHROPIC_API_KEY", None)
        if original_endpoint is not None:
            os.environ["AZURE_AI_ANTHROPIC_ENDPOINT"] = original_endpoint
        else:
            os.environ.pop("AZURE_AI_ANTHROPIC_ENDPOINT", None)


def test_azure_anthropic_provider_base_url_normalization() -> None:
    """Test AzureAnthropicProvider normalizes base_url with trailing slash."""
    provider = AzureAnthropicProvider(
        api_key="test-key",
        base_url="https://test-resource.services.ai.azure.com/anthropic",
    )
    assert (
        str(provider.client.base_url)
        == "https://test-resource.services.ai.azure.com/anthropic/"
    )


def test_azure_anthropic_provider_base_url_already_normalized() -> None:
    """Test AzureAnthropicProvider preserves already normalized base_url."""
    provider = AzureAnthropicProvider(
        api_key="test-key",
        base_url="https://test-resource.services.ai.azure.com/anthropic/",
    )
    assert (
        str(provider.client.base_url)
        == "https://test-resource.services.ai.azure.com/anthropic/"
    )


def test_azure_anthropic_provider_model_name() -> None:
    """Test AzureAnthropicProvider strips 'azure/' prefix from model_id."""
    provider = AzureAnthropicProvider(
        api_key="test-key",
        base_url="https://test-resource.services.ai.azure.com/anthropic/",
    )
    assert (
        provider._model_name("azure/claude-sonnet-4-20250514")
        == "claude-sonnet-4-20250514"
    )  # pyright: ignore[reportPrivateUsage]
    assert (
        provider._model_name("claude-sonnet-4-20250514") == "claude-sonnet-4-20250514"
    )  # pyright: ignore[reportPrivateUsage]


def test_azure_anthropic_beta_provider_initialization() -> None:
    """Test AzureAnthropicBetaProvider initialization with api_key and base_url."""
    provider = AzureAnthropicBetaProvider(
        api_key="test-api-key",
        base_url="https://test-resource.services.ai.azure.com/anthropic/",
    )
    assert provider.id == "azure:anthropic-beta"
    assert provider.default_scope == "azure/claude-"


def test_azure_routed_anthropic_provider_id() -> None:
    """Test AzureRoutedAnthropicProvider uses 'azure' as provider id."""
    provider = AzureRoutedAnthropicProvider(
        api_key="test-api-key",
        base_url="https://test-resource.services.ai.azure.com/anthropic/",
    )
    assert provider.id == "azure"


def test_azure_routed_anthropic_beta_provider_id() -> None:
    """Test AzureRoutedAnthropicBetaProvider uses 'azure' as provider id."""
    provider = AzureRoutedAnthropicBetaProvider(
        api_key="test-api-key",
        base_url="https://test-resource.services.ai.azure.com/anthropic/",
    )
    assert provider.id == "azure"


def test_azure_anthropic_provider_has_beta_provider() -> None:
    """Test AzureAnthropicProvider has a beta provider instance."""
    provider = AzureAnthropicProvider(
        api_key="test-api-key",
        base_url="https://test-resource.services.ai.azure.com/anthropic/",
    )
    assert hasattr(provider, "_beta_provider")
    assert isinstance(provider._beta_provider, AzureAnthropicBetaProvider)  # pyright: ignore[reportPrivateUsage]


def test_azure_provider_routes_claude_models_to_anthropic() -> None:
    """Test AzureProvider routes Claude models to AzureAnthropicProvider."""
    from mirascope.llm.providers.azure import AzureProvider

    provider = AzureProvider(
        api_key="test-openai-key",
        base_url="https://test-resource.openai.azure.com/",
        anthropic_api_key="test-anthropic-key",
        anthropic_base_url="https://test-resource.services.ai.azure.com/anthropic/",
    )

    # Test Claude model detection
    assert provider._is_claude_model("azure/claude-sonnet-4-20250514")  # pyright: ignore[reportPrivateUsage]
    assert provider._is_claude_model("azure/claude-3-5-sonnet-20241022")  # pyright: ignore[reportPrivateUsage]
    assert not provider._is_claude_model("azure/gpt-4o")  # pyright: ignore[reportPrivateUsage]
    assert not provider._is_claude_model("azure/gpt-4o-mini")  # pyright: ignore[reportPrivateUsage]


def test_azure_provider_chooses_correct_subprovider() -> None:
    """Test AzureProvider chooses correct sub-provider based on model."""
    from mirascope.llm.providers.azure import AzureProvider
    from mirascope.llm.providers.azure.openai import AzureOpenAIProvider

    provider = AzureProvider(
        api_key="test-openai-key",
        base_url="https://test-resource.openai.azure.com/",
        anthropic_api_key="test-anthropic-key",
        anthropic_base_url="https://test-resource.services.ai.azure.com/anthropic/",
    )

    # Claude models should use Anthropic provider
    claude_subprovider = provider._choose_subprovider(
        "azure/claude-sonnet-4-20250514", []
    )  # pyright: ignore[reportPrivateUsage]
    assert isinstance(claude_subprovider, AzureRoutedAnthropicProvider)

    # OpenAI models should use OpenAI provider
    openai_subprovider = provider._choose_subprovider("azure/gpt-4o", [])  # pyright: ignore[reportPrivateUsage]
    assert isinstance(openai_subprovider, AzureOpenAIProvider)
