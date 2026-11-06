"""Opper provider implementation."""

from __future__ import annotations

from typing import ClassVar

from ..openai.completions._utils import (
    CompletionsModelFeatureInfo,
    feature_info_for_openai_model,
)
from ..openai.completions.base_provider import BaseOpenAICompletionsProvider
from ..openai.model_id import model_name as openai_model_name

OPENAI_MODEL_PREFIXES = ("gpt-", "o1", "o3", "o4")


class OpperProvider(BaseOpenAICompletionsProvider):
    """Provider for Opper's OpenAI-compatible gateway API.

    Inherits from BaseOpenAICompletionsProvider with Opper-specific configuration:
    - Uses Opper's API endpoint
    - Requires OPPER_API_KEY

    Opper model IDs are either bare pool names such as "claude-sonnet-4-6", which
    let Opper pick the route, or "provider/model" IDs such as
    "anthropic/claude-sonnet-4-6", which pin one route.

    Usage:
        Option 1: Use "opper/" prefix for explicit Opper models:

        ```python
        from mirascope import llm

        llm.register_provider("opper", scope="opper/")

        @llm.call("opper/claude-sonnet-4-6")
        def my_prompt():
            return [llm.messages.user("Hello!")]
        ```

        Option 2: Route existing model IDs through Opper:

        ```python
        from mirascope import llm

        # Register for openai and anthropic models via Opper
        llm.register_provider("opper", scope=["openai/", "anthropic/"])

        # Now openai/ models go through Opper
        @llm.call("openai/gpt-5.4-mini")
        def my_prompt():
            return [llm.messages.user("Hello!")]
        ```
    """

    id: ClassVar[str] = "opper"
    default_scope: ClassVar[str | list[str]] = []
    default_base_url: ClassVar[str | None] = "https://api.opper.ai/v3/compat"
    api_key_env_var: ClassVar[str] = "OPPER_API_KEY"
    api_key_required: ClassVar[bool] = True
    provider_name: ClassVar[str | None] = "Opper"

    def _model_name(self, model_id: str) -> str:
        """Strip 'opper/' prefix from model ID for Opper API."""
        return model_id.removeprefix("opper/")

    def _model_feature_info(self, model_id: str) -> CompletionsModelFeatureInfo:
        """Return OpenAI feature info for OpenAI models, empty info otherwise."""
        base_model_id = model_id.removeprefix("opper/")
        if base_model_id.startswith("openai/"):
            openai_name = openai_model_name(base_model_id, None)
            return feature_info_for_openai_model(openai_name)
        if base_model_id.startswith(OPENAI_MODEL_PREFIXES):
            return feature_info_for_openai_model(base_model_id)
        return CompletionsModelFeatureInfo()
