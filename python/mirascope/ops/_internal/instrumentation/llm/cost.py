"""Cost calculation utilities for LLM instrumentation."""

from __future__ import annotations

import logging
from dataclasses import dataclass

from .....llm.responses.usage import Usage

logger = logging.getLogger(__name__)


@dataclass
class TokenCostCalculateResponse:
    """Response from cost calculation."""

    input_cost_centicents: float | None = None
    output_cost_centicents: float | None = None
    cache_read_cost_centicents: float | None = None
    cache_write_cost_centicents: float | None = None
    total_cost_centicents: float | None = None


def extract_cache_write_breakdown(usage: Usage) -> dict[str, float] | None:
    """Extract cache write breakdown from Anthropic's raw usage data.

    Returns a dict like {"ephemeral5m": 100, "ephemeral1h": 50} if available,
    or None if the breakdown isn't available.
    """
    raw = usage.raw
    if raw is None:
        return None

    # Check for Anthropic's cache_creation breakdown
    cache_creation = getattr(raw, "cache_creation", None)
    if cache_creation is None:
        return None

    ephemeral_5m = getattr(cache_creation, "ephemeral_5m_input_tokens", None)
    ephemeral_1h = getattr(cache_creation, "ephemeral_1h_input_tokens", None)

    if ephemeral_5m is None and ephemeral_1h is None:
        return None

    breakdown: dict[str, float] = {}
    if ephemeral_5m is not None and ephemeral_5m > 0:
        breakdown["ephemeral5m"] = float(ephemeral_5m)
    if ephemeral_1h is not None and ephemeral_1h > 0:
        breakdown["ephemeral1h"] = float(ephemeral_1h)

    return breakdown if breakdown else None


def calculate_cost_sync(
    provider_id: str,
    model_id: str,
    usage: Usage,
) -> TokenCostCalculateResponse | None:
    """Calculate cost synchronously. Returns None (cloud service removed)."""
    return None


async def calculate_cost_async(
    provider_id: str,
    model_id: str,
    usage: Usage,
) -> TokenCostCalculateResponse | None:
    """Calculate cost asynchronously. Returns None (cloud service removed)."""
    return None
