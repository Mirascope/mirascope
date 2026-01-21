"""OpenAI model ids, and related utilities."""

from typing import Literal, TypeAlias, get_args

from .model_info import OpenAIKnownModels

OpenAIModelId = OpenAIKnownModels | str
"""Valid OpenAI model IDs including API-specific variants."""

OPENAI_KNOWN_MODELS: set[str] = set(get_args(OpenAIKnownModels))

ApiMode: TypeAlias = Literal["responses", "completions"]


def model_name(model_id: OpenAIModelId, api_mode: ApiMode | None) -> str:
    """Extract the openai model name from the ModelId

    Args:
        model_id: Full model ID (e.g. "openai/gpt-4o")
        api_mode: API mode to append as suffix ("responses" or "completions").
          If None, no suffix will be added (just the base model name).

    Returns:
        Provider-specific model ID with API suffix (e.g. "gpt-4o:responses")
    """
    base_name = (
        model_id.split("/")[1].removesuffix(":responses").removesuffix(":completions")
    )
    if api_mode is None:
        return base_name
    return f"{base_name}:{api_mode}"
