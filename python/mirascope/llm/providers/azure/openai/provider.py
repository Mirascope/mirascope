"""Azure OpenAI provider implementation."""

import os
from typing import ClassVar

from openai import AsyncOpenAI, OpenAI

from ...openai.completions.base_provider import BaseOpenAICompletionsProvider


class AzureOpenAIProvider(BaseOpenAICompletionsProvider):
    """Provider for Azure OpenAI's OpenAI-compatible API.

    Inherits from BaseOpenAICompletionsProvider with Azure OpenAI-specific configuration:
    - Uses Azure AI API v1 with standard OpenAI client
    - Requires AZURE_OPENAI_API_KEY and AZURE_OPENAI_ENDPOINT
    - Automatically normalizes endpoint URL to include /openai/v1/ suffix

    This provider is used internally by AzureProvider for OpenAI models on Azure.
    """

    id: ClassVar[str] = "azure:openai"
    default_scope: ClassVar[str | list[str]] = "azure/"
    default_base_url: ClassVar[str | None] = None
    api_key_env_var: ClassVar[str] = "AZURE_OPENAI_API_KEY"
    api_key_required: ClassVar[bool] = True
    provider_name: ClassVar[str | None] = "Azure OpenAI"

    def __init__(
        self,
        *,
        api_key: str | None = None,
        base_url: str | None = None,
    ) -> None:
        """Initialize the Azure OpenAI provider.

        Args:
            api_key: API key for Azure OpenAI. Defaults to AZURE_OPENAI_API_KEY env var.
            base_url: Azure OpenAI endpoint URL. Defaults to AZURE_OPENAI_ENDPOINT env var.
                The URL will be normalized to include /openai/v1/ suffix if not present.
        """
        resolved_api_key = api_key or os.environ.get(self.api_key_env_var)
        resolved_base_url = base_url or os.environ.get("AZURE_OPENAI_ENDPOINT")

        if not resolved_api_key:
            raise ValueError(
                "Azure OpenAI API key is required. "
                "Set the AZURE_OPENAI_API_KEY environment variable "
                "or pass the api_key parameter to register_provider()."
            )

        if not resolved_base_url:
            raise ValueError(
                "Azure OpenAI endpoint is required. "
                "Set the AZURE_OPENAI_ENDPOINT environment variable "
                "(e.g., https://YOUR-RESOURCE.openai.azure.com/) "
                "or pass the base_url parameter to register_provider()."
            )

        # Normalize base_url to include /openai/v1/ suffix with trailing slash
        if not resolved_base_url.rstrip("/").endswith("/openai/v1"):
            resolved_base_url = resolved_base_url.rstrip("/") + "/openai/v1/"
        elif not resolved_base_url.endswith("/"):
            resolved_base_url += "/"

        self.client = OpenAI(
            api_key=resolved_api_key,
            base_url=resolved_base_url,
        )
        self.async_client = AsyncOpenAI(
            api_key=resolved_api_key,
            base_url=resolved_base_url,
        )

    def _model_name(self, model_id: str) -> str:
        """Strip 'azure/' prefix from model ID for Azure OpenAI API."""
        return model_id.removeprefix("azure/")


class AzureRoutedOpenAIProvider(AzureOpenAIProvider):
    """Azure OpenAI provider that reports provider_id as 'azure'.

    Used when accessed through the unified AzureProvider routing.
    """

    id: ClassVar[str] = "azure"
