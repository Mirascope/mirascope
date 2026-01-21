"""Tests for llm.providers.azure Anthropic providers."""

import os
from collections.abc import Awaitable, Generator
from typing import cast

import pytest
from anthropic import types
from anthropic.types.beta.parsed_beta_message import ParsedBetaMessage

from mirascope.llm.messages import user
from mirascope.llm.providers.azure import AzureProvider
from mirascope.llm.providers.azure.anthropic import (
    AzureAnthropicBetaProvider,
    AzureAnthropicProvider,
    AzureAnthropicRoutedBetaProvider,
    AzureAnthropicRoutedProvider,
)
from mirascope.llm.providers.azure.anthropic._utils import (
    azure_model_name,
    beta_decode_response,
    beta_encode_request,
    coerce_async_token_provider,
    coerce_sync_token_provider,
    decode_response,
    encode_request,
    is_awaitable_str,
)


def test_azure_anthropic_provider_initialization() -> None:
    """Test AzureAnthropicProvider initialization with api_key and base_url."""
    provider = AzureAnthropicProvider(
        api_key="test-api-key",
        base_url="https://test-resource.services.ai.azure.com/anthropic/",
    )
    assert provider.id == "azure:anthropic"
    assert "azure/claude-sonnet-4-5" in provider.default_scope
    assert "azure/azureml://registries/azureml-anthropic/" in provider.default_scope


def test_azure_anthropic_provider_missing_api_key() -> None:
    """Test AzureAnthropicProvider raises error when API key is missing."""
    original_key = os.environ.pop("AZURE_ANTHROPIC_API_KEY", None)
    original_endpoint = os.environ.pop("AZURE_AI_ANTHROPIC_ENDPOINT", None)
    try:
        with pytest.raises(ValueError) as exc_info:
            AzureAnthropicProvider(
                base_url="https://test.services.ai.azure.com/anthropic/"
            )
        assert "Azure Anthropic API key" in str(exc_info.value)
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


def test_azure_anthropic_provider_accepts_token_provider() -> None:
    """Test AzureAnthropicProvider accepts Azure AD token providers."""

    def token_provider() -> str:
        return "token"

    provider = AzureAnthropicProvider(
        azure_ad_token_provider=token_provider,
        base_url="https://test-resource.services.ai.azure.com/anthropic/",
    )
    assert provider.client is not None
    assert provider.async_client is not None


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

    def token_provider() -> DummyAwaitable:
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
async def test_azure_token_provider_async_accepts_str() -> None:
    """Test async token provider wrapper accepts string results."""

    def token_provider() -> str:
        return "token"

    async_provider = coerce_async_token_provider(token_provider)
    assert callable(async_provider)
    result_obj = async_provider()
    if is_awaitable_str(result_obj):
        result = await cast(Awaitable[str], result_obj)
    else:
        result = result_obj
    assert result == "token"


@pytest.mark.asyncio
async def test_azure_token_provider_async_accepts_async() -> None:
    """Test async token provider wrapper accepts awaitable results."""

    async def token_provider() -> str:
        return "token"

    async_provider = coerce_async_token_provider(token_provider)
    assert callable(async_provider)
    result_obj = async_provider()
    if is_awaitable_str(result_obj):
        result = await cast(Awaitable[str], result_obj)
    else:
        result = result_obj
    assert result == "token"


@pytest.mark.asyncio
async def test_azure_token_provider_async_rejects_empty_string() -> None:
    """Test async token provider wrapper rejects empty token strings."""

    def token_provider() -> str:
        return ""

    async_provider = coerce_async_token_provider(token_provider)
    assert callable(async_provider)
    result_obj = async_provider()
    if is_awaitable_str(result_obj):
        with pytest.raises(ValueError, match="Expected Azure token provider"):
            await cast(Awaitable[str], result_obj)
    else:
        pytest.fail("Expected async token provider to return an awaitable.")


def test_azure_token_provider_is_awaitable_check() -> None:
    """Test awaitable detection for token providers."""

    async def token_provider() -> str:
        return "token"

    coro = token_provider()
    try:
        assert is_awaitable_str(coro) is True
    finally:
        coro.close()


def test_azure_anthropic_model_name_passthrough() -> None:
    """Test azure_model_name returns non-prefixed IDs unchanged."""
    assert azure_model_name("claude-sonnet-4-5") == "claude-sonnet-4-5"


