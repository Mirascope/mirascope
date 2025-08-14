from typing import Literal, TypeAlias, overload

from .anthropic import (
    AnthropicClient,
    AnthropicModel,
    get_anthropic_client,
)
from .google import GoogleClient, GoogleModel, get_google_client
from .openai import OpenAIClient, OpenAIModel, get_openai_client

Provider: TypeAlias = Literal["openai", "anthropic", "google"]
Model: TypeAlias = OpenAIModel | AnthropicModel | GoogleModel | str


@overload
def get_client(provider: Literal["anthropic"]) -> AnthropicClient:
    """Get an Anthropic client instance."""
    ...


@overload
def get_client(provider: Literal["google"]) -> GoogleClient:
    """Get a Google client instance."""
    ...


@overload
def get_client(provider: Literal["openai"]) -> OpenAIClient:
    """Get an OpenAI client instance."""
    ...


def get_client(provider: Provider) -> AnthropicClient | GoogleClient | OpenAIClient:
    """Get a client instance for the specified provider.

    Args:
        provider: The provider name ("openai", "anthropic", or "google").

    Returns:
        A client instance for the specified provider. The specific client type
        depends on the provider:
        - "openai" returns OpenAIClient
        - "anthropic" returns AnthropicClient
        - "google" returns GoogleClient

    Multiple calls to get_client will return the same Client rather than constructing
    new ones.

    Raises:
        ValueError: If the provider is not supported.
    """
    match provider:
        case "openai":
            return get_openai_client()
        case "anthropic":
            return get_anthropic_client()
        case "google":
            return get_google_client()
        case _:
            raise ValueError(f"Unknown provider: {provider}")
