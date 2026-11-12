"""Runcrate provider implementation."""

from __future__ import annotations

from typing import ClassVar

from ..openai.completions._utils import CompletionsModelFeatureInfo
from ..openai.completions.base_provider import BaseOpenAICompletionsProvider


class RuncrateProvider(BaseOpenAICompletionsProvider):
    """Provider for Runcrate's OpenAI-compatible API.

    Inherits from BaseOpenAICompletionsProvider with Runcrate-specific configuration:
    - Uses Runcrate's API endpoint
    - Requires RUNCRATE_API_KEY

    Runcrate serves open models with vendor-prefixed IDs
    (e.g. "deepseek-ai/DeepSeek-V4.1-Flash", "zai-org/GLM-5.3").

    Usage:
        Use the "runcrate/" prefix for Runcrate models:

        ```python
        from mirascope import llm

        llm.register_provider("runcrate", scope="runcrate/")

        @llm.call("runcrate/deepseek-ai/DeepSeek-V4.1-Flash")
        def my_prompt():
            return [llm.messages.user("Hello!")]
        ```
    """

    id: ClassVar[str] = "runcrate"
    default_scope: ClassVar[str | list[str]] = []
    default_base_url: ClassVar[str | None] = "https://api.runcrate.ai/v1"
    api_key_env_var: ClassVar[str] = "RUNCRATE_API_KEY"
    api_key_required: ClassVar[bool] = True
    provider_name: ClassVar[str | None] = "Runcrate"

    def _model_name(self, model_id: str) -> str:
        """Strip 'runcrate/' prefix from model ID for the Runcrate API."""
        return model_id.removeprefix("runcrate/")

    def _model_feature_info(self, model_id: str) -> CompletionsModelFeatureInfo:
        """Return empty feature info: Runcrate serves open models only.

        Open-weight IDs such as "openai/gpt-oss-120b" are not OpenAI API models,
        so OpenAI's per-model feature table does not apply to them.
        """
        return CompletionsModelFeatureInfo()