def test_azure_anthropic_beta_provider_initialization() -> None:
    """Test AzureAnthropicBetaProvider initialization with api_key and base_url."""
    provider = AzureAnthropicBetaProvider(
        api_key="test-api-key",
        base_url="https://test-resource.services.ai.azure.com/anthropic/",
    )
    assert provider.id == "azure:anthropic-beta"
    assert "azure/claude-sonnet-4-5" in provider.default_scope
    assert "azure/azureml://registries/azureml-anthropic/" in provider.default_scope


def test_azure_anthropic_beta_provider_missing_api_key() -> None:
    """Test AzureAnthropicBetaProvider requires an API key."""
    original_key = os.environ.pop("AZURE_ANTHROPIC_API_KEY", None)
    try:
        with pytest.raises(ValueError, match="AZURE_ANTHROPIC_API_KEY"):
            AzureAnthropicBetaProvider(
                base_url="https://test-resource.services.ai.azure.com/anthropic/",
            )
    finally:
        if original_key is not None:
            os.environ["AZURE_ANTHROPIC_API_KEY"] = original_key


def test_azure_anthropic_beta_provider_missing_base_url() -> None:
    """Test AzureAnthropicBetaProvider requires a base URL."""
    original_endpoint = os.environ.pop("AZURE_AI_ANTHROPIC_ENDPOINT", None)
    try:
        with pytest.raises(ValueError, match="AZURE_AI_ANTHROPIC_ENDPOINT"):
            AzureAnthropicBetaProvider(api_key="test-key")
    finally:
        if original_endpoint is not None:
            os.environ["AZURE_AI_ANTHROPIC_ENDPOINT"] = original_endpoint


def test_azure_routed_anthropic_provider_id() -> None:
    """Test AzureAnthropicRoutedProvider uses 'azure' as provider id."""
    provider = AzureAnthropicRoutedProvider(
        api_key="test-api-key",
        base_url="https://test-resource.services.ai.azure.com/anthropic/",
    )
    assert provider.id == "azure"


