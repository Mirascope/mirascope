"""Unified Azure provider implementation."""

from __future__ import annotations

from collections.abc import Awaitable, Callable, Sequence
from typing import TYPE_CHECKING, Any, Literal
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
    AsyncContextTool,
    AsyncContextToolkit,
    AsyncTool,
    AsyncToolkit,
    ContextTool,
    ContextToolkit,
    Tool,
    Toolkit,
)
from ..base import BaseProvider
from ..openai._utils.errors import OPENAI_ERROR_MAP
from ..openai.model_id import OPENAI_KNOWN_MODELS
from . import _utils as azure_utils
from .model_id import AzureModelId

if TYPE_CHECKING:
    from openai import OpenAI
    from openai.lib.azure import AsyncAzureADTokenProvider, AzureADTokenProvider

    from ...models import Params
    from .anthropic import AzureAnthropicRoutedProvider
    from .openai.provider import AzureOpenAIRoutedProvider
else:
    OpenAI = Any  # type: ignore[misc]
    AzureADTokenProvider = Any  # type: ignore[misc]
    AsyncAzureADTokenProvider = Any  # type: ignore[misc]

AZURE_ANTHROPIC_MODEL_PREFIXES = tuple(azure_utils.default_anthropic_scopes())

RoutingProviderId = Literal["anthropic", "openai"]

AZURE_OPENAI_MODEL_PREFIXES = tuple(
    {
        f"azure/{model_id.split('/', 1)[1].split(':', 1)[0]}"
        for model_id in OPENAI_KNOWN_MODELS
    }
)


def _default_routing_scopes() -> dict[RoutingProviderId, list[str]]:
    return {
        "anthropic": list(AZURE_ANTHROPIC_MODEL_PREFIXES),
        "openai": list(AZURE_OPENAI_MODEL_PREFIXES),
    }


