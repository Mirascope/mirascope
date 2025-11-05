"""OpenAI client implementation."""

from .azure_completions import (
    AzureOpenAICompletionsClient,
    clear_cache as clear_azure_completions_cache,
    client as azure_completions_client,
    get_client as get_azure_completions_client,
)
from .azure_responses import (
    AzureOpenAIResponsesClient,
    clear_cache as clear_azure_responses_cache,
    client as azure_responses_client,
    get_client as get_azure_responses_client,
)
from .completions import (
    OpenAICompletionsClient,
    OpenAICompletionsModelId,
    clear_cache as clear_completions_cache,
    client as completions_client,
    get_client as get_completions_client,
)
from .responses import (
    OpenAIResponsesClient,
    OpenAIResponsesModelId,
    clear_cache as clear_responses_cache,
    client as responses_client,
    get_client as get_responses_client,
)

__all__ = [
    "AzureOpenAICompletionsClient",
    "AzureOpenAIResponsesClient",
    "OpenAICompletionsClient",
    "OpenAICompletionsModelId",
    "OpenAIResponsesClient",
    "OpenAIResponsesModelId",
    "azure_completions_client",
    "azure_responses_client",
    "clear_azure_completions_cache",
    "clear_azure_responses_cache",
    "clear_completions_cache",
    "clear_responses_cache",
    "completions_client",
    "get_azure_completions_client",
    "get_azure_responses_client",
    "get_completions_client",
    "get_responses_client",
    "responses_client",
]
