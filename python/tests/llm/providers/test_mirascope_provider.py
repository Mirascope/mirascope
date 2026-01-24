"""Tests for MirascopeProvider and utilities."""

import os
from unittest.mock import AsyncMock, Mock, patch

import pytest

from mirascope.llm.providers.mirascope import _utils
from mirascope.llm.providers.mirascope.provider import MirascopeProvider
from mirascope.llm.tools import (
    AsyncContextToolkit,
    AsyncToolkit,
    ContextToolkit,
    Toolkit,
)


class TestMirascopeUtils:
    """Tests for Mirascope utility functions."""

    def test_extract_model_scope_valid(self) -> None:
        """Test extracting model scope from valid model IDs."""
        assert _utils.extract_model_scope("openai/gpt-4") == "openai"
        assert _utils.extract_model_scope("anthropic/claude-3") == "anthropic"
        assert _utils.extract_model_scope("google/gemini-pro") == "google"
        assert _utils.extract_model_scope("openai/gpt-4-with-extra/stuff") == "openai"

    def test_extract_model_scope_invalid(self) -> None:
        """Test extracting model scope from invalid model IDs."""
        assert _utils.extract_model_scope("gpt-4") is None
        assert _utils.extract_model_scope("") is None
        assert _utils.extract_model_scope("no-slash") is None

    def test_get_default_router_base_url_default(self) -> None:
        """Test getting default router base URL."""
        original_url = os.environ.pop("MIRASCOPE_ROUTER_BASE_URL", None)
        try:
            url = _utils.get_default_router_base_url()
            assert url == "https://mirascope.com/router/v2"
        finally:
            if original_url is not None:
                os.environ["MIRASCOPE_ROUTER_BASE_URL"] = original_url

    def test_get_default_router_base_url_from_env(self) -> None:
        """Test getting router base URL from environment variable."""
        original_url = os.environ.get("MIRASCOPE_ROUTER_BASE_URL")
        os.environ["MIRASCOPE_ROUTER_BASE_URL"] = "http://localhost:3000/router/v2"
        try:
            url = _utils.get_default_router_base_url()
            assert url == "http://localhost:3000/router/v2"
        finally:
            if original_url is not None:
                os.environ["MIRASCOPE_ROUTER_BASE_URL"] = original_url
            else:
                os.environ.pop("MIRASCOPE_ROUTER_BASE_URL", None)

    def test_create_underlying_provider_openai(self) -> None:
        """Test creating OpenAI provider."""
        provider = _utils.create_underlying_provider(
            model_scope="openai",
            api_key="test-key",
            router_base_url="http://localhost:3000/router/v2",
        )
        assert provider.id == "openai"
        assert "localhost:3000/router/v2/openai" in str(provider.client.base_url)

    def test_create_underlying_provider_anthropic(self) -> None:
        """Test creating Anthropic provider."""
        provider = _utils.create_underlying_provider(
            model_scope="anthropic",
            api_key="test-key",
            router_base_url="http://localhost:3000/router/v2",
        )
        assert provider.id == "anthropic"
        assert "localhost:3000/router/v2/anthropic" in str(provider.client.base_url)

    def test_create_underlying_provider_google(self) -> None:
        """Test creating Google provider."""
        provider = _utils.create_underlying_provider(
            model_scope="google",
            api_key="test-key",
            router_base_url="http://localhost:3000/router/v2",
        )
        assert provider.id == "google"

    def test_create_underlying_provider_unsupported(self) -> None:
        """Test creating provider with unsupported prefix."""
        with pytest.raises(ValueError) as exc_info:
            _utils.create_underlying_provider(
                model_scope="unknown",
                api_key="test-key",
                router_base_url="http://localhost:3000/router/v2",
            )
        assert "Unsupported provider: unknown" in str(exc_info.value)
        assert "anthropic, google, openai" in str(exc_info.value)

    def test_create_underlying_provider_caching(self) -> None:
        """Test that provider creation is cached."""
        provider1 = _utils.create_underlying_provider(
            model_scope="openai",
            api_key="test-key",
            router_base_url="http://localhost:3000/router/v2",
        )
        provider2 = _utils.create_underlying_provider(
            model_scope="openai",
            api_key="test-key",
            router_base_url="http://localhost:3000/router/v2",
        )
        # Should be the exact same instance due to caching
        assert provider1 is provider2

        # Different parameters should create different instances
        provider3 = _utils.create_underlying_provider(
            model_scope="openai",
            api_key="different-key",
            router_base_url="http://localhost:3000/router/v2",
        )
        assert provider1 is not provider3


