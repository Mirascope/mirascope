"""Anthropic client implementation."""

from collections.abc import Sequence
from typing import Any, TypeAlias

from anthropic.types import MessageParam

from ..messages import Message
from ..responses import (
    AsyncContextStream,
    AsyncContextStructuredStream,
    AsyncStream,
    AsyncStructuredStream,
    ContextResponse,
    ContextStream,
    ContextStructuredStream,
    Response,
    Stream,
    StructuredStream,
)
from ..tools import ContextToolDef, ToolDef
from .base import BaseClient, BaseParams
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
        model: ANTHROPIC_REGISTERED_LLMS,
        messages: Sequence[AnthropicMessage],
        tools: Sequence[ToolDef | ContextToolDef[..., Any, Any]],
        params: AnthropicParams | None = None,
    ) -> ContextResponse:
        raise NotImplementedError

    def structured_call(
        self,
        *,
        model: ANTHROPIC_REGISTERED_LLMS,
        messages: Sequence[AnthropicMessage],
        tools: Sequence[ToolDef] | None = None,
        response_format: type,
        params: AnthropicParams | None = None,
    ) -> Response:
        raise NotImplementedError

    def structured_context_call(
        self,
        *,
        model: ANTHROPIC_REGISTERED_LLMS,
        messages: Sequence[AnthropicMessage],
        tools: Sequence[ToolDef | ContextToolDef[..., Any, Any]],
        response_format: type,
        params: AnthropicParams | None = None,
    ) -> ContextResponse:
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
        model: ANTHROPIC_REGISTERED_LLMS,
        messages: Sequence[AnthropicMessage],
        tools: Sequence[ToolDef | ContextToolDef[..., Any, Any]],
        params: AnthropicParams | None = None,
    ) -> ContextResponse:
        raise NotImplementedError

    async def structured_call_async(
        self,
        *,
        model: ANTHROPIC_REGISTERED_LLMS,
        messages: Sequence[AnthropicMessage],
        tools: Sequence[ToolDef] | None = None,
        response_format: type,
        params: AnthropicParams | None = None,
    ) -> Response:
        raise NotImplementedError

    async def structured_context_call_async(
        self,
        *,
        model: ANTHROPIC_REGISTERED_LLMS,
        messages: Sequence[AnthropicMessage],
        tools: Sequence[ToolDef | ContextToolDef[..., Any, Any]],
        response_format: type,
        params: AnthropicParams | None = None,
    ) -> ContextResponse:
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
        model: ANTHROPIC_REGISTERED_LLMS,
        messages: Sequence[AnthropicMessage],
        tools: Sequence[ToolDef | ContextToolDef[..., Any, Any]],
        params: AnthropicParams | None = None,
    ) -> ContextStream:
        raise NotImplementedError

    def structured_stream(
        self,
        *,
        model: ANTHROPIC_REGISTERED_LLMS,
        messages: Sequence[AnthropicMessage],
        tools: Sequence[ToolDef] | None = None,
        response_format: type,
        params: AnthropicParams | None = None,
    ) -> StructuredStream:
        raise NotImplementedError

    def structured_context_stream(
        self,
        *,
        model: ANTHROPIC_REGISTERED_LLMS,
        messages: Sequence[AnthropicMessage],
        tools: Sequence[ToolDef | ContextToolDef[..., Any, Any]],
        response_format: type,
        params: AnthropicParams | None = None,
    ) -> ContextStructuredStream:
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
        model: ANTHROPIC_REGISTERED_LLMS,
        messages: Sequence[AnthropicMessage],
        tools: Sequence[ToolDef | ContextToolDef[..., Any, Any]],
        params: AnthropicParams | None = None,
    ) -> AsyncContextStream:
        raise NotImplementedError

    async def structured_stream_async(
        self,
        *,
        model: ANTHROPIC_REGISTERED_LLMS,
        messages: Sequence[AnthropicMessage],
        tools: Sequence[ToolDef] | None = None,
        response_format: type,
        params: AnthropicParams | None = None,
    ) -> AsyncStructuredStream:
        raise NotImplementedError

    async def structured_context_stream_async(
        self,
        *,
        model: ANTHROPIC_REGISTERED_LLMS,
        messages: Sequence[AnthropicMessage],
        tools: Sequence[ToolDef | ContextToolDef[..., Any, Any]],
        response_format: type,
        params: AnthropicParams | None = None,
    ) -> AsyncContextStructuredStream:
        raise NotImplementedError
