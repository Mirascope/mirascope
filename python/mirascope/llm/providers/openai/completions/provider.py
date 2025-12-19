"""OpenAI Completions API provider implementation."""

from ..model_id import model_name
from .base_provider import BaseOpenAICompletionsProvider


class OpenAICompletionsProvider(BaseOpenAICompletionsProvider):
    """Provider for OpenAI's ChatCompletions API."""

    id = "openai:completions"
    default_scope = "openai/"
    default_base_url = None
    api_key_env_var = "OPENAI_API_KEY"
    api_key_required = False
    provider_name = "OpenAI"

    def _provider_model_name(self, model_id: str) -> str:
        """Get the model name for tracking in Response.

        Returns the model name with :completions suffix for tracking which API was used.
        """
        return model_name(model_id, "completions")
