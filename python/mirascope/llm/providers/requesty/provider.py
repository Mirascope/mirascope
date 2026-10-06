"""Requesty provider implementation."""

from __future__ import annotations

from typing import ClassVar

from ..openai.completions._utils import (
    CompletionsModelFeatureInfo,
    feature_info_for_openai_model,
)
from ..openai.completions.base_provider import BaseOpenAICompletionsProvider
from ..openai.model_id import model_name as openai_model_name


class RequestyProvider(BaseOpenAICompletionsProvider):
    """Provider for Requesty's OpenAI-compatible router API.

    Inherits from BaseOpenAICompletionsProvider with Requesty-specific configuration:
    - Uses Requesty's API endpoint
    - Requires REQUESTY_API_KEY

    Usage:
        Option 1: Use "requesty/" prefix for explicit Requesty models:

        ```python
        from mirascope import llm

        llm.register_provider("requesty", scope="requesty/")

        @llm.call("requesty/openai/gpt-4o-mini")
        def my_prompt():
            return [llm.messages.user("Hello!")]
        ```

        Option 2: Route existing model IDs through Requesty:

        ```python
        from mirascope import llm

        # Register for openai and anthropic models via Requesty
        llm.register_provider("requesty", scope=["openai/", "anthropic/"])

        # Now openai/ models go through Requesty
        @llm.call("openai/gpt-4o-mini")
        def my_prompt():
            return [llm.messages.user("Hello!")]
        ```

        For the EU region, pass `base_url="https://router.eu.requesty.ai/v1"`.
    """

    id: ClassVar[str] = "requesty"
    default_scope: ClassVar[str | list[str]] = []
    default_base_url: ClassVar[str | None] = "https://router.requesty.ai/v1"
    api_key_env_var: ClassVar[str] = "REQUESTY_API_KEY"
    api_key_required: ClassVar[bool] = True
    provider_name: ClassVar[str | None] = "Requesty"

    def _model_name(self, model_id: str) -> str:
        """Strip 'requesty/' prefix from model ID for Requesty API."""
        return model_id.removeprefix("requesty/")

    def _model_feature_info(self, model_id: str) -> CompletionsModelFeatureInfo:
        """Return OpenAI feature info for openai/* models, empty info otherwise."""
        base_model_id = model_id.removeprefix("requesty/")
        if base_model_id.startswith("openai/"):
            openai_name = openai_model_name(base_model_id, None)
            return feature_info_for_openai_model(openai_name)
        return CompletionsModelFeatureInfo()