class TestMirascopeProvider:
    """Tests for MirascopeProvider."""

    def test_mirascope_provider_initialization_with_api_key(self) -> None:
        """Test MirascopeProvider initialization with api_key."""
        provider = MirascopeProvider(api_key="test-api-key")
        assert provider.id == "mirascope"
        assert provider.default_scope == ["anthropic/", "google/", "openai/"]
        assert provider.api_key == "test-api-key"
        assert provider.router_base_url == "https://mirascope.com/router/v2"

    def test_mirascope_provider_missing_api_key(self) -> None:
        """Test MirascopeProvider raises error when API key is missing."""
        original_key = os.environ.pop("MIRASCOPE_API_KEY", None)
        try:
            with pytest.raises(ValueError) as exc_info:
                MirascopeProvider()
            assert "Mirascope API key not found" in str(exc_info.value)
            assert "MIRASCOPE_API_KEY" in str(exc_info.value)
        finally:
            if original_key is not None:
                os.environ["MIRASCOPE_API_KEY"] = original_key

    def test_mirascope_provider_uses_env_var_api_key(self) -> None:
        """Test MirascopeProvider uses MIRASCOPE_API_KEY from environment."""
        original_key = os.environ.get("MIRASCOPE_API_KEY")
        os.environ["MIRASCOPE_API_KEY"] = "env-test-key"
        try:
            provider = MirascopeProvider()
            assert provider.api_key == "env-test-key"
        finally:
            if original_key is not None:
                os.environ["MIRASCOPE_API_KEY"] = original_key
            else:
                os.environ.pop("MIRASCOPE_API_KEY", None)

    def test_mirascope_provider_custom_base_url(self) -> None:
        """Test MirascopeProvider with custom base_url."""
        provider = MirascopeProvider(
            api_key="test-key", base_url="http://localhost:3000/router/v2"
        )
        assert provider.router_base_url == "http://localhost:3000/router/v2"

    def test_mirascope_provider_uses_env_var_base_url(self) -> None:
        """Test MirascopeProvider uses MIRASCOPE_ROUTER_BASE_URL from environment."""
        original_url = os.environ.get("MIRASCOPE_ROUTER_BASE_URL")
        os.environ["MIRASCOPE_ROUTER_BASE_URL"] = "http://custom:8080/router/v2"
        try:
            provider = MirascopeProvider(api_key="test-key")
            assert provider.router_base_url == "http://custom:8080/router/v2"
        finally:
            if original_url is not None:
                os.environ["MIRASCOPE_ROUTER_BASE_URL"] = original_url
            else:
                os.environ.pop("MIRASCOPE_ROUTER_BASE_URL", None)

    def test_get_underlying_provider_invalid_format(self) -> None:
        """Test _get_underlying_provider with invalid model ID format."""
        provider = MirascopeProvider(api_key="test-key")

        with pytest.raises(ValueError) as exc_info:
            provider._get_underlying_provider("gpt-4")  # pyright: ignore[reportPrivateUsage]
        assert "Invalid model ID format: gpt-4" in str(exc_info.value)
        assert "'scope/model-name'" in str(exc_info.value)

    def test_get_underlying_provider_valid_openai(self) -> None:
        """Test _get_underlying_provider with valid OpenAI model ID."""
        provider = MirascopeProvider(api_key="test-key")
        underlying = provider._get_underlying_provider("openai/gpt-4")  # pyright: ignore[reportPrivateUsage]
        assert underlying.id == "openai"

    def test_get_underlying_provider_valid_anthropic(self) -> None:
        """Test _get_underlying_provider with valid Anthropic model ID."""
        provider = MirascopeProvider(api_key="test-key")
        underlying = provider._get_underlying_provider("anthropic/claude-3")  # pyright: ignore[reportPrivateUsage]
        assert underlying.id == "anthropic"

    def test_get_underlying_provider_valid_google(self) -> None:
        """Test _get_underlying_provider with valid Google model ID."""
        provider = MirascopeProvider(api_key="test-key")
        underlying = provider._get_underlying_provider("google/gemini-pro")  # pyright: ignore[reportPrivateUsage]
        assert underlying.id == "google"

    @patch("mirascope.llm.providers.mirascope._utils.create_underlying_provider")
    def test_call_delegates_to_underlying_provider(
        self, mock_create_provider: Mock
    ) -> None:
        """Test that _call delegates to underlying provider."""
        mock_underlying = Mock()
        mock_underlying.call.return_value = Mock()
        mock_create_provider.return_value = mock_underlying

        provider = MirascopeProvider(api_key="test-key")
        provider._call(model_id="openai/gpt-4", messages=[], toolkit=Toolkit(None))  # pyright: ignore[reportPrivateUsage]

        mock_underlying.call.assert_called_once()

    @patch("mirascope.llm.providers.mirascope._utils.create_underlying_provider")
    def test_context_call_delegates_to_underlying_provider(
        self, mock_create_provider: Mock
    ) -> None:
        """Test that _context_call delegates to underlying provider."""
        from mirascope.llm.context import Context

        mock_underlying = Mock()
        mock_underlying.context_call.return_value = Mock()
        mock_create_provider.return_value = mock_underlying

        provider = MirascopeProvider(api_key="test-key")
        ctx = Context(deps={})
        provider._context_call(  # pyright: ignore[reportPrivateUsage]
            ctx=ctx, model_id="openai/gpt-4", messages=[], toolkit=ContextToolkit(None)
        )

        mock_underlying.context_call.assert_called_once()

    @pytest.mark.asyncio
    @patch("mirascope.llm.providers.mirascope._utils.create_underlying_provider")
    async def test_call_async_delegates_to_underlying_provider(
        self, mock_create_provider: Mock
    ) -> None:
        """Test that _call_async delegates to underlying provider."""
        mock_underlying = Mock()
        mock_underlying.call_async = AsyncMock(return_value=Mock())
        mock_create_provider.return_value = mock_underlying

        provider = MirascopeProvider(api_key="test-key")
        await provider._call_async(  # pyright: ignore[reportPrivateUsage]
            model_id="openai/gpt-4", messages=[], toolkit=AsyncToolkit(None)
        )

        mock_underlying.call_async.assert_called_once()

    @pytest.mark.asyncio
    @patch("mirascope.llm.providers.mirascope._utils.create_underlying_provider")
    async def test_context_call_async_delegates_to_underlying_provider(
        self, mock_create_provider: Mock
    ) -> None:
        """Test that _context_call_async delegates to underlying provider."""
        from mirascope.llm.context import Context

        mock_underlying = Mock()
        mock_underlying.context_call_async = AsyncMock(return_value=Mock())
        mock_create_provider.return_value = mock_underlying

        provider = MirascopeProvider(api_key="test-key")
        ctx = Context(deps={})
        await provider._context_call_async(  # pyright: ignore[reportPrivateUsage]
            ctx=ctx,
            model_id="openai/gpt-4",
            messages=[],
            toolkit=AsyncContextToolkit(None),
        )

        mock_underlying.context_call_async.assert_called_once()

    @patch("mirascope.llm.providers.mirascope._utils.create_underlying_provider")
    def test_stream_delegates_to_underlying_provider(
        self, mock_create_provider: Mock
    ) -> None:
        """Test that _stream delegates to underlying provider."""
        mock_underlying = Mock()
        mock_underlying.stream.return_value = Mock()
        mock_create_provider.return_value = mock_underlying

        provider = MirascopeProvider(api_key="test-key")
        provider._stream(model_id="openai/gpt-4", messages=[], toolkit=Toolkit(None))  # pyright: ignore[reportPrivateUsage]

        mock_underlying.stream.assert_called_once()

    @patch("mirascope.llm.providers.mirascope._utils.create_underlying_provider")
    def test_context_stream_delegates_to_underlying_provider(
        self, mock_create_provider: Mock
    ) -> None:
        """Test that _context_stream delegates to underlying provider."""
        from mirascope.llm.context import Context

        mock_underlying = Mock()
        mock_underlying.context_stream.return_value = Mock()
        mock_create_provider.return_value = mock_underlying

        provider = MirascopeProvider(api_key="test-key")
        ctx = Context(deps={})
        provider._context_stream(  # pyright: ignore[reportPrivateUsage]
            ctx=ctx, model_id="openai/gpt-4", messages=[], toolkit=ContextToolkit(None)
        )

        mock_underlying.context_stream.assert_called_once()

    @pytest.mark.asyncio
    @patch("mirascope.llm.providers.mirascope._utils.create_underlying_provider")
    async def test_stream_async_delegates_to_underlying_provider(
        self, mock_create_provider: Mock
    ) -> None:
        """Test that _stream_async delegates to underlying provider."""
        mock_underlying = Mock()
        mock_underlying.stream_async = AsyncMock(return_value=Mock())
        mock_create_provider.return_value = mock_underlying

        provider = MirascopeProvider(api_key="test-key")
        await provider._stream_async(  # pyright: ignore[reportPrivateUsage]
            model_id="openai/gpt-4", messages=[], toolkit=AsyncToolkit(None)
        )

        mock_underlying.stream_async.assert_called_once()

    @pytest.mark.asyncio
    @patch("mirascope.llm.providers.mirascope._utils.create_underlying_provider")
    async def test_context_stream_async_delegates_to_underlying_provider(
        self, mock_create_provider: Mock
    ) -> None:
        """Test that _context_stream_async delegates to underlying provider."""
        from mirascope.llm.context import Context

        mock_underlying = Mock()
        mock_underlying.context_stream_async = AsyncMock(return_value=Mock())
        mock_create_provider.return_value = mock_underlying

        provider = MirascopeProvider(api_key="test-key")
        ctx = Context(deps={})
        await provider._context_stream_async(  # pyright: ignore[reportPrivateUsage]
            ctx=ctx,
            model_id="openai/gpt-4",
            messages=[],
            toolkit=AsyncContextToolkit(None),
        )

        mock_underlying.context_stream_async.assert_called_once()


