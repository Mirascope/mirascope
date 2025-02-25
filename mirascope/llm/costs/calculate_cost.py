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
]


def calculate_cost(
    provider: Provider,
    model: str,
    prompt_tokens: int,
    completion_tokens: int | None = None,
    stream: bool = False,
    **kwargs: Any,  # noqa: ANN401
) -> float | None:
    """Calculate the cost for an LLM API call.

    This function calculates the cost in USD for an API call to a language model
    based on the provider, model, and token usage.

    Args:
        provider: The LLM provider (e.g., "openai", "anthropic")
        model: The model name (e.g., "gpt-4", "claude-3-opus")
        prompt_tokens: Number of input/prompt tokens
        completion_tokens: Number of output/completion tokens (if applicable)
        stream: Whether the call was streamed
        **kwargs: Additional provider-specific parameters
            - audio_seconds: For audio models like Whisper
            - cached: Whether the response was cached (affects cost for some providers)
            - images: Number or size of images for multimodal models
            - context_length: For providers that price differently based on context window size

    Returns:
        The calculated cost in USD or None if unable to calculate
    """
    if provider == "openai":
        from ._openai_calculate_cost import calculate_cost as openai_calculate_cost

        return openai_calculate_cost(model, prompt_tokens, completion_tokens, **kwargs)
    elif provider == "anthropic":
        from ._anthropic_calculate_cost import (
            calculate_cost as anthropic_calculate_cost,
        )

        return anthropic_calculate_cost(
            model, prompt_tokens, completion_tokens, **kwargs
        )
    elif provider == "azure":
        from ._azure_calculate_cost import calculate_cost as azure_calculate_cost

        return azure_calculate_cost(model, prompt_tokens, completion_tokens, **kwargs)
    elif provider == "bedrock":
        from ._bedrock_calculate_cost import calculate_cost as bedrock_calculate_cost

        return bedrock_calculate_cost(model, prompt_tokens, completion_tokens, **kwargs)
    elif provider == "cohere":
        from ._cohere_calculate_cost import calculate_cost as cohere_calculate_cost

        return cohere_calculate_cost(model, prompt_tokens, completion_tokens, **kwargs)
    elif provider == "gemini":
        from ._gemini_calculate_cost import calculate_cost as gemini_calculate_cost

        return gemini_calculate_cost(model, prompt_tokens, completion_tokens, **kwargs)
    elif provider == "google":
        from ._google_calculate_cost import calculate_cost as google_calculate_cost

        return google_calculate_cost(model, prompt_tokens, completion_tokens, **kwargs)
    elif provider == "groq":
        from ._groq_calculate_cost import calculate_cost as groq_calculate_cost

        return groq_calculate_cost(model, prompt_tokens, completion_tokens, **kwargs)
    elif provider == "mistral":
        from ._mistral_calculate_cost import calculate_cost as mistral_calculate_cost

        return mistral_calculate_cost(model, prompt_tokens, completion_tokens, **kwargs)
    elif provider == "vertex":
        from ._vertex_calculate_cost import calculate_cost as vertex_calculate_cost

        return vertex_calculate_cost(model, prompt_tokens, completion_tokens, **kwargs)
    elif provider == "litellm":
        from ._openai_calculate_cost import (
            calculate_cost as provider_calculate_cost,
        )

        return provider_calculate_cost(
            model.split(":")[-1] if ":" in model else model,
            prompt_tokens,
            completion_tokens,
            **kwargs,
        )

    else:
        raise ValueError(f"Unsupported provider: {provider}")
