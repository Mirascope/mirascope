"""Azure Anthropic provider implementation."""

import os
from typing import ClassVar

from anthropic.lib.foundry import AnthropicFoundry, AsyncAnthropicFoundry

from ...anthropic.base_provider import BaseAnthropicProvider
from .beta_provider import AzureAnthropicBetaProvider


class AzureAnthropicProvider(BaseAnthropicProvider):
    """Provider for Azure-hosted Anthropic Claude models.

    Inherits from BaseAnthropicProvider with Azure Anthropic-specific configuration:
    - Uses Azure AI Foundry API with AnthropicFoundry client
    - Requires AZURE_ANTHROPIC_API_KEY and AZURE_AI_ANTHROPIC_ENDPOINT
    - Automatically normalizes endpoint URL to include trailing slash

    This provider is used internally by AzureProvider for Claude models on Azure.
    """

    id: ClassVar[str] = "azure:anthropic"
    default_scope: ClassVar[str | list[str]] = "azure/claude-"
    default_base_url: ClassVar[str | None] = None
    api_key_env_var: ClassVar[str] = "AZURE_ANTHROPIC_API_KEY"
    api_key_required: ClassVar[bool] = True
    provider_name: ClassVar[str | None] = "Azure Anthropic"

    def __init__(
        self,
        *,
        api_key: str | None = None,
        base_url: str | None = None,
    ) -> None:
        """Initialize the Azure Anthropic provider.

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
        # Pass resolved values to avoid redundant env var reads
        self._beta_provider = AzureAnthropicBetaProvider(
            api_key=resolved_api_key, base_url=resolved_base_url
        )

    def _model_name(self, model_id: str) -> str:
        """Strip 'azure/' prefix from model ID for Azure Anthropic API."""
        return model_id.removeprefix("azure/")


class AzureRoutedAnthropicProvider(AzureAnthropicProvider):
    """Azure Anthropic provider that reports provider_id as 'azure'.

    Used when accessed through the unified AzureProvider routing.
    """

    id: ClassVar[str] = "azure"
