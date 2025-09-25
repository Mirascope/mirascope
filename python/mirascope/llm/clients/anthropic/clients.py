"""Anthropic client implementation."""

import os
from collections.abc import Sequence
from contextvars import ContextVar
from functools import lru_cache
from typing import overload
from typing_extensions import Unpack

from anthropic import Anthropic, AsyncAnthropic

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
    AsyncTool,
    ContextTool,
    Tool,
)
from ..base import BaseClient, Params
from . import _utils
from .model_ids import AnthropicModelId

ANTHROPIC_CLIENT_CONTEXT: ContextVar["AnthropicClient | None"] = ContextVar(
    "ANTHROPIC_CLIENT_CONTEXT", default=None
)


@lru_cache(maxsize=256)
def _anthropic_singleton(
    api_key: str | None, base_url: str | None
) -> "AnthropicClient":
    """Return a cached Anthropic client instance for the given parameters."""
    return AnthropicClient(api_key=api_key, base_url=base_url)


def client(
    *, api_key: str | None = None, base_url: str | None = None
) -> "AnthropicClient":
    """Create or retrieve an Anthropic client with the given parameters.

    If a client has already been created with these parameters, it will be
    retrieved from cache and returned.

    Args:
        api_key: API key for authentication. If None, uses ANTHROPIC_API_KEY env var.
        base_url: Base URL for the API. If None, uses ANTHROPIC_BASE_URL env var.

    Returns:
        An Anthropic client instance.
    """
    api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
    base_url = base_url or os.getenv("ANTHROPIC_BASE_URL")
    return _anthropic_singleton(api_key, base_url)


def get_client() -> "AnthropicClient":
    """Retrieve the current Anthropic client from context, or a global default.

    Returns:
        The current Anthropic client from context if available, otherwise
        a global default client based on environment variables.
    """
    ctx_client = ANTHROPIC_CLIENT_CONTEXT.get()
    return ctx_client or client()


