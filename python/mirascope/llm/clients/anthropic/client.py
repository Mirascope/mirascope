"""Anthropic client implementation."""

import os
from collections.abc import Sequence
from typing import overload

import httpx
from anthropic import Anthropic, AsyncAnthropic

from ...context import Context, DepsT
from ...formatting import FormatT
from ...messages import Message
from ...responses import (
    AsyncChunkIterator,
    AsyncContextResponse,
    AsyncContextStreamResponse,
    AsyncResponse,
    AsyncStreamResponse,
    ChunkIterator,
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
from ..base._utils import CallResult, StreamResult
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

    def _make_call(
        self,
        *,
        model_id: AnthropicModelId,
        messages: Sequence[Message],
        tools: Sequence[Tool | ContextTool] | None = None,
        format: type[FormatT] | None = None,
        params: AnthropicParams | None = None,
    ) -> CallResult[None] | CallResult[FormatT]:
        """Core logic for making a call to the Anthropic API."""
        if params:
            raise NotImplementedError("param use not yet supported")

        input_messages, kwargs = _utils.prepare_anthropic_request(
            model_id=model_id, messages=messages, tools=tools, format=format
        )

        anthropic_response = self.client.messages.create(**kwargs)

        assistant_message, finish_reason = _utils.decode_response(anthropic_response)

        return CallResult(
            raw=anthropic_response,
            provider="anthropic",
            model_id=model_id,
            params=params,
            format_type=format,
            input_messages=input_messages,
            assistant_message=assistant_message,
            finish_reason=finish_reason,
        )

    async def _make_call_async(
        self,
        *,
        model_id: AnthropicModelId,
        messages: Sequence[Message],
        tools: Sequence[AsyncTool | AsyncContextTool] | None = None,
        format: type[FormatT] | None = None,
        params: AnthropicParams | None = None,
    ) -> CallResult[None] | CallResult[FormatT]:
        """Core logic for making an async call to the Anthropic API."""
        if params:
            raise NotImplementedError("param use not yet supported")

        input_messages, kwargs = _utils.prepare_anthropic_request(
            model_id=model_id,
            messages=messages,
            tools=tools,
            format=format,
        )

        anthropic_response = await self.async_client.messages.create(**kwargs)

        assistant_message, finish_reason = _utils.decode_response(anthropic_response)

        return CallResult(
            raw=anthropic_response,
            provider="anthropic",
            model_id=model_id,
            params=params,
            format_type=format,
            input_messages=input_messages,
            assistant_message=assistant_message,
            finish_reason=finish_reason,
        )

    def _make_stream(
        self,
        *,
        model_id: AnthropicModelId,
        messages: Sequence[Message],
        tools: Sequence[Tool | ContextTool] | None = None,
        format: type[FormatT] | None = None,
        params: AnthropicParams | None = None,
    ) -> StreamResult[ChunkIterator, None] | StreamResult[ChunkIterator, FormatT]:
        """Core logic for making a streaming call to the Anthropic API."""
        if params:
            raise NotImplementedError("param use not yet supported")

        input_messages, kwargs = _utils.prepare_anthropic_request(
            model_id=model_id, messages=messages, tools=tools, format=format
        )

        anthropic_stream = self.client.messages.stream(**kwargs)

        chunk_iterator = _utils.convert_anthropic_stream_to_chunk_iterator(
            anthropic_stream
        )

        return StreamResult(
            provider="anthropic",
            model_id=model_id,
            input_messages=input_messages,
            format_type=format,
            params=params,
            chunk_iterator=chunk_iterator,
        )

    async def _make_stream_async(
        self,
        *,
        model_id: AnthropicModelId,
        messages: Sequence[Message],
        tools: Sequence[AsyncTool | AsyncContextTool] | None = None,
        format: type[FormatT] | None = None,
        params: AnthropicParams | None = None,
    ) -> (
        StreamResult[AsyncChunkIterator, None]
        | StreamResult[AsyncChunkIterator, FormatT]
    ):
        """Core logic for making an async streaming call to the Anthropic API."""
        if params:
            raise NotImplementedError("param use not yet supported")

        input_messages, kwargs = _utils.prepare_anthropic_request(
            model_id=model_id, messages=messages, tools=tools, format=format
        )

        anthropic_stream = self.async_client.messages.stream(**kwargs)

        chunk_iterator = _utils.convert_anthropic_stream_to_async_chunk_iterator(
            anthropic_stream
        )

        return StreamResult(
            provider="anthropic",
            model_id=model_id,
            input_messages=input_messages,
            format_type=format,
            params=params,
            chunk_iterator=chunk_iterator,
        )

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
        format: type[FormatT],
        params: AnthropicParams | None = None,
    ) -> Response[FormatT]: ...

    @overload
    def call(
        self,
        *,
        model_id: AnthropicModelId,
        messages: Sequence[Message],
        tools: Sequence[Tool] | None = None,
        format: type[FormatT] | None,
        params: AnthropicParams | None = None,
    ) -> Response | Response[FormatT]: ...

    def call(
        self,
        *,
        model_id: AnthropicModelId,
        messages: Sequence[Message],
        tools: Sequence[Tool] | None = None,
        format: type[FormatT] | None = None,
        params: AnthropicParams | None = None,
    ) -> Response | Response[FormatT]:
        """Make a call to the Anthropic API."""
        return self._make_call(
            model_id=model_id,
            messages=messages,
            tools=tools,
            format=format,
            params=params,
        ).to_response(tools=tools)

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
        format: type[FormatT],
        params: AnthropicParams | None = None,
    ) -> ContextResponse[DepsT, FormatT]: ...

    @overload
    def context_call(
        self,
        *,
        ctx: Context[DepsT],
        model_id: AnthropicModelId,
        messages: Sequence[Message],
        tools: Sequence[Tool | ContextTool[DepsT]] | None = None,
        format: type[FormatT] | None,
        params: AnthropicParams | None = None,
    ) -> ContextResponse[DepsT, None] | ContextResponse[DepsT, FormatT]: ...

    def context_call(
        self,
        *,
        ctx: Context[DepsT],
        model_id: AnthropicModelId,
        messages: Sequence[Message],
        tools: Sequence[Tool | ContextTool[DepsT]] | None = None,
        format: type[FormatT] | None = None,
        params: AnthropicParams | None = None,
    ) -> ContextResponse[DepsT, None] | ContextResponse[DepsT, FormatT]:
        return self._make_call(
            model_id=model_id,
            messages=messages,
            tools=tools,
            format=format,
            params=params,
        ).to_context_response(ctx=ctx, tools=tools)

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
        format: type[FormatT],
        params: AnthropicParams | None = None,
    ) -> AsyncResponse[FormatT]: ...

    @overload
    async def call_async(
        self,
        *,
        model_id: AnthropicModelId,
        messages: Sequence[Message],
        tools: Sequence[AsyncTool] | None = None,
        format: type[FormatT] | None,
        params: AnthropicParams | None = None,
    ) -> AsyncResponse | AsyncResponse[FormatT]: ...

    async def call_async(
        self,
        *,
        model_id: AnthropicModelId,
        messages: Sequence[Message],
        tools: Sequence[AsyncTool] | None = None,
        format: type[FormatT] | None = None,
        params: AnthropicParams | None = None,
    ) -> AsyncResponse | AsyncResponse[FormatT]:
        """Make an async call to the Anthropic API."""
        result = await self._make_call_async(
            model_id=model_id,
            messages=messages,
            tools=tools,
            format=format,
            params=params,
        )
        return result.to_async_response(tools=tools)

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
        format: type[FormatT],
        params: AnthropicParams | None = None,
    ) -> AsyncContextResponse[DepsT, FormatT]: ...

    @overload
    async def context_call_async(
        self,
        *,
        ctx: Context[DepsT],
        model_id: AnthropicModelId,
        messages: Sequence[Message],
        tools: Sequence[AsyncTool | AsyncContextTool[DepsT]] | None = None,
        format: type[FormatT] | None,
        params: AnthropicParams | None = None,
    ) -> AsyncContextResponse[DepsT, None] | AsyncContextResponse[DepsT, FormatT]: ...

    async def context_call_async(
        self,
        *,
        ctx: Context[DepsT],
        model_id: AnthropicModelId,
        messages: Sequence[Message],
        tools: Sequence[AsyncTool | AsyncContextTool[DepsT]] | None = None,
        format: type[FormatT] | None = None,
        params: AnthropicParams | None = None,
    ) -> AsyncContextResponse[DepsT, None] | AsyncContextResponse[DepsT, FormatT]:
        result = await self._make_call_async(
            model_id=model_id,
            messages=messages,
            tools=tools,
            format=format,
            params=params,
        )
        return result.to_async_context_response(ctx=ctx, tools=tools)

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
        format: type[FormatT],
        params: AnthropicParams | None = None,
    ) -> StreamResponse[FormatT]: ...

    @overload
    def stream(
        self,
        *,
        model_id: AnthropicModelId,
        messages: Sequence[Message],
        tools: Sequence[Tool] | None = None,
        format: type[FormatT] | None,
        params: AnthropicParams | None = None,
    ) -> StreamResponse | StreamResponse[FormatT]: ...

    def stream(
        self,
        *,
        model_id: AnthropicModelId,
        messages: Sequence[Message],
        tools: Sequence[Tool] | None = None,
        format: type[FormatT] | None = None,
        params: AnthropicParams | None = None,
    ) -> StreamResponse | StreamResponse[FormatT]:
        """Make a streaming call to the Anthropic API."""
        result = self._make_stream(
            model_id=model_id,
            messages=messages,
            tools=tools,
            format=format,
            params=params,
        )
        return result.to_stream_response(tools=tools)

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
    ) -> ContextStreamResponse[DepsT, None]: ...

    @overload
    def context_stream(
        self,
        *,
        ctx: Context[DepsT],
        model_id: AnthropicModelId,
        messages: Sequence[Message],
        tools: Sequence[Tool | ContextTool[DepsT]] | None = None,
        format: type[FormatT],
        params: AnthropicParams | None = None,
    ) -> ContextStreamResponse[DepsT, FormatT]: ...

    @overload
    def context_stream(
        self,
        *,
        ctx: Context[DepsT],
        model_id: AnthropicModelId,
        messages: Sequence[Message],
        tools: Sequence[Tool | ContextTool[DepsT]] | None = None,
        format: type[FormatT] | None,
        params: AnthropicParams | None = None,
    ) -> ContextStreamResponse[DepsT, None] | ContextStreamResponse[DepsT, FormatT]: ...

    def context_stream(
        self,
        *,
        ctx: Context[DepsT],
        model_id: AnthropicModelId,
        messages: Sequence[Message],
        tools: Sequence[Tool | ContextTool[DepsT]] | None = None,
        format: type[FormatT] | None = None,
        params: AnthropicParams | None = None,
    ) -> ContextStreamResponse[DepsT, None] | ContextStreamResponse[DepsT, FormatT]:
        result = self._make_stream(
            model_id=model_id,
            messages=messages,
            tools=tools,
            format=format,
            params=params,
        )
        return result.to_context_stream_response(ctx=ctx, tools=tools)

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
        format: type[FormatT],
        params: AnthropicParams | None = None,
    ) -> AsyncStreamResponse[FormatT]: ...

    @overload
    async def stream_async(
        self,
        *,
        model_id: AnthropicModelId,
        messages: Sequence[Message],
        tools: Sequence[AsyncTool] | None = None,
        format: type[FormatT] | None,
        params: AnthropicParams | None = None,
    ) -> AsyncStreamResponse | AsyncStreamResponse[FormatT]: ...

    async def stream_async(
        self,
        *,
        model_id: AnthropicModelId,
        messages: Sequence[Message],
        tools: Sequence[AsyncTool] | None = None,
        format: type[FormatT] | None = None,
        params: AnthropicParams | None = None,
    ) -> AsyncStreamResponse | AsyncStreamResponse[FormatT]:
        """Make an async streaming call to the Anthropic API."""
        result = await self._make_stream_async(
            model_id=model_id,
            messages=messages,
            tools=tools,
            format=format,
            params=params,
        )
        return result.to_async_stream_response(tools=tools)

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
    ) -> AsyncContextStreamResponse[DepsT, None]: ...

    @overload
    async def context_stream_async(
        self,
        *,
        ctx: Context[DepsT],
        model_id: AnthropicModelId,
        messages: Sequence[Message],
        tools: Sequence[AsyncTool | AsyncContextTool[DepsT]] | None = None,
        format: type[FormatT],
        params: AnthropicParams | None = None,
    ) -> AsyncContextStreamResponse[DepsT, FormatT]: ...

    @overload
    async def context_stream_async(
        self,
        *,
        ctx: Context[DepsT],
        model_id: AnthropicModelId,
        messages: Sequence[Message],
        tools: Sequence[AsyncTool | AsyncContextTool[DepsT]] | None = None,
        format: type[FormatT] | None,
        params: AnthropicParams | None = None,
    ) -> (
        AsyncContextStreamResponse[DepsT, None]
        | AsyncContextStreamResponse[DepsT, FormatT]
    ): ...

    async def context_stream_async(
        self,
        *,
        ctx: Context[DepsT],
        model_id: AnthropicModelId,
        messages: Sequence[Message],
        tools: Sequence[AsyncTool | AsyncContextTool[DepsT]] | None = None,
        format: type[FormatT] | None = None,
        params: AnthropicParams | None = None,
    ) -> (
        AsyncContextStreamResponse[DepsT, None]
        | AsyncContextStreamResponse[DepsT, FormatT]
    ):
        result = await self._make_stream_async(
            model_id=model_id,
            messages=messages,
            tools=tools,
            format=format,
            params=params,
        )
        return result.to_async_context_stream_response(ctx=ctx, tools=tools)
