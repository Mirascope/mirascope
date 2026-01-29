"""OpenRouter provider implementation."""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from ..openai.completions._utils import SKIP_MODEL_FEATURES
from ..openai.completions.base_provider import BaseOpenAICompletionsProvider
from ..openai.model_id import model_name as openai_model_name

if TYPE_CHECKING:
    from ..openai.completions._utils import SkipModelFeaturesType


class OpenRouterProvider(BaseOpenAICompletionsProvider):
    """Provider for OpenRouter's OpenAI-compatible API.

    Inherits from BaseOpenAICompletionsProvider with OpenRouter-specific configuration:
    - Uses OpenRouter's API endpoint
    - Requires OPENROUTER_API_KEY

    Usage:
        Option 1: Use "openrouter/" prefix for explicit OpenRouter models:

        ```python
        from mirascope import llm

        llm.register_provider("openrouter", scope="openrouter/")

        @llm.call("openrouter/openai/gpt-4o")
        def my_prompt():
            return [llm.messages.user("Hello!")]
        ```

        Option 2: Route existing model IDs through OpenRouter:

        ```python
        from mirascope import llm

        # Register for openai and anthropic models via OpenRouter
        llm.register_provider("openrouter", scope=["openai/", "anthropic/"])

        # Now openai/ models go through OpenRouter
        @llm.call("openai/gpt-4")
        def my_prompt():
            return [llm.messages.user("Hello!")]
        ```
    """

    id: ClassVar[str] = "openrouter"
    default_scope: ClassVar[str | list[str]] = []
    default_base_url: ClassVar[str | None] = "https://openrouter.ai/api/v1"
    api_key_env_var: ClassVar[str] = "OPENROUTER_API_KEY"
    api_key_required: ClassVar[bool] = True
    provider_name: ClassVar[str | None] = "OpenRouter"

    def _model_name(self, model_id: str) -> str:
        """Strip 'openrouter/' prefix from model ID for OpenRouter API."""
        return model_id.removeprefix("openrouter/")

    def _model_features_name(self, model_id: str) -> str | SkipModelFeaturesType:
        """Return OpenAI model name for openai/* models, SKIP_MODEL_FEATURES otherwise."""
        base_model_id = model_id.removeprefix("openrouter/")
        if base_model_id.startswith("openai/"):
            return openai_model_name(base_model_id, None)
        return SKIP_MODEL_FEATURES
