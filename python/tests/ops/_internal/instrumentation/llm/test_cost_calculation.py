"""Unit tests for cost calculation in ops instrumentation."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import llm_prices
import pytest

from mirascope.llm.responses.usage import Usage
from mirascope.ops._internal.instrumentation.llm.cost import (
    calculate_cost_async,
    calculate_cost_sync,
    extract_cache_write_breakdown,
)


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
        mock_cache_creation = MagicMock(spec=[])  # Empty spec = no attributes

        mock_raw = MagicMock()
        mock_raw.cache_creation = mock_cache_creation

        usage = Usage(input_tokens=100, output_tokens=50, raw=mock_raw)
        result = extract_cache_write_breakdown(usage)
        assert result is None


def _price(provider: str, model: str) -> llm_prices.Price:
    """Look up a price row the tests expect `llm_prices` to list."""
    price = llm_prices.lookup_provider(provider, model)
    assert price is not None
    return price


def _anthropic_raw_usage(ephemeral_5m: int, ephemeral_1h: int) -> MagicMock:
    """Mock Anthropic's raw usage with a cache_creation breakdown."""
    mock_cache_creation = MagicMock()
    mock_cache_creation.ephemeral_5m_input_tokens = ephemeral_5m
    mock_cache_creation.ephemeral_1h_input_tokens = ephemeral_1h
    mock_raw = MagicMock()
    mock_raw.cache_creation = mock_cache_creation
    return mock_raw


