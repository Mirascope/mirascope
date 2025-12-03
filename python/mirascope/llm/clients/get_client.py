from typing import Literal, overload

from .anthropic import (
    AnthropicClient,
    client as anthropic_client,
    get_client as get_anthropic_client,
)
from .google import (
    GoogleClient,
    client as google_client,
    get_client as get_google_client,
)
from .openai import (
    OpenAICompletionsClient,
    OpenAIResponsesClient,
    completions_client as openai_completions_client,
    get_completions_client as get_openai_completions_client,
    get_responses_client as get_openai_responses_client,
    responses_client as openai_responses_client,
)
from .providers import Provider


@overload
def get_client(provider: Literal["anthropic"]) -> AnthropicClient:
    """Get an Anthropic client instance."""
    ...


@overload
def get_client(provider: Literal["google"]) -> GoogleClient:
    """Get a Google client instance."""
    ...


@overload
def get_client(provider: Literal["openai"]) -> OpenAICompletionsClient:
    """Get an OpenAI client instance."""
    ...


@overload
def get_client(
    provider: Literal["openai:responses"],
) -> OpenAIResponsesClient:
    """Get an OpenAI responses client instance."""
    ...


def get_client(
    provider: Provider,
) -> AnthropicClient | GoogleClient | OpenAICompletionsClient | OpenAIResponsesClient:
    """Get a client instance for the specified provider.

    Args:
        provider: The provider name ("openai", "anthropic", or "google").

    Returns:
        A client instance for the specified provider. The specific client type
        depends on the provider:
        - "openai" returns `OpenAICompletionsClient` (ChatCompletion API)
        - "openai:responses" returns `OpenAIResponsesClient` (Responses API)
        - "anthropic" returns `AnthropicClient`
        - "google" returns `GoogleClient`

    Multiple calls to get_client will return the same Client rather than constructing
    new ones.

    Raises:
        ValueError: If the provider is not supported.
    """
    match provider:
        case "anthropic":
            return get_anthropic_client()
        case "google":
            return get_google_client()
        case "openai":
            return get_openai_completions_client()
        case "openai:responses":
            return get_openai_responses_client()
        case _:
            raise ValueError(f"Unknown provider: {provider}")


@overload
def client(
    provider: Literal["openai"],
    *,
    api_key: str | None = None,
    base_url: str | None = None,
) -> OpenAICompletionsClient:
    """Create a cached OpenAI chat completions client with the given parameters."""
    ...


@overload
def client(
    provider: Literal["openai:responses"],
    *,
    api_key: str | None = None,
    base_url: str | None = None,
) -> OpenAIResponsesClient:
    """Create a cached OpenAI responses client with the given parameters."""
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
) -> AnthropicClient | GoogleClient | OpenAICompletionsClient | OpenAIResponsesClient:
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
        case "anthropic":
            return anthropic_client(api_key=api_key, base_url=base_url)
        case "google":
            return google_client(api_key=api_key, base_url=base_url)
        case "openai":
            return openai_completions_client(api_key=api_key, base_url=base_url)
        case "openai:responses":
            return openai_responses_client(api_key=api_key, base_url=base_url)
        case _:  # pragma: no cover
            raise ValueError(f"Unknown provider: {provider}")
