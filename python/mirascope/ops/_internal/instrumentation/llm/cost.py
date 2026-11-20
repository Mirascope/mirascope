"""Cost calculation utilities for LLM instrumentation."""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass

import llm_prices

from .....llm.responses.usage import Usage

logger = logging.getLogger(__name__)

_CENTICENTS_PER_USD = 10_000

# Mirascope provider ids that bill at another provider's prices.
_PRICING_PROVIDER_ALIASES: dict[str, str] = {
    "anthropic-beta": "anthropic",
}


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


def _normalize_provider_id(provider_id: str) -> str:
    """Normalize a Mirascope provider id to the provider whose prices apply.

    Args:
        provider_id: The provider id (e.g., "openai:completions", "anthropic-beta").

    Returns:
        The pricing provider name (e.g., "openai", "anthropic").
    """
    provider_id = provider_id.split(":", 1)[0]
    return _PRICING_PROVIDER_ALIASES.get(provider_id, provider_id)


def _normalize_model_id(model_id: str) -> str:
    """Normalize model_id by stripping provider prefix and any :suffix.

    Args:
        model_id: The full model ID (e.g., "openai/gpt-4o:responses").

    Returns:
        The base model name (e.g., "gpt-4o").
    """
    # Strip provider prefix (e.g., "openai/gpt-4o" -> "gpt-4o")
    if "/" in model_id:
        model_id = model_id.split("/", 1)[1]
    # Strip any :suffix (e.g., ":responses", ":completions")
    return re.sub(r":.*$", "", model_id)


def _to_priced_usage(usage: Usage) -> llm_prices.Usage:
    """Convert Mirascope usage to `llm_prices.Usage`.

    Mirascope's `input_tokens` includes cache reads and writes, while `llm_prices`
    expects them split out. Cache writes use Anthropic's 5m/1h breakdown when the raw
    usage has one; any cache writes it does not cover bill at the default 5m lifetime.
    """
    cache_read = max(usage.cache_read_tokens, 0)
    cache_write = max(usage.cache_write_tokens, 0)
    breakdown = extract_cache_write_breakdown(usage) or {}
    cache_write_1h = min(int(breakdown.get("ephemeral1h", 0)), cache_write)
    cache_write_5m = cache_write - cache_write_1h
    return llm_prices.Usage(
        input=max(usage.input_tokens - cache_read - cache_write, 0),
        output=max(usage.output_tokens, 0),
        cache_read=cache_read,
        cache_write_5m=cache_write_5m,
        cache_write_1h=cache_write_1h,
    )


def _calculate_cost(
    provider_id: str,
    model_id: str,
    usage: Usage,
) -> TokenCostCalculateResponse | None:
    """Calculate cost from the bundled `llm_prices` table. Returns None on any failure."""
    pricing_provider = _normalize_provider_id(provider_id)
    normalized_model = _normalize_model_id(model_id)
    logger.debug(
        "Calculating cost for provider=%s (pricing=%s), model=%s (normalized=%s), "
        "usage=(input=%s, output=%s, cache_read=%s, cache_write=%s)",
        provider_id,
        pricing_provider,
        model_id,
        normalized_model,
        usage.input_tokens,
        usage.output_tokens,
        usage.cache_read_tokens,
        usage.cache_write_tokens,
    )
    try:
        price = llm_prices.lookup_provider(pricing_provider, normalized_model)
        if price is None:
            logger.debug(
                "No price listed for %s/%s", pricing_provider, normalized_model
            )
            return None
        cost = price.cost_usage(_to_priced_usage(usage))
        if cost is None:
            logger.debug("Price for %s is missing a rate this usage needs", price.model)
            return None
    except Exception:
        logger.debug("Failed to calculate cost", exc_info=True)
        return None
    result = TokenCostCalculateResponse(
        input_cost_centicents=cost.input * _CENTICENTS_PER_USD,
        output_cost_centicents=cost.output * _CENTICENTS_PER_USD,
        cache_read_cost_centicents=cost.cache_read * _CENTICENTS_PER_USD,
        cache_write_cost_centicents=cost.cache_write * _CENTICENTS_PER_USD,
        total_cost_centicents=cost.total * _CENTICENTS_PER_USD,
    )
    logger.debug(
        "Cost calculation result: input=%s, output=%s, total=%s centicents",
        result.input_cost_centicents,
        result.output_cost_centicents,
        result.total_cost_centicents,
    )
    return result


def calculate_cost_sync(
    provider_id: str,
    model_id: str,
    usage: Usage,
) -> TokenCostCalculateResponse | None:
    """Calculate cost synchronously. Returns None on any failure.

    Prices come from the `llm_prices` table installed with the `ops` extra, so no
    network call is made. Returns None when the provider or model has no listed price.
    """
    return _calculate_cost(provider_id, model_id, usage)


async def calculate_cost_async(
    provider_id: str,
    model_id: str,
    usage: Usage,
) -> TokenCostCalculateResponse | None:
    """Calculate cost asynchronously. Returns None on any failure.

    Prices come from the `llm_prices` table installed with the `ops` extra, so no
    network call is made. Returns None when the provider or model has no listed price.
    """
    return _calculate_cost(provider_id, model_id, usage)
