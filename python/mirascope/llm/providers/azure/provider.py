"""Unified Azure OpenAI provider implementation.

Model ID format:
    - azure/{original_provider}/{deployment}
        - OpenAI example: "azure/openai/gpt-5-mini"
"""

from __future__ import annotations

from collections.abc import Sequence
from typing import TYPE_CHECKING
from typing_extensions import Unpack

from openai import OpenAI

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
from ..base import BaseProvider
from ..openai._utils.errors import OPENAI_ERROR_MAP
from .model_id import AzureModelId
from .openai.provider import AzureOpenAIProvider

if TYPE_CHECKING:
    from ...models import Params


class AzureProvider(BaseProvider[OpenAI]):
    """Unified provider for Azure OpenAI using OpenAI-compatible routing.

    Model IDs follow the pattern ``azure/{original_provider}/{deployment}``.
    This provider currently supports the ``azure/openai/...`` scope.
    """

    id = "azure"
    default_scope = "azure/openai/"
    error_map = OPENAI_ERROR_MAP

    def __init__(
        self,
        *,
        api_key: str | None = None,
        base_url: str | None = None,
    ) -> None:
        """Initialize the Azure provider with the OpenAI-compatible client."""
        self._openai_provider = AzureOpenAIProvider(
            api_key=api_key,
            base_url=base_url,
        )
        self.client = self._openai_provider.client

    def get_error_status(self, e: Exception) -> int | None:
        """Extract HTTP status code from OpenAI exception."""
        return getattr(e, "status_code", None)

    def _choose_subprovider(
        self, model_id: AzureModelId, messages: Sequence[Message]
    ) -> AzureOpenAIProvider:
        """Choose the Azure OpenAI subprovider.

        Args:
            model_id: The model identifier.
            messages: The messages to send to the LLM.

        Returns:
            The Azure OpenAI subprovider.
        """
        return self._openai_provider

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
