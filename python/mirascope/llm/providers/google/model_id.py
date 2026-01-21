"""Google registered LLM models."""

from typing import TypeAlias, get_args

from .model_info import GoogleKnownModels

GoogleModelId: TypeAlias = GoogleKnownModels | str
"""The Google model ids registered with Mirascope."""

GOOGLE_KNOWN_MODELS: set[str] = set(get_args(GoogleKnownModels))


def model_name(model_id: GoogleModelId) -> str:
    """Extract the google model name from a full model ID.

    Args:
        model_id: Full model ID (e.g. "google/gemini-2.5-flash")

    Returns:
        Provider-specific model ID (e.g. "gemini-2.5-flash")
    """
    return model_id.removeprefix("google/")
