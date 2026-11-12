"""Groq provider implementation."""

from typing import ClassVar

from ..openai.completions.base_provider import BaseOpenAICompletionsProvider


class GroqProvider(BaseOpenAICompletionsProvider):
    """Provider for Groq's OpenAI-compatible API.

    Inherits from BaseOpenAICompletionsProvider with Groq-specific configuration:
    - Uses Groq's API endpoint (https://api.groq.com/openai/v1)
    - Requires GROQ_API_KEY

    Groq model names are sent as-is after the "groq/" prefix, including models
    that carry their own vendor prefix (e.g. "groq/openai/gpt-oss-120b" is sent
    as "openai/gpt-oss-120b"). Because those are open-weight models served by
    Groq rather than OpenAI API models, no OpenAI feature info is applied.

    Usage:
        ```python
        from mirascope import llm

        @llm.call("groq/llama-3.3-70b-versatile")
        def my_prompt():
            return [llm.messages.user("Hello!")]
        ```
    """

    id: ClassVar[str] = "groq"
    default_scope: ClassVar[str | list[str]] = "groq/"
    default_base_url: ClassVar[str | None] = "https://api.groq.com/openai/v1"
    api_key_env_var: ClassVar[str] = "GROQ_API_KEY"
    api_key_required: ClassVar[bool] = True
    provider_name: ClassVar[str | None] = "Groq"

    def _model_name(self, model_id: str) -> str:
        """Strip 'groq/' prefix from model ID for the Groq API."""
        return model_id.removeprefix("groq/")
