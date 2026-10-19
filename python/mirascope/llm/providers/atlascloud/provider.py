"""Atlas Cloud provider implementation."""

from __future__ import annotations

from typing import ClassVar

from ..openai.completions._utils import (
    CompletionsModelFeatureInfo,
    feature_info_for_openai_model,
)
from ..openai.completions.base_provider import BaseOpenAICompletionsProvider
from ..openai.model_id import model_name as openai_model_name


class AtlasCloudProvider(BaseOpenAICompletionsProvider):
    """Provider for Atlas Cloud's OpenAI-compatible API.

    Inherits from BaseOpenAICompletionsProvider with Atlas Cloud-specific configuration:
    - Uses Atlas Cloud's API endpoint
    - Requires ATLASCLOUD_API_KEY

    Usage:
        Option 1: Use "atlascloud/" prefix for explicit Atlas Cloud models:

        ```python
        from mirascope import llm

        llm.register_provider("atlascloud", scope="atlascloud/")

        @llm.call("atlascloud/deepseek-ai/deepseek-v4-flash")
        def my_prompt():
            return [llm.messages.user("Hello!")]
        ```

        Option 2: Route existing model IDs through Atlas Cloud:

        ```python
        from mirascope import llm

        # Register for openai and anthropic models via Atlas Cloud
        llm.register_provider("atlascloud", scope=["openai/", "anthropic/"])

        # Now openai/ models go through Atlas Cloud
        @llm.call("openai/gpt-4.1-mini")
        def my_prompt():
            return [llm.messages.user("Hello!")]
        ```
    """

    id: ClassVar[str] = "atlascloud"
    default_scope: ClassVar[str | list[str]] = []
    default_base_url: ClassVar[str | None] = "https://api.atlascloud.ai/v1"
    api_key_env_var: ClassVar[str] = "ATLASCLOUD_API_KEY"
    api_key_required: ClassVar[bool] = True
    provider_name: ClassVar[str | None] = "Atlas Cloud"

    def _model_name(self, model_id: str) -> str:
        """Strip 'atlascloud/' prefix from model ID for Atlas Cloud API."""
        return model_id.removeprefix("atlascloud/")

    def _model_feature_info(self, model_id: str) -> CompletionsModelFeatureInfo:
        """Return OpenAI feature info for openai/* models, empty info otherwise."""
        base_model_id = model_id.removeprefix("atlascloud/")
        if base_model_id.startswith("openai/"):
            openai_name = openai_model_name(base_model_id, None)
            return feature_info_for_openai_model(openai_name)
        return CompletionsModelFeatureInfo()
