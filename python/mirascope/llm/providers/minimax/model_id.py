"""MiniMax registered LLM models."""

from typing import TypeAlias, get_args

from .model_info import MiniMaxKnownModels

MiniMaxModelId: TypeAlias = MiniMaxKnownModels | str
"""The MiniMax model ids registered with Mirascope."""

MINIMAX_KNOWN_MODELS: set[str] = set(get_args(MiniMaxKnownModels))


def model_name(model_id: MiniMaxModelId) -> str:
    """Extract the MiniMax model name from the ModelId.

    Args:
        model_id: Full model ID (e.g. ``"minimax/MiniMax-M3"``).

    Returns:
        Provider-specific model name (e.g. ``"MiniMax-M3"``).
    """
    return model_id.removeprefix("minimax/")
