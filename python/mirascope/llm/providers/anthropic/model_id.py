"""Anthropic registered LLM models."""

from typing import TypeAlias, get_args

from .model_info import AnthropicKnownModels

AnthropicModelId: TypeAlias = AnthropicKnownModels | str
"""The Anthropic model ids registered with Mirascope."""

ANTHROPIC_KNOWN_MODELS: set[str] = set(get_args(AnthropicKnownModels))


def model_name(model_id: AnthropicModelId) -> str:
    """Extract the anthropic model name from the ModelId

    Args:
        model_id: Full model ID (e.g. "anthropic/claude-sonnet-4-5" or
            "anthropic-beta/claude-sonnet-4-5")

    Returns:
        Provider-specific model ID (e.g. "claude-sonnet-4-5")
    """
    return model_id.removeprefix("anthropic-beta/").removeprefix("anthropic/")