class AzureProvider(BaseProvider[OpenAI | None]):
    """Unified provider for Azure-hosted models using routing.

    Auto-routing is strict. It matches only:
    - Known OpenAI model names (``azure/<model>`` from ``OPENAI_KNOWN_MODELS``)
    - Known Anthropic model names (``azure/<model>`` from
      ``ANTHROPIC_KNOWN_MODELS``)
    - The Azure Foundry registry prefix
      ``azure/azureml://registries/azureml-anthropic/``

    Custom deployment names are not auto-detected. If a model id does not
    match one of the defaults above, you must add routing prefixes via
    ``routing_scopes``; otherwise calling this provider raises ``ValueError``
    with guidance on how to configure routing.
    """

    id = "azure"
    default_scope = "azure/"
    error_map = OPENAI_ERROR_MAP

    def __init__(
        self,
        *,
        api_key: str | AzureADTokenProvider | AsyncAzureADTokenProvider | None = None,
        base_url: str | None = None,
        anthropic_api_key: str | None = None,
        anthropic_base_url: str | None = None,
        anthropic_azure_ad_token_provider: Callable[[], str]
        | Callable[[], Awaitable[str]]
        | None = None,
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

    def _get_openai_provider(self) -> AzureOpenAIRoutedProvider:
        if self._openai_provider is None:
            try:
                from .openai.provider import AzureOpenAIRoutedProvider
            except ImportError:
                from ...._stubs import make_import_error

                raise make_import_error("openai", "AzureOpenAIProvider") from None
            self._openai_provider = AzureOpenAIRoutedProvider(
                api_key=self._openai_api_key,
                base_url=self._openai_base_url,
            )
            self.client = self._openai_provider.client
        return self._openai_provider

    def get_error_status(self, e: Exception) -> int | None:
        """Extract HTTP status code from OpenAI exception."""
        return getattr(e, "status_code", None)  # pragma: no cover

    def _choose_subprovider(
        self, model_id: AzureModelId, messages: Sequence[Message]
    ) -> AzureOpenAIRoutedProvider | AzureAnthropicRoutedProvider:
        """Choose the Azure subprovider.

        Args:
            model_id: The model identifier.
            messages: The messages to send to the LLM.

        Returns:
            The Azure subprovider.
        """
        route = self._route_provider(model_id)
        if route == "anthropic":
            return self._get_anthropic_provider()
        if route == "openai":
            return self._get_openai_provider()

        message = (
            "AzureProvider could not determine which SDK to use for "
            f"model_id='{model_id}'. Auto-routing only supports known OpenAI "
            "model names and Anthropic prefixes. If you deployed with a custom "
            "name, pass routing_scopes={'anthropic': ['azure/<deployment>']} or "
            "routing_scopes={'openai': ['azure/<deployment>']} when registering "
            "the AzureProvider."
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
            try:
                from .anthropic import AzureAnthropicRoutedProvider
            except ImportError:
                from ...._stubs import make_import_error

                raise make_import_error("anthropic", "AzureAnthropicProvider") from None

            self._anthropic_provider = AzureAnthropicRoutedProvider(
                api_key=self._anthropic_api_key,
                base_url=self._anthropic_base_url,
                azure_ad_token_provider=self._anthropic_azure_ad_token_provider,
            )

        return self._anthropic_provider

    def _call(
        self,
        *,
        model_id: AzureModelId,
        messages: Sequence[Message],
        tools: Sequence[Tool] | Toolkit | None = None,
        format: type[FormattableT]
        | Format[FormattableT]
        | OutputParser[FormattableT]
        | None = None,
        **params: Unpack[Params],
    ) -> Response | Response[FormattableT]:
        """Generate an `llm.Response` by synchronously calling the Azure API.

        Args:
            model_id: Model identifier to use.
            messages: Messages to send to the LLM.
            tools: Optional tools that the model may invoke.
            format: Optional response format specifier.
            **params: Additional parameters to configure output (e.g. temperature). See `llm.Params`.

        Returns:
            An `llm.Response` object containing the LLM-generated content.
        """
        client = self._choose_subprovider(model_id, messages)
        return client.call(
            model_id=model_id,
            messages=messages,
            tools=tools,
            format=format,
            **params,
        )

    def _context_call(
        self,
        *,
        ctx: Context[DepsT],
        model_id: AzureModelId,
        messages: Sequence[Message],
        tools: Sequence[Tool | ContextTool[DepsT]]
        | ContextToolkit[DepsT]
        | None = None,
        format: type[FormattableT]
        | Format[FormattableT]
        | OutputParser[FormattableT]
        | None = None,
        **params: Unpack[Params],
    ) -> ContextResponse[DepsT, None] | ContextResponse[DepsT, FormattableT]:
        """Generate an `llm.ContextResponse` by synchronously calling the Azure API.

        Args:
            ctx: Context object with dependencies for tools.
            model_id: Model identifier to use.
            messages: Messages to send to the LLM.
            tools: Optional tools that the model may invoke.
            format: Optional response format specifier.
            **params: Additional parameters to configure output (e.g. temperature). See `llm.Params`.

        Returns:
            An `llm.ContextResponse` object containing the LLM-generated content.
        """
        client = self._choose_subprovider(model_id, messages)
        return client.context_call(
            ctx=ctx,
            model_id=model_id,
            messages=messages,
            tools=tools,
            format=format,
            **params,
        )

    async def _call_async(
        self,
        *,
        model_id: AzureModelId,
        messages: Sequence[Message],
        tools: Sequence[AsyncTool] | AsyncToolkit | None = None,
        format: type[FormattableT]
        | Format[FormattableT]
        | OutputParser[FormattableT]
        | None = None,
        **params: Unpack[Params],
    ) -> AsyncResponse | AsyncResponse[FormattableT]:
        """Generate an `llm.AsyncResponse` by calling the Azure API asynchronously.

        Args:
            model_id: Model identifier to use.
            messages: Messages to send to the LLM.
            tools: Optional tools that the model may invoke.
            format: Optional response format specifier.
            **params: Additional parameters to configure output (e.g. temperature). See `llm.Params`.

        Returns:
            An `llm.AsyncResponse` object containing the LLM-generated content.
        """
        client = self._choose_subprovider(model_id, messages)
        return await client.call_async(
            model_id=model_id,
            messages=messages,
            tools=tools,
            format=format,
            **params,
        )

    async def _context_call_async(
        self,
        *,
        ctx: Context[DepsT],
        model_id: AzureModelId,
        messages: Sequence[Message],
        tools: Sequence[AsyncTool | AsyncContextTool[DepsT]]
        | AsyncContextToolkit[DepsT]
        | None = None,
        format: type[FormattableT]
        | Format[FormattableT]
        | OutputParser[FormattableT]
        | None = None,
        **params: Unpack[Params],
    ) -> AsyncContextResponse[DepsT, None] | AsyncContextResponse[DepsT, FormattableT]:
        """Generate an `llm.AsyncContextResponse` by calling the Azure API asynchronously.

        Args:
            ctx: Context object with dependencies for tools.
            model_id: Model identifier to use.
            messages: Messages to send to the LLM.
            tools: Optional tools that the model may invoke.
            format: Optional response format specifier.
            **params: Additional parameters to configure output (e.g. temperature). See `llm.Params`.

        Returns:
            An `llm.AsyncContextResponse` object containing the LLM-generated content.
        """
        client = self._choose_subprovider(model_id, messages)
        return await client.context_call_async(
            ctx=ctx,
            model_id=model_id,
            messages=messages,
            tools=tools,
            format=format,
            **params,
        )

    def _stream(
        self,
        *,
        model_id: AzureModelId,
        messages: Sequence[Message],
        tools: Sequence[Tool] | Toolkit | None = None,
        format: type[FormattableT]
        | Format[FormattableT]
        | OutputParser[FormattableT]
        | None = None,
        **params: Unpack[Params],
    ) -> StreamResponse | StreamResponse[FormattableT]:
        """Generate an `llm.StreamResponse` by streaming the Azure API response.

        Args:
            model_id: Model identifier to use.
            messages: Messages to send to the LLM.
            tools: Optional tools that the model may invoke.
            format: Optional response format specifier.
            **params: Additional parameters to configure output (e.g. temperature). See `llm.Params`.

        Returns:
            An `llm.StreamResponse` for streaming the LLM-generated content.
        """
        client = self._choose_subprovider(model_id, messages)
        return client.stream(
            model_id=model_id,
            messages=messages,
            tools=tools,
            format=format,
            **params,
        )

    def _context_stream(
        self,
        *,
        ctx: Context[DepsT],
        model_id: AzureModelId,
        messages: Sequence[Message],
        tools: Sequence[Tool | ContextTool[DepsT]]
        | ContextToolkit[DepsT]
        | None = None,
        format: type[FormattableT]
        | Format[FormattableT]
        | OutputParser[FormattableT]
        | None = None,
        **params: Unpack[Params],
    ) -> ContextStreamResponse[DepsT] | ContextStreamResponse[DepsT, FormattableT]:
        """Generate an `llm.ContextStreamResponse` by streaming the Azure API response.

        Args:
            ctx: Context object with dependencies for tools.
            model_id: Model identifier to use.
            messages: Messages to send to the LLM.
            tools: Optional tools that the model may invoke.
            format: Optional response format specifier.
            **params: Additional parameters to configure output (e.g. temperature). See `llm.Params`.

        Returns:
            An `llm.ContextStreamResponse` for streaming the LLM-generated content.
        """
        client = self._choose_subprovider(model_id, messages)
        return client.context_stream(
            ctx=ctx,
            model_id=model_id,
            messages=messages,
            tools=tools,
            format=format,
            **params,
        )

    async def _stream_async(
        self,
        *,
        model_id: AzureModelId,
        messages: Sequence[Message],
        tools: Sequence[AsyncTool] | AsyncToolkit | None = None,
        format: type[FormattableT]
        | Format[FormattableT]
        | OutputParser[FormattableT]
        | None = None,
        **params: Unpack[Params],
    ) -> AsyncStreamResponse | AsyncStreamResponse[FormattableT]:
        """Generate an `llm.AsyncStreamResponse` by streaming the Azure API response.

        Args:
            model_id: Model identifier to use.
            messages: Messages to send to the LLM.
            tools: Optional tools that the model may invoke.
            format: Optional response format specifier.
            **params: Additional parameters to configure output (e.g. temperature). See `llm.Params`.

        Returns:
            An `llm.AsyncStreamResponse` for streaming the LLM-generated content.
        """
        client = self._choose_subprovider(model_id, messages)
        return await client.stream_async(
            model_id=model_id,
            messages=messages,
            tools=tools,
            format=format,
            **params,
        )

    async def _context_stream_async(
        self,
        *,
        ctx: Context[DepsT],
        model_id: AzureModelId,
        messages: Sequence[Message],
        tools: Sequence[AsyncTool | AsyncContextTool[DepsT]]
        | AsyncContextToolkit[DepsT]
        | None = None,
        format: type[FormattableT]
        | Format[FormattableT]
        | OutputParser[FormattableT]
        | None = None,
        **params: Unpack[Params],
    ) -> (
        AsyncContextStreamResponse[DepsT]
        | AsyncContextStreamResponse[DepsT, FormattableT]
    ):
        """Generate an `llm.AsyncContextStreamResponse` by streaming the Azure API response.

        Args:
            ctx: Context object with dependencies for tools.
            model_id: Model identifier to use.
            messages: Messages to send to the LLM.
            tools: Optional tools that the model may invoke.
            format: Optional response format specifier.
            **params: Additional parameters to configure output (e.g. temperature). See `llm.Params`.

        Returns:
            An `llm.AsyncContextStreamResponse` for streaming the LLM-generated content.
        """
        client = self._choose_subprovider(model_id, messages)
        return await client.context_stream_async(
            ctx=ctx,
            model_id=model_id,
            messages=messages,
            tools=tools,
            format=format,
            **params,
        )
