"""Anthropic client implementation."""

from collections.abc import Sequence
from typing import TypeAlias

from anthropic.types import MessageParam

from ..clients import BaseParams
from ..context import Context, DepsT
from ..formatting import FormatT
from ..messages import Message
from ..responses import (
    AsyncStreamResponse,
    Response,
    StreamResponse,
)
from ..tools import AsyncContextTool, AsyncTool, ContextTool, Tool
from ..types import Jsonable
from .base import BaseClient
from .register import ANTHROPIC_REGISTERED_LLMS

AnthropicMessage: TypeAlias = Message | MessageParam


class AnthropicParams(BaseParams, total=False):
    """The parameters for the Anthropic LLM model."""


class AnthropicClient(
    BaseClient[AnthropicMessage, AnthropicParams, ANTHROPIC_REGISTERED_LLMS]
):
    """The client for the Anthropic LLM model."""

    def call(
        self,
        *,
        model: ANTHROPIC_REGISTERED_LLMS,
        messages: Sequence[AnthropicMessage],
        tools: Sequence[Tool] | None = None,
        params: AnthropicParams | None = None,
    ) -> Response[None]:
        raise NotImplementedError

    def context_call(
        self,
        *,
        ctx: Context[DepsT],
        model: ANTHROPIC_REGISTERED_LLMS,
        messages: Sequence[AnthropicMessage],
        tools: Sequence[Tool | ContextTool[..., Jsonable, DepsT]],
        params: AnthropicParams | None = None,
    ) -> Response[None]:
        raise NotImplementedError

    def structured_call(
        self,
        *,
        model: ANTHROPIC_REGISTERED_LLMS,
        messages: Sequence[AnthropicMessage],
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
        messages: Sequence[AnthropicMessage],
        tools: Sequence[Tool | ContextTool[..., Jsonable, DepsT]],
        format: type[FormatT],
        params: AnthropicParams | None = None,
    ) -> Response[FormatT]:
        raise NotImplementedError

    async def call_async(
        self,
        *,
        model: ANTHROPIC_REGISTERED_LLMS,
        messages: Sequence[AnthropicMessage],
        tools: Sequence[AsyncTool] | None = None,
        params: AnthropicParams | None = None,
    ) -> Response[None]:
        raise NotImplementedError

    async def context_call_async(
        self,
        *,
        ctx: Context[DepsT],
        model: ANTHROPIC_REGISTERED_LLMS,
        messages: Sequence[AnthropicMessage],
        tools: Sequence[AsyncTool | AsyncContextTool[..., Jsonable, DepsT]],
        params: AnthropicParams | None = None,
    ) -> Response[None]:
        raise NotImplementedError

    async def structured_call_async(
        self,
        *,
        model: ANTHROPIC_REGISTERED_LLMS,
        messages: Sequence[AnthropicMessage],
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
        messages: Sequence[AnthropicMessage],
        tools: Sequence[AsyncTool | AsyncContextTool[..., Jsonable, DepsT]],
        format: type[FormatT],
        params: AnthropicParams | None = None,
    ) -> Response[FormatT]:
        raise NotImplementedError

    def stream(
        self,
        *,
        model: ANTHROPIC_REGISTERED_LLMS,
        messages: Sequence[AnthropicMessage],
        tools: Sequence[Tool] | None = None,
        params: AnthropicParams | None = None,
    ) -> StreamResponse[None]:
        raise NotImplementedError

    def context_stream(
        self,
        *,
        ctx: Context[DepsT],
        model: ANTHROPIC_REGISTERED_LLMS,
        messages: Sequence[AnthropicMessage],
        tools: Sequence[Tool | ContextTool[..., Jsonable, DepsT]],
        params: AnthropicParams | None = None,
    ) -> StreamResponse[None]:
        raise NotImplementedError

    def structured_stream(
        self,
        *,
        model: ANTHROPIC_REGISTERED_LLMS,
        messages: Sequence[AnthropicMessage],
        tools: Sequence[Tool] | None = None,
        format: type[FormatT],
        params: AnthropicParams | None = None,
    ) -> StreamResponse[FormatT]:
        raise NotImplementedError

    def structured_context_stream(
        self,
        *,
        ctx: Context[DepsT],
        model: ANTHROPIC_REGISTERED_LLMS,
        messages: Sequence[AnthropicMessage],
        tools: Sequence[Tool | ContextTool[..., Jsonable, DepsT]],
        format: type[FormatT],
        params: AnthropicParams | None = None,
    ) -> StreamResponse[FormatT]:
        raise NotImplementedError

    async def stream_async(
        self,
        *,
        model: ANTHROPIC_REGISTERED_LLMS,
        messages: Sequence[AnthropicMessage],
        tools: Sequence[AsyncTool] | None = None,
        params: AnthropicParams | None = None,
    ) -> AsyncStreamResponse[None]:
        raise NotImplementedError

    async def context_stream_async(
        self,
        *,
        ctx: Context[DepsT],
        model: ANTHROPIC_REGISTERED_LLMS,
        messages: Sequence[AnthropicMessage],
        tools: Sequence[AsyncTool | AsyncContextTool[..., Jsonable, DepsT]],
        params: AnthropicParams | None = None,
    ) -> AsyncStreamResponse[None]:
        raise NotImplementedError

    async def structured_stream_async(
        self,
        *,
        model: ANTHROPIC_REGISTERED_LLMS,
        messages: Sequence[AnthropicMessage],
        tools: Sequence[AsyncTool] | None = None,
        format: type[FormatT],
        params: AnthropicParams | None = None,
    ) -> AsyncStreamResponse[FormatT]:
        raise NotImplementedError

    async def structured_context_stream_async(
        self,
        *,
        ctx: Context[DepsT],
        model: ANTHROPIC_REGISTERED_LLMS,
        messages: Sequence[AnthropicMessage],
        tools: Sequence[AsyncTool | AsyncContextTool[..., Jsonable, DepsT]],
        format: type[FormatT],
        params: AnthropicParams | None = None,
    ) -> AsyncStreamResponse[FormatT]:
        raise NotImplementedError
