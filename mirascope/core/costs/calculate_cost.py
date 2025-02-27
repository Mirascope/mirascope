"""Cost calculation utilities for LLM API calls."""

from __future__ import annotations

from ..base.types import CostMetadata, Provider
from ._anthropic_calculate_cost import (
    calculate_cost as anthropic_calculate_cost,
)
from ._azure_calculate_cost import calculate_cost as azure_calculate_cost
from ._bedrock_calculate_cost import calculate_cost as bedrock_calculate_cost
from ._cohere_calculate_cost import calculate_cost as cohere_calculate_cost
from ._gemini_calculate_cost import calculate_cost as gemini_calculate_cost
from ._google_calculate_cost import calculate_cost as google_calculate_cost
from ._groq_calculate_cost import calculate_cost as groq_calculate_cost
from ._litellm_calculate_cost import calculate_cost as litellm_calculate_cost
from ._mistral_calculate_cost import calculate_cost as mistral_calculate_cost
from ._openai_calculate_cost import calculate_cost as openai_calculate_cost
from ._vertex_calculate_cost import calculate_cost as vertex_calculate_cost
from ._xai_calculate_cost import calculate_cost as xai_calculate_cost


def calculate_cost(
    provider: Provider,
    model: str,
    metadata: CostMetadata | None = None,
) -> float | None:
    """Calculate the cost for an LLM API call.

    This function routes to the appropriate provider-specific cost calculation function,
    preserving existing behavior while providing a unified interface.

    Args:
        provider: The LLM provider (e.g., "openai", "anthropic")
        model: The model name (e.g., "gpt-4", "claude-3-opus")
        metadata: Additional metadata required for cost calculation

    Returns:
        The calculated cost in USD or None if unable to calculate
    """

    # Initialize empty metadata if none provided
    if metadata is None:
        metadata = CostMetadata()

    # Set default values
    if metadata.cached_tokens is None:
        metadata.cached_tokens = 0

    # Route to provider-specific implementations
    if provider == "openai":
        return openai_calculate_cost(metadata, model)

    elif provider == "anthropic":
        return anthropic_calculate_cost(metadata, model)

    elif provider == "azure":
        return azure_calculate_cost(metadata, model)

    elif provider == "bedrock":
        return bedrock_calculate_cost(metadata, model)

    elif provider == "cohere":
        return cohere_calculate_cost(metadata, model)

    elif provider == "gemini":
        return gemini_calculate_cost(metadata, model)

    elif provider == "google":
        return google_calculate_cost(metadata, model)

    elif provider == "groq":
        return groq_calculate_cost(metadata, model)

    elif provider == "mistral":
        return mistral_calculate_cost(metadata, model)

    elif provider == "vertex":
        return vertex_calculate_cost(metadata, model)

    elif provider == "xai":
        return xai_calculate_cost(metadata, model)

    elif provider == "litellm":
        return litellm_calculate_cost(metadata, model)
    else:
        raise ValueError(f"Unsupported provider: {provider}")
