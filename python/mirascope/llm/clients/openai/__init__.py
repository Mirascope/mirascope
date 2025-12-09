"""OpenAI client implementation."""

from .completions import (
    OpenAICompletionsClient,
    OpenAICompletionsModelId,
    client as completions_client,
)
from .responses import (
    OpenAIResponsesClient,
    OpenAIResponsesModelId,
    client as responses_client,
)

__all__ = [
    "OpenAICompletionsClient",
    "OpenAICompletionsModelId",
    "OpenAIResponsesClient",
    "OpenAIResponsesModelId",
    "completions_client",
    "responses_client",
]
