"""Cheaper Inference provider implementation."""

from __future__ import annotations

from typing import ClassVar

from ..openai.completions._utils import (
    CompletionsModelFeatureInfo,
    feature_info_for_openai_model,
)
from ..openai.completions.base_provider import BaseOpenAICompletionsProvider

OPENAI_MODEL_PREFIXES = ("gpt-", "o1", "o3", "o4")


class CheaperInferenceProvider(BaseOpenAICompletionsProvider):
    """Provider for Cheaper Inference's OpenAI-compatible API.

    Inherits from BaseOpenAICompletionsProvider with Cheaper Inference-specific
    configuration:
    - Uses Cheaper Inference's API endpoint
    - Requires CHEAPER_INFERENCE_API_KEY

    Cheaper Inference model IDs have no vendor prefix (e.g. "gpt-5.4-mini").

    Usage:
        Use the "cheaperinference/" prefix for Cheaper Inference models:

        ```python
        from mirascope import llm

        llm.register_provider("cheaperinference", scope="cheaperinference/")

        @llm.call("cheaperinference/gpt-5.4-mini")
        def my_prompt():
            return [llm.messages.user("Hello!")]
        ```
    """

    id: ClassVar[str] = "cheaperinference"
    default_scope: ClassVar[str | list[str]] = []
    default_base_url: ClassVar[str | None] = "https://api.cheaperinference.com/v1"
    api_key_env_var: ClassVar[str] = "CHEAPER_INFERENCE_API_KEY"
    api_key_required: ClassVar[bool] = True
    provider_name: ClassVar[str | None] = "Cheaper Inference"

    def _model_name(self, model_id: str) -> str:
        """Strip 'cheaperinference/' prefix from model ID for the Cheaper Inference API."""
        return model_id.removeprefix("cheaperinference/")

    def _model_feature_info(self, model_id: str) -> CompletionsModelFeatureInfo:
        """Return OpenAI feature info for OpenAI models, empty info otherwise."""
        base_model_id = model_id.removeprefix("cheaperinference/")
        if base_model_id.startswith(OPENAI_MODEL_PREFIXES):
            return feature_info_for_openai_model(base_model_id)
        return CompletionsModelFeatureInfo()
