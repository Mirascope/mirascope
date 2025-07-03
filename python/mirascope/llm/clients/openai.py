"""OpenAI client implementation."""

from collections.abc import Sequence
from typing import Any, TypeAlias

from openai.types.chat import ChatCompletionMessageParam

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
from .register import OPENAI_REGISTERED_LLMS

OpenAIMessage: TypeAlias = Message | ChatCompletionMessageParam


class OpenAIParams(BaseParams, total=False):
    """The parameters for the OpenAI LLM model."""


class OpenAIClient(BaseClient[OpenAIMessage, OpenAIParams, OPENAI_REGISTERED_LLMS]):
    """The client for the OpenAI LLM model."""

    def call(
        self,
        *,
        model: OPENAI_REGISTERED_LLMS,
        messages: Sequence[OpenAIMessage],
        tools: Sequence[ToolDef] | None = None,
        params: OpenAIParams | None = None,
    ) -> Response:
        raise NotImplementedError

    def context_call(
        self,
        *,
        model: OPENAI_REGISTERED_LLMS,
        messages: Sequence[OpenAIMessage],
        tools: Sequence[ToolDef | ContextToolDef[..., Any, Any]],
        params: OpenAIParams | None = None,
    ) -> ContextResponse:
        raise NotImplementedError

    def structured_call(
        self,
        *,
        model: OPENAI_REGISTERED_LLMS,
        messages: Sequence[OpenAIMessage],
        tools: Sequence[ToolDef] | None = None,
        response_format: type,
        params: OpenAIParams | None = None,
    ) -> Response:
        raise NotImplementedError

    def structured_context_call(
        self,
        *,
        model: OPENAI_REGISTERED_LLMS,
        messages: Sequence[OpenAIMessage],
        tools: Sequence[ToolDef | ContextToolDef[..., Any, Any]],
        response_format: type,
        params: OpenAIParams | None = None,
    ) -> ContextResponse:
        raise NotImplementedError

    async def call_async(
        self,
        *,
        model: OPENAI_REGISTERED_LLMS,
        messages: Sequence[OpenAIMessage],
        tools: Sequence[ToolDef] | None = None,
        params: OpenAIParams | None = None,
    ) -> Response:
        raise NotImplementedError

    async def context_call_async(
        self,
        *,
        model: OPENAI_REGISTERED_LLMS,
        messages: Sequence[OpenAIMessage],
        tools: Sequence[ToolDef | ContextToolDef[..., Any, Any]],
        params: OpenAIParams | None = None,
    ) -> ContextResponse:
        raise NotImplementedError

    async def structured_call_async(
        self,
        *,
        model: OPENAI_REGISTERED_LLMS,
        messages: Sequence[OpenAIMessage],
        tools: Sequence[ToolDef] | None = None,
        response_format: type,
        params: OpenAIParams | None = None,
    ) -> Response:
        raise NotImplementedError

    async def structured_context_call_async(
        self,
        *,
        model: OPENAI_REGISTERED_LLMS,
        messages: Sequence[OpenAIMessage],
        tools: Sequence[ToolDef | ContextToolDef[..., Any, Any]],
        response_format: type,
        params: OpenAIParams | None = None,
    ) -> ContextResponse:
        raise NotImplementedError

    def stream(
        self,
        *,
        model: OPENAI_REGISTERED_LLMS,
        messages: Sequence[OpenAIMessage],
        tools: Sequence[ToolDef] | None = None,
        params: OpenAIParams | None = None,
    ) -> Stream:
        raise NotImplementedError

    def context_stream(
        self,
        *,
        model: OPENAI_REGISTERED_LLMS,
        messages: Sequence[OpenAIMessage],
        tools: Sequence[ToolDef | ContextToolDef[..., Any, Any]],
        params: OpenAIParams | None = None,
    ) -> ContextStream:
        raise NotImplementedError

    def structured_stream(
        self,
        *,
        model: OPENAI_REGISTERED_LLMS,
        messages: Sequence[OpenAIMessage],
        tools: Sequence[ToolDef] | None = None,
        response_format: type,
        params: OpenAIParams | None = None,
    ) -> StructuredStream:
        raise NotImplementedError

    def structured_context_stream(
        self,
        *,
        model: OPENAI_REGISTERED_LLMS,
        messages: Sequence[OpenAIMessage],
        tools: Sequence[ToolDef | ContextToolDef[..., Any, Any]],
        response_format: type,
        params: OpenAIParams | None = None,
    ) -> ContextStructuredStream:
        raise NotImplementedError

    async def stream_async(
        self,
        *,
        model: OPENAI_REGISTERED_LLMS,
        messages: Sequence[OpenAIMessage],
        tools: Sequence[ToolDef] | None = None,
        params: OpenAIParams | None = None,
    ) -> AsyncStream:
        raise NotImplementedError

    async def context_stream_async(
        self,
        *,
        model: OPENAI_REGISTERED_LLMS,
        messages: Sequence[OpenAIMessage],
        tools: Sequence[ToolDef | ContextToolDef[..., Any, Any]],
        params: OpenAIParams | None = None,
    ) -> AsyncContextStream:
        raise NotImplementedError

    async def structured_stream_async(
        self,
        *,
        model: OPENAI_REGISTERED_LLMS,
        messages: Sequence[OpenAIMessage],
        tools: Sequence[ToolDef] | None = None,
        response_format: type,
        params: OpenAIParams | None = None,
    ) -> AsyncStructuredStream:
        raise NotImplementedError

    async def structured_context_stream_async(
        self,
        *,
        model: OPENAI_REGISTERED_LLMS,
        messages: Sequence[OpenAIMessage],
        tools: Sequence[ToolDef | ContextToolDef[..., Any, Any]],
        response_format: type,
        params: OpenAIParams | None = None,
    ) -> AsyncContextStructuredStream:
        raise NotImplementedError
