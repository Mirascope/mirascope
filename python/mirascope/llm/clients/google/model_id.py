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


def model_name(model_id: GoogleModelId) -> str:
    """Extract the google model name from a full model ID.

    Args:
        model_id: Full model ID (e.g. "google/gemini-2.5-flash")

    Returns:
        Provider-specific model ID (e.g. "gemini-2.5-flash")
    """
    return model_id.removeprefix("google/")
