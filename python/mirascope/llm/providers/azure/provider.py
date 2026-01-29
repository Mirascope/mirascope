"""Unified Azure provider implementation.

Model ID formats:
    - azure/{original_provider}/{deployment}
        - OpenAI example: "azure/openai/gpt-5-mini"
        - Anthropic example: "azure/anthropic/claude-sonnet-4-5"
    - Azure Foundry registry models:
        - "azure/azureml://registries/azureml-anthropic/..."
"""

from __future__ import annotations

import os
from collections.abc import Callable, Sequence
from typing import TYPE_CHECKING, ClassVar, Literal
from typing_extensions import Unpack

from ...context import Context, DepsT
from ...formatting import Format, FormattableT, OutputParser
from ...messages import Message
from ...responses import (
    AsyncContextResponse,
    AsyncContextStreamResponse,
    AsyncResponse,
    AsyncStreamResponse,
    ContextResponse,
    ContextStreamResponse,
    Response,
    StreamResponse,
)
from ...tools import (
    AsyncContextToolkit,
    AsyncToolkit,
    ContextToolkit,
    Toolkit,
)
from ..base import BaseProvider, ProviderErrorMap
from . import _utils as azure_utils
from .anthropic import AzureAnthropicRoutedProvider
from .model_id import AzureModelId
from .openai.provider import AzureOpenAIRoutedProvider

if TYPE_CHECKING:
    from anthropic import Anthropic
    from anthropic.lib.foundry import AnthropicFoundry
    from openai import OpenAI

    from ...models import Params
else:

    class Anthropic:  # pragma: no cover - typing-only fallback
        pass

    class AnthropicFoundry:  # pragma: no cover - typing-only fallback
        pass

    class OpenAI:  # pragma: no cover - typing-only fallback
        pass


RoutingProviderId = Literal["anthropic", "openai"]


def _default_routing_scopes() -> dict[RoutingProviderId, list[str]]:
    """Build default routing scopes at runtime to avoid import-time dependencies."""
    anthropic_scopes = list(azure_utils.default_anthropic_scopes())

    try:
        from ..openai.model_id import OPENAI_KNOWN_MODELS

        openai_scopes = {
            "azure/openai/",
            *(
                f"azure/openai/{model_id.split('/', 1)[1].split(':', 1)[0]}"
                for model_id in OPENAI_KNOWN_MODELS
            ),
        }
    except ImportError:
        openai_scopes = {"azure/openai/"}

    return {
        "anthropic": anthropic_scopes,
        "openai": list(openai_scopes),
    }


