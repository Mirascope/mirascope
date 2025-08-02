"""Anthropic client implementation."""

from collections.abc import Sequence

import httpx
from anthropic import Anthropic, NotGiven

from ...context import Context, DepsT
from ...formatting import FormatT
from ...messages import Message
from ...responses import Response, StreamResponse
from ...streams import AsyncStream, Stream
from ...tools import AsyncContextTool, AsyncTool, ContextTool, Tool
from ...types import Jsonable
from ..base import BaseClient
from .converter import AnthropicConverter
from .params import AnthropicParams
from .registered_llms import ANTHROPIC_REGISTERED_LLMS


class AnthropicClient(BaseClient[AnthropicParams, ANTHROPIC_REGISTERED_LLMS]):
    """The client for the Anthropic LLM model."""

    client: Anthropic

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
        model: ANTHROPIC_REGISTERED_LLMS,
        messages: Sequence[Message],
        tools: Sequence[Tool] | None = None,
        params: AnthropicParams | None = None,
    ) -> Response[None]:
        """Make a call to the Anthropic API."""
        if tools:
            raise NotImplementedError("tool use not yet supported")
        if params:
            raise NotImplementedError("param use not yet supported")

        # Convert model to just the model name (remove "anthropic:" prefix if present)
        model_name = model.split(":")[-1] if ":" in model else model

        # Convert messages to MessageParam format
        system_message, converted_messages = AnthropicConverter.encode_messages(
            messages
        )

        anthropic_response = self.client.messages.create(
            max_tokens=1024,
            model=model_name,
            messages=converted_messages,
            system=system_message or NotGiven(),
        )

        finish_reason = AnthropicConverter.decode_finish_reason(
            anthropic_response.stop_reason
        )
        assistant_message = AnthropicConverter.decode_assistant_message(
            anthropic_response
        )

        return Response(
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
        model: ANTHROPIC_REGISTERED_LLMS,
        messages: Sequence[Message],
        tools: Sequence[Tool | ContextTool[..., Jsonable, DepsT]],
        params: AnthropicParams | None = None,
    ) -> Response[None]:
        raise NotImplementedError

    def structured_call(
        self,
        *,
        model: ANTHROPIC_REGISTERED_LLMS,
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
        model: ANTHROPIC_REGISTERED_LLMS,
        messages: Sequence[Message],
        tools: Sequence[Tool | ContextTool[..., Jsonable, DepsT]],
        format: type[FormatT],
        params: AnthropicParams | None = None,
    ) -> Response[FormatT]:
        raise NotImplementedError

    async def call_async(
        self,
        *,
        model: ANTHROPIC_REGISTERED_LLMS,
        messages: Sequence[Message],
        tools: Sequence[AsyncTool] | None = None,
        params: AnthropicParams | None = None,
    ) -> Response[None]:
        raise NotImplementedError

    async def context_call_async(
        self,
        *,
        ctx: Context[DepsT],
        model: ANTHROPIC_REGISTERED_LLMS,
        messages: Sequence[Message],
        tools: Sequence[AsyncTool | AsyncContextTool[..., Jsonable, DepsT]],
        params: AnthropicParams | None = None,
    ) -> Response[None]:
        raise NotImplementedError

    async def structured_call_async(
        self,
        *,
        model: ANTHROPIC_REGISTERED_LLMS,
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
        model: ANTHROPIC_REGISTERED_LLMS,
        messages: Sequence[Message],
        tools: Sequence[AsyncTool | AsyncContextTool[..., Jsonable, DepsT]],
        format: type[FormatT],
        params: AnthropicParams | None = None,
    ) -> Response[FormatT]:
        raise NotImplementedError

    def stream(
        self,
        *,
        model: ANTHROPIC_REGISTERED_LLMS,
        messages: Sequence[Message],
        tools: Sequence[Tool] | None = None,
        params: AnthropicParams | None = None,
    ) -> StreamResponse[Stream, None]:
        raise NotImplementedError

    def context_stream(
        self,
        *,
        ctx: Context[DepsT],
        model: ANTHROPIC_REGISTERED_LLMS,
        messages: Sequence[Message],
        tools: Sequence[Tool | ContextTool[..., Jsonable, DepsT]],
        params: AnthropicParams | None = None,
    ) -> StreamResponse[Stream, None]:
        raise NotImplementedError

    def structured_stream(
        self,
        *,
        model: ANTHROPIC_REGISTERED_LLMS,
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
        model: ANTHROPIC_REGISTERED_LLMS,
        messages: Sequence[Message],
        tools: Sequence[Tool | ContextTool[..., Jsonable, DepsT]],
        format: type[FormatT],
        params: AnthropicParams | None = None,
    ) -> StreamResponse[Stream, FormatT]:
        raise NotImplementedError

    async def stream_async(
        self,
        *,
        model: ANTHROPIC_REGISTERED_LLMS,
        messages: Sequence[Message],
        tools: Sequence[AsyncTool] | None = None,
        params: AnthropicParams | None = None,
    ) -> StreamResponse[AsyncStream, None]:
        raise NotImplementedError

    async def context_stream_async(
        self,
        *,
        ctx: Context[DepsT],
        model: ANTHROPIC_REGISTERED_LLMS,
        messages: Sequence[Message],
        tools: Sequence[AsyncTool | AsyncContextTool[..., Jsonable, DepsT]],
        params: AnthropicParams | None = None,
    ) -> StreamResponse[AsyncStream, None]:
        raise NotImplementedError

    async def structured_stream_async(
        self,
        *,
        model: ANTHROPIC_REGISTERED_LLMS,
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
        model: ANTHROPIC_REGISTERED_LLMS,
        messages: Sequence[Message],
        tools: Sequence[AsyncTool | AsyncContextTool[..., Jsonable, DepsT]],
        format: type[FormatT],
        params: AnthropicParams | None = None,
    ) -> StreamResponse[AsyncStream, FormatT]:
        raise NotImplementedError
