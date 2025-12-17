"""Ollama provider implementation."""

import os
from typing import ClassVar

from openai import AsyncOpenAI, OpenAI

from ..openai.completions.base_provider import BaseOpenAICompletionsProvider


class OllamaProvider(BaseOpenAICompletionsProvider):
    """Provider for Ollama's OpenAI-compatible API.

    Inherits from BaseOpenAICompletionsProvider with Ollama-specific configuration:
    - Uses Ollama's local API endpoint (default: http://localhost:11434/v1/)
    - API key is not required (Ollama ignores API keys)
    - Supports OLLAMA_BASE_URL environment variable

    Usage:
        Register the provider with model ID prefixes you want to use:

        ```python
        import llm

        # Register for ollama models
        llm.register_provider("ollama", "ollama/")

        # Now you can use ollama models directly
        @llm.call("ollama/llama2")
        def my_prompt():
            return [llm.messages.user("Hello!")]
        ```
    """

    id: ClassVar[str] = "ollama"
    default_scope: ClassVar[str | list[str]] = "ollama/"
    default_base_url: ClassVar[str | None] = "http://localhost:11434/v1/"
    api_key_env_var: ClassVar[str] = "OLLAMA_API_KEY"
    api_key_required: ClassVar[bool] = False
    provider_name: ClassVar[str | None] = "Ollama"

    def __init__(
        self,
        *,
        api_key: str | None = None,
        base_url: str | None = None,
    ) -> None:
        """Initialize the Ollama provider.

        Args:
            api_key: API key (optional). Defaults to OLLAMA_API_KEY env var or 'ollama'.
            base_url: Custom base URL. Defaults to OLLAMA_BASE_URL env var
                or http://localhost:11434/v1/.
        """
        resolved_api_key = api_key or os.environ.get(self.api_key_env_var) or "ollama"
        resolved_base_url = (
            base_url or os.environ.get("OLLAMA_BASE_URL") or self.default_base_url
        )

        self.client = OpenAI(
            api_key=resolved_api_key,
            base_url=resolved_base_url,
        )
        self.async_client = AsyncOpenAI(
            api_key=resolved_api_key,
            base_url=resolved_base_url,
        )

    def _model_name(self, model_id: str) -> str:
        """Strip 'ollama/' prefix from model ID for Ollama API."""
        return model_id.removeprefix("ollama/")
