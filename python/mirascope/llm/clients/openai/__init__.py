"""OpenAI client implementation."""

from .completions import (
    OpenAICompletionsClient,
    OpenAICompletionsModelId,
    client as completions_client,
    get_client as get_completions_client,
)
from .responses import (
    OpenAIResponsesClient,
    OpenAIResponsesModelId,
    client as responses_client,
    get_client as get_responses_client,
)

__all__ = [
    "OpenAICompletionsClient",
    "OpenAICompletionsModelId",
    "OpenAIResponsesClient",
    "OpenAIResponsesModelId",
    "completions_client",
    "get_completions_client",
    "get_responses_client",
    "responses_client",
]
