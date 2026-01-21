"""Unit tests for cost calculation in ops instrumentation."""

from __future__ import annotations

from typing import TYPE_CHECKING
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from mirascope.llm.responses.usage import Usage
from mirascope.ops._internal.instrumentation.llm.cost import (
    _is_via_router,  # pyright: ignore[reportPrivateUsage]
    _normalize_model_id,  # pyright: ignore[reportPrivateUsage]
    calculate_cost_async,
    calculate_cost_sync,
    extract_cache_write_breakdown,
)

if TYPE_CHECKING:
    pass


class TestNormalizeModelId:
    """Tests for _normalize_model_id function."""

    def test_normalize_with_prefix(self) -> None:
        """Test normalizing model_id with provider prefix."""
        assert _normalize_model_id("openai/gpt-4o") == "gpt-4o"
        assert (
            _normalize_model_id("anthropic/claude-sonnet-4-20250514")
            == "claude-sonnet-4-20250514"
        )
        assert _normalize_model_id("google/gemini-2.0-flash") == "gemini-2.0-flash"

    def test_normalize_with_prefix_and_suffix(self) -> None:
        """Test normalizing model_id with prefix and API suffix."""
        assert _normalize_model_id("openai/gpt-4o:responses") == "gpt-4o"
        assert _normalize_model_id("openai/gpt-4o:completions") == "gpt-4o"
        assert _normalize_model_id("openai/o1:responses") == "o1"

    def test_normalize_without_prefix(self) -> None:
        """Test normalizing model_id without prefix."""
        assert _normalize_model_id("gpt-4o") == "gpt-4o"
        assert (
            _normalize_model_id("claude-sonnet-4-20250514")
            == "claude-sonnet-4-20250514"
        )

    def test_normalize_without_prefix_with_suffix(self) -> None:
        """Test normalizing model_id without prefix but with suffix."""
        assert _normalize_model_id("gpt-4o:responses") == "gpt-4o"
        assert _normalize_model_id("gpt-4o:completions") == "gpt-4o"

    def test_normalize_future_suffix(self) -> None:
        """Test that any :suffix is stripped (future-proofing)."""
        assert _normalize_model_id("openai/gpt-4o:new_api_mode") == "gpt-4o"
        assert _normalize_model_id("gpt-4o:unknown") == "gpt-4o"


class TestIsViaRouter:
    """Tests for _is_via_router function."""

    def test_via_router_with_mirascope_provider(self) -> None:
        """Test detection when MirascopeProvider is registered."""
        from mirascope.llm.providers.mirascope import MirascopeProvider

        # Create actual MirascopeProvider instance for isinstance check
        # We mock get_provider_for_model to return it
        mock_provider = MagicMock(spec=MirascopeProvider)
        # Make the mock appear as MirascopeProvider instance
        mock_provider.__class__ = MirascopeProvider  # pyright: ignore[reportAttributeAccessIssue]

        with patch(
            "mirascope.ops._internal.instrumentation.llm.cost.get_provider_for_model",
            return_value=mock_provider,
        ):
            result = _is_via_router("openai/gpt-4o")
            assert result is True

    def test_via_router_with_openai_provider(self) -> None:
        """Test detection returns False for non-MirascopeProvider."""
        from mirascope.llm.providers.openai import OpenAIProvider

        mock_provider = MagicMock(spec=OpenAIProvider)

        with patch(
            "mirascope.ops._internal.instrumentation.llm.cost.get_provider_for_model",
            return_value=mock_provider,
        ):
            result = _is_via_router("openai/gpt-4o")
            assert result is False

    def test_via_router_exception_returns_false(self) -> None:
        """Test that exceptions return False."""
        with patch(
            "mirascope.ops._internal.instrumentation.llm.cost.get_provider_for_model",
            side_effect=Exception("No provider"),
        ):
            result = _is_via_router("unknown/model")
            assert result is False


def _make_mock_cost_response(
    input_cost: float = 25.0,
    output_cost: float = 50.0,
    total_cost: float = 75.0,
    cache_read_cost: float | None = None,
    cache_write_cost: float | None = None,
) -> MagicMock:
    """Create a mock TokenCostCalculateResponse."""
    mock = MagicMock()
    mock.input_cost_centicents = input_cost
    mock.output_cost_centicents = output_cost
    mock.total_cost_centicents = total_cost
    mock.cache_read_cost_centicents = cache_read_cost
    mock.cache_write_cost_centicents = cache_write_cost
    return mock


