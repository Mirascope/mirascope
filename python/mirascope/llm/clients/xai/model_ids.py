"""Grok registered LLM models."""

from typing import Literal, TypeAlias

GrokModelId: TypeAlias = (
    Literal[
        "grok-4",
        "grok-4-fast",
        "grok-3",
        "grok-3-mini",
        "grok-code-fast-1",
        "grok-2-vision",
        "grok-2-latest",
        "grok-2",
        "grok-2-image-1212",
    ]
    | str
)
"""The Grok model ids registered with Mirascope."""
