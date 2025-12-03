from typing import Literal, TypeAlias, cast, get_args

from .anthropic import (
    AnthropicModelId,
)
from .google import (
    GoogleModelId,
)
from .openai import (
    OpenAICompletionsModelId,
    OpenAIResponsesModelId,
)

Provider: TypeAlias = Literal[
    "anthropic",  # AnthropicClient
    "google",  # GoogleClient
    "openai:responses",  # OpenAIResponsesClient
    "openai",  # OpenAICompletionsClient
]
PROVIDERS = get_args(Provider)

ModelId: TypeAlias = (
    AnthropicModelId
    | GoogleModelId
    | OpenAIResponsesModelId
    | OpenAICompletionsModelId
    | str
)


def model_id_to_provider(model_id: ModelId) -> Provider:
    """Extract the provider from a model ID.

    Args:
        model_id: The model ID in format "provider/model_name".

    Returns:
        The provider extracted from the model ID.

    Raises:
        ValueError: If the model_id doesn't contain "/" or the provider is not supported.
    """
    # TODO(dandelion): Refactor this (to extract model lab?) but provider is separate from ModelId
    if "/" not in model_id:
        raise ValueError(
            f"Invalid model_id format: '{model_id}'. "
            "Expected format: 'provider/model_name'"
        )

    provider = model_id.split("/", 1)[0]

    if provider not in PROVIDERS:
        raise ValueError(
            f"Unknown provider: '{provider}'. "
            f"Supported providers are: {', '.join(PROVIDERS)}"
        )

    return cast(Provider, provider)
