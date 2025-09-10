"""Anthropic client implementation."""

import os
from collections.abc import Sequence
from typing import overload

import httpx
from anthropic import Anthropic

from ...context import Context, DepsT
from ...formatting import FormatT
from ...messages import Message
from ...responses import (
    AsyncContextResponse,
    AsyncResponse,
    AsyncStreamResponse,
    ContextResponse,
    Response,
    StreamResponse,
)
from ...tools import AsyncContextTool, AsyncTool, ContextTool, Tool, Toolkit
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
        if params:
            raise NotImplementedError("param use not yet supported")

        input_messages, message_params, system, tool_params, tool_choice = (
            _utils.prepare_anthropic_request(
                model_id=model_id, messages=messages, tools=tools, format=format
            )
        )

        anthropic_response = self.client.messages.create(
            max_tokens=1024,
            model=model_id,
            messages=message_params,
            system=system,
            tools=tool_params,
            tool_choice=tool_choice,
        )

        assistant_message, finish_reason = _utils.decode_response(anthropic_response)

        return Response(
            raw=anthropic_response,
            provider="anthropic",
            model_id=model_id,
            params=params,
            toolkit=Toolkit(tools=tools),
            input_messages=input_messages,
            assistant_message=assistant_message,
            finish_reason=finish_reason,
            format_type=format,
        )

    @overload
    def context_call(
        self,
        *,
        ctx: Context[DepsT],
        model_id: AnthropicModelId,
        messages: Sequence[Message],
        tools: Sequence[Tool | ContextTool[DepsT]],
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
        tools: Sequence[Tool | ContextTool[DepsT]],
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
        tools: Sequence[Tool | ContextTool[DepsT]],
        format: type[FormatT] | None,
        params: AnthropicParams | None = None,
    ) -> ContextResponse[DepsT, None] | ContextResponse[DepsT, FormatT]: ...

    def context_call(
        self,
        *,
        ctx: Context[DepsT],
        model_id: AnthropicModelId,
        messages: Sequence[Message],
        tools: Sequence[Tool | ContextTool[DepsT]],
        format: type[FormatT] | None = None,
        params: AnthropicParams | None = None,
    ) -> ContextResponse[DepsT, None] | ContextResponse[DepsT, FormatT]:
        raise NotImplementedError

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
        raise NotImplementedError

    @overload
    async def context_call_async(
        self,
        *,
        ctx: Context[DepsT],
        model_id: AnthropicModelId,
        messages: Sequence[Message],
        tools: Sequence[AsyncTool | AsyncContextTool[DepsT]],
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
        tools: Sequence[AsyncTool | AsyncContextTool[DepsT]],
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
        tools: Sequence[AsyncTool | AsyncContextTool[DepsT]],
        format: type[FormatT] | None,
        params: AnthropicParams | None = None,
    ) -> AsyncContextResponse[DepsT, None] | AsyncContextResponse[DepsT, FormatT]: ...

    async def context_call_async(
        self,
        *,
        ctx: Context[DepsT],
        model_id: AnthropicModelId,
        messages: Sequence[Message],
        tools: Sequence[AsyncTool | AsyncContextTool[DepsT]],
        format: type[FormatT] | None = None,
        params: AnthropicParams | None = None,
    ) -> AsyncContextResponse[DepsT, None] | AsyncContextResponse[DepsT, FormatT]:
        raise NotImplementedError

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
        if params:
            raise NotImplementedError("param use not yet supported")

        input_messages, message_params, system, tool_params, tool_choice = (
            _utils.prepare_anthropic_request(
                model_id=model_id, messages=messages, tools=tools, format=format
            )
        )

        anthropic_stream = self.client.messages.stream(
            max_tokens=1024,
            model=model_id,
            messages=message_params,
            system=system,
            tools=tool_params,
            tool_choice=tool_choice,
        )

        chunk_iterator = _utils.convert_anthropic_stream_to_chunk_iterator(
            anthropic_stream
        )

        return StreamResponse(
            provider="anthropic",
            model_id=model_id,
            params=params,
            toolkit=Toolkit(tools=tools),
            input_messages=input_messages,
            chunk_iterator=chunk_iterator,
            format_type=format,
        )

    @overload
    def context_stream(
        self,
        *,
        ctx: Context[DepsT],
        model_id: AnthropicModelId,
        messages: Sequence[Message],
        tools: Sequence[Tool | ContextTool[DepsT]],
        format: None = None,
        params: AnthropicParams | None = None,
    ) -> StreamResponse: ...

    @overload
    def context_stream(
        self,
        *,
        ctx: Context[DepsT],
        model_id: AnthropicModelId,
        messages: Sequence[Message],
        tools: Sequence[Tool | ContextTool[DepsT]],
        format: type[FormatT],
        params: AnthropicParams | None = None,
    ) -> StreamResponse[FormatT]: ...

    @overload
    def context_stream(
        self,
        *,
        ctx: Context[DepsT],
        model_id: AnthropicModelId,
        messages: Sequence[Message],
        tools: Sequence[Tool | ContextTool[DepsT]],
        format: type[FormatT] | None,
        params: AnthropicParams | None = None,
    ) -> StreamResponse | StreamResponse[FormatT]: ...

    def context_stream(
        self,
        *,
        ctx: Context[DepsT],
        model_id: AnthropicModelId,
        messages: Sequence[Message],
        tools: Sequence[Tool | ContextTool[DepsT]],
        format: type[FormatT] | None = None,
        params: AnthropicParams | None = None,
    ) -> StreamResponse | StreamResponse[FormatT]:
        raise NotImplementedError

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
        raise NotImplementedError

    @overload
    async def context_stream_async(
        self,
        *,
        ctx: Context[DepsT],
        model_id: AnthropicModelId,
        messages: Sequence[Message],
        tools: Sequence[AsyncTool | AsyncContextTool[DepsT]],
        format: None = None,
        params: AnthropicParams | None = None,
    ) -> AsyncStreamResponse: ...

    @overload
    async def context_stream_async(
        self,
        *,
        ctx: Context[DepsT],
        model_id: AnthropicModelId,
        messages: Sequence[Message],
        tools: Sequence[AsyncTool | AsyncContextTool[DepsT]],
        format: type[FormatT],
        params: AnthropicParams | None = None,
    ) -> AsyncStreamResponse[FormatT]: ...

    @overload
    async def context_stream_async(
        self,
        *,
        ctx: Context[DepsT],
        model_id: AnthropicModelId,
        messages: Sequence[Message],
        tools: Sequence[AsyncTool | AsyncContextTool[DepsT]],
        format: type[FormatT] | None,
        params: AnthropicParams | None = None,
    ) -> AsyncStreamResponse | AsyncStreamResponse[FormatT]: ...

    async def context_stream_async(
        self,
        *,
        ctx: Context[DepsT],
        model_id: AnthropicModelId,
        messages: Sequence[Message],
        tools: Sequence[AsyncTool | AsyncContextTool[DepsT]],
        format: type[FormatT] | None = None,
        params: AnthropicParams | None = None,
    ) -> AsyncStreamResponse | AsyncStreamResponse[FormatT]:
        raise NotImplementedError
