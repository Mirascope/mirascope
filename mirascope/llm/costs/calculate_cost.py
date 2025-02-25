"""Cost calculation utilities for LLM API calls."""

from __future__ import annotations

from typing import Any, Literal

Provider = Literal[
    "anthropic",
    "azure",
    "bedrock",
    "cohere",
    "gemini",
    "google",
    "groq",
    "litellm",
    "mistral",
    "openai",
    "vertex",
    "xai",
]


def calculate_cost(
    provider: Provider,
    model: str,
    input_tokens: int | float | None,
    output_tokens: int | float | None = None,
    cached_tokens: int | float | None = None,
    **kwargs: Any,  # noqa: ANN401
) -> float | None:
    """Calculate the cost for an LLM API call.

    This function routes to the appropriate provider-specific cost calculation function,
    preserving existing behavior while providing a unified interface.

    Args:
        provider: The LLM provider (e.g., "openai", "anthropic")
        model: The model name (e.g., "gpt-4", "claude-3-opus")
        input_tokens: Number of input/prompt tokens
        output_tokens: Number of output/completion tokens (if applicable)
        cached_tokens: Number of tokens served from cache (may be priced differently)
        **kwargs: Additional provider-specific parameters

    Returns:
        The calculated cost in USD or None if unable to calculate
    """
    if cached_tokens is None:
        cached_tokens = 0

    if provider == "openai":
        from ._openai_calculate_cost import calculate_cost as openai_calculate_cost

        return openai_calculate_cost(input_tokens, cached_tokens, output_tokens, model)

    elif provider == "anthropic":
        from ._anthropic_calculate_cost import (
            calculate_cost as anthropic_calculate_cost,
        )

        return anthropic_calculate_cost(
            input_tokens, cached_tokens, output_tokens, model
        )

    elif provider == "azure":
        from ._azure_calculate_cost import calculate_cost as azure_calculate_cost

        return azure_calculate_cost(input_tokens, cached_tokens, output_tokens, model)

    elif provider == "bedrock":
        from ._bedrock_calculate_cost import calculate_cost as bedrock_calculate_cost

        return bedrock_calculate_cost(input_tokens, cached_tokens, output_tokens, model)

    elif provider == "cohere":
        from ._cohere_calculate_cost import calculate_cost as cohere_calculate_cost

        return cohere_calculate_cost(input_tokens, cached_tokens, output_tokens, model)

    elif provider == "gemini":
        from ._gemini_calculate_cost import calculate_cost as gemini_calculate_cost

        return gemini_calculate_cost(input_tokens, cached_tokens, output_tokens, model)

    elif provider == "google":
        from ._google_calculate_cost import calculate_cost as google_calculate_cost

        return google_calculate_cost(input_tokens, cached_tokens, output_tokens, model)

    elif provider == "groq":
        from ._groq_calculate_cost import calculate_cost as groq_calculate_cost

        return groq_calculate_cost(input_tokens, cached_tokens, output_tokens, model)

    elif provider == "mistral":
        from ._mistral_calculate_cost import calculate_cost as mistral_calculate_cost

        return mistral_calculate_cost(input_tokens, cached_tokens, output_tokens, model)

    elif provider == "vertex":
        from ._vertex_calculate_cost import calculate_cost as vertex_calculate_cost

        context_length = kwargs.get("context_length", 0)
        return vertex_calculate_cost(
            input_tokens, cached_tokens, output_tokens, model, context_length
        )

    elif provider == "xai":
        from ._xai_calculate_cost import calculate_cost as xai_calculate_cost

        return xai_calculate_cost(input_tokens, cached_tokens, output_tokens, model)

    elif provider == "litellm":
        # LiteLLM currently does not support cost calculation
        return None
    else:
        raise ValueError(f"Unsupported provider: {provider}")
