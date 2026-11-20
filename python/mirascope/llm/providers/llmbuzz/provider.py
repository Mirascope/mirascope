"""llm.buzz provider implementation."""

from __future__ import annotations

from typing import ClassVar

from ..openai.completions._utils import (
    CompletionsModelFeatureInfo,
    feature_info_for_openai_model,
)
from ..openai.completions.base_provider import BaseOpenAICompletionsProvider
from ..openai.model_id import model_name as openai_model_name


class LLMBuzzProvider(BaseOpenAICompletionsProvider):
    """Provider for llm.buzz's OpenAI-compatible API.

    Inherits from BaseOpenAICompletionsProvider with llm.buzz-specific configuration:
    - Uses llm.buzz's API endpoint
    - Requires LLM_BUZZ_API_KEY

    llm.buzz model IDs carry a vendor prefix (e.g. "openai/gpt-5.4-mini").

    Usage:
        Option 1: Use "llmbuzz/" prefix for explicit llm.buzz models:

        ```python
        from mirascope import llm

        llm.register_provider("llmbuzz", scope="llmbuzz/")

        @llm.call("llmbuzz/openai/gpt-5.4-mini")
        def my_prompt():
            return [llm.messages.user("Hello!")]
        ```

        Option 2: Route existing model IDs through llm.buzz:

        ```python
        from mirascope import llm

        # Register for openai and anthropic models via llm.buzz
        llm.register_provider("llmbuzz", scope=["openai/", "anthropic/"])

        # Now openai/ models go through llm.buzz
        @llm.call("openai/gpt-4.1-mini")
        def my_prompt():
            return [llm.messages.user("Hello!")]
        ```
    """

    id: ClassVar[str] = "llmbuzz"
    default_scope: ClassVar[str | list[str]] = []
    default_base_url: ClassVar[str | None] = "https://api.llm.buzz/api/v1"
    api_key_env_var: ClassVar[str] = "LLM_BUZZ_API_KEY"
    api_key_required: ClassVar[bool] = True
    provider_name: ClassVar[str | None] = "llm.buzz"

    def _model_name(self, model_id: str) -> str:
        """Strip 'llmbuzz/' prefix from model ID for llm.buzz API."""
        return model_id.removeprefix("llmbuzz/")

    def _model_feature_info(self, model_id: str) -> CompletionsModelFeatureInfo:
        """Return OpenAI feature info for openai/* models, empty info otherwise."""
        base_model_id = model_id.removeprefix("llmbuzz/")
        if base_model_id.startswith("openai/"):
            openai_name = openai_model_name(base_model_id, None)
            return feature_info_for_openai_model(openai_name)
        return CompletionsModelFeatureInfo()
