"""xAI model information.

Static list of the Grok models xAI exposes through their Responses API,
sourced from https://docs.x.ai/docs/models. Update by hand when xAI publishes
new model IDs."""

from typing import Literal

XAIKnownModels = Literal[
    "xai/grok-2-1212",
    "xai/grok-2-latest",
    "xai/grok-2-vision-1212",
    "xai/grok-2-vision-latest",
    "xai/grok-3",
    "xai/grok-3-fast",
    "xai/grok-3-mini",
    "xai/grok-3-mini-fast",
    "xai/grok-4",
    "xai/grok-4-fast-non-reasoning",
    "xai/grok-4-fast-reasoning",
    "xai/grok-4-latest",
    "xai/grok-beta",
    "xai/grok-code-fast-1",
    "xai/grok-vision-beta",
]
