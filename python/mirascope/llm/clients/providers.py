from collections.abc import Callable
from typing import Any, Literal, TypeAlias, TypedDict, get_args, overload

from .anthropic import (
    AnthropicClient,
    AnthropicModelId,
    clear_cache as clear_anthropic_cache,
    client as anthropic_client,
    get_client as get_anthropic_client,
)
from .anthropic_bedrock import (
    AnthropicBedrockClient,
    AnthropicBedrockModelId,
    clear_cache as clear_anthropic_bedrock_cache,
    client as anthropic_bedrock_client,
    get_client as get_anthropic_bedrock_client,
)
from .anthropic_vertex import (
    AnthropicVertexClient,
    AnthropicVertexModelId,
    clear_cache as clear_anthropic_vertex_cache,
    client as anthropic_vertex_client,
    get_client as get_anthropic_vertex_client,
)
from .azure_openai.completions import (
    AzureOpenAICompletionsClient,
    AzureOpenAICompletionsModelId,
    clear_cache as clear_azure_openai_completions_cache,
    client as azure_openai_completions_client,
    get_client as get_azure_openai_completions_client,
)
from .azure_openai.responses import (
    AzureOpenAIResponsesClient,
    AzureOpenAIResponsesModelId,
    clear_cache as clear_azure_openai_responses_cache,
    client as azure_openai_responses_client,
    get_client as get_azure_openai_responses_client,
)
from .google import (
    GoogleClient,
    GoogleModelId,
    clear_cache as clear_google_cache,
    client as google_client,
    get_client as get_google_client,
)
from .openai import (
    OpenAICompletionsClient,
    OpenAICompletionsModelId,
    OpenAIResponsesClient,
    OpenAIResponsesModelId,
    clear_completions_cache as clear_openai_completions_cache,
    clear_responses_cache as clear_openai_responses_cache,
    completions_client as openai_completions_client,
    get_completions_client as get_openai_completions_client,
    get_responses_client as get_openai_responses_client,
    responses_client as openai_responses_client,
)

Provider: TypeAlias = Literal[
    "anthropic",  # AnthropicClient
    "anthropic-bedrock",  # AnthropicBedrockClient
    "anthropic-vertex",  # AnthropicVertexClient
    "azure-openai:completions",  # AzureOpenAICompletionsClient
    "azure-openai:responses",  # AzureOpenAIResponsesClient
    "google",  # GoogleClient
    "openai:completions",  # OpenAICompletionsClient
    "openai:responses",  # OpenAIResponsesClient
    "openai",  # Alias for "openai:responses"
]
PROVIDERS = get_args(Provider)

ModelId: TypeAlias = (
    AnthropicModelId
    | AnthropicBedrockModelId
    | AnthropicVertexModelId
    | AzureOpenAICompletionsModelId
    | AzureOpenAIResponsesModelId
    | GoogleModelId
    | OpenAIResponsesModelId
    | OpenAICompletionsModelId
    | str
)


class ProviderInfo(TypedDict):
    """Information about a provider implementation."""

    name: Provider
    """The provider identifier (e.g., "anthropic", "openai:completions")."""

    clear_cache: Callable[[], None]
    """Function to clear the provider's client cache."""

    get_client: Callable[[], Any]
    """Function to get the default provider client instance."""

    client: Callable[..., Any]
    """Function to create a cached client instance with custom parameters."""


PROVIDER_INFO: dict[Provider, ProviderInfo] = {
    "anthropic": {
        "name": "anthropic",
        "clear_cache": clear_anthropic_cache,
        "get_client": get_anthropic_client,
        "client": anthropic_client,
    },
    "anthropic-bedrock": {
        "name": "anthropic",
        "clear_cache": clear_anthropic_bedrock_cache,
        "get_client": get_anthropic_bedrock_client,
        "client": anthropic_bedrock_client,
    },
    "anthropic-vertex": {
        "name": "anthropic-vertex",
        "clear_cache": clear_anthropic_vertex_cache,
        "get_client": get_anthropic_vertex_client,
        "client": anthropic_vertex_client,
    },
    "azure-openai:completions": {
        "name": "azure-openai:completions",
        "clear_cache": clear_azure_openai_completions_cache,
        "get_client": get_azure_openai_completions_client,
        "client": azure_openai_completions_client,
    },
    "azure-openai:responses": {
        "name": "azure-openai:responses",
        "clear_cache": clear_azure_openai_responses_cache,
        "get_client": get_azure_openai_responses_client,
        "client": azure_openai_responses_client,
    },
    "google": {
        "name": "google",
        "clear_cache": clear_google_cache,
        "get_client": get_google_client,
        "client": google_client,
    },
    "openai:completions": {
        "name": "openai:completions",
        "clear_cache": clear_openai_completions_cache,
        "get_client": get_openai_completions_client,
        "client": openai_completions_client,
    },
    "openai:responses": {
        "name": "openai:responses",
        "clear_cache": clear_openai_responses_cache,
        "get_client": get_openai_responses_client,
        "client": openai_responses_client,
    },
}


