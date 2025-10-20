"""Azure OpenAI Responses API client."""

from .clients import (
    AzureOpenAIResponsesClient,
    client,
    get_client,
)

__all__ = [
    "AzureOpenAIResponsesClient",
    "client",
    "get_client",
]
