"""Unified Azure client implementation."""

from collections.abc import Sequence
from typing_extensions import Unpack

from openai import OpenAI

from ...context import Context, DepsT
from ...formatting import Format, FormattableT
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
from ..base import BaseProvider, Params
from .model_id import AzureModelId
from .openai import AzureOpenAIProvider, AzureRoutedOpenAIProvider


class AzureProvider(BaseProvider[OpenAI]):
    """Unified provider for Azure that routes to appropriate sub-providers based on model_id."""

    id = "azure"
    default_scope = "azure/"

    def __init__(
        self, *, api_key: str | None = None, base_url: str | None = None
    ) -> None:
        """Initialize the Azure provider with sub-providers."""
        self._openai_provider = AzureRoutedOpenAIProvider(
            api_key=api_key, base_url=base_url
        )
        # Use OpenAI provider's client as the main client
        self.client = self._openai_provider.client

    def _choose_subprovider(
        self, model_id: AzureModelId, messages: Sequence[Message]
    ) -> AzureOpenAIProvider:
        """Choose the appropriate provider based on model_id and messages.

        Args:
            model_id: The model identifier.
            messages: The messages to send to the LLM.

        Returns:
            The appropriate sub-provider for the model.
        """
        # Currently only OpenAI models are supported
        # Future: add logic to route to Foundry or other providers based on model_id
        return self._openai_provider

    def _call(
        self,
        *,
        model_id: AzureModelId,
        messages: Sequence[Message],
        tools: Sequence[Tool] | Toolkit | None = None,
        format: type[FormattableT] | Format[FormattableT] | None = None,
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
        format: type[FormattableT] | Format[FormattableT] | None = None,
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
        format: type[FormattableT] | Format[FormattableT] | None = None,
        **params: Unpack[Params],
    ) -> AsyncResponse | AsyncResponse[FormattableT]:
        """Generate an `llm.AsyncResponse` by asynchronously calling the Azure API.

        Args:
            model_id: Model identifier to use.
            messages: Messages to send to the LLM.
            tools: Optional tools that the model may invoke.
            format: Optional response format specifier.
            **params: Additional parameters to configure output (e.g. temperature). See `llm.Params`.

        Returns:
            An `llm.AsyncResponse` object containing the LLM-generated content.
        """
        return await self._choose_subprovider(model_id, messages).call_async(
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
        format: type[FormattableT] | Format[FormattableT] | None = None,
        **params: Unpack[Params],
    ) -> AsyncContextResponse[DepsT, None] | AsyncContextResponse[DepsT, FormattableT]:
        """Generate an `llm.AsyncContextResponse` by asynchronously calling the Azure API.

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
        return await self._choose_subprovider(model_id, messages).context_call_async(
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
        format: type[FormattableT] | Format[FormattableT] | None = None,
        **params: Unpack[Params],
    ) -> StreamResponse | StreamResponse[FormattableT]:
        """Generate an `llm.StreamResponse` by synchronously streaming from the Azure API.

        Args:
            model_id: Model identifier to use.
            messages: Messages to send to the LLM.
            tools: Optional tools that the model may invoke.
            format: Optional response format specifier.
            **params: Additional parameters to configure output (e.g. temperature). See `llm.Params`.

        Returns:
            An `llm.StreamResponse` object for iterating over the LLM-generated content.
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
        format: type[FormattableT] | Format[FormattableT] | None = None,
        **params: Unpack[Params],
    ) -> ContextStreamResponse[DepsT] | ContextStreamResponse[DepsT, FormattableT]:
        """Generate an `llm.ContextStreamResponse` by synchronously streaming from the Azure API.

        Args:
            ctx: Context object with dependencies for tools.
            model_id: Model identifier to use.
            messages: Messages to send to the LLM.
            tools: Optional tools that the model may invoke.
            format: Optional response format specifier.
            **params: Additional parameters to configure output (e.g. temperature). See `llm.Params`.

        Returns:
            An `llm.ContextStreamResponse` object for iterating over the LLM-generated content.
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
        format: type[FormattableT] | Format[FormattableT] | None = None,
        **params: Unpack[Params],
    ) -> AsyncStreamResponse | AsyncStreamResponse[FormattableT]:
        """Generate an `llm.AsyncStreamResponse` by asynchronously streaming from the Azure API.

        Args:
            model_id: Model identifier to use.
            messages: Messages to send to the LLM.
            tools: Optional tools that the model may invoke.
            format: Optional response format specifier.
            **params: Additional parameters to configure output (e.g. temperature). See `llm.Params`.

        Returns:
            An `llm.AsyncStreamResponse` object for asynchronously iterating over the LLM-generated content.
        """
        return await self._choose_subprovider(model_id, messages).stream_async(
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
        format: type[FormattableT] | Format[FormattableT] | None = None,
        **params: Unpack[Params],
    ) -> (
        AsyncContextStreamResponse[DepsT]
        | AsyncContextStreamResponse[DepsT, FormattableT]
    ):
        """Generate an `llm.AsyncContextStreamResponse` by asynchronously streaming from the Azure API.

        Args:
            ctx: Context object with dependencies for tools.
            model_id: Model identifier to use.
            messages: Messages to send to the LLM.
            tools: Optional tools that the model may invoke.
            format: Optional response format specifier.
            **params: Additional parameters to configure output (e.g. temperature). See `llm.Params`.

        Returns:
            An `llm.AsyncContextStreamResponse` object for asynchronously iterating over the LLM-generated content.
        """
        return await self._choose_subprovider(model_id, messages).context_stream_async(
            ctx=ctx,
            model_id=model_id,
            messages=messages,
            tools=tools,
            format=format,
            **params,
        )
