"""Azure Anthropic Beta provider implementation."""

import os
from typing import ClassVar

from anthropic.lib.foundry import AnthropicFoundry, AsyncAnthropicFoundry

from ...anthropic.base_beta_provider import BaseAnthropicBetaProvider


class AzureAnthropicBetaProvider(BaseAnthropicBetaProvider):
    """Provider for Azure-hosted Anthropic Claude models using Beta API.

    Inherits from BaseAnthropicBetaProvider with Azure Anthropic-specific configuration:
    - Uses Azure AI Foundry API with AnthropicFoundry client
    - Provides access to Beta API features (e.g., Extended Thinking)
    - Requires AZURE_ANTHROPIC_API_KEY and AZURE_AI_ANTHROPIC_ENDPOINT

    This provider is used internally by AzureAnthropicProvider for Beta API calls.
    """

    id: ClassVar[str] = "azure:anthropic-beta"
    default_scope: ClassVar[str | list[str]] = "azure/claude-"
    default_base_url: ClassVar[str | None] = None
    api_key_env_var: ClassVar[str] = "AZURE_ANTHROPIC_API_KEY"
    api_key_required: ClassVar[bool] = True
    provider_name: ClassVar[str | None] = "Azure Anthropic Beta"

    def __init__(
        self,
        *,
        api_key: str | None = None,
        base_url: str | None = None,
    ) -> None:
        """Initialize the Azure Anthropic Beta provider.

        Args:
            api_key: API key for Azure Anthropic. Defaults to AZURE_ANTHROPIC_API_KEY env var.
            base_url: Azure Anthropic endpoint URL. Defaults to AZURE_AI_ANTHROPIC_ENDPOINT env var.
                The URL will be normalized to include trailing slash if not present.
        """
        resolved_api_key = api_key or os.environ.get(self.api_key_env_var)
        resolved_base_url = base_url or os.environ.get("AZURE_AI_ANTHROPIC_ENDPOINT")

        if not resolved_api_key:
            raise ValueError(
                "Azure Anthropic API key is required. "
                "Set the AZURE_ANTHROPIC_API_KEY environment variable "
                "or pass the api_key parameter to register_provider()."
            )

        if not resolved_base_url:
            raise ValueError(
                "Azure Anthropic endpoint is required. "
                "Set the AZURE_AI_ANTHROPIC_ENDPOINT environment variable "
                "(e.g., https://YOUR-RESOURCE.services.ai.azure.com/anthropic) "
                "or pass the base_url parameter to register_provider()."
            )

        # URL normalization: ensure exactly one trailing slash (avoid double slashes)
        resolved_base_url = resolved_base_url.rstrip("/") + "/"

        self.client = AnthropicFoundry(
            api_key=resolved_api_key,
            base_url=resolved_base_url,
        )
        self.async_client = AsyncAnthropicFoundry(
            api_key=resolved_api_key,
            base_url=resolved_base_url,
        )

    def _model_name(self, model_id: str) -> str:
        """Strip 'azure/' prefix from model ID for Azure Anthropic API."""
        return model_id.removeprefix("azure/")


class AzureRoutedAnthropicBetaProvider(AzureAnthropicBetaProvider):
    """Azure Anthropic Beta provider that reports provider_id as 'azure'.

    Used when accessed through the unified AzureProvider routing.
    """

    id: ClassVar[str] = "azure"
