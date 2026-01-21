"""Cost calculation utilities for LLM instrumentation."""

from __future__ import annotations

import logging
import re
from typing import Any

from .....api._generated.token_cost import (
    TokenCostCalculateRequestUsage,
    TokenCostCalculateResponse,
)
from .....api.client import get_async_client, get_sync_client
from .....llm.providers import get_provider_for_model
from .....llm.providers.mirascope import MirascopeProvider
from .....llm.responses.usage import Usage

logger = logging.getLogger(__name__)


def _is_via_router(model_id: str) -> bool:
    """Check if the model_id routes through MirascopeProvider (Mirascope Router).

    Args:
        model_id: The full model ID (e.g., "openai/gpt-4o").

    Returns:
        True if the registered provider for this model is MirascopeProvider.
    """
    try:
        provider = get_provider_for_model(model_id)
        return isinstance(provider, MirascopeProvider)
    except Exception:
        return False


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
    """Calculate cost synchronously. Returns None on any failure."""
    normalized_model = _normalize_model_id(model_id)
    via_router = _is_via_router(model_id)
    logger.debug(
        "Calculating cost for provider=%s, model=%s (normalized=%s), "
        "via_router=%s, usage=(input=%s, output=%s, cache_read=%s, cache_write=%s)",
        provider_id,
        model_id,
        normalized_model,
        via_router,
        usage.input_tokens,
        usage.output_tokens,
        usage.cache_read_tokens,
        usage.cache_write_tokens,
    )
    try:
        client = get_sync_client()
        logger.debug("Got sync client, making API request")
        cache_breakdown = extract_cache_write_breakdown(usage)
        if cache_breakdown:
            logger.debug("Cache write breakdown: %s", cache_breakdown)
        # Build usage kwargs, only including optional fields if they have values
        usage_kwargs: dict[str, Any] = {
            "input_tokens": usage.input_tokens,
            "output_tokens": usage.output_tokens,
        }
        if usage.cache_read_tokens:
            usage_kwargs["cache_read_tokens"] = usage.cache_read_tokens
        if usage.cache_write_tokens:
            usage_kwargs["cache_write_tokens"] = usage.cache_write_tokens
        if cache_breakdown:
            usage_kwargs["cache_write_breakdown"] = cache_breakdown
        result = client.token_cost.calculate(
            provider=provider_id,
            model=normalized_model,
            usage=TokenCostCalculateRequestUsage(**usage_kwargs),
            via_router=via_router,
        )
        logger.debug(
            "Cost calculation result: input=%s, output=%s, total=%s centicents",
            result.input_cost_centicents,
            result.output_cost_centicents,
            result.total_cost_centicents,
        )
        return result
    except Exception:
        logger.debug("Failed to calculate cost", exc_info=True)
        return None


async def calculate_cost_async(
    provider_id: str,
    model_id: str,
    usage: Usage,
) -> TokenCostCalculateResponse | None:
    """Calculate cost asynchronously. Returns None on any failure."""
    normalized_model = _normalize_model_id(model_id)
    via_router = _is_via_router(model_id)
    logger.debug(
        "Calculating cost (async) for provider=%s, model=%s (normalized=%s), "
        "via_router=%s, usage=(input=%s, output=%s, cache_read=%s, cache_write=%s)",
        provider_id,
        model_id,
        normalized_model,
        via_router,
        usage.input_tokens,
        usage.output_tokens,
        usage.cache_read_tokens,
        usage.cache_write_tokens,
    )
    try:
        client = get_async_client()
        logger.debug("Got async client, making API request")
        cache_breakdown = extract_cache_write_breakdown(usage)
        if cache_breakdown:
            logger.debug("Cache write breakdown: %s", cache_breakdown)
        # Build usage kwargs, only including optional fields if they have values
        usage_kwargs: dict[str, Any] = {
            "input_tokens": usage.input_tokens,
            "output_tokens": usage.output_tokens,
        }
        if usage.cache_read_tokens:
            usage_kwargs["cache_read_tokens"] = usage.cache_read_tokens
        if usage.cache_write_tokens:
            usage_kwargs["cache_write_tokens"] = usage.cache_write_tokens
        if cache_breakdown:
            usage_kwargs["cache_write_breakdown"] = cache_breakdown
        result = await client.token_cost.calculate(
            provider=provider_id,
            model=normalized_model,
            usage=TokenCostCalculateRequestUsage(**usage_kwargs),
            via_router=via_router,
        )
        logger.debug(
            "Cost calculation result (async): input=%s, output=%s, total=%s centicents",
            result.input_cost_centicents,
            result.output_cost_centicents,
            result.total_cost_centicents,
        )
        return result
    except Exception:
        logger.debug("Failed to calculate cost (async)", exc_info=True)
        return None
