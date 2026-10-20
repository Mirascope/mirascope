"""API Route provider implementation."""

from __future__ import annotations

from typing import ClassVar

from ..openai.completions._utils import (
    CompletionsModelFeatureInfo,
    feature_info_for_openai_model,
)
from ..openai.completions.base_provider import BaseOpenAICompletionsProvider

OPENAI_MODEL_PREFIXES = ("gpt-", "o1", "o3", "o4")


class APIRouteProvider(BaseOpenAICompletionsProvider):
    """Provider for API Route's OpenAI-compatible Chat Completions API.

    Uses API_ROUTE_API_KEY and https://global.api-route.com/v1 by default.
    Both can be overridden with the api_key and base_url parameters.

    Prefix an exact API Route model ID with "api-route/" to select this provider.
    Only this routing prefix is removed before sending the model ID to the API.

    Example:
        ```python
        from mirascope import llm

        @llm.call("api-route/claude-sonnet-4-6")
        def greet():
            return "Hello!"
        ```

        To customize the endpoint, register with an explicit scope:

        ```python
        llm.register_provider(
            "api-route",
            scope="api-route/",
            base_url="https://global.api-route.com/v1",
        )
        ```
    """

    id: ClassVar[str] = "api-route"
    default_scope: ClassVar[str | list[str]] = []
    default_base_url: ClassVar[str | None] = "https://global.api-route.com/v1"
    api_key_env_var: ClassVar[str] = "API_ROUTE_API_KEY"
    api_key_required: ClassVar[bool] = True
    provider_name: ClassVar[str | None] = "API Route"

    def _model_name(self, model_id: str) -> str:
        """Strip only the Mirascope routing prefix from the API Route model ID."""
        return model_id.removeprefix("api-route/")

    def _model_feature_info(self, model_id: str) -> CompletionsModelFeatureInfo:
        """Use OpenAI feature information for unprefixed OpenAI model names."""
        model_name = self._model_name(model_id)
        if model_name.startswith(OPENAI_MODEL_PREFIXES):
            return feature_info_for_openai_model(model_name)
        return CompletionsModelFeatureInfo()
