"""Tests for Azure OpenAI providers."""

import os
from collections.abc import Awaitable, Generator

import pytest

from mirascope.llm.providers.azure import AzureOpenAIProvider, AzureProvider
from mirascope.llm.providers.azure.model_id import model_name as azure_model_name
from mirascope.llm.providers.azure.openai._utils import (
    coerce_async_token_provider,
    coerce_sync_token_provider,
    is_awaitable_str,
)


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


def test_azure_openai_provider_accepts_token_provider() -> None:
    """Test AzureOpenAIProvider accepts Azure AD token providers."""

    def token_provider() -> str:
        return "token"

    provider = AzureOpenAIProvider(
        api_key=token_provider, base_url="https://example.openai.azure.com"
    )
    assert provider.client.api_key == ""
    assert provider.async_client.api_key == ""


def test_azure_token_provider_sync_accepts_str() -> None:
    """Test sync token provider wrapper accepts string results."""

    def token_provider() -> str:
        return "token"

    sync_provider = coerce_sync_token_provider(token_provider)
    assert callable(sync_provider)
    assert sync_provider() == "token"


def test_azure_token_provider_sync_rejects_async() -> None:
    """Test sync token provider wrapper rejects awaitable results."""

    class DummyAwaitable(Awaitable[str]):
        def __await__(self) -> Generator[object, None, str]:
            async def _coro() -> str:
                return "token"

            return _coro().__await__()

    def token_provider() -> Awaitable[str]:
        return DummyAwaitable()

    sync_provider = coerce_sync_token_provider(token_provider)
    assert callable(sync_provider)

    with pytest.raises(ValueError, match="Async Azure token provider"):
        sync_provider()


def test_azure_token_provider_sync_rejects_empty_string() -> None:
    """Test sync token provider wrapper rejects empty token strings."""

    def token_provider() -> str:
        return ""

    sync_provider = coerce_sync_token_provider(token_provider)
    assert callable(sync_provider)

    with pytest.raises(ValueError, match="Expected Azure token provider"):
        sync_provider()


@pytest.mark.asyncio
async def test_azure_token_provider_async_accepts_sync() -> None:
    """Test async token provider wrapper accepts sync results."""

    def token_provider() -> str:
        return "token"

    async_provider = coerce_async_token_provider(token_provider)
    assert callable(async_provider)

    result_obj = async_provider()
    if is_awaitable_str(result_obj):
        result = await result_obj
    else:
        result = result_obj
    assert result == "token"


@pytest.mark.asyncio
async def test_azure_token_provider_async_accepts_awaitable() -> None:
    """Test async token provider wrapper awaits async results."""

    class DummyAwaitable(Awaitable[str]):
        def __await__(self) -> Generator[object, None, str]:
            async def _coro() -> str:
                return "token"

            return _coro().__await__()

    def token_provider() -> Awaitable[str]:
        return DummyAwaitable()

    async_provider = coerce_async_token_provider(token_provider)
    assert callable(async_provider)

    result_obj = async_provider()
    assert is_awaitable_str(result_obj) is True
    result = await result_obj
    assert result == "token"

    awaitable = token_provider()
    assert is_awaitable_str(awaitable) is True
    await awaitable


@pytest.mark.asyncio
async def test_azure_token_provider_async_rejects_empty_string() -> None:
    """Test async token provider wrapper rejects empty token strings."""

    def token_provider() -> str:
        return ""

    async_provider = coerce_async_token_provider(token_provider)
    assert callable(async_provider)

    with pytest.raises(ValueError, match="Expected Azure token provider"):
        await async_provider()


def test_azure_model_name() -> None:
    """Test azure model_name extracts deployment name correctly."""
    assert azure_model_name("azure/gpt-5-mini") == "gpt-5-mini"
    assert azure_model_name("gpt-5-mini") == "gpt-5-mini"


def test_azure_provider_initialization() -> None:
    """Test AzureProvider initialization."""
    provider = AzureProvider(
        api_key="test-key", base_url="https://example.openai.azure.com"
    )
    assert provider.id == "azure"
    assert provider.default_scope == "azure/"
    assert provider.client is not None
    assert (
        str(provider.client.base_url) == "https://example.openai.azure.com/openai/v1/"
    )


def test_azure_provider_missing_openai_raises_import_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test AzureProvider raises ImportError when OpenAI is unavailable."""
    import builtins
    import sys
    from types import ModuleType
    from typing import Any

    from mirascope.llm.messages import user

    sys.modules.pop("mirascope.llm.providers.azure.openai.provider", None)
    sys.modules.pop("mirascope.llm.providers.azure.openai", None)

    original_import = builtins.__import__

    def mock_import(name: str, *args: Any, **kwargs: Any) -> ModuleType:  # noqa: ANN401
        if name == "openai" or name.startswith("openai."):
            raise ImportError(f"No module named '{name}'")
        return original_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", mock_import)

    provider = AzureProvider(
        api_key="test-key", base_url="https://example.openai.azure.com"
    )
    assert provider.client is None

    with pytest.raises(ImportError, match="openai"):
        provider.call(model_id="azure/gpt-4o", messages=[user("hello")])
