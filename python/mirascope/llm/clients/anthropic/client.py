"""Anthropic client implementation."""

import os
from collections.abc import Sequence
from typing import overload

import httpx
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
from ..base import BaseClient
from . import _utils
from .model_ids import AnthropicModelId
from .params import AnthropicParams

_global_client: "AnthropicClient | None" = None


def get_anthropic_client() -> "AnthropicClient":
    """Get a global Anthropic client instance.

    Returns:
        An Anthropic client instance. Multiple calls return the same instance.
    """
    global _global_client
    if _global_client is None:
        api_key = os.getenv("ANTHROPIC_API_KEY")
        _global_client = AnthropicClient(api_key=api_key)
    return _global_client


class AnthropicClient(BaseClient[AnthropicParams, AnthropicModelId, Anthropic]):
    """The client for the Anthropic LLM model."""

    def __init__(
        self, *, api_key: str | None = None, base_url: str | httpx.URL | None = None
    ) -> None:
        """Initialize the AnthropicClient with optional API key.

        If api_key is not set, Anthropic will look for it in env as "ANTHROPIC_API_KEY".
        """
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
        params: AnthropicParams | None = None,
    ) -> Response: ...

    @overload
    def call(
        self,
        *,
        model_id: AnthropicModelId,
        messages: Sequence[Message],
        tools: Sequence[Tool] | None = None,
        format: type[FormattableT] | Format[FormattableT],
        params: AnthropicParams | None = None,
    ) -> Response[FormattableT]: ...

    @overload
    def call(
        self,
        *,
        model_id: AnthropicModelId,
        messages: Sequence[Message],
        tools: Sequence[Tool] | None = None,
        format: type[FormattableT] | Format[FormattableT] | None,
        params: AnthropicParams | None = None,
    ) -> Response | Response[FormattableT]: ...

    def call(
        self,
        *,
        model_id: AnthropicModelId,
        messages: Sequence[Message],
        tools: Sequence[Tool] | None = None,
        format: type[FormattableT] | Format[FormattableT] | None = None,
        params: AnthropicParams | None = None,
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
        params: AnthropicParams | None = None,
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
        params: AnthropicParams | None = None,
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
        params: AnthropicParams | None = None,
    ) -> ContextResponse[DepsT, None] | ContextResponse[DepsT, FormattableT]: ...

    def context_call(
        self,
        *,
        ctx: Context[DepsT],
        model_id: AnthropicModelId,
        messages: Sequence[Message],
        tools: Sequence[Tool | ContextTool[DepsT]] | None = None,
        format: type[FormattableT] | Format[FormattableT] | None = None,
        params: AnthropicParams | None = None,
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
        params: AnthropicParams | None = None,
    ) -> AsyncResponse: ...

    @overload
    async def call_async(
        self,
        *,
        model_id: AnthropicModelId,
        messages: Sequence[Message],
        tools: Sequence[AsyncTool] | None = None,
        format: type[FormattableT] | Format[FormattableT],
        params: AnthropicParams | None = None,
    ) -> AsyncResponse[FormattableT]: ...

    @overload
    async def call_async(
        self,
        *,
        model_id: AnthropicModelId,
        messages: Sequence[Message],
        tools: Sequence[AsyncTool] | None = None,
        format: type[FormattableT] | Format[FormattableT] | None,
        params: AnthropicParams | None = None,
    ) -> AsyncResponse | AsyncResponse[FormattableT]: ...

    async def call_async(
        self,
        *,
        model_id: AnthropicModelId,
        messages: Sequence[Message],
        tools: Sequence[AsyncTool] | None = None,
        format: type[FormattableT] | Format[FormattableT] | None = None,
        params: AnthropicParams | None = None,
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
        params: AnthropicParams | None = None,
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
        params: AnthropicParams | None = None,
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
        params: AnthropicParams | None = None,
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
        params: AnthropicParams | None = None,
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
        params: AnthropicParams | None = None,
    ) -> StreamResponse: ...

    @overload
    def stream(
        self,
        *,
        model_id: AnthropicModelId,
        messages: Sequence[Message],
        tools: Sequence[Tool] | None = None,
        format: type[FormattableT] | Format[FormattableT],
        params: AnthropicParams | None = None,
    ) -> StreamResponse[FormattableT]: ...

    @overload
    def stream(
        self,
        *,
        model_id: AnthropicModelId,
        messages: Sequence[Message],
        tools: Sequence[Tool] | None = None,
        format: type[FormattableT] | Format[FormattableT] | None,
        params: AnthropicParams | None = None,
    ) -> StreamResponse | StreamResponse[FormattableT]: ...

    def stream(
        self,
        *,
        model_id: AnthropicModelId,
        messages: Sequence[Message],
        tools: Sequence[Tool] | None = None,
        format: type[FormattableT] | Format[FormattableT] | None = None,
        params: AnthropicParams | None = None,
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
        params: AnthropicParams | None = None,
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
        params: AnthropicParams | None = None,
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
        params: AnthropicParams | None = None,
    ) -> ContextStreamResponse[DepsT] | ContextStreamResponse[DepsT, FormattableT]: ...

    def context_stream(
        self,
        *,
        ctx: Context[DepsT],
        model_id: AnthropicModelId,
        messages: Sequence[Message],
        tools: Sequence[Tool | ContextTool[DepsT]] | None = None,
        format: type[FormattableT] | Format[FormattableT] | None = None,
        params: AnthropicParams | None = None,
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
        params: AnthropicParams | None = None,
    ) -> AsyncStreamResponse: ...

    @overload
    async def stream_async(
        self,
        *,
        model_id: AnthropicModelId,
        messages: Sequence[Message],
        tools: Sequence[AsyncTool] | None = None,
        format: type[FormattableT] | Format[FormattableT],
        params: AnthropicParams | None = None,
    ) -> AsyncStreamResponse[FormattableT]: ...

    @overload
    async def stream_async(
        self,
        *,
        model_id: AnthropicModelId,
        messages: Sequence[Message],
        tools: Sequence[AsyncTool] | None = None,
        format: type[FormattableT] | Format[FormattableT] | None,
        params: AnthropicParams | None = None,
    ) -> AsyncStreamResponse | AsyncStreamResponse[FormattableT]: ...

    async def stream_async(
        self,
        *,
        model_id: AnthropicModelId,
        messages: Sequence[Message],
        tools: Sequence[AsyncTool] | None = None,
        format: type[FormattableT] | Format[FormattableT] | None = None,
        params: AnthropicParams | None = None,
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
        params: AnthropicParams | None = None,
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
        params: AnthropicParams | None = None,
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
        params: AnthropicParams | None = None,
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
        params: AnthropicParams | None = None,
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
