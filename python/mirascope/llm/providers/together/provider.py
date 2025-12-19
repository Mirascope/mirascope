"""Together AI provider implementation."""

from typing import ClassVar

from ..openai.completions.base_provider import BaseOpenAICompletionsProvider


class TogetherProvider(BaseOpenAICompletionsProvider):
    """Provider for Together AI's OpenAI-compatible API.

    Inherits from BaseOpenAICompletionsProvider with Together-specific configuration:
    - Uses Together AI's API endpoint
    - Requires TOGETHER_API_KEY

    Usage:
        Register the provider with model ID prefixes you want to use:

        ```python
        import llm

        # Register for meta-llama models
        llm.register_provider("together", "meta-llama/")

        # Now you can use meta-llama models directly
        @llm.call("meta-llama/Llama-3.3-70B-Instruct-Turbo")
        def my_prompt():
            return [llm.messages.user("Hello!")]
        ```
    """

    id: ClassVar[str] = "together"
    default_scope: ClassVar[str | list[str]] = []
    default_base_url: ClassVar[str | None] = "https://api.together.xyz/v1"
    api_key_env_var: ClassVar[str] = "TOGETHER_API_KEY"
    api_key_required: ClassVar[bool] = True
    provider_name: ClassVar[str | None] = "Together"

    def _model_name(self, model_id: str) -> str:
        """Return the model ID as-is for Together API."""
        return model_id