class TestExtractCacheWriteBreakdown:
    """Tests for extract_cache_write_breakdown function."""

    def test_extract_breakdown_with_anthropic_usage(self) -> None:
        """Test extraction with Anthropic's cache_creation breakdown."""
        # Mock Anthropic's raw usage structure
        mock_cache_creation = MagicMock()
        mock_cache_creation.ephemeral_5m_input_tokens = 100
        mock_cache_creation.ephemeral_1h_input_tokens = 50

        mock_raw = MagicMock()
        mock_raw.cache_creation = mock_cache_creation

        usage = Usage(input_tokens=150, output_tokens=50, raw=mock_raw)
        result = extract_cache_write_breakdown(usage)

        assert result == {"ephemeral5m": 100.0, "ephemeral1h": 50.0}

    def test_extract_breakdown_only_5m(self) -> None:
        """Test extraction with only 5m cache tokens."""
        mock_cache_creation = MagicMock()
        mock_cache_creation.ephemeral_5m_input_tokens = 100
        mock_cache_creation.ephemeral_1h_input_tokens = 0

        mock_raw = MagicMock()
        mock_raw.cache_creation = mock_cache_creation

        usage = Usage(input_tokens=100, output_tokens=50, raw=mock_raw)
        result = extract_cache_write_breakdown(usage)

        assert result == {"ephemeral5m": 100.0}

    def test_extract_breakdown_only_1h(self) -> None:
        """Test extraction with only 1h cache tokens."""
        mock_cache_creation = MagicMock()
        mock_cache_creation.ephemeral_5m_input_tokens = 0
        mock_cache_creation.ephemeral_1h_input_tokens = 200

        mock_raw = MagicMock()
        mock_raw.cache_creation = mock_cache_creation

        usage = Usage(input_tokens=200, output_tokens=50, raw=mock_raw)
        result = extract_cache_write_breakdown(usage)

        assert result == {"ephemeral1h": 200.0}

    def test_extract_breakdown_no_raw(self) -> None:
        """Test extraction returns None when no raw data."""
        usage = Usage(input_tokens=100, output_tokens=50, raw=None)
        result = extract_cache_write_breakdown(usage)
        assert result is None

    def test_extract_breakdown_no_cache_creation(self) -> None:
        """Test extraction returns None when no cache_creation attribute."""
        mock_raw = MagicMock(spec=[])  # No cache_creation attribute
        usage = Usage(input_tokens=100, output_tokens=50, raw=mock_raw)
        result = extract_cache_write_breakdown(usage)
        assert result is None

    def test_extract_breakdown_zero_values(self) -> None:
        """Test extraction returns None when all cache values are zero."""
        mock_cache_creation = MagicMock()
        mock_cache_creation.ephemeral_5m_input_tokens = 0
        mock_cache_creation.ephemeral_1h_input_tokens = 0

        mock_raw = MagicMock()
        mock_raw.cache_creation = mock_cache_creation

        usage = Usage(input_tokens=100, output_tokens=50, raw=mock_raw)
        result = extract_cache_write_breakdown(usage)
        assert result is None

    def test_extract_breakdown_ephemeral_attributes_none(self) -> None:
        """Test extraction returns None when cache_creation exists but has no ephemeral attributes."""
        # Create a cache_creation mock that exists but doesn't have the ephemeral_*_input_tokens attributes
        mock_cache_creation = MagicMock(spec=[])  # Empty spec = no attributes

        mock_raw = MagicMock()
        mock_raw.cache_creation = mock_cache_creation

        usage = Usage(input_tokens=100, output_tokens=50, raw=mock_raw)
        result = extract_cache_write_breakdown(usage)
        assert result is None


