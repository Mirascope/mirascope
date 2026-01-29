"""Tests for llm.providers.azure Anthropic providers."""

import inspect
import os
from collections.abc import Awaitable, Generator

import pytest

pytest.importorskip("anthropic", reason="anthropic package required")

from anthropic import types
from anthropic.types.beta.parsed_beta_message import ParsedBetaMessage

from mirascope.llm.messages import user
from mirascope.llm.providers.anthropic._utils.beta_decode import beta_decode_response
from mirascope.llm.providers.anthropic._utils.beta_encode import beta_encode_request
from mirascope.llm.providers.anthropic._utils.decode import decode_response
from mirascope.llm.providers.anthropic._utils.encode import encode_request
from mirascope.llm.providers.azure import AzureProvider
from mirascope.llm.providers.azure.anthropic import (
    AzureAnthropicBetaProvider,
    AzureAnthropicProvider,
    AzureAnthropicRoutedBetaProvider,
    AzureAnthropicRoutedProvider,
)
from mirascope.llm.providers.azure.anthropic._utils import (
    azure_model_name,
    coerce_async_token_provider,
    coerce_sync_token_provider,
)
from mirascope.llm.tools import Toolkit


def test_azure_anthropic_provider_initialization() -> None:
    """Test AzureAnthropicProvider initialization with api_key and base_url."""
    provider = AzureAnthropicProvider(
        api_key="test-api-key",
        base_url="https://test-resource.services.ai.azure.com/anthropic/",
    )
    assert provider.id == "azure:anthropic"
    assert "azure/anthropic/" in provider.default_scope
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

    sync_provider = coerce_sync_token_provider(token_provider)  # pyright: ignore[reportArgumentType]
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
    result = await async_provider()
    assert result == "token"


@pytest.mark.asyncio
async def test_azure_token_provider_async_wraps_sync() -> None:
    """Test async token provider wrapper wraps sync providers for async use."""

    def token_provider() -> str:
        return "token"

    async_provider = coerce_async_token_provider(token_provider)
    assert callable(async_provider)
    result = await async_provider()
    assert result == "token"


@pytest.mark.asyncio
async def test_azure_token_provider_async_rejects_empty_string() -> None:
    """Test async token provider wrapper rejects empty token strings."""

    def token_provider() -> str:
        return ""

    async_provider = coerce_async_token_provider(token_provider)
    assert callable(async_provider)
    with pytest.raises(ValueError, match="Expected Azure token provider"):
        await async_provider()


def test_azure_token_provider_is_awaitable_check() -> None:
    """Test awaitable detection using inspect.isawaitable."""

    async def token_provider() -> str:
        return "token"

    coro = token_provider()
    try:
        assert inspect.isawaitable(coro) is True
    finally:
        coro.close()


def test_azure_anthropic_model_name_passthrough() -> None:
    """Test azure_model_name returns non-prefixed IDs unchanged."""
    assert azure_model_name("claude-sonnet-4-5") == "claude-sonnet-4-5"


def test_azure_anthropic_model_name_strips_azure_anthropic_prefix() -> None:
    """Test azure_model_name strips azure/anthropic/ prefix."""
    assert azure_model_name("azure/anthropic/claude-sonnet-4-5") == "claude-sonnet-4-5"


def test_azure_anthropic_model_name_strips_azure_prefix() -> None:
    """Test azure_model_name strips azure/ prefix."""
    assert (
        azure_model_name("azure/azureml://registries/azureml-anthropic/model")
        == "azureml://registries/azureml-anthropic/model"
    )


