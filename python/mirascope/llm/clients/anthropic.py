"""Anthropic client implementation."""

from collections.abc import Sequence
from typing import Any, TypeAlias

from anthropic.types import MessageParam

from ..context import Context
from ..messages import Message
from ..models.base import BaseParams
from ..responses import Response
from ..streams import (
    AsyncStream,
    AsyncStructuredStream,
    Stream,
    StructuredStream,
)
from ..tools import ContextToolDef, ToolDef
from ..types import DepsT, FormatT
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
        tools: Sequence[ToolDef] | None = None,
        params: AnthropicParams | None = None,
    ) -> Response:
        raise NotImplementedError

    def context_call(
        self,
        *,
        ctx: Context[DepsT],
        model: ANTHROPIC_REGISTERED_LLMS,
        messages: Sequence[AnthropicMessage],
        tools: Sequence[ToolDef | ContextToolDef[..., Any, DepsT]],
        params: AnthropicParams | None = None,
    ) -> Response:
        raise NotImplementedError

    def structured_call(
        self,
        *,
        model: ANTHROPIC_REGISTERED_LLMS,
        messages: Sequence[AnthropicMessage],
        tools: Sequence[ToolDef] | None = None,
        response_format: type[FormatT],
        params: AnthropicParams | None = None,
    ) -> Response[FormatT]:
        raise NotImplementedError

    def structured_context_call(
        self,
        *,
        ctx: Context[DepsT],
        model: ANTHROPIC_REGISTERED_LLMS,
        messages: Sequence[AnthropicMessage],
        tools: Sequence[ToolDef | ContextToolDef[..., Any, DepsT]],
        response_format: type[FormatT],
        params: AnthropicParams | None = None,
    ) -> Response[FormatT]:
        raise NotImplementedError

    async def call_async(
        self,
        *,
        model: ANTHROPIC_REGISTERED_LLMS,
        messages: Sequence[AnthropicMessage],
        tools: Sequence[ToolDef] | None = None,
        params: AnthropicParams | None = None,
    ) -> Response:
        raise NotImplementedError

    async def context_call_async(
        self,
        *,
        ctx: Context[DepsT],
        model: ANTHROPIC_REGISTERED_LLMS,
        messages: Sequence[AnthropicMessage],
        tools: Sequence[ToolDef | ContextToolDef[..., Any, DepsT]],
        params: AnthropicParams | None = None,
    ) -> Response:
        raise NotImplementedError

    async def structured_call_async(
        self,
        *,
        model: ANTHROPIC_REGISTERED_LLMS,
        messages: Sequence[AnthropicMessage],
        tools: Sequence[ToolDef] | None = None,
        response_format: type[FormatT],
        params: AnthropicParams | None = None,
    ) -> Response[FormatT]:
        raise NotImplementedError

    async def structured_context_call_async(
        self,
        *,
        ctx: Context[DepsT],
        model: ANTHROPIC_REGISTERED_LLMS,
        messages: Sequence[AnthropicMessage],
        tools: Sequence[ToolDef | ContextToolDef[..., Any, DepsT]],
        response_format: type[FormatT],
        params: AnthropicParams | None = None,
    ) -> Response[FormatT]:
        raise NotImplementedError

    def stream(
        self,
        *,
        model: ANTHROPIC_REGISTERED_LLMS,
        messages: Sequence[AnthropicMessage],
        tools: Sequence[ToolDef] | None = None,
        params: AnthropicParams | None = None,
    ) -> Stream:
        raise NotImplementedError

    def context_stream(
        self,
        *,
        ctx: Context[DepsT],
        model: ANTHROPIC_REGISTERED_LLMS,
        messages: Sequence[AnthropicMessage],
        tools: Sequence[ToolDef | ContextToolDef[..., Any, DepsT]],
        params: AnthropicParams | None = None,
    ) -> Stream:
        raise NotImplementedError

    def structured_stream(
        self,
        *,
        model: ANTHROPIC_REGISTERED_LLMS,
        messages: Sequence[AnthropicMessage],
        tools: Sequence[ToolDef] | None = None,
        response_format: type[FormatT],
        params: AnthropicParams | None = None,
    ) -> StructuredStream[FormatT]:
        raise NotImplementedError

    def structured_context_stream(
        self,
        *,
        ctx: Context[DepsT],
        model: ANTHROPIC_REGISTERED_LLMS,
        messages: Sequence[AnthropicMessage],
        tools: Sequence[ToolDef | ContextToolDef[..., Any, DepsT]],
        response_format: type[FormatT],
        params: AnthropicParams | None = None,
    ) -> StructuredStream[FormatT]:
        raise NotImplementedError

    async def stream_async(
        self,
        *,
        model: ANTHROPIC_REGISTERED_LLMS,
        messages: Sequence[AnthropicMessage],
        tools: Sequence[ToolDef] | None = None,
        params: AnthropicParams | None = None,
    ) -> AsyncStream:
        raise NotImplementedError

    async def context_stream_async(
        self,
        *,
        ctx: Context[DepsT],
        model: ANTHROPIC_REGISTERED_LLMS,
        messages: Sequence[AnthropicMessage],
        tools: Sequence[ToolDef | ContextToolDef[..., Any, DepsT]],
        params: AnthropicParams | None = None,
    ) -> AsyncStream:
        raise NotImplementedError

    async def structured_stream_async(
        self,
        *,
        model: ANTHROPIC_REGISTERED_LLMS,
        messages: Sequence[AnthropicMessage],
        tools: Sequence[ToolDef] | None = None,
        response_format: type[FormatT],
        params: AnthropicParams | None = None,
    ) -> AsyncStructuredStream[FormatT]:
        raise NotImplementedError

    async def structured_context_stream_async(
        self,
        *,
        ctx: Context[DepsT],
        model: ANTHROPIC_REGISTERED_LLMS,
        messages: Sequence[AnthropicMessage],
        tools: Sequence[ToolDef | ContextToolDef[..., Any, DepsT]],
        response_format: type[FormatT],
        params: AnthropicParams | None = None,
    ) -> AsyncStructuredStream[FormatT]:
        raise NotImplementedError