class TestCalculateCostSync:
    """Tests for calculate_cost_sync function."""

    def test_calculate_cost_success(self) -> None:
        """Test successful cost calculation."""
        mock_response = _make_mock_cost_response()
        mock_client = MagicMock()
        mock_client.token_cost.calculate.return_value = mock_response

        with patch(
            "mirascope.ops._internal.instrumentation.llm.cost.get_sync_client",
            return_value=mock_client,
        ):
            usage = Usage(input_tokens=100, output_tokens=50)
            result = calculate_cost_sync("openai", "gpt-4o", usage)

            assert result is not None
            assert result.input_cost_centicents == 25.0
            assert result.output_cost_centicents == 50.0
            assert result.total_cost_centicents == 75.0

    def test_calculate_cost_normalizes_model_id(self) -> None:
        """Test that model_id is normalized before API call."""
        mock_response = _make_mock_cost_response()
        mock_client = MagicMock()
        mock_client.token_cost.calculate.return_value = mock_response

        with patch(
            "mirascope.ops._internal.instrumentation.llm.cost.get_sync_client",
            return_value=mock_client,
        ):
            usage = Usage(input_tokens=100, output_tokens=50)
            # Pass prefixed model_id with suffix
            result = calculate_cost_sync("openai", "openai/gpt-4o:responses", usage)

            assert result is not None
            # Verify the API was called with normalized model name
            call_kwargs = mock_client.token_cost.calculate.call_args.kwargs
            assert call_kwargs["model"] == "gpt-4o"

    def test_calculate_cost_with_cache_tokens(self) -> None:
        """Test cost calculation with cache tokens."""
        mock_response = _make_mock_cost_response(
            cache_read_cost=5.0, cache_write_cost=10.0
        )
        mock_client = MagicMock()
        mock_client.token_cost.calculate.return_value = mock_response

        with patch(
            "mirascope.ops._internal.instrumentation.llm.cost.get_sync_client",
            return_value=mock_client,
        ):
            usage = Usage(
                input_tokens=100,
                output_tokens=50,
                cache_read_tokens=20,
                cache_write_tokens=10,
            )
            result = calculate_cost_sync("anthropic", "claude-sonnet-4-20250514", usage)

            assert result is not None
            assert result.cache_read_cost_centicents == 5.0
            assert result.cache_write_cost_centicents == 10.0

            # Verify the API was called with correct parameters
            call_kwargs = mock_client.token_cost.calculate.call_args.kwargs
            assert call_kwargs["usage"].cache_read_tokens == 20
            assert call_kwargs["usage"].cache_write_tokens == 10

    def test_calculate_cost_with_cache_write_breakdown(self) -> None:
        """Test cost calculation includes cache write breakdown from Anthropic raw data."""
        mock_response = _make_mock_cost_response(
            cache_read_cost=5.0, cache_write_cost=15.0
        )
        mock_client = MagicMock()
        mock_client.token_cost.calculate.return_value = mock_response

        # Create Anthropic-style raw usage with cache_creation breakdown
        mock_cache_creation = MagicMock()
        mock_cache_creation.ephemeral_5m_input_tokens = 100
        mock_cache_creation.ephemeral_1h_input_tokens = 50

        mock_raw = MagicMock()
        mock_raw.cache_creation = mock_cache_creation

        with patch(
            "mirascope.ops._internal.instrumentation.llm.cost.get_sync_client",
            return_value=mock_client,
        ):
            usage = Usage(
                input_tokens=200,
                output_tokens=50,
                cache_read_tokens=30,
                cache_write_tokens=150,
                raw=mock_raw,
            )
            result = calculate_cost_sync("anthropic", "claude-sonnet-4-20250514", usage)

            assert result is not None
            assert result.cache_write_cost_centicents == 15.0

            # Verify the API was called with cache_write_breakdown
            call_kwargs = mock_client.token_cost.calculate.call_args.kwargs
            assert call_kwargs["usage"].cache_write_breakdown == {
                "ephemeral5m": 100.0,
                "ephemeral1h": 50.0,
            }

    def test_calculate_cost_client_error_returns_none(self) -> None:
        """Test that client errors return None without raising."""
        mock_client = MagicMock()
        mock_client.token_cost.calculate.side_effect = RuntimeError("API error")

        with patch(
            "mirascope.ops._internal.instrumentation.llm.cost.get_sync_client",
            return_value=mock_client,
        ):
            usage = Usage(input_tokens=100, output_tokens=50)
            result = calculate_cost_sync("openai", "gpt-4o", usage)

            assert result is None

    def test_calculate_cost_get_client_error_returns_none(self) -> None:
        """Test that get_sync_client errors return None without raising."""
        with patch(
            "mirascope.ops._internal.instrumentation.llm.cost.get_sync_client",
            side_effect=RuntimeError("No API key"),
        ):
            usage = Usage(input_tokens=100, output_tokens=50)
            result = calculate_cost_sync("openai", "gpt-4o", usage)

            assert result is None


