"""Anthropic registered LLM models."""

from typing import Literal, TypeAlias

AnthropicModelId: TypeAlias = (
    Literal[
        "anthropic/claude-3-7-sonnet-latest",
        "anthropic/claude-3-7-sonnet-20250219",
        "anthropic/claude-3-5-haiku-latest",
        "anthropic/claude-3-5-haiku-20241022",
        "anthropic/claude-haiku-4-5",
        "anthropic/claude-haiku-4-5-20251001",
        "anthropic/claude-sonnet-4-20250514",
        "anthropic/claude-sonnet-4-0",
        "anthropic/claude-4-sonnet-20250514",
        "anthropic/claude-sonnet-4-5",
        "anthropic/claude-sonnet-4-5-20250929",
        "anthropic/claude-opus-4-0",
        "anthropic/claude-opus-4-20250514",
        "anthropic/claude-4-opus-20250514",
        "anthropic/claude-opus-4-1-20250805",
        "anthropic/claude-3-opus-latest",
        "anthropic/claude-3-opus-20240229",
        "anthropic/claude-3-haiku-20240307",
    ]
    | str
)
"""The Anthropic model ids registered with Mirascope."""
