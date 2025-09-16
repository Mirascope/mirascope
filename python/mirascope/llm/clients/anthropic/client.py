"""Anthropic client implementation."""

import os
from collections.abc import Sequence
from typing import cast, overload

import httpx
from anthropic import Anthropic, AsyncAnthropic

from ...context import Context, DepsT
from ...formatting import FormatT
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

    @overload
    def call(
        self,
        *,
        ctx: Context[DepsT],
        model_id: AnthropicModelId,
        messages: Sequence[Message],
        tools: Sequence[Tool | ContextTool[DepsT]] | None = None,
        format: None = None,
        params: AnthropicParams | None = None,
    ) -> ContextResponse[DepsT]: ...

    @overload
    def call(
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
    def call(
        self,
        *,
        ctx: Context[DepsT],
        model_id: AnthropicModelId,
        messages: Sequence[Message],
        tools: Sequence[Tool | ContextTool[DepsT]] | None = None,
        format: type[FormatT] | None,
        params: AnthropicParams | None = None,
    ) -> ContextResponse[DepsT] | ContextResponse[DepsT, FormatT]: ...

    def call(
        self,
        *,
        ctx: Context[DepsT] | None = None,
        model_id: AnthropicModelId,
        messages: Sequence[Message],
        tools: Sequence[Tool] | Sequence[Tool | ContextTool[DepsT]] | None = None,
        format: type[FormatT] | None = None,
        params: AnthropicParams | None = None,
    ) -> (
        Response
        | Response[FormatT]
        | ContextResponse[DepsT]
        | ContextResponse[DepsT, FormatT]
    ):
        """Make a call to the Anthropic API."""
        input_messages, kwargs = _utils.prepare_anthropic_request(
            model_id=model_id,
            messages=messages,
            tools=tools,
            format=format,
            params=params,
        )

        anthropic_response = self.client.messages.create(**kwargs)

        assistant_message, finish_reason = _utils.decode_response(anthropic_response)

        if ctx is not None:
            return ContextResponse(
                raw=anthropic_response,
                provider="anthropic",
                model_id=model_id,
                params=params,
                tools=tools,
                input_messages=input_messages,
                assistant_message=assistant_message,
                finish_reason=finish_reason,
                format_type=format,
            )
        else:
            tools = cast(Sequence[Tool] | None, tools)
            return Response(
                raw=anthropic_response,
                provider="anthropic",
                model_id=model_id,
                params=params,
                tools=tools,
                input_messages=input_messages,
                assistant_message=assistant_message,
                finish_reason=finish_reason,
                format_type=format,
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

    @overload
    async def call_async(
        self,
        *,
        ctx: Context[DepsT],
        model_id: AnthropicModelId,
        messages: Sequence[Message],
        tools: Sequence[AsyncTool | AsyncContextTool[DepsT]] | None = None,
        format: None = None,
        params: AnthropicParams | None = None,
    ) -> AsyncContextResponse[DepsT]: ...

    @overload
    async def call_async(
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
    async def call_async(
        self,
        *,
        ctx: Context[DepsT],
        model_id: AnthropicModelId,
        messages: Sequence[Message],
        tools: Sequence[AsyncTool | AsyncContextTool[DepsT]] | None = None,
        format: type[FormatT] | None,
        params: AnthropicParams | None = None,
    ) -> AsyncContextResponse[DepsT] | AsyncContextResponse[DepsT, FormatT]: ...

    async def call_async(
        self,
        *,
        ctx: Context[DepsT] | None = None,
        model_id: AnthropicModelId,
        messages: Sequence[Message],
        tools: Sequence[AsyncTool]
        | Sequence[AsyncTool | AsyncContextTool[DepsT]]
        | None = None,
        format: type[FormatT] | None = None,
        params: AnthropicParams | None = None,
    ) -> (
        AsyncResponse
        | AsyncResponse[FormatT]
        | AsyncContextResponse[DepsT]
        | AsyncContextResponse[DepsT, FormatT]
    ):
        """Make an async call to the Anthropic API."""
        input_messages, kwargs = _utils.prepare_anthropic_request(
            model_id=model_id,
            messages=messages,
            tools=tools,
            format=format,
            params=params,
        )

        anthropic_response = await self.async_client.messages.create(**kwargs)

        assistant_message, finish_reason = _utils.decode_response(anthropic_response)

        if ctx is not None:
            return AsyncContextResponse(
                raw=anthropic_response,
                provider="anthropic",
                model_id=model_id,
                params=params,
                tools=tools,
                input_messages=input_messages,
                assistant_message=assistant_message,
                finish_reason=finish_reason,
                format_type=format,
            )
        else:
            tools = cast(Sequence[AsyncTool] | None, tools)
            return AsyncResponse(
                raw=anthropic_response,
                provider="anthropic",
                model_id=model_id,
                params=params,
                tools=tools,
                input_messages=input_messages,
                assistant_message=assistant_message,
                finish_reason=finish_reason,
                format_type=format,
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

    @overload
    def stream(
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
    def stream(
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
    def stream(
        self,
        *,
        ctx: Context[DepsT],
        model_id: AnthropicModelId,
        messages: Sequence[Message],
        tools: Sequence[Tool | ContextTool[DepsT]] | None = None,
        format: type[FormatT] | None,
        params: AnthropicParams | None = None,
    ) -> ContextStreamResponse[DepsT] | ContextStreamResponse[DepsT, FormatT]: ...

    def stream(
        self,
        *,
        ctx: Context[DepsT] | None = None,
        model_id: AnthropicModelId,
        messages: Sequence[Message],
        tools: Sequence[Tool] | Sequence[Tool | ContextTool[DepsT]] | None = None,
        format: type[FormatT] | None = None,
        params: AnthropicParams | None = None,
    ) -> (
        StreamResponse
        | StreamResponse[FormatT]
        | ContextStreamResponse[DepsT]
        | ContextStreamResponse[DepsT, FormatT]
    ):
        """Make a streaming call to the Anthropic API."""
        input_messages, kwargs = _utils.prepare_anthropic_request(
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

        if ctx is not None:
            return ContextStreamResponse(
                provider="anthropic",
                model_id=model_id,
                params=params,
                tools=tools,
                input_messages=input_messages,
                chunk_iterator=chunk_iterator,
                format_type=format,
            )
        else:
            tools = cast(Sequence[Tool] | None, tools)
            return StreamResponse(
                provider="anthropic",
                model_id=model_id,
                params=params,
                tools=tools,
                input_messages=input_messages,
                chunk_iterator=chunk_iterator,
                format_type=format,
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

    @overload
    async def stream_async(
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
    async def stream_async(
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
    async def stream_async(
        self,
        *,
        ctx: Context[DepsT],
        model_id: AnthropicModelId,
        messages: Sequence[Message],
        tools: Sequence[AsyncTool | AsyncContextTool[DepsT]] | None = None,
        format: type[FormatT] | None,
        params: AnthropicParams | None = None,
    ) -> (
        AsyncContextStreamResponse[DepsT] | AsyncContextStreamResponse[DepsT, FormatT]
    ): ...

    async def stream_async(
        self,
        *,
        ctx: Context[DepsT] | None = None,
        model_id: AnthropicModelId,
        messages: Sequence[Message],
        tools: Sequence[AsyncTool]
        | Sequence[AsyncTool | AsyncContextTool[DepsT]]
        | None = None,
        format: type[FormatT] | None = None,
        params: AnthropicParams | None = None,
    ) -> (
        AsyncStreamResponse
        | AsyncStreamResponse[FormatT]
        | AsyncContextStreamResponse[DepsT]
        | AsyncContextStreamResponse[DepsT, FormatT]
    ):
        """Make an async streaming call to the Anthropic API."""
        input_messages, kwargs = _utils.prepare_anthropic_request(
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

        if ctx is not None:
            return AsyncContextStreamResponse(
                provider="anthropic",
                model_id=model_id,
                params=params,
                tools=tools,
                input_messages=input_messages,
                chunk_iterator=chunk_iterator,
                format_type=format,
            )
        else:
            tools = cast(Sequence[AsyncTool] | None, tools)
            return AsyncStreamResponse(
                provider="anthropic",
                model_id=model_id,
                params=params,
                tools=tools,
                input_messages=input_messages,
                chunk_iterator=chunk_iterator,
                format_type=format,
            )
