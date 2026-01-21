"""Azure Anthropic beta provider implementation."""

from __future__ import annotations

import os
from typing import ClassVar

from anthropic.lib.foundry import (
    AnthropicFoundry,
    AsyncAnthropicFoundry,
    AzureADTokenProvider,
)

from ...anthropic import _utils as anthropic_utils
from ...anthropic.beta_provider import BaseAnthropicBetaProvider
from .. import _utils as azure_utils
from . import _utils


class AzureAnthropicBetaProvider(
    BaseAnthropicBetaProvider[AnthropicFoundry, AsyncAnthropicFoundry]
):
    """Provider using the Azure Anthropic beta API."""

    id: ClassVar[str] = "azure:anthropic-beta"
    default_scope: ClassVar[str | list[str]] = azure_utils.default_anthropic_scopes()
    error_map = anthropic_utils.ANTHROPIC_ERROR_MAP

    def __init__(
        self,
        *,
        api_key: str | None = None,
        base_url: str | None = None,
        azure_ad_token_provider: AzureADTokenProvider | None = None,
    ) -> None:
        """Initialize the Azure Anthropic beta provider. Only sync token providers supported."""
        resolved_api_key = api_key or os.environ.get("AZURE_ANTHROPIC_API_KEY")
        resolved_base_url = base_url or os.environ.get("AZURE_AI_ANTHROPIC_ENDPOINT")

        if not resolved_api_key and azure_ad_token_provider is None:
            raise ValueError(
                "Azure Anthropic API key or Azure AD token provider is required. "
                "Set the AZURE_ANTHROPIC_API_KEY environment variable "
                "or pass the api_key or azure_ad_token_provider parameter to "
                "register_provider()."
            )

        if not resolved_base_url:
            raise ValueError(
                "Azure Anthropic endpoint is required. "
                "Set the AZURE_AI_ANTHROPIC_ENDPOINT environment variable "
                "or pass the base_url parameter to register_provider()."
            )

        normalized_base_url = _utils.normalize_base_url(resolved_base_url)
        sync_token_provider = _utils.coerce_sync_token_provider(azure_ad_token_provider)
        async_token_provider = _utils.coerce_async_token_provider(sync_token_provider)

        self.client = AnthropicFoundry(
            api_key=resolved_api_key,
            azure_ad_token_provider=sync_token_provider,
            base_url=normalized_base_url,
        )
        self.async_client = AsyncAnthropicFoundry(
            api_key=resolved_api_key,
            azure_ad_token_provider=async_token_provider,
            base_url=normalized_base_url,
        )

    def _model_name(self, model_id: str) -> str:
        return _utils.azure_model_name(model_id)


class AzureAnthropicRoutedBetaProvider(AzureAnthropicBetaProvider):
    """Azure Anthropic beta provider that reports provider_id as 'azure'."""

    id: ClassVar[str] = "azure"
