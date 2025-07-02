"""OpenAI provider implementation."""

from collections.abc import Sequence
from typing import Any, Literal, TypeAlias

from openai.types.chat import ChatCompletionMessageParam

from ..clients.base import BaseClient
from ..messages import Message
from ..models.base import LLM, BaseParams
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

REGISTERED_LLMS: TypeAlias = Literal["openai:gpt-4o-mini"]
"""The OpenAI models registered with Mirascope."""


class Params(BaseParams, total=False):
    """The parameters for the OpenAI LLM model."""


class Client(BaseClient[Message | ChatCompletionMessageParam, BaseParams]):
    """The client for the OpenAI LLM model."""
    
    def call(
        self,
        *,
        messages: Sequence[Message | ChatCompletionMessageParam],
        tools: Sequence[ToolDef] | None = None,
        params: BaseParams | None = None,
    ) -> Response:
        raise NotImplementedError
    
    def context_call(
        self,
        *,
        messages: Sequence[Message | ChatCompletionMessageParam],
        tools: Sequence[ToolDef | ContextToolDef[..., Any, Any]],
        params: BaseParams | None = None,
    ) -> ContextResponse:
        raise NotImplementedError
    
    def structured_call(
        self,
        *,
        messages: Sequence[Message | ChatCompletionMessageParam],
        tools: Sequence[ToolDef] | None = None,
        response_format: type,
        params: BaseParams | None = None,
    ) -> Response:
        raise NotImplementedError
    
    def structured_context_call(
        self,
        *,
        messages: Sequence[Message | ChatCompletionMessageParam],
        tools: Sequence[ToolDef | ContextToolDef[..., Any, Any]],
        response_format: type,
        params: BaseParams | None = None,
    ) -> ContextResponse:
        raise NotImplementedError
    
    async def call_async(
        self,
        *,
        messages: Sequence[Message | ChatCompletionMessageParam],
        tools: Sequence[ToolDef] | None = None,
        params: BaseParams | None = None,
    ) -> Response:
        raise NotImplementedError
    
    async def context_call_async(
        self,
        *,
        messages: Sequence[Message | ChatCompletionMessageParam],
        tools: Sequence[ToolDef | ContextToolDef[..., Any, Any]],
        params: BaseParams | None = None,
    ) -> ContextResponse:
        raise NotImplementedError
    
    async def structured_call_async(
        self,
        *,
        messages: Sequence[Message | ChatCompletionMessageParam],
        tools: Sequence[ToolDef] | None = None,
        response_format: type,
        params: BaseParams | None = None,
    ) -> Response:
        raise NotImplementedError
    
    async def structured_context_call_async(
        self,
        *,
        messages: Sequence[Message | ChatCompletionMessageParam],
        tools: Sequence[ToolDef | ContextToolDef[..., Any, Any]],
        response_format: type,
        params: BaseParams | None = None,
    ) -> ContextResponse:
        raise NotImplementedError
    
    def stream(
        self,
        *,
        messages: Sequence[Message | ChatCompletionMessageParam],
        tools: Sequence[ToolDef] | None = None,
        params: BaseParams | None = None,
    ) -> Stream:
        raise NotImplementedError
    
    def context_stream(
        self,
        *,
        messages: Sequence[Message | ChatCompletionMessageParam],
        tools: Sequence[ToolDef | ContextToolDef[..., Any, Any]],
        params: BaseParams | None = None,
    ) -> ContextStream:
        raise NotImplementedError
    
    def structured_stream(
        self,
        *,
        messages: Sequence[Message | ChatCompletionMessageParam],
        tools: Sequence[ToolDef] | None = None,
        response_format: type,
        params: BaseParams | None = None,
    ) -> StructuredStream:
        raise NotImplementedError
    
    def structured_context_stream(
        self,
        *,
        messages: Sequence[Message | ChatCompletionMessageParam],
        tools: Sequence[ToolDef | ContextToolDef[..., Any, Any]],
        response_format: type,
        params: BaseParams | None = None,
    ) -> ContextStructuredStream:
        raise NotImplementedError
    
    async def stream_async(
        self,
        *,
        messages: Sequence[Message | ChatCompletionMessageParam],
        tools: Sequence[ToolDef] | None = None,
        params: BaseParams | None = None,
    ) -> AsyncStream:
        raise NotImplementedError
    
    async def context_stream_async(
        self,
        *,
        messages: Sequence[Message | ChatCompletionMessageParam],
        tools: Sequence[ToolDef | ContextToolDef[..., Any, Any]],
        params: BaseParams | None = None,
    ) -> AsyncContextStream:
        raise NotImplementedError
    
    async def structured_stream_async(
        self,
        *,
        messages: Sequence[Message | ChatCompletionMessageParam],
        tools: Sequence[ToolDef] | None = None,
        response_format: type,
        params: BaseParams | None = None,
    ) -> AsyncStructuredStream:
        raise NotImplementedError
    
    async def structured_context_stream_async(
        self,
        *,
        messages: Sequence[Message | ChatCompletionMessageParam],
        tools: Sequence[ToolDef | ContextToolDef[..., Any, Any]],
        response_format: type,
        params: BaseParams | None = None,
    ) -> AsyncContextStructuredStream:
        raise NotImplementedError


class Model(LLM[Message | ChatCompletionMessageParam, BaseParams, Client]):
    """The OpenAI-specific implementation of the `LLM` interface."""