@overload
def get_client(provider: Literal["anthropic"]) -> AnthropicClient:
    """Get an Anthropic client instance."""
    ...


@overload
def get_client(provider: Literal["anthropic-bedrock"]) -> AnthropicBedrockClient:
    """Get an Anthropic Bedrock client instance."""
    ...


@overload
def get_client(provider: Literal["anthropic-vertex"]) -> AnthropicVertexClient:
    """Get an Anthropic Vertex AI client instance."""
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
    | AnthropicBedrockClient
    | AnthropicVertexClient
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
        - "anthropic-bedrock" returns `AnthropicBedrockClient`
        - "anthropic-vertex" returns `AnthropicVertexClient`
        - "azure-openai:completions" returns `AzureOpenAICompletionsClient`
        - "azure-openai:responses" returns `AzureOpenAIResponsesClient`
        - "google" returns `GoogleClient`

    Multiple calls to get_client will return the same Client rather than constructing
    new ones.

    Raises:
        ValueError: If the provider is not supported.
    """
    normalized_provider: Provider = (
        "openai:responses" if provider == "openai" else provider
    )

    if normalized_provider in PROVIDER_INFO:
        return PROVIDER_INFO[normalized_provider]["get_client"]()

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
    provider: Literal["anthropic-bedrock"],
    *,
    base_url: str | None = None,
    aws_region: str | None = None,
    aws_access_key: str | None = None,
    aws_secret_key: str | None = None,
    aws_session_token: str | None = None,
    aws_profile: str | None = None,
) -> AnthropicBedrockClient:
    """Create a cached Anthropic Bedrock client with the given parameters."""
    ...


@overload
def client(
    provider: Literal["anthropic-vertex"],
    *,
    project_id: str | None = None,
    region: str | None = None,
) -> AnthropicVertexClient:
    """Create a cached Anthropic Vertex AI client with the given parameters."""
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
    azure_api_version: str | None = None,
    azure_ad_token_provider: AzureADTokenProvider | None = None,
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
    | AnthropicBedrockClient
    | AnthropicVertexClient
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
            For Bedrock, this overrides the default Bedrock endpoint.
        **kwargs: Provider-specific parameters:
            - For Azure providers:
                - azure_ad_token_provider: Azure AD token provider
            - For Bedrock provider:
                - aws_region: AWS region
                - aws_access_key: AWS access key
                - aws_secret_key: AWS secret key
                - aws_session_token: AWS session token
                - aws_profile: AWS profile name
            - For Vertex AI provider:
                - project_id: GCP project ID
                - region: GCP region

    Returns:
        A cached client instance for the specified provider with the given parameters.

    Raises:
        ValueError: If the provider is not supported or required parameters are missing.
    """
    normalized_provider: Provider = (
        "openai:responses" if provider == "openai" else provider
    )

    if normalized_provider not in PROVIDER_INFO:
        raise ValueError(f"Unknown provider: {provider}")  # pragma: no cover

    client_factory = PROVIDER_INFO[normalized_provider]["client"]
    if normalized_provider.startswith("azure-openai:"):
        return client_factory(
            api_key=api_key,
            base_url=base_url,
            azure_ad_token_provider=kwargs.get("azure_ad_token_provider"),
            azure_ad_token_provider_async=kwargs.get("azure_ad_token_provider_async"),
        )
    elif normalized_provider == "anthropic-bedrock":
        return anthropic_bedrock_client(
            base_url=base_url,
            aws_region=kwargs.get("aws_region"),
            aws_access_key=kwargs.get("aws_access_key"),
            aws_secret_key=kwargs.get("aws_secret_key"),
            aws_session_token=kwargs.get("aws_session_token"),
            aws_profile=kwargs.get("aws_profile"),
        )
    elif normalized_provider == "anthropic-vertex":
        return anthropic_vertex_client(
            project_id=kwargs.get("project_id"),
            region=kwargs.get("region"),
        )
    return client_factory(api_key=api_key, base_url=base_url)
