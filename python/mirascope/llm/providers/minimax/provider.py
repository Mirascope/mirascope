"""MiniMax provider implementation."""

from typing import ClassVar

from ..openai.completions.base_provider import BaseOpenAICompletionsProvider
from .model_id import model_name


class MiniMaxProvider(BaseOpenAICompletionsProvider):
    """Provider for MiniMax's OpenAI-compatible API.

    Inherits from BaseOpenAICompletionsProvider with MiniMax-specific configuration:
    - Uses MiniMax's API endpoint (https://api.minimax.io/v1)
    - Requires MINIMAX_API_KEY

    Available models:
    - MiniMax-M3 (default, flagship): 512K context window
    - MiniMax-M2.7: 192K context window
    - MiniMax-M2.7-highspeed: high-throughput variant

    Usage:
        ```python
        from mirascope import llm

        @llm.call("minimax/MiniMax-M3")
        def my_prompt():
            return [llm.messages.user("Hello!")]
        ```
    """

    id: ClassVar[str] = "minimax"
    default_scope: ClassVar[str | list[str]] = "minimax/"
    default_base_url: ClassVar[str | None] = "https://api.minimax.io/v1"
    api_key_env_var: ClassVar[str] = "MINIMAX_API_KEY"
    api_key_required: ClassVar[bool] = True
    provider_name: ClassVar[str | None] = "MiniMax"

    def _model_name(self, model_id: str) -> str:
        """Strip 'minimax/' prefix from model ID for MiniMax API."""
        return model_name(model_id)