class TestCalculateCostAsync:
    """Tests for calculate_cost_async function."""

    @pytest.mark.asyncio
    async def test_calculate_cost_async_success(self) -> None:
        """Test successful async cost calculation."""
        mock_response = _make_mock_cost_response()
        mock_client = MagicMock()
        mock_client.token_cost.calculate = AsyncMock(return_value=mock_response)

        with patch(
            "mirascope.ops._internal.instrumentation.llm.cost.get_async_client",
            return_value=mock_client,
        ):
            usage = Usage(input_tokens=100, output_tokens=50)
            result = await calculate_cost_async("openai", "gpt-4o", usage)

            assert result is not None
            assert result.input_cost_centicents == 25.0
            assert result.output_cost_centicents == 50.0
            assert result.total_cost_centicents == 75.0

    @pytest.mark.asyncio
    async def test_calculate_cost_async_with_cache_tokens(self) -> None:
        """Test async cost calculation with cache tokens."""
        mock_response = _make_mock_cost_response(
            cache_read_cost=5.0, cache_write_cost=10.0
        )
        mock_client = MagicMock()
        mock_client.token_cost.calculate = AsyncMock(return_value=mock_response)

        with patch(
            "mirascope.ops._internal.instrumentation.llm.cost.get_async_client",
            return_value=mock_client,
        ):
            usage = Usage(
                input_tokens=100,
                output_tokens=50,
                cache_read_tokens=20,
                cache_write_tokens=10,
            )
            result = await calculate_cost_async(
                "anthropic", "claude-sonnet-4-20250514", usage
            )

            assert result is not None
            assert result.cache_read_cost_centicents == 5.0
            assert result.cache_write_cost_centicents == 10.0

    @pytest.mark.asyncio
    async def test_calculate_cost_async_with_cache_write_breakdown(self) -> None:
        """Test async cost calculation includes cache write breakdown from Anthropic raw data."""
        mock_response = _make_mock_cost_response(
            cache_read_cost=5.0, cache_write_cost=15.0
        )
        mock_client = MagicMock()
        mock_client.token_cost.calculate = AsyncMock(return_value=mock_response)

        # Create Anthropic-style raw usage with cache_creation breakdown
        mock_cache_creation = MagicMock()
        mock_cache_creation.ephemeral_5m_input_tokens = 100
        mock_cache_creation.ephemeral_1h_input_tokens = 50

        mock_raw = MagicMock()
        mock_raw.cache_creation = mock_cache_creation

        with patch(
            "mirascope.ops._internal.instrumentation.llm.cost.get_async_client",
            return_value=mock_client,
        ):
            usage = Usage(
                input_tokens=200,
                output_tokens=50,
                cache_read_tokens=30,
                cache_write_tokens=150,
                raw=mock_raw,
            )
            result = await calculate_cost_async(
                "anthropic", "claude-sonnet-4-20250514", usage
            )

            assert result is not None
            assert result.cache_write_cost_centicents == 15.0

            # Verify the API was called with cache_write_breakdown
            call_kwargs = mock_client.token_cost.calculate.call_args.kwargs
            assert call_kwargs["usage"].cache_write_breakdown == {
                "ephemeral5m": 100.0,
                "ephemeral1h": 50.0,
            }

    @pytest.mark.asyncio
    async def test_calculate_cost_async_client_error_returns_none(self) -> None:
        """Test that async client errors return None without raising."""
        mock_client = MagicMock()
        mock_client.token_cost.calculate = AsyncMock(
            side_effect=RuntimeError("API error")
        )

        with patch(
            "mirascope.ops._internal.instrumentation.llm.cost.get_async_client",
            return_value=mock_client,
        ):
            usage = Usage(input_tokens=100, output_tokens=50)
            result = await calculate_cost_async("openai", "gpt-4o", usage)

            assert result is None

    @pytest.mark.asyncio
    async def test_calculate_cost_async_get_client_error_returns_none(self) -> None:
        """Test that get_async_client errors return None without raising."""
        with patch(
            "mirascope.ops._internal.instrumentation.llm.cost.get_async_client",
            side_effect=RuntimeError("No API key"),
        ):
            usage = Usage(input_tokens=100, output_tokens=50)
            result = await calculate_cost_async("openai", "gpt-4o", usage)

            assert result is None