class AzureProvider(BaseProvider["OpenAI | AnthropicFoundry | Anthropic | None"]):
    """Unified provider for Azure-hosted models using routing.

    Auto-routing is strict. It matches only:
    - Known OpenAI deployments (``azure/openai/<deployment>``)
    - Known Anthropic models (``azure/anthropic/<model>``)
    - The Azure Foundry registry prefix
      ``azure/azureml://registries/azureml-anthropic/``

    Custom deployment names are not auto-detected. If a model id does not
    match one of the defaults above, you must add routing prefixes via
    ``routing_scopes``; otherwise calling this provider raises ``ValueError``
    with guidance on how to configure routing.
    """

    id = "azure"
    default_scope = "azure/openai/"
    error_map: ClassVar[ProviderErrorMap] = {}

    def __init__(
        self,
        *,
        api_key: str | None = None,
        base_url: str | None = None,
        anthropic_api_key: str | None = None,
        anthropic_base_url: str | None = None,
        anthropic_azure_ad_token_provider: Callable[[], str] | None = None,
        routing_scopes: dict[RoutingProviderId, list[str]] | None = None,
    ) -> None:
        """Initialize the Azure provider with the OpenAI-compatible client.

        Args:
            api_key: Azure OpenAI API key or Azure AD token provider.
            base_url: Azure OpenAI endpoint base URL.
            anthropic_api_key: Azure Anthropic API key.
            anthropic_base_url: Azure Anthropic endpoint base URL.
            anthropic_azure_ad_token_provider: Azure AD token provider for
                Anthropic Foundry endpoints.
            routing_scopes: Optional mapping of provider ids to additional
                model-id prefixes (for example, ``"azure/my-deployment"``) used
                for routing. These prefixes extend the defaults (exact known
                model names plus the Azure Foundry registry prefix), and routing
                selects the longest matching prefix. If no prefix matches a
                model id at call time, this provider raises ``ValueError`` with
                guidance on how to configure routing.
        """
        self._openai_provider: AzureOpenAIRoutedProvider | None = None
        self.client = None
        self._openai_api_key = api_key
        self._openai_base_url = base_url
        self._anthropic_api_key = anthropic_api_key
        self._anthropic_base_url = anthropic_base_url
        self._anthropic_azure_ad_token_provider = anthropic_azure_ad_token_provider
        self._anthropic_provider: AzureAnthropicRoutedProvider | None = None
        self._routing_scopes = _default_routing_scopes()
        if routing_scopes:
            for provider_id, scopes in routing_scopes.items():
                self._routing_scopes[provider_id].extend(scopes)

        env_api_key = os.environ.get("AZURE_OPENAI_API_KEY")
        env_base_url = os.environ.get("AZURE_OPENAI_ENDPOINT")

        if self._openai_api_key is None and env_api_key:
            self._openai_api_key = env_api_key
        if self._openai_base_url is None and env_base_url:
            self._openai_base_url = env_base_url

        if self._openai_api_key and self._openai_base_url:
            self._get_openai_provider()

    def _get_openai_provider(self) -> AzureOpenAIRoutedProvider:
        if self._openai_provider is None:
            self._openai_provider = AzureOpenAIRoutedProvider(
                api_key=self._openai_api_key,
                base_url=self._openai_base_url,
            )
            self.client = self._openai_provider.client
        return self._openai_provider

    def get_error_status(self, e: Exception) -> int | None:
        """Extract HTTP status code from OpenAI exception."""
        return getattr(e, "status_code", None)

    def _choose_subprovider(
        self, model_id: AzureModelId, messages: Sequence[Message]
    ) -> AzureOpenAIRoutedProvider | AzureAnthropicRoutedProvider:
        """Choose the Azure subprovider."""
        route = self._route_provider(model_id)
        if route == "anthropic":
            return self._get_anthropic_provider()
        if route == "openai":
            return self._get_openai_provider()

        message = (
            "AzureProvider could not determine which SDK to use for "
            f"model_id='{model_id}'. Auto-routing supports:\n"
            "  - OpenAI deployments: 'azure/openai/<deployment>'\n"
            "    (e.g. 'azure/openai/gpt-5-mini')\n"
            "  - Anthropic models: 'azure/anthropic/<model>' or 'azure/azureml://...'\n"
            "    (e.g. 'azure/anthropic/claude-sonnet-4-5')\n"
            "For custom deployments, use routing_scopes parameter."
        )
        raise ValueError(message)

    def _route_provider(self, model_id: AzureModelId) -> RoutingProviderId | None:
        best_match: tuple[RoutingProviderId, int] | None = None
        for provider_id, scopes in self._routing_scopes.items():
            for scope in scopes:
                if model_id.startswith(scope):
                    match = (provider_id, len(scope))
                    if best_match is None or match[1] > best_match[1]:
                        best_match = match
        if best_match is None:
            return None
        return best_match[0]

    def _get_anthropic_provider(self) -> AzureAnthropicRoutedProvider:
        if self._anthropic_provider is None:
            self._anthropic_provider = AzureAnthropicRoutedProvider(
                api_key=self._anthropic_api_key,
                base_url=self._anthropic_base_url,
                azure_ad_token_provider=self._anthropic_azure_ad_token_provider,
            )
            self.client = self._anthropic_provider.client

        return self._anthropic_provider

    def _call(
        self,
        *,
        model_id: AzureModelId,
        messages: Sequence[Message],
        toolkit: Toolkit,
        format: type[FormattableT]
        | Format[FormattableT]
        | OutputParser[FormattableT]
        | None = None,
        **params: Unpack[Params],
    ) -> Response | Response[FormattableT]:
        """Generate an `llm.Response` by synchronously calling the Azure API."""
        client = self._choose_subprovider(model_id, messages)
        return client.call(
            model_id=model_id,
            messages=messages,
            toolkit=toolkit,
            format=format,
            **params,
        )

    def _context_call(
        self,
        *,
        ctx: Context[DepsT],
        model_id: AzureModelId,
        messages: Sequence[Message],
        toolkit: ContextToolkit[DepsT],
        format: type[FormattableT]
        | Format[FormattableT]
        | OutputParser[FormattableT]
        | None = None,
        **params: Unpack[Params],
    ) -> ContextResponse[DepsT, None] | ContextResponse[DepsT, FormattableT]:
        """Generate an `llm.ContextResponse` by synchronously calling the Azure API."""
        client = self._choose_subprovider(model_id, messages)
        return client.context_call(
            ctx=ctx,
            model_id=model_id,
            messages=messages,
            toolkit=toolkit,
            format=format,
            **params,
        )

    async def _call_async(
        self,
        *,
        model_id: AzureModelId,
        messages: Sequence[Message],
        toolkit: AsyncToolkit,
        format: type[FormattableT]
        | Format[FormattableT]
        | OutputParser[FormattableT]
        | None = None,
        **params: Unpack[Params],
    ) -> AsyncResponse | AsyncResponse[FormattableT]:
        """Generate an `llm.AsyncResponse` by calling the Azure API asynchronously."""
        client = self._choose_subprovider(model_id, messages)
        return await client.call_async(
            model_id=model_id,
            messages=messages,
            toolkit=toolkit,
            format=format,
            **params,
        )

    async def _context_call_async(
        self,
        *,
        ctx: Context[DepsT],
        model_id: AzureModelId,
        messages: Sequence[Message],
        toolkit: AsyncContextToolkit[DepsT],
        format: type[FormattableT]
        | Format[FormattableT]
        | OutputParser[FormattableT]
        | None = None,
        **params: Unpack[Params],
    ) -> AsyncContextResponse[DepsT, None] | AsyncContextResponse[DepsT, FormattableT]:
        """Generate an `llm.AsyncContextResponse` by calling the Azure API asynchronously."""
        client = self._choose_subprovider(model_id, messages)
        return await client.context_call_async(
            ctx=ctx,
            model_id=model_id,
            messages=messages,
            toolkit=toolkit,
            format=format,
            **params,
        )

    def _stream(
        self,
        *,
        model_id: AzureModelId,
        messages: Sequence[Message],
        toolkit: Toolkit,
        format: type[FormattableT]
        | Format[FormattableT]
        | OutputParser[FormattableT]
        | None = None,
        **params: Unpack[Params],
    ) -> StreamResponse | StreamResponse[FormattableT]:
        """Generate an `llm.StreamResponse` by streaming the Azure API response."""
        client = self._choose_subprovider(model_id, messages)
        return client.stream(
            model_id=model_id,
            messages=messages,
            toolkit=toolkit,
            format=format,
            **params,
        )

    def _context_stream(
        self,
        *,
        ctx: Context[DepsT],
        model_id: AzureModelId,
        messages: Sequence[Message],
        toolkit: ContextToolkit[DepsT],
        format: type[FormattableT]
        | Format[FormattableT]
        | OutputParser[FormattableT]
        | None = None,
        **params: Unpack[Params],
    ) -> ContextStreamResponse[DepsT] | ContextStreamResponse[DepsT, FormattableT]:
        """Generate an `llm.ContextStreamResponse` by streaming the Azure API response."""
        client = self._choose_subprovider(model_id, messages)
        return client.context_stream(
            ctx=ctx,
            model_id=model_id,
            messages=messages,
            toolkit=toolkit,
            format=format,
            **params,
        )

    async def _stream_async(
        self,
        *,
        model_id: AzureModelId,
        messages: Sequence[Message],
        toolkit: AsyncToolkit,
        format: type[FormattableT]
        | Format[FormattableT]
        | OutputParser[FormattableT]
        | None = None,
        **params: Unpack[Params],
    ) -> AsyncStreamResponse | AsyncStreamResponse[FormattableT]:
        """Generate an `llm.AsyncStreamResponse` by streaming the Azure API response."""
        client = self._choose_subprovider(model_id, messages)
        return await client.stream_async(
            model_id=model_id,
            messages=messages,
            toolkit=toolkit,
            format=format,
            **params,
        )

    async def _context_stream_async(
        self,
        *,
        ctx: Context[DepsT],
        model_id: AzureModelId,
        messages: Sequence[Message],
        toolkit: AsyncContextToolkit[DepsT],
        format: type[FormattableT]
        | Format[FormattableT]
        | OutputParser[FormattableT]
        | None = None,
        **params: Unpack[Params],
    ) -> (
        AsyncContextStreamResponse[DepsT]
        | AsyncContextStreamResponse[DepsT, FormattableT]
    ):
        """Generate an `llm.AsyncContextStreamResponse` by streaming the Azure API response."""
        client = self._choose_subprovider(model_id, messages)
        return await client.context_stream_async(
            ctx=ctx,
            model_id=model_id,
            messages=messages,
            toolkit=toolkit,
            format=format,
            **params,
        )
