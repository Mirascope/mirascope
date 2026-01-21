"""Tests for Azure OpenAI providers."""

import os
import sys

import pytest

from mirascope import llm
from mirascope.llm.providers.azure import AzureOpenAIProvider, AzureProvider
from mirascope.llm.providers.azure._utils import wrap_async_token_provider
from mirascope.llm.providers.azure.model_id import model_name as azure_model_name
from mirascope.llm.providers.openai.completions._utils import encode_request
from mirascope.llm.tools import Toolkit


def test_azure_openai_provider_requires_api_key() -> None:
    """Test that AzureOpenAIProvider requires an API key."""
    original_key = os.environ.pop("AZURE_OPENAI_API_KEY", None)
    try:
        with pytest.raises(ValueError, match="AZURE_OPENAI_API_KEY"):
            AzureOpenAIProvider(base_url="https://example.openai.azure.com")
    finally:
        if original_key is not None:
            os.environ["AZURE_OPENAI_API_KEY"] = original_key


def test_azure_openai_provider_requires_endpoint() -> None:
    """Test that AzureOpenAIProvider requires an endpoint."""
    original_endpoint = os.environ.pop("AZURE_OPENAI_ENDPOINT", None)
    try:
        with pytest.raises(ValueError, match="AZURE_OPENAI_ENDPOINT"):
            AzureOpenAIProvider(api_key="test-key")
    finally:
        if original_endpoint is not None:
            os.environ["AZURE_OPENAI_ENDPOINT"] = original_endpoint


def test_azure_openai_provider_base_url_normalized() -> None:
    """Test AzureOpenAIProvider normalizes the Azure endpoint."""
    provider = AzureOpenAIProvider(
        api_key="test-key", base_url="https://example.openai.azure.com"
    )
    assert (
        str(provider.client.base_url) == "https://example.openai.azure.com/openai/v1/"
    )


def test_azure_model_name() -> None:
    """Test azure model_name extracts deployment name correctly."""
    assert azure_model_name("azure/openai/gpt-5-mini") == "gpt-5-mini"
    assert azure_model_name("gpt-5-mini") == "gpt-5-mini"


def test_azure_provider_get_error_status() -> None:
    """Test AzureProvider.get_error_status extracts status code."""
    provider = AzureProvider(
        api_key="test-key", base_url="https://example.openai.azure.com"
    )

    class MockException(Exception):
        status_code = 401

    assert provider.get_error_status(MockException()) == 401
    assert provider.get_error_status(ValueError("no status")) is None


def test_azure_openai_provider_get_error_status() -> None:
    """Test AzureOpenAIProvider.get_error_status extracts status code."""
    provider = AzureOpenAIProvider(
        api_key="test-key", base_url="https://example.openai.azure.com"
    )

    class MockException(Exception):
        status_code = 418

    assert provider.get_error_status(MockException()) == 418
    assert provider.get_error_status(ValueError("no status")) is None


@pytest.mark.asyncio
async def test_wrap_async_token_provider_awaits_coroutine() -> None:
    """Test async token provider wrapper awaits awaitable results."""

    async def token_provider() -> str:
        return "token"

    async_provider = wrap_async_token_provider(token_provider)
    assert callable(async_provider)
    result = await async_provider()
    assert result == "token"


def test_azure_provider_openai_scopes_fallback_on_import_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test AzureProvider falls back to base OpenAI scope if model list import fails."""
    import builtins
    from types import ModuleType
    from typing import Any

    sys.modules.pop("mirascope.llm.providers.openai.model_id", None)
    original_import = builtins.__import__

    def mock_import(name: str, *args: Any, **kwargs: Any) -> ModuleType:  # noqa: ANN401
        if name == "openai.model_id":
            raise ImportError("boom")
        return original_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", mock_import)

    provider = AzureProvider()
    assert "azure/openai/" in provider._routing_scopes["openai"]  # pyright: ignore[reportPrivateUsage]


def test_azure_provider_openai_import_error_raises(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test AzureProvider raises ImportError when OpenAI provider cannot import."""
    import builtins
    from types import ModuleType
    from typing import Any

    sys.modules.pop("mirascope.llm.providers.azure.openai.provider", None)
    sys.modules.pop("mirascope.llm.providers.azure.openai", None)
    original_import = builtins.__import__

    def mock_import(name: str, *args: Any, **kwargs: Any) -> ModuleType:  # noqa: ANN401
        if name in {"openai.provider", "mirascope.llm.providers.azure.openai.provider"}:
            raise ImportError("boom")
        return original_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", mock_import)

    with pytest.raises(ImportError, match="openai"):
        AzureProvider(api_key="test-key", base_url="https://example.openai.azure.com")


def test_azure_model_id_preserved_in_error_messages() -> None:
    """Test that Azure model_id is preserved in FeatureNotSupportedError messages.

    When using Azure, errors should show the original model_id (e.g., 'azure/openai/my-deployment')
    rather than a transformed version.
    """
    azure_model_id = "azure/openai/my-deployment:responses"
    azure_deployment_name = azure_model_name(azure_model_id)

    with pytest.raises(llm.FeatureNotSupportedError) as exc_info:
        encode_request(
            model_id=azure_model_id,
            model_name=azure_deployment_name,
            messages=[llm.messages.user("test")],
            tools=Toolkit(None),
            format=None,
            params={},
        )

    # The error message should contain the original Azure model_id
    assert azure_model_id in str(exc_info.value)
