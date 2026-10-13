"""xAI registered LLM models."""

from typing import TypeAlias, get_args

from .model_info import XAIKnownModels

XAIModelId: TypeAlias = XAIKnownModels | str
"""The xAI model ids registered with Mirascope."""

XAI_KNOWN_MODELS: set[str] = set(get_args(XAIKnownModels))
