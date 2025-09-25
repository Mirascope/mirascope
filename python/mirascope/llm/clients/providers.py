from typing import Literal, TypeAlias, get_args, overload

from .anthropic import (
    AnthropicClient,
    AnthropicModelId,
    client as anthropic_client,
    get_client as get_anthropic_client,
)
from .google import (
    GoogleClient,
    GoogleModelId,
    client as google_client,
    get_client as get_google_client,
)
from .openai import (
    OpenAIClient,
    OpenAIModelId,
    client as openai_client,
    get_client as get_openai_client,
)

Provider: TypeAlias = Literal["openai", "anthropic", "google"]
PROVIDERS = get_args(Provider)

ModelId: TypeAlias = OpenAIModelId | AnthropicModelId | GoogleModelId | str


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


@overload
def client(
    provider: Literal["openai"],
    *,
    api_key: str | None = None,
    base_url: str | None = None,
) -> OpenAIClient:
    """Create a cached OpenAI client with the given parameters."""
    ...


@overload
def client(
    provider: Literal["anthropic"],
    *,
    api_key: str | None = None,
    base_url: str | None = None,
) -> AnthropicClient:
    """Create a cached Anthropic client with the given parameters."""
    ...


@overload
def client(
    provider: Literal["google"],
    *,
    api_key: str | None = None,
    base_url: str | None = None,
) -> GoogleClient:
    """Create a cached Google client with the given parameters."""
    ...


def client(
    provider: Provider, *, api_key: str | None = None, base_url: str | None = None
) -> AnthropicClient | GoogleClient | OpenAIClient:
    """Create a cached client instance for the specified provider.

    Args:
        provider: The provider name ("openai", "anthropic", or "google").
        api_key: API key for authentication. If None, uses provider-specific env var.
        base_url: Base URL for the API. If None, uses provider-specific env var.

    Returns:
        A cached client instance for the specified provider with the given parameters.

    Raises:
        ValueError: If the provider is not supported.
    """
    match provider:
        case "openai":
            return openai_client(api_key=api_key, base_url=base_url)
        case "anthropic":
            return anthropic_client(api_key=api_key, base_url=base_url)
        case "google":
            return google_client(api_key=api_key, base_url=base_url)
        case _:  # pragma: no cover
            raise ValueError(f"Unknown provider: {provider}")
