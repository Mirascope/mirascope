"""Azure OpenAI provider implementation."""

from __future__ import annotations

import os
from typing import ClassVar

from openai import AsyncOpenAI, OpenAI
from openai.lib.azure import AsyncAzureADTokenProvider, AzureADTokenProvider

from ...openai._utils.errors import OPENAI_ERROR_MAP
from ...openai.completions.base_provider import BaseOpenAICompletionsProvider
from .._utils import normalize_base_url
from ..model_id import model_name as azure_model_name
from ._utils import coerce_async_token_provider, coerce_sync_token_provider


class AzureOpenAIProvider(BaseOpenAICompletionsProvider):
    """Provider for Azure OpenAI's OpenAI-compatible API."""

    id: ClassVar[str] = "azure:openai"
    default_scope: ClassVar[str | list[str]] = "azure/"
    api_key_env_var: ClassVar[str] = "AZURE_OPENAI_API_KEY"
    api_key_required: ClassVar[bool] = True
    provider_name: ClassVar[str | None] = "Azure OpenAI"
    error_map = OPENAI_ERROR_MAP

    def __init__(
        self,
        *,
        api_key: str | AzureADTokenProvider | AsyncAzureADTokenProvider | None = None,
        base_url: str | None = None,
    ) -> None:
        """Initialize the Azure OpenAI provider."""
        resolved_api_key = api_key or os.environ.get(self.api_key_env_var)
        if self.api_key_required and not resolved_api_key:
            raise ValueError(
                "Azure OpenAI API key is required. "
                "Set the AZURE_OPENAI_API_KEY environment variable "
                "or pass the api_key parameter to register_provider()."
            )

        resolved_base_url = base_url or os.environ.get("AZURE_OPENAI_ENDPOINT")
        if not resolved_base_url:
            raise ValueError(
                "Azure OpenAI endpoint is required. "
                "Set the AZURE_OPENAI_ENDPOINT environment variable "
                "or pass the base_url parameter to register_provider()."
            )

        normalized_base_url = normalize_base_url(resolved_base_url, suffix="openai/v1")

        sync_api_key = coerce_sync_token_provider(resolved_api_key)
        async_api_key = coerce_async_token_provider(resolved_api_key)

        self.client = OpenAI(
            api_key=sync_api_key,
            base_url=normalized_base_url,
        )
        self.async_client = AsyncOpenAI(
            api_key=async_api_key,
            base_url=normalized_base_url,
        )

    def get_error_status(self, e: Exception) -> int | None:
        """Extract HTTP status code from OpenAI exception."""
        return getattr(e, "status_code", None)

    def _model_name(self, model_id: str) -> str:
        """Extract the Azure deployment name from the model ID."""
        return azure_model_name(model_id)


class AzureOpenAIRoutedProvider(AzureOpenAIProvider):
    """Azure OpenAI provider that reports provider_id as "azure"."""

    id: ClassVar[str] = "azure"