class TestCalculateCostSync:
    """Tests for calculate_cost_sync function."""

    def test_calculate_cost_openai(self) -> None:
        """Test that input and output tokens are priced in centicents."""
        price = _price("openai", "gpt-4o")
        assert price.input is not None
        assert price.output is not None
        usage = Usage(input_tokens=1_000_000, output_tokens=100_000)

        result = calculate_cost_sync("openai", "openai/gpt-4o", usage)

        assert result is not None
        assert result.input_cost_centicents == pytest.approx(price.input * 10_000)
        assert result.output_cost_centicents == pytest.approx(price.output * 1_000)
        assert result.cache_read_cost_centicents == 0.0
        assert result.cache_write_cost_centicents == 0.0
        assert result.total_cost_centicents == pytest.approx(
            price.input * 10_000 + price.output * 1_000
        )

    def test_calculate_cost_strips_api_suffix(self) -> None:
        """Test that `:responses` and `:completions` suffixes are ignored."""
        usage = Usage(input_tokens=1_000, output_tokens=500)

        responses = calculate_cost_sync("openai", "openai/gpt-4o:responses", usage)
        completions = calculate_cost_sync(
            "openai:completions", "openai/gpt-4o:completions", usage
        )
        plain = calculate_cost_sync("openai", "openai/gpt-4o", usage)

        assert plain is not None
        assert responses == plain
        assert completions == plain

    def test_calculate_cost_cache_read_not_billed_as_input(self) -> None:
        """Test that cached input tokens bill at the cache read price, not twice."""
        price = _price("openai", "gpt-4o")
        assert price.input is not None
        assert price.cache_read is not None
        # Mirascope's input_tokens includes the cached tokens.
        usage = Usage(input_tokens=10_000, output_tokens=0, cache_read_tokens=8_000)

        result = calculate_cost_sync("openai", "openai/gpt-4o", usage)

        assert result is not None
        assert result.input_cost_centicents == pytest.approx(price.input * 20)
        assert result.cache_read_cost_centicents == pytest.approx(price.cache_read * 80)
        assert result.total_cost_centicents == pytest.approx(
            price.input * 20 + price.cache_read * 80
        )

    def test_calculate_cost_anthropic_cache_write_breakdown(self) -> None:
        """Test that Anthropic's 5m and 1h cache writes bill at their own prices."""
        price = _price("anthropic", "claude-sonnet-4-5")
        assert price.input is not None
        assert price.output is not None
        rate_5m = price.cache_write["5m"]
        rate_1h = price.cache_write["1h"]
        assert rate_1h > rate_5m
        usage = Usage(
            input_tokens=1_000 + 3_000 + 1_000,
            output_tokens=200,
            cache_write_tokens=3_000 + 1_000,
            raw=_anthropic_raw_usage(ephemeral_5m=3_000, ephemeral_1h=1_000),
        )

        result = calculate_cost_sync("anthropic", "anthropic/claude-sonnet-4-5", usage)

        assert result is not None
        assert result.input_cost_centicents == pytest.approx(price.input * 10)
        assert result.cache_write_cost_centicents == pytest.approx(
            rate_5m * 30 + rate_1h * 10
        )
        assert result.output_cost_centicents == pytest.approx(price.output * 2)

    def test_calculate_cost_cache_write_without_breakdown_bills_5m(self) -> None:
        """Test that cache writes without a breakdown use the default 5m lifetime."""
        price = _price("anthropic", "claude-sonnet-4-5")
        usage = Usage(input_tokens=4_000, output_tokens=0, cache_write_tokens=4_000)

        result = calculate_cost_sync(
            "anthropic-beta", "anthropic-beta/claude-sonnet-4-5", usage
        )

        assert result is not None
        assert result.input_cost_centicents == 0.0
        assert result.cache_write_cost_centicents == pytest.approx(
            price.cache_write["5m"] * 40
        )

    def test_calculate_cost_google(self) -> None:
        """Test that Google models are priced under the `google` provider id."""
        price = _price("google", "gemini-2.5-flash")
        assert price.input is not None
        usage = Usage(input_tokens=1_000_000, output_tokens=0)

        result = calculate_cost_sync("google", "google/gemini-2.5-flash", usage)

        assert result is not None
        assert result.total_cost_centicents == pytest.approx(price.input * 10_000)

    def test_calculate_cost_unknown_model_returns_none(self) -> None:
        """Test that a model with no listed price returns None."""
        usage = Usage(input_tokens=100, output_tokens=50)
        assert calculate_cost_sync("openai", "openai/not-a-model", usage) is None

    def test_calculate_cost_unpriced_provider_returns_none(self) -> None:
        """Test that a local provider is not priced with a hosted provider's rates."""
        usage = Usage(input_tokens=100, output_tokens=50)
        assert calculate_cost_sync("ollama", "ollama/gpt-oss:20b", usage) is None
        assert (
            calculate_cost_sync("mlx", "mlx-community/Qwen3-8B-4bit-DWQ-053125", usage)
            is None
        )

    def test_calculate_cost_missing_rate_returns_none(self) -> None:
        """Test that None is returned when the price lacks a rate the usage needs."""
        usage = Usage(input_tokens=100, output_tokens=50)
        with patch.object(llm_prices.Price, "cost_usage", return_value=None):
            assert calculate_cost_sync("openai", "openai/gpt-4o", usage) is None

    def test_calculate_cost_failure_returns_none(self) -> None:
        """Test that a pricing failure never breaks instrumentation."""
        usage = Usage(input_tokens=100, output_tokens=50)
        with patch.object(
            llm_prices, "lookup_provider", side_effect=RuntimeError("boom")
        ):
            assert calculate_cost_sync("openai", "openai/gpt-4o", usage) is None


class TestCalculateCostAsync:
    """Tests for calculate_cost_async function."""

    @pytest.mark.asyncio
    async def test_calculate_cost_async_matches_sync(self) -> None:
        """Test that async cost calculation matches the sync result."""
        usage = Usage(input_tokens=1_000, output_tokens=500, cache_read_tokens=200)
        result = await calculate_cost_async("openai", "openai/gpt-4o", usage)
        assert result is not None
        assert result == calculate_cost_sync("openai", "openai/gpt-4o", usage)

    @pytest.mark.asyncio
    async def test_calculate_cost_async_unknown_model_returns_none(self) -> None:
        """Test that async cost calculation returns None for an unknown model."""
        usage = Usage(input_tokens=100, output_tokens=50)
        result = await calculate_cost_async("openai", "openai/not-a-model", usage)
        assert result is None