class AnthropicClient(BaseClient[AnthropicModelId, Anthropic]):
    """The client for the Anthropic LLM model."""

    @property
    def _context_var(self) -> ContextVar["AnthropicClient | None"]:
        return ANTHROPIC_CLIENT_CONTEXT

    def __init__(
        self, *, api_key: str | None = None, base_url: str | None = None
    ) -> None:
        """Initialize the Anthropic client."""
        self.client = Anthropic(api_key=api_key, base_url=base_url)
        self.async_client = AsyncAnthropic(api_key=api_key, base_url=base_url)

    @overload
    def call(
        self,
        *,
        model_id: AnthropicModelId,
        messages: Sequence[Message],
        tools: Sequence[Tool] | None = None,
        format: None = None,
        **params: Unpack[Params],
    ) -> Response: ...

    @overload
    def call(
        self,
        *,
        model_id: AnthropicModelId,
        messages: Sequence[Message],
        tools: Sequence[Tool] | None = None,
        format: type[FormattableT] | Format[FormattableT],
        **params: Unpack[Params],
    ) -> Response[FormattableT]: ...

    @overload
    def call(
        self,
        *,
        model_id: AnthropicModelId,
        messages: Sequence[Message],
        tools: Sequence[Tool] | None = None,
        format: type[FormattableT] | Format[FormattableT] | None,
        **params: Unpack[Params],
    ) -> Response | Response[FormattableT]: ...

    def call(
        self,
        *,
        model_id: AnthropicModelId,
        messages: Sequence[Message],
        tools: Sequence[Tool] | None = None,
        format: type[FormattableT] | Format[FormattableT] | None = None,
        **params: Unpack[Params],
    ) -> Response | Response[FormattableT]:
        """Make a call to the Anthropic API."""
        input_messages, format, kwargs = _utils.prepare_anthropic_request(
            model_id=model_id,
            messages=messages,
            tools=tools,
            format=format,
            params=params,
        )

        anthropic_response = self.client.messages.create(**kwargs)

        assistant_message, finish_reason = _utils.decode_response(anthropic_response)

        return Response(
            raw=anthropic_response,
            provider="anthropic",
            model_id=model_id,
            params=params,
            tools=tools,
            input_messages=input_messages,
            assistant_message=assistant_message,
            finish_reason=finish_reason,
            format=format,
        )

    @overload
    def context_call(
        self,
        *,
        ctx: Context[DepsT],
        model_id: AnthropicModelId,
        messages: Sequence[Message],
        tools: Sequence[Tool | ContextTool[DepsT]] | None = None,
        format: None = None,
        **params: Unpack[Params],
    ) -> ContextResponse[DepsT, None]: ...

    @overload
    def context_call(
        self,
        *,
        ctx: Context[DepsT],
        model_id: AnthropicModelId,
        messages: Sequence[Message],
        tools: Sequence[Tool | ContextTool[DepsT]] | None = None,
        format: type[FormattableT] | Format[FormattableT],
        **params: Unpack[Params],
    ) -> ContextResponse[DepsT, FormattableT]: ...

    @overload
    def context_call(
        self,
        *,
        ctx: Context[DepsT],
        model_id: AnthropicModelId,
        messages: Sequence[Message],
        tools: Sequence[Tool | ContextTool[DepsT]] | None = None,
        format: type[FormattableT] | Format[FormattableT] | None,
        **params: Unpack[Params],
    ) -> ContextResponse[DepsT, None] | ContextResponse[DepsT, FormattableT]: ...

    def context_call(
        self,
        *,
        ctx: Context[DepsT],
        model_id: AnthropicModelId,
        messages: Sequence[Message],
        tools: Sequence[Tool | ContextTool[DepsT]] | None = None,
        format: type[FormattableT] | Format[FormattableT] | None = None,
        **params: Unpack[Params],
    ) -> ContextResponse[DepsT, None] | ContextResponse[DepsT, FormattableT]:
        """Make a call to the Anthropic API."""
        input_messages, format, kwargs = _utils.prepare_anthropic_request(
            model_id=model_id,
            messages=messages,
            tools=tools,
            format=format,
            params=params,
        )

        anthropic_response = self.client.messages.create(**kwargs)

        assistant_message, finish_reason = _utils.decode_response(anthropic_response)

        return ContextResponse(
            raw=anthropic_response,
            provider="anthropic",
            model_id=model_id,
            params=params,
            tools=tools,
            input_messages=input_messages,
            assistant_message=assistant_message,
            finish_reason=finish_reason,
            format=format,
        )

    @overload
    async def call_async(
        self,
        *,
        model_id: AnthropicModelId,
        messages: Sequence[Message],
        tools: Sequence[AsyncTool] | None = None,
        format: None = None,
        **params: Unpack[Params],
    ) -> AsyncResponse: ...

    @overload
    async def call_async(
        self,
        *,
        model_id: AnthropicModelId,
        messages: Sequence[Message],
        tools: Sequence[AsyncTool] | None = None,
        format: type[FormattableT] | Format[FormattableT],
        **params: Unpack[Params],
    ) -> AsyncResponse[FormattableT]: ...

    @overload
    async def call_async(
        self,
        *,
        model_id: AnthropicModelId,
        messages: Sequence[Message],
        tools: Sequence[AsyncTool] | None = None,
        format: type[FormattableT] | Format[FormattableT] | None,
        **params: Unpack[Params],
    ) -> AsyncResponse | AsyncResponse[FormattableT]: ...

    async def call_async(
        self,
        *,
        model_id: AnthropicModelId,
        messages: Sequence[Message],
        tools: Sequence[AsyncTool] | None = None,
        format: type[FormattableT] | Format[FormattableT] | None = None,
        **params: Unpack[Params],
    ) -> AsyncResponse | AsyncResponse[FormattableT]:
        """Make an async call to the Anthropic API."""
        input_messages, format, kwargs = _utils.prepare_anthropic_request(
            model_id=model_id,
            messages=messages,
            tools=tools,
            format=format,
            params=params,
        )

        anthropic_response = await self.async_client.messages.create(**kwargs)

        assistant_message, finish_reason = _utils.decode_response(anthropic_response)

        return AsyncResponse(
            raw=anthropic_response,
            provider="anthropic",
            model_id=model_id,
            params=params,
            tools=tools,
            input_messages=input_messages,
            assistant_message=assistant_message,
            finish_reason=finish_reason,
            format=format,
        )

    @overload
    async def context_call_async(
        self,
        *,
        ctx: Context[DepsT],
        model_id: AnthropicModelId,
        messages: Sequence[Message],
        tools: Sequence[AsyncTool | AsyncContextTool[DepsT]] | None = None,
        format: None = None,
        **params: Unpack[Params],
    ) -> AsyncContextResponse[DepsT, None]: ...

    @overload
    async def context_call_async(
        self,
        *,
        ctx: Context[DepsT],
        model_id: AnthropicModelId,
        messages: Sequence[Message],
        tools: Sequence[AsyncTool | AsyncContextTool[DepsT]] | None = None,
        format: type[FormattableT] | Format[FormattableT],
        **params: Unpack[Params],
    ) -> AsyncContextResponse[DepsT, FormattableT]: ...

    @overload
    async def context_call_async(
        self,
        *,
        ctx: Context[DepsT],
        model_id: AnthropicModelId,
        messages: Sequence[Message],
        tools: Sequence[AsyncTool | AsyncContextTool[DepsT]] | None = None,
        format: type[FormattableT] | Format[FormattableT] | None,
        **params: Unpack[Params],
    ) -> (
        AsyncContextResponse[DepsT, None] | AsyncContextResponse[DepsT, FormattableT]
    ): ...

    async def context_call_async(
        self,
        *,
        ctx: Context[DepsT],
        model_id: AnthropicModelId,
        messages: Sequence[Message],
        tools: Sequence[AsyncTool | AsyncContextTool[DepsT]] | None = None,
        format: type[FormattableT] | Format[FormattableT] | None = None,
        **params: Unpack[Params],
    ) -> AsyncContextResponse[DepsT, None] | AsyncContextResponse[DepsT, FormattableT]:
        """Make an async call to the Anthropic API."""
        input_messages, format, kwargs = _utils.prepare_anthropic_request(
            model_id=model_id,
            messages=messages,
            tools=tools,
            format=format,
            params=params,
        )

        anthropic_response = await self.async_client.messages.create(**kwargs)

        assistant_message, finish_reason = _utils.decode_response(anthropic_response)

        return AsyncContextResponse(
            raw=anthropic_response,
            provider="anthropic",
            model_id=model_id,
            params=params,
            tools=tools,
            input_messages=input_messages,
            assistant_message=assistant_message,
            finish_reason=finish_reason,
            format=format,
        )

    @overload
    def stream(
        self,
        *,
        model_id: AnthropicModelId,
        messages: Sequence[Message],
        tools: Sequence[Tool] | None = None,
        format: None = None,
        **params: Unpack[Params],
    ) -> StreamResponse: ...

    @overload
    def stream(
        self,
        *,
        model_id: AnthropicModelId,
        messages: Sequence[Message],
        tools: Sequence[Tool] | None = None,
        format: type[FormattableT] | Format[FormattableT],
        **params: Unpack[Params],
    ) -> StreamResponse[FormattableT]: ...

    @overload
    def stream(
        self,
        *,
        model_id: AnthropicModelId,
        messages: Sequence[Message],
        tools: Sequence[Tool] | None = None,
        format: type[FormattableT] | Format[FormattableT] | None,
        **params: Unpack[Params],
    ) -> StreamResponse | StreamResponse[FormattableT]: ...

    def stream(
        self,
        *,
        model_id: AnthropicModelId,
        messages: Sequence[Message],
        tools: Sequence[Tool] | None = None,
        format: type[FormattableT] | Format[FormattableT] | None = None,
        **params: Unpack[Params],
    ) -> StreamResponse | StreamResponse[FormattableT]:
        """Make a streaming call to the Anthropic API."""
        input_messages, format, kwargs = _utils.prepare_anthropic_request(
            model_id=model_id,
            messages=messages,
            tools=tools,
            format=format,
            params=params,
        )

        anthropic_stream = self.client.messages.stream(**kwargs)

        chunk_iterator = _utils.convert_anthropic_stream_to_chunk_iterator(
            anthropic_stream
        )

        return StreamResponse(
            provider="anthropic",
            model_id=model_id,
            params=params,
            tools=tools,
            input_messages=input_messages,
            chunk_iterator=chunk_iterator,
            format=format,
        )

    @overload
    def context_stream(
        self,
        *,
        ctx: Context[DepsT],
        model_id: AnthropicModelId,
        messages: Sequence[Message],
        tools: Sequence[Tool | ContextTool[DepsT]] | None = None,
        format: None = None,
        **params: Unpack[Params],
    ) -> ContextStreamResponse[DepsT]: ...

    @overload
    def context_stream(
        self,
        *,
        ctx: Context[DepsT],
        model_id: AnthropicModelId,
        messages: Sequence[Message],
        tools: Sequence[Tool | ContextTool[DepsT]] | None = None,
        format: type[FormattableT] | Format[FormattableT],
        **params: Unpack[Params],
    ) -> ContextStreamResponse[DepsT, FormattableT]: ...

    @overload
    def context_stream(
        self,
        *,
        ctx: Context[DepsT],
        model_id: AnthropicModelId,
        messages: Sequence[Message],
        tools: Sequence[Tool | ContextTool[DepsT]] | None = None,
        format: type[FormattableT] | Format[FormattableT] | None,
        **params: Unpack[Params],
    ) -> ContextStreamResponse[DepsT] | ContextStreamResponse[DepsT, FormattableT]: ...

    def context_stream(
        self,
        *,
        ctx: Context[DepsT],
        model_id: AnthropicModelId,
        messages: Sequence[Message],
        tools: Sequence[Tool | ContextTool[DepsT]] | None = None,
        format: type[FormattableT] | Format[FormattableT] | None = None,
        **params: Unpack[Params],
    ) -> ContextStreamResponse[DepsT] | ContextStreamResponse[DepsT, FormattableT]:
        """Make a streaming call to the Anthropic API."""
        input_messages, format, kwargs = _utils.prepare_anthropic_request(
            model_id=model_id,
            messages=messages,
            tools=tools,
            format=format,
            params=params,
        )

        anthropic_stream = self.client.messages.stream(**kwargs)

        chunk_iterator = _utils.convert_anthropic_stream_to_chunk_iterator(
            anthropic_stream
        )

        return ContextStreamResponse(
            provider="anthropic",
            model_id=model_id,
            params=params,
            tools=tools,
            input_messages=input_messages,
            chunk_iterator=chunk_iterator,
            format=format,
        )

    @overload
    async def stream_async(
        self,
        *,
        model_id: AnthropicModelId,
        messages: Sequence[Message],
        tools: Sequence[AsyncTool] | None = None,
        format: None = None,
        **params: Unpack[Params],
    ) -> AsyncStreamResponse: ...

    @overload
    async def stream_async(
        self,
        *,
        model_id: AnthropicModelId,
        messages: Sequence[Message],
        tools: Sequence[AsyncTool] | None = None,
        format: type[FormattableT] | Format[FormattableT],
        **params: Unpack[Params],
    ) -> AsyncStreamResponse[FormattableT]: ...

    @overload
    async def stream_async(
        self,
        *,
        model_id: AnthropicModelId,
        messages: Sequence[Message],
        tools: Sequence[AsyncTool] | None = None,
        format: type[FormattableT] | Format[FormattableT] | None,
        **params: Unpack[Params],
    ) -> AsyncStreamResponse | AsyncStreamResponse[FormattableT]: ...

    async def stream_async(
        self,
        *,
        model_id: AnthropicModelId,
        messages: Sequence[Message],
        tools: Sequence[AsyncTool] | None = None,
        format: type[FormattableT] | Format[FormattableT] | None = None,
        **params: Unpack[Params],
    ) -> AsyncStreamResponse | AsyncStreamResponse[FormattableT]:
        """Make an async streaming call to the Anthropic API."""
        input_messages, format, kwargs = _utils.prepare_anthropic_request(
            model_id=model_id,
            messages=messages,
            tools=tools,
            format=format,
            params=params,
        )

        anthropic_stream = self.async_client.messages.stream(**kwargs)

        chunk_iterator = _utils.convert_anthropic_stream_to_async_chunk_iterator(
            anthropic_stream
        )

        return AsyncStreamResponse(
            provider="anthropic",
            model_id=model_id,
            params=params,
            tools=tools,
            input_messages=input_messages,
            chunk_iterator=chunk_iterator,
            format=format,
        )

    @overload
    async def context_stream_async(
        self,
        *,
        ctx: Context[DepsT],
        model_id: AnthropicModelId,
        messages: Sequence[Message],
        tools: Sequence[AsyncTool | AsyncContextTool[DepsT]] | None = None,
        format: None = None,
        **params: Unpack[Params],
    ) -> AsyncContextStreamResponse[DepsT]: ...

    @overload
    async def context_stream_async(
        self,
        *,
        ctx: Context[DepsT],
        model_id: AnthropicModelId,
        messages: Sequence[Message],
        tools: Sequence[AsyncTool | AsyncContextTool[DepsT]] | None = None,
        format: type[FormattableT] | Format[FormattableT],
        **params: Unpack[Params],
    ) -> AsyncContextStreamResponse[DepsT, FormattableT]: ...

    @overload
    async def context_stream_async(
        self,
        *,
        ctx: Context[DepsT],
        model_id: AnthropicModelId,
        messages: Sequence[Message],
        tools: Sequence[AsyncTool | AsyncContextTool[DepsT]] | None = None,
        format: type[FormattableT] | Format[FormattableT] | None,
        **params: Unpack[Params],
    ) -> (
        AsyncContextStreamResponse | AsyncContextStreamResponse[DepsT, FormattableT]
    ): ...

    async def context_stream_async(
        self,
        *,
        ctx: Context[DepsT],
        model_id: AnthropicModelId,
        messages: Sequence[Message],
        tools: Sequence[AsyncTool | AsyncContextTool[DepsT]] | None = None,
        format: type[FormattableT] | Format[FormattableT] | None = None,
        **params: Unpack[Params],
    ) -> AsyncContextStreamResponse | AsyncContextStreamResponse[DepsT, FormattableT]:
        """Make an async streaming call to the Anthropic API."""
        input_messages, format, kwargs = _utils.prepare_anthropic_request(
            model_id=model_id,
            messages=messages,
            tools=tools,
            format=format,
            params=params,
        )

        anthropic_stream = self.async_client.messages.stream(**kwargs)

        chunk_iterator = _utils.convert_anthropic_stream_to_async_chunk_iterator(
            anthropic_stream
        )

        return AsyncContextStreamResponse(
            provider="anthropic",
            model_id=model_id,
            params=params,
            tools=tools,
            input_messages=input_messages,
            chunk_iterator=chunk_iterator,
            format=format,
        )
