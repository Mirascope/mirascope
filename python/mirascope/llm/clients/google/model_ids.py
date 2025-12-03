"""Google registered LLM models."""

from typing import Literal, TypeAlias

GoogleModelId: TypeAlias = (
    Literal[
        "google/gemini-3-pro-preview",
        "google/gemini-2.5-pro",
        "google/gemini-2.5-flash",
        "google/gemini-2.5-flash-lite",
        "google/gemini-2.0-flash",
        "google/gemini-2.0-flash-lite",
    ]
    | str
)
"""The Google model ids registered with Mirascope."""
