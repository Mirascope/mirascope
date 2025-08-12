"""Anthropic client implementation."""

from collections.abc import Sequence

import httpx
from anthropic import Anthropic

from ...context import Context, DepsT
from ...formatting import FormatT
from ...messages import Message
from ...responses import Response, StreamResponse
from ...streams import AsyncStream, Stream
from ...tools import AsyncContextTool, AsyncTool, ContextTool, Tool
from ...types import Jsonable
from ..base import BaseClient
from . import _utils
from .models import AnthropicModel
from .params import AnthropicParams


class AnthropicClient(BaseClient[AnthropicParams, AnthropicModel, Anthropic]):
    """The client for the Anthropic LLM model."""

    def __init__(
        self, *, api_key: str | None = None, base_url: str | httpx.URL | None = None
    ) -> None:
        """Initialize the AnthropicClient with optional API key.

        If api_key is not set, Anthropic will look for it in env as "ANTHROPIC_API_KEY".
        """
        self.client = Anthropic(api_key=api_key, base_url=base_url)

    def call(
        self,
        *,
        model: AnthropicModel,
        messages: Sequence[Message],
        tools: Sequence[Tool] | None = None,
        params: AnthropicParams | None = None,
    ) -> Response[None]:
        """Make a call to the Anthropic API."""
        if params:
            raise NotImplementedError("param use not yet supported")

        message_params, system, tool_params = _utils.prepare_anthropic_request(
            messages, tools
        )

        anthropic_response = self.client.messages.create(
            max_tokens=1024,
            model=model,
            messages=message_params,
            system=system,
            tools=tool_params,
        )

        assistant_message, finish_reason = _utils.decode_response(anthropic_response)

        return Response(
            provider="anthropic",
            model=model,
            raw=anthropic_response,
            input_messages=messages,
            assistant_message=assistant_message,
            finish_reason=finish_reason,
        )

    def context_call(
        self,
        *,
        ctx: Context[DepsT],
        model: AnthropicModel,
        messages: Sequence[Message],
        tools: Sequence[Tool | ContextTool[..., Jsonable, DepsT]],
        params: AnthropicParams | None = None,
    ) -> Response[None]:
        raise NotImplementedError

    def structured_call(
        self,
        *,
        model: AnthropicModel,
        messages: Sequence[Message],
        tools: Sequence[Tool] | None = None,
        format: type[FormatT],
        params: AnthropicParams | None = None,
    ) -> Response[FormatT]:
        raise NotImplementedError

    def structured_context_call(
        self,
        *,
        ctx: Context[DepsT],
        model: AnthropicModel,
        messages: Sequence[Message],
        tools: Sequence[Tool | ContextTool[..., Jsonable, DepsT]],
        format: type[FormatT],
        params: AnthropicParams | None = None,
    ) -> Response[FormatT]:
        raise NotImplementedError

    async def call_async(
        self,
        *,
        model: AnthropicModel,
        messages: Sequence[Message],
        tools: Sequence[AsyncTool] | None = None,
        params: AnthropicParams | None = None,
    ) -> Response[None]:
        raise NotImplementedError

    async def context_call_async(
        self,
        *,
        ctx: Context[DepsT],
        model: AnthropicModel,
        messages: Sequence[Message],
        tools: Sequence[AsyncTool | AsyncContextTool[..., Jsonable, DepsT]],
        params: AnthropicParams | None = None,
    ) -> Response[None]:
        raise NotImplementedError

    async def structured_call_async(
        self,
        *,
        model: AnthropicModel,
        messages: Sequence[Message],
        tools: Sequence[AsyncTool] | None = None,
        format: type[FormatT],
        params: AnthropicParams | None = None,
    ) -> Response[FormatT]:
        raise NotImplementedError

    async def structured_context_call_async(
        self,
        *,
        ctx: Context[DepsT],
        model: AnthropicModel,
        messages: Sequence[Message],
        tools: Sequence[AsyncTool | AsyncContextTool[..., Jsonable, DepsT]],
        format: type[FormatT],
        params: AnthropicParams | None = None,
    ) -> Response[FormatT]:
        raise NotImplementedError

    def stream(
        self,
        *,
        model: AnthropicModel,
        messages: Sequence[Message],
        tools: Sequence[Tool] | None = None,
        params: AnthropicParams | None = None,
    ) -> StreamResponse[Stream, None]:
        """Make a streaming call to the Anthropic API."""
        if params:
            raise NotImplementedError("param use not yet supported")

        message_params, system, tool_params = _utils.prepare_anthropic_request(
            messages, tools
        )

        anthropic_stream = self.client.messages.stream(
            max_tokens=1024,
            model=model,
            messages=message_params,
            system=system,
            tools=tool_params,
        )

        chunk_iterator = _utils.convert_anthropic_stream_to_chunk_iterator(
            anthropic_stream
        )

        return StreamResponse(
            provider="anthropic",
            model=model,
            input_messages=messages,
            chunk_iterator=chunk_iterator,
        )

    def context_stream(
        self,
        *,
        ctx: Context[DepsT],
        model: AnthropicModel,
        messages: Sequence[Message],
        tools: Sequence[Tool | ContextTool[..., Jsonable, DepsT]],
        params: AnthropicParams | None = None,
    ) -> StreamResponse[Stream, None]:
        raise NotImplementedError

    def structured_stream(
        self,
        *,
        model: AnthropicModel,
        messages: Sequence[Message],
        tools: Sequence[Tool] | None = None,
        format: type[FormatT],
        params: AnthropicParams | None = None,
    ) -> StreamResponse[Stream, FormatT]:
        raise NotImplementedError

    def structured_context_stream(
        self,
        *,
        ctx: Context[DepsT],
        model: AnthropicModel,
        messages: Sequence[Message],
        tools: Sequence[Tool | ContextTool[..., Jsonable, DepsT]],
        format: type[FormatT],
        params: AnthropicParams | None = None,
    ) -> StreamResponse[Stream, FormatT]:
        raise NotImplementedError

    async def stream_async(
        self,
        *,
        model: AnthropicModel,
        messages: Sequence[Message],
        tools: Sequence[AsyncTool] | None = None,
        params: AnthropicParams | None = None,
    ) -> StreamResponse[AsyncStream, None]:
        raise NotImplementedError

    async def context_stream_async(
        self,
        *,
        ctx: Context[DepsT],
        model: AnthropicModel,
        messages: Sequence[Message],
        tools: Sequence[AsyncTool | AsyncContextTool[..., Jsonable, DepsT]],
        params: AnthropicParams | None = None,
    ) -> StreamResponse[AsyncStream, None]:
        raise NotImplementedError

    async def structured_stream_async(
        self,
        *,
        model: AnthropicModel,
        messages: Sequence[Message],
        tools: Sequence[AsyncTool] | None = None,
        format: type[FormatT],
        params: AnthropicParams | None = None,
    ) -> StreamResponse[AsyncStream, FormatT]:
        raise NotImplementedError

    async def structured_context_stream_async(
        self,
        *,
        ctx: Context[DepsT],
        model: AnthropicModel,
        messages: Sequence[Message],
        tools: Sequence[AsyncTool | AsyncContextTool[..., Jsonable, DepsT]],
        format: type[FormatT],
        params: AnthropicParams | None = None,
    ) -> StreamResponse[AsyncStream, FormatT]:
        raise NotImplementedError
