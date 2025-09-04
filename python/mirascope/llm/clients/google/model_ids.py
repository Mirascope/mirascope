"""Google registered LLM models."""

from typing import Literal, TypeAlias

GoogleModelId: TypeAlias = (
    Literal[
        "gemini-2.5-pro",
        "gemini-2.5-flash",
        "gemini-2.5-flash-lite",
        "gemini-2.0-flash",
        "gemini-2.0-flash-lite",
    ]
    | str
)
"""The Google model ids registered with Mirascope."""
