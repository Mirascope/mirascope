from collections.abc import Callable
from typing import Any, Literal, TypeAlias, get_args, overload

from .anthropic import (
    AnthropicClient,
    AnthropicModelId,
    client as anthropic_client,
    get_client as get_anthropic_client,
)
from .azure_openai.completions import (
    AzureOpenAICompletionsClient,
    client as azure_openai_completions_client,
    get_client as get_azure_openai_completions_client,
)
from .azure_openai.responses import (
    AzureOpenAIResponsesClient,
    client as azure_openai_responses_client,
    get_client as get_azure_openai_responses_client,
)
from .google import (
    GoogleClient,
    GoogleModelId,
    client as google_client,
    get_client as get_google_client,
)
from .openai import (
    OpenAICompletionsClient,
    OpenAICompletionsModelId,
    OpenAIResponsesClient,
    OpenAIResponsesModelId,
    completions_client as openai_completions_client,
    get_completions_client as get_openai_completions_client,
    get_responses_client as get_openai_responses_client,
    responses_client as openai_responses_client,
)

Provider: TypeAlias = Literal[
    "anthropic",
    "azure-openai:completions",  # AzureOpenAICompletionsClient
    "azure-openai:responses",  # AzureOpenAIResponsesClient
    "google",
    "openai:completions",  # OpenAICompletionsClient
    "openai:responses",  # OpenAIResponsesClient
    "openai",  # Alias for "openai:responses"
]
PROVIDERS = get_args(Provider)

ModelId: TypeAlias = (
    AnthropicModelId
    | GoogleModelId
    | OpenAIResponsesModelId
    | OpenAICompletionsModelId
    | str
)


@overload
def get_client(provider: Literal["anthropic"]) -> AnthropicClient:
    """Get an Anthropic client instance."""
    ...


@overload
def get_client(
    provider: Literal["azure-openai:completions"],
) -> AzureOpenAICompletionsClient:
    """Get an Azure OpenAI completions client instance."""
    ...


@overload
def get_client(
    provider: Literal["azure-openai:responses"],
) -> AzureOpenAIResponsesClient:
    """Get an Azure OpenAI responses client instance."""
    ...


@overload
def get_client(provider: Literal["google"]) -> GoogleClient:
    """Get a Google client instance."""
    ...


@overload
def get_client(provider: Literal["openai:completions"]) -> OpenAICompletionsClient:
    """Get an OpenAI client instance."""
    ...


@overload
def get_client(
    provider: Literal["openai:responses", "openai"],
) -> OpenAIResponsesClient:
    """Get an OpenAI responses client instance."""
    ...


def get_client(
    provider: Provider,
) -> (
    AnthropicClient
    | AzureOpenAICompletionsClient
    | AzureOpenAIResponsesClient
    | GoogleClient
    | OpenAICompletionsClient
    | OpenAIResponsesClient
):
    """Get a client instance for the specified provider.

    Args:
        provider: The provider name ("openai:completions", "anthropic", or "google").

    Returns:
        A client instance for the specified provider. The specific client type
        depends on the provider:
        - "openai:completions" returns `OpenAICompletionsClient` (ChatCompletion API)
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
        case "azure-openai:completions":
            return get_azure_openai_completions_client()
        case "azure-openai:responses":
            return get_azure_openai_responses_client()
        case "google":
            return get_google_client()
        case "openai:completions":
            return get_openai_completions_client()
        case "openai:responses" | "openai":
            return get_openai_responses_client()
        case _:
            raise ValueError(f"Unknown provider: {provider}")


@overload
def client(
    provider: Literal["openai:completions"],
    *,
    api_key: str | None = None,
    base_url: str | None = None,
) -> OpenAICompletionsClient:
    """Create a cached OpenAI chat completions client with the given parameters."""
    ...


@overload
def client(
    provider: Literal["openai:responses", "openai"],
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


@overload
def client(
    provider: Literal["azure-openai:completions"],
    *,
    api_key: str | None = None,
    base_url: str | None = None,
    azure_ad_token_provider: Callable[[], str] | None = None,
    azure_ad_token_provider_async: Callable[[], Any] | None = None,
) -> AzureOpenAICompletionsClient:
    """Create a cached Azure OpenAI completions client with the given parameters."""
    ...


@overload
def client(
    provider: Literal["azure-openai:responses"],
    *,
    api_key: str | None = None,
    base_url: str | None = None,
    azure_ad_token_provider: Callable[[], str] | None = None,
    azure_ad_token_provider_async: Callable[[], Any] | None = None,
) -> AzureOpenAIResponsesClient:
    """Create a cached Azure OpenAI responses client with the given parameters."""
    ...


def client(
    provider: Provider,
    *,
    api_key: str | None = None,
    base_url: str | None = None,
    **kwargs: Any,
) -> (
    AnthropicClient
    | AzureOpenAICompletionsClient
    | AzureOpenAIResponsesClient
    | GoogleClient
    | OpenAICompletionsClient
    | OpenAIResponsesClient
):
    """Create a cached client instance for the specified provider.

    Args:
        provider: The provider name.
        api_key: API key for authentication. If None, uses provider-specific env var.
        base_url: Base URL for the API. For Azure, this is the endpoint URL.
        **kwargs: Provider-specific parameters. For Azure providers, accepts:
            - azure_ad_token_provider: Azure AD token provider for keyless authentication

    Returns:
        A cached client instance for the specified provider with the given parameters.

    Raises:
        ValueError: If the provider is not supported or required parameters are missing.
    """
    match provider:
        case "anthropic":
            return anthropic_client(api_key=api_key, base_url=base_url)
        case "azure-openai:completions":
            return azure_openai_completions_client(
                api_key=api_key,
                base_url=base_url,
                azure_ad_token_provider=kwargs.get("azure_ad_token_provider"),
                azure_ad_token_provider_async=kwargs.get(
                    "azure_ad_token_provider_async"
                ),
            )
        case "azure-openai:responses":
            return azure_openai_responses_client(
                api_key=api_key,
                base_url=base_url,
                azure_ad_token_provider=kwargs.get("azure_ad_token_provider"),
                azure_ad_token_provider_async=kwargs.get(
                    "azure_ad_token_provider_async"
                ),
            )
        case "google":
            return google_client(api_key=api_key, base_url=base_url)
        case "openai:completions":
            return openai_completions_client(api_key=api_key, base_url=base_url)
        case "openai:responses" | "openai":
            return openai_responses_client(api_key=api_key, base_url=base_url)
        case _:  # pragma: no cover
            raise ValueError(f"Unknown provider: {provider}")