class TestMirascopeProviderErrorHandling:
    """Tests for MirascopeProvider error handling."""

    def test_error_map_exists(self) -> None:
        """Test that error_map class variable is defined."""
        assert hasattr(MirascopeProvider, "error_map")
        assert isinstance(MirascopeProvider.error_map, dict)
        assert len(MirascopeProvider.error_map) == 0

    def test_get_error_status_returns_none(self) -> None:
        """Test that get_error_status returns None."""
        provider = MirascopeProvider(api_key="test-key")
        result = provider.get_error_status(Exception("test"))
        assert result is None

    @patch("mirascope.llm.providers.mirascope._utils.create_underlying_provider")
    def test_error_propagation_from_underlying_provider(
        self, mock_create_provider: Mock
    ) -> None:
        """Test that errors from underlying providers propagate correctly."""
        from mirascope.llm.exceptions import RateLimitError

        # Mock underlying provider to raise a Mirascope exception
        mock_underlying = Mock()
        mock_underlying.call.side_effect = RateLimitError(
            "Rate limit exceeded", provider="openai"
        )
        mock_create_provider.return_value = mock_underlying

        provider = MirascopeProvider(api_key="test-key")

        # Should propagate the RateLimitError from underlying provider
        with pytest.raises(RateLimitError) as exc_info:
            provider.call(model_id="openai/gpt-4", messages=[], toolkit=Toolkit(None))

        assert "Rate limit exceeded" in str(exc_info.value)

    @pytest.mark.asyncio
    @patch("mirascope.llm.providers.mirascope._utils.create_underlying_provider")
    async def test_async_error_propagation_from_underlying_provider(
        self, mock_create_provider: Mock
    ) -> None:
        """Test that errors from underlying providers propagate correctly in async calls."""
        from mirascope.llm.exceptions import AuthenticationError

        # Mock underlying provider to raise a Mirascope exception
        mock_underlying = Mock()
        mock_underlying.call_async = AsyncMock(
            side_effect=AuthenticationError("Invalid API key", provider="anthropic")
        )
        mock_create_provider.return_value = mock_underlying

        provider = MirascopeProvider(api_key="test-key")

        # Should propagate the AuthenticationError from underlying provider
        with pytest.raises(AuthenticationError) as exc_info:
            await provider.call_async(
                model_id="anthropic/claude-3", messages=[], toolkit=AsyncToolkit(None)
            )

        assert "Invalid API key" in str(exc_info.value)

    @patch("mirascope.llm.providers.mirascope._utils.create_underlying_provider")
    def test_stream_error_propagation_from_underlying_provider(
        self, mock_create_provider: Mock
    ) -> None:
        """Test that errors from underlying providers propagate correctly in streams."""
        from mirascope.llm.exceptions import ServerError

        # Mock underlying provider to raise a Mirascope exception
        mock_underlying = Mock()
        mock_underlying.stream.side_effect = ServerError(
            "Internal server error", provider="google"
        )
        mock_create_provider.return_value = mock_underlying

        provider = MirascopeProvider(api_key="test-key")

        # Should propagate the ServerError from underlying provider
        with pytest.raises(ServerError) as exc_info:
            provider.stream(
                model_id="google/gemini-pro", messages=[], toolkit=Toolkit(None)
            )

        assert "Internal server error" in str(exc_info.value)
