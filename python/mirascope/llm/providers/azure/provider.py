"""Unified Azure OpenAI provider implementation."""

from __future__ import annotations

from collections.abc import Sequence
from typing import TYPE_CHECKING, Any
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
from .model_id import AzureModelId

if TYPE_CHECKING:
    from openai import OpenAI
    from openai.lib.azure import AsyncAzureADTokenProvider, AzureADTokenProvider

    from ...models import Params
    from .openai.provider import AzureOpenAIRoutedProvider
else:
    OpenAI = Any  # type: ignore[misc]
    AzureADTokenProvider = Any  # type: ignore[misc]
    AsyncAzureADTokenProvider = Any  # type: ignore[misc]


class AzureProvider(BaseProvider[OpenAI | None]):
    """Unified provider for Azure OpenAI using OpenAI-compatible routing."""

    id = "azure"
    default_scope = "azure/"
    error_map = OPENAI_ERROR_MAP

    def __init__(
        self,
        *,
        api_key: str | AzureADTokenProvider | AsyncAzureADTokenProvider | None = None,
        base_url: str | None = None,
    ) -> None:
        """Initialize the Azure provider with the OpenAI-compatible client."""
        self._openai_provider: AzureOpenAIRoutedProvider | None = None
        self.client = None

        try:
            from .openai.provider import AzureOpenAIRoutedProvider
        except ImportError:
            return

        self._openai_provider = AzureOpenAIRoutedProvider(
            api_key=api_key,
            base_url=base_url,
        )
        self.client = self._openai_provider.client

    def _get_openai_provider(self) -> AzureOpenAIRoutedProvider:
        if self._openai_provider is None:
            raise ImportError(
                "The 'openai' packages are required to use AzureOpenAIProvider. "
                "Install them with: `uv add 'mirascope[openai]'`. "
                "Or use `uv add 'mirascope[all]'` to support all optional features."
            )
        return self._openai_provider

    def get_error_status(self, e: Exception) -> int | None:
        """Extract HTTP status code from OpenAI exception."""
        return getattr(e, "status_code", None)  # pragma: no cover

    def _choose_subprovider(
        self, model_id: AzureModelId, messages: Sequence[Message]
    ) -> AzureOpenAIRoutedProvider:
        """Choose the Azure OpenAI subprovider.

        Args:
            model_id: The model identifier.
            messages: The messages to send to the LLM.

        Returns:
            The Azure OpenAI subprovider.
        """
        return self._get_openai_provider()

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