def test_azure_anthropic_beta_provider_initialization() -> None:
    """Test AzureAnthropicBetaProvider initialization with api_key and base_url."""
    provider = AzureAnthropicBetaProvider(
        api_key="test-api-key",
        base_url="https://test-resource.services.ai.azure.com/anthropic/",
    )
    assert provider.id == "azure:anthropic-beta"
    assert "azure/anthropic/" in provider.default_scope
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
    model_id = "azure/anthropic/claude-sonnet-4-20250514"
    _, _, kwargs = encode_request(
        model_id=model_id,
        messages=[user("hello")],
        tools=Toolkit(None),
        format=None,
        params={},
        model_name_override=azure_model_name(model_id),
        provider_id="azure",
    )
    assert kwargs["model"] == "claude-sonnet-4-20250514"


def test_azure_anthropic_beta_encode_request_sets_model() -> None:
    """Test beta_encode_request uses the Azure deployment name for model."""
    model_id = "azure/anthropic/claude-sonnet-4-20250514"
    _, _, kwargs = beta_encode_request(
        model_id=model_id,
        messages=[user("hello")],
        tools=Toolkit(None),
        format=None,
        params={},
        model_name_override=azure_model_name(model_id),
        provider_id="azure",
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
    model_id = "azure/anthropic/claude-sonnet-4-20250514"
    assistant_message, _, _ = decode_response(
        response,
        model_id,
        include_thoughts=False,
        provider_id="azure",
        provider_model_name=azure_model_name(model_id),
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
    model_id = "azure/anthropic/claude-sonnet-4-20250514"
    assistant_message, _, _ = beta_decode_response(
        response,
        model_id,
        include_thoughts=False,
        provider_id="azure",
        provider_model_name=azure_model_name(model_id),
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
    import importlib
    import sys
    from types import ModuleType
    from typing import Any

    modules_to_remove = [
        "mirascope.llm.providers.azure.provider",
        "mirascope.llm.providers.azure.anthropic.provider",
        "mirascope.llm.providers.azure.anthropic",
        "mirascope.llm.providers.azure",
    ]
    original_modules = {name: sys.modules.get(name) for name in modules_to_remove}
    for name in modules_to_remove:
        sys.modules.pop(name, None)

    original_import = builtins.__import__

    def mock_import(name: str, *args: Any, **kwargs: Any) -> ModuleType:  # noqa: ANN401
        level = args[3] if len(args) > 3 else 0
        if level == 0 and (name == "anthropic" or name.startswith("anthropic.")):
            raise ImportError(f"No module named '{name}'")
        return original_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", mock_import)

    try:
        azure_module = importlib.import_module("mirascope.llm.providers.azure")
        provider = azure_module.AzureProvider(
            api_key="test-openai-key",
            base_url="https://test-resource.openai.azure.com/",
            anthropic_api_key="test-anthropic-key",
            anthropic_base_url="https://test-resource.services.ai.azure.com/anthropic/",
        )

        with pytest.raises(ImportError, match="anthropic"):
            provider.call(
                model_id="azure/anthropic/claude-sonnet-4-5",
                messages=[user("hello")],
                toolkit=Toolkit(None),
            )
    finally:
        for name, module in original_modules.items():
            if module is None:
                sys.modules.pop(name, None)
            else:
                sys.modules[name] = module


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
    import importlib
    import sys
    from types import ModuleType
    from typing import Any

    original_import = builtins.__import__

    def mock_import(name: str, *args: Any, **kwargs: Any) -> ModuleType:  # noqa: ANN401
        level = args[3] if len(args) > 3 else 0
        if level == 0 and (name == "anthropic" or name.startswith("anthropic.")):
            raise ImportError(f"No module named '{name}'")
        return original_import(name, *args, **kwargs)

    modules_to_remove = [
        "mirascope.llm.providers.azure.provider",
        "mirascope.llm.providers.azure.anthropic.provider",
        "mirascope.llm.providers.azure.anthropic",
        "mirascope.llm.providers.azure",
    ]
    original_modules = {name: sys.modules.get(name) for name in modules_to_remove}
    for name in modules_to_remove:
        sys.modules.pop(name, None)

    monkeypatch.setattr(builtins, "__import__", mock_import)

    try:
        azure_module = importlib.import_module("mirascope.llm.providers.azure")
        azure_openai_module = importlib.import_module(
            "mirascope.llm.providers.azure.openai.provider"
        )

        monkeypatch.setattr(
            azure_openai_module.AzureOpenAIRoutedProvider,
            "call",
            lambda *args, **kwargs: (_ for _ in ()).throw(
                AssertionError("OpenAI route should not be used.")
            ),
        )

        provider = azure_module.AzureProvider(
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
                toolkit=Toolkit(None),
            )
    finally:
        for name, module in original_modules.items():
            if module is None:
                sys.modules.pop(name, None)
            else:
                sys.modules[name] = module


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
            toolkit=Toolkit(None),
        )


def test_should_use_beta_with_strict_format() -> None:
    """Test _should_use_beta returns True for strict format mode."""
    from mirascope import llm

    provider = AzureAnthropicProvider(
        api_key="test-api-key",
        base_url="https://test-resource.services.ai.azure.com/anthropic/",
    )
    strict_format = llm.format(str, mode="strict")
    assert provider._should_use_beta(  # pyright: ignore[reportPrivateUsage]
        "azure/anthropic/claude-sonnet-4-5", strict_format, Toolkit(None)
    )


def test_should_use_beta_returns_false_for_non_strict() -> None:
    """Test _should_use_beta returns False for non-strict format."""
    from mirascope import llm

    provider = AzureAnthropicProvider(
        api_key="test-api-key",
        base_url="https://test-resource.services.ai.azure.com/anthropic/",
    )
    flexible_format = llm.format(str, mode="tool")
    assert not provider._should_use_beta(  # pyright: ignore[reportPrivateUsage]
        "azure/anthropic/claude-sonnet-4-5", flexible_format, Toolkit(None)
    )


def test_should_use_beta_with_strict_tools() -> None:
    """Test _should_use_beta returns True for strict tools."""
    from mirascope import llm

    @llm.tool(strict=True)
    def strict_tool(x: int) -> int:
        """A strict tool."""
        return x

    provider = AzureAnthropicProvider(
        api_key="test-api-key",
        base_url="https://test-resource.services.ai.azure.com/anthropic/",
    )
    toolkit_with_strict = Toolkit([strict_tool])
    assert provider._should_use_beta(  # pyright: ignore[reportPrivateUsage]
        "azure/anthropic/claude-sonnet-4-5", None, toolkit_with_strict
    )


def test_azure_provider_lazy_init_client(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test AzureProvider client is None when credentials are incomplete."""
    # Clear environment variables to ensure no fallback
    monkeypatch.delenv("AZURE_OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("AZURE_OPENAI_ENDPOINT", raising=False)

    # When only api_key is provided (base_url missing), client should be None
    provider_partial = AzureProvider(
        api_key="test-openai-key",
    )
    assert provider_partial.client is None


def test_azure_provider_eager_init_client() -> None:
    """Test AzureProvider eagerly initializes client when both api_key and base_url provided."""
    provider = AzureProvider(
        api_key="test-openai-key",
        base_url="https://test-resource.openai.azure.com/",
    )

    # Client should be initialized immediately when both credentials are provided
    assert provider.client is not None


def test_azure_provider_env_fallback_for_partial_credentials(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test AzureProvider uses env vars to fill in missing credentials."""
    monkeypatch.setenv(
        "AZURE_OPENAI_ENDPOINT", "https://env-resource.openai.azure.com/"
    )
    monkeypatch.delenv("AZURE_OPENAI_API_KEY", raising=False)

    # When api_key is provided and base_url comes from env, client should be initialized
    provider = AzureProvider(
        api_key="test-openai-key",
    )
    assert provider.client is not None
    assert provider._openai_base_url == "https://env-resource.openai.azure.com/"  # pyright: ignore[reportPrivateUsage]
