"""Azure OpenAI Completions API client."""

from .clients import (
    AzureOpenAICompletionsClient,
    client,
    get_client,
)

__all__ = [
    "AzureOpenAICompletionsClient",
    "client",
    "get_client",
]
