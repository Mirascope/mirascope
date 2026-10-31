"""AtmoRouter provider implementation."""

from __future__ import annotations

from typing import ClassVar

from ..openai.completions.base_provider import BaseOpenAICompletionsProvider


class AtmoRouterProvider(BaseOpenAICompletionsProvider):
    """Provider for AtmoRouter's OpenAI-compatible API.

    Inherits from BaseOpenAICompletionsProvider with AtmoRouter-specific
    configuration:
    - Uses AtmoRouter's API endpoint
    - Requires ATMOROUTER_API_KEY

    AtmoRouter model IDs carry their own route prefix (e.g. "cc/claude-sonnet-4-6"),
    so only the "atmorouter/" scope is stripped before the request is sent.

    Usage:
        Use the "atmorouter/" prefix for AtmoRouter models:

        ```python
        from mirascope import llm

        llm.register_provider("atmorouter", scope="atmorouter/")

        @llm.call("atmorouter/cc/claude-sonnet-4-6")
        def my_prompt():
            return [llm.messages.user("Hello!")]
        ```
    """

    id: ClassVar[str] = "atmorouter"
    default_scope: ClassVar[str | list[str]] = []
    default_base_url: ClassVar[str | None] = "https://atmorouter.dev/v1"
    api_key_env_var: ClassVar[str] = "ATMOROUTER_API_KEY"
    api_key_required: ClassVar[bool] = True
    provider_name: ClassVar[str | None] = "AtmoRouter"

    def _model_name(self, model_id: str) -> str:
        """Strip 'atmorouter/' prefix from model ID for the AtmoRouter API."""
        return model_id.removeprefix("atmorouter/")