def test_azure_routed_anthropic_beta_provider_id() -> None:
    """Test AzureAnthropicRoutedBetaProvider uses 'azure' as provider id."""
    provider = AzureAnthropicRoutedBetaProvider(
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


def test_azure_anthropic_provider_get_error_status() -> None:
    """Test AzureAnthropicProvider get_error_status returns status code."""
    provider = AzureAnthropicProvider(
        api_key="test-api-key",
        base_url="https://test-resource.services.ai.azure.com/anthropic/",
    )

    class DummyError(Exception):
        status_code = 418

    assert provider.get_error_status(DummyError()) == 418


def test_azure_anthropic_encode_request_sets_model() -> None:
    """Test encode_request uses the Azure deployment name for model."""
    _, _, kwargs = encode_request(
        model_id="azure/claude-sonnet-4-20250514",
        messages=[user("hello")],
        tools=None,
        format=None,
        params={},
    )
    assert kwargs["model"] == "claude-sonnet-4-20250514"


def test_azure_anthropic_beta_encode_request_sets_model() -> None:
    """Test beta_encode_request uses the Azure deployment name for model."""
    _, _, kwargs = beta_encode_request(
        model_id="azure/claude-sonnet-4-20250514",
        messages=[user("hello")],
        tools=None,
        format=None,
        params={},
    )
    assert kwargs["model"] == "claude-sonnet-4-20250514"


def test_azure_anthropic_decode_response_sets_provider_id() -> None:
    """Test decode_response overrides assistant provider_id."""
    response = types.Message.model_validate(
        {
            "id": "msg_123",
            "type": "message",
            "role": "assistant",
            "content": [{"type": "text", "text": "hello"}],
            "model": "claude-sonnet-4",
            "stop_reason": "end_turn",
            "stop_sequence": None,
            "usage": {"input_tokens": 1, "output_tokens": 2},
        }
    )
    assistant_message, _, _ = decode_response(
        response,
        "azure/claude-sonnet-4-20250514",
        include_thoughts=False,
        provider_id="azure",
    )
    assert assistant_message.provider_id == "azure"


def test_azure_anthropic_beta_decode_response_sets_provider_id() -> None:
    """Test beta_decode_response overrides assistant provider_id."""
    response = ParsedBetaMessage.model_validate(
        {
            "id": "msg_456",
            "type": "message",
            "role": "assistant",
            "content": [{"type": "text", "text": "hello"}],
            "model": "claude-sonnet-4",
            "stop_reason": "end_turn",
            "stop_sequence": None,
            "usage": {"input_tokens": 1, "output_tokens": 2},
        }
    )
    assistant_message, _, _ = beta_decode_response(
        response,
        "azure/claude-sonnet-4-20250514",
        include_thoughts=False,
        provider_id="azure",
    )
    assert assistant_message.provider_id == "azure"


def test_azure_anthropic_beta_provider_get_error_status() -> None:
    """Test AzureAnthropicBetaProvider get_error_status returns status code."""
    provider = AzureAnthropicBetaProvider(
        api_key="test-key",
        base_url="https://test-resource.services.ai.azure.com/anthropic/",
    )

    class DummyError(Exception):
        status_code = 418

    assert provider.get_error_status(DummyError()) == 418


def test_azure_provider_missing_anthropic_raises_import_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test AzureProvider raises ImportError when Anthropic is unavailable."""
    import builtins
    import sys
    from types import ModuleType
    from typing import Any

    sys.modules.pop("mirascope.llm.providers.azure.anthropic.provider", None)
    sys.modules.pop("mirascope.llm.providers.azure.anthropic", None)

    original_import = builtins.__import__

    def mock_import(name: str, *args: Any, **kwargs: Any) -> ModuleType:  # noqa: ANN401
        if name == "anthropic" or name.startswith("anthropic."):
            raise ImportError(f"No module named '{name}'")
        return original_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", mock_import)

    provider = AzureProvider(
        api_key="test-openai-key",
        base_url="https://test-resource.openai.azure.com/",
        anthropic_api_key="test-anthropic-key",
        anthropic_base_url="https://test-resource.services.ai.azure.com/anthropic/",
    )

    with pytest.raises(ImportError, match="anthropic"):
        provider.call(
            model_id="azure/claude-sonnet-4-5",
            messages=[user("hello")],
        )


def test_azure_provider_creates_anthropic_subprovider() -> None:
    """Test AzureProvider can create the Anthropic subprovider."""
    provider = AzureProvider(
        anthropic_api_key="test-anthropic-key",
        anthropic_base_url="https://test-resource.services.ai.azure.com/anthropic/",
    )
    subprovider = provider._get_anthropic_provider()  # pyright: ignore[reportPrivateUsage]
    assert subprovider.id == "azure"


def test_azure_provider_routes_custom_anthropic_scope(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test AzureProvider routes custom scoped models to Anthropic."""
    import builtins
    from types import ModuleType
    from typing import Any

    from mirascope.llm.providers.azure.openai.provider import AzureOpenAIRoutedProvider

    original_import = builtins.__import__

    def mock_import(name: str, *args: Any, **kwargs: Any) -> ModuleType:  # noqa: ANN401
        if name == "anthropic" or name.startswith("anthropic."):
            raise ImportError(f"No module named '{name}'")
        return original_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", mock_import)
    monkeypatch.setattr(
        AzureOpenAIRoutedProvider,
        "call",
        lambda *args, **kwargs: (_ for _ in ()).throw(
            AssertionError("OpenAI route should not be used.")
        ),
    )

    provider = AzureProvider(
        api_key="test-openai-key",
        base_url="https://test-resource.openai.azure.com/",
        anthropic_api_key="test-anthropic-key",
        anthropic_base_url="https://test-resource.services.ai.azure.com/anthropic/",
        routing_scopes={"anthropic": ["azure/custom-deployment"]},
    )

    with pytest.raises(ImportError, match="anthropic"):
        provider.call(
            model_id="azure/custom-deployment",
            messages=[user("hello")],
        )


def test_azure_provider_requires_routing_for_unknown_model() -> None:
    """Test AzureProvider raises when routing cannot be determined."""
    provider = AzureProvider(
        api_key="test-openai-key",
        base_url="https://test-resource.openai.azure.com/",
    )

    with pytest.raises(ValueError, match="could not determine"):
        provider.call(
            model_id="azure/custom-deployment",
            messages=[user("hello")],
        )
