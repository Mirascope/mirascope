"""Unit tests for cost calculation in ops instrumentation."""

from __future__ import annotations

from unittest.mock import MagicMock

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


class TestCalculateCostSync:
    """Tests for calculate_cost_sync function."""

    def test_calculate_cost_returns_none(self) -> None:
        """Test that cost calculation returns None (cloud service removed)."""
        usage = Usage(input_tokens=100, output_tokens=50)
        result = calculate_cost_sync("openai", "gpt-4o", usage)
        assert result is None


class TestCalculateCostAsync:
    """Tests for calculate_cost_async function."""

    @pytest.mark.asyncio
    async def test_calculate_cost_async_returns_none(self) -> None:
        """Test that async cost calculation returns None (cloud service removed)."""
        usage = Usage(input_tokens=100, output_tokens=50)
        result = await calculate_cost_async("openai", "gpt-4o", usage)
        assert result is None
