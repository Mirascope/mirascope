from collections.abc import Callable
from typing import Any, Literal, TypeAlias, get_args, overload

from openai.lib.azure import AzureADTokenProvider

from .anthropic import (
    AnthropicClient,
    AnthropicModelId,
    clear_cache as clear_anthropic_cache,
    client as anthropic_client,
    get_client as get_anthropic_client,
)
from .anthropic_bedrock import (
    AnthropicBedrockClient,
    clear_cache as clear_anthropic_bedrock_cache,
    client as anthropic_bedrock_client,
    get_client as get_anthropic_bedrock_client,
)
from .anthropic_vertex import (
    AnthropicVertexClient,
    clear_cache as clear_anthropic_vertex_cache,
    client as anthropic_vertex_client,
    get_client as get_anthropic_vertex_client,
)
from .azure_openai.completions import (
    AzureOpenAICompletionsClient,
    clear_cache as clear_azure_openai_completions_cache,
    client as azure_openai_completions_client,
    get_client as get_azure_openai_completions_client,
)
from .azure_openai.responses import (
    AzureOpenAIResponsesClient,
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
    | GoogleModelId
    | OpenAIResponsesModelId
    | OpenAICompletionsModelId
    | str
)


PROVIDER_REGISTRY: dict[Provider, Callable[[], None]] = {
    "anthropic": clear_anthropic_cache,
    "anthropic-bedrock": clear_anthropic_bedrock_cache,
    "anthropic-vertex": clear_anthropic_vertex_cache,
    "azure-openai:completions": clear_azure_openai_completions_cache,
    "azure-openai:responses": clear_azure_openai_responses_cache,
    "google": clear_google_cache,
    "openai:completions": clear_openai_completions_cache,
    "openai:responses": clear_openai_responses_cache,
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
    match provider:
        case "anthropic":
            return get_anthropic_client()
        case "anthropic-bedrock":
            return get_anthropic_bedrock_client()
        case "anthropic-vertex":
            return get_anthropic_vertex_client()
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
    azure_api_version: str | None = None,
    azure_ad_token_provider: AzureADTokenProvider | None = None,
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
                - azure_api_version: Azure OpenAI API version
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
    match provider:
        case "anthropic":
            return anthropic_client(api_key=api_key, base_url=base_url)
        case "anthropic-bedrock":
            return anthropic_bedrock_client(
                base_url=base_url,
                aws_region=kwargs.get("aws_region"),
                aws_access_key=kwargs.get("aws_access_key"),
                aws_secret_key=kwargs.get("aws_secret_key"),
                aws_session_token=kwargs.get("aws_session_token"),
                aws_profile=kwargs.get("aws_profile"),
            )
        case "anthropic-vertex":
            return anthropic_vertex_client(
                project_id=kwargs.get("project_id"),
                region=kwargs.get("region"),
            )
        case "azure-openai:completions":
            return azure_openai_completions_client(
                api_key=api_key,
                base_url=base_url,
                azure_api_version=kwargs.get("azure_api_version"),
                azure_ad_token_provider=kwargs.get("azure_ad_token_provider"),
            )
        case "azure-openai:responses":
            return azure_openai_responses_client(
                api_key=api_key,
                base_url=base_url,
                azure_api_version=kwargs.get("azure_api_version"),
                azure_ad_token_provider=kwargs.get("azure_ad_token_provider"),
            )
        case "google":
            return google_client(api_key=api_key, base_url=base_url)
        case "openai:completions":
            return openai_completions_client(api_key=api_key, base_url=base_url)
        case "openai:responses" | "openai":
            return openai_responses_client(api_key=api_key, base_url=base_url)
        case _:  # pragma: no cover
            raise ValueError(f"Unknown provider: {provider}")
