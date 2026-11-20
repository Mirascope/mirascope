"""Standard Compute provider implementation."""

from __future__ import annotations

from typing import ClassVar

from ..openai.completions._utils import (
    CompletionsModelFeatureInfo,
    feature_info_for_openai_model,
)
from ..openai.completions.base_provider import BaseOpenAICompletionsProvider
from ..openai.model_id import model_name as openai_model_name


class StandardComputeProvider(BaseOpenAICompletionsProvider):
    """Provider for Standard Compute's OpenAI-compatible gateway API.

    Inherits from BaseOpenAICompletionsProvider with Standard Compute-specific configuration:
    - Uses Standard Compute's API endpoint
    - Requires STANDARDCOMPUTE_API_KEY

    Usage:
        Option 1: Use "standardcompute/" prefix for explicit Standard Compute models:

        ```python
        from mirascope import llm

        llm.register_provider("standardcompute", scope="standardcompute/")

        @llm.call("standardcompute/openai/gpt-4o-mini")
        def my_prompt():
            return [llm.messages.user("Hello!")]
        ```

        Option 2: Route existing model IDs through Standard Compute:

        ```python
        from mirascope import llm

        # Register for openai and anthropic models via Standard Compute
        llm.register_provider("standardcompute", scope=["openai/", "anthropic/"])

        # Now openai/ models go through Standard Compute
        @llm.call("openai/gpt-4o-mini")
        def my_prompt():
            return [llm.messages.user("Hello!")]
        ```

        For the US region endpoint, pass `base_url="https://us.stdcmpt.com/v1"`.
    """

    id: ClassVar[str] = "standardcompute"
    default_scope: ClassVar[str | list[str]] = []
    default_base_url: ClassVar[str | None] = "https://api.stdcmpt.com/v1"
    api_key_env_var: ClassVar[str] = "STANDARDCOMPUTE_API_KEY"
    api_key_required: ClassVar[bool] = True
    provider_name: ClassVar[str | None] = "Standard Compute"

    def _model_name(self, model_id: str) -> str:
        """Strip 'standardcompute/' prefix from model ID for Standard Compute API."""
        return model_id.removeprefix("standardcompute/")

    def _model_feature_info(self, model_id: str) -> CompletionsModelFeatureInfo:
        """Return OpenAI feature info for openai/* models, empty info otherwise."""
        base_model_id = model_id.removeprefix("standardcompute/")
        if base_model_id.startswith("openai/"):
            openai_name = openai_model_name(base_model_id, None)
            return feature_info_for_openai_model(openai_name)
        return CompletionsModelFeatureInfo()
