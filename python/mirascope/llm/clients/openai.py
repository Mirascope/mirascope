"""OpenAI client implementation."""

from collections.abc import Sequence
from typing import Any, TypeAlias

from openai.types.chat import ChatCompletionMessageParam
from typing_extensions import TypeVar

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
from .base import BaseClient
from .register import OPENAI_REGISTERED_LLMS

T = TypeVar("T", bound=object | None, default=None)
DepsT = TypeVar("DepsT", default=None)

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
        ctx: Context[DepsT],
        model: OPENAI_REGISTERED_LLMS,
        messages: Sequence[OpenAIMessage],
        tools: Sequence[ToolDef | ContextToolDef[..., Any, DepsT]],
        params: OpenAIParams | None = None,
    ) -> Response:
        raise NotImplementedError

    def structured_call(
        self,
        *,
        model: OPENAI_REGISTERED_LLMS,
        messages: Sequence[OpenAIMessage],
        tools: Sequence[ToolDef] | None = None,
        response_format: type[T],
        params: OpenAIParams | None = None,
    ) -> Response[T]:
        raise NotImplementedError

    def structured_context_call(
        self,
        *,
        ctx: Context[DepsT],
        model: OPENAI_REGISTERED_LLMS,
        messages: Sequence[OpenAIMessage],
        tools: Sequence[ToolDef | ContextToolDef[..., Any, DepsT]],
        response_format: type[T],
        params: OpenAIParams | None = None,
    ) -> Response[T]:
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
        ctx: Context[DepsT],
        model: OPENAI_REGISTERED_LLMS,
        messages: Sequence[OpenAIMessage],
        tools: Sequence[ToolDef | ContextToolDef[..., Any, DepsT]],
        params: OpenAIParams | None = None,
    ) -> Response:
        raise NotImplementedError

    async def structured_call_async(
        self,
        *,
        model: OPENAI_REGISTERED_LLMS,
        messages: Sequence[OpenAIMessage],
        tools: Sequence[ToolDef] | None = None,
        response_format: type[T],
        params: OpenAIParams | None = None,
    ) -> Response[T]:
        raise NotImplementedError

    async def structured_context_call_async(
        self,
        *,
        ctx: Context[DepsT],
        model: OPENAI_REGISTERED_LLMS,
        messages: Sequence[OpenAIMessage],
        tools: Sequence[ToolDef | ContextToolDef[..., Any, DepsT]],
        response_format: type[T],
        params: OpenAIParams | None = None,
    ) -> Response[T]:
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
        ctx: Context[DepsT],
        model: OPENAI_REGISTERED_LLMS,
        messages: Sequence[OpenAIMessage],
        tools: Sequence[ToolDef | ContextToolDef[..., Any, DepsT]],
        params: OpenAIParams | None = None,
    ) -> Stream:
        raise NotImplementedError

    def structured_stream(
        self,
        *,
        model: OPENAI_REGISTERED_LLMS,
        messages: Sequence[OpenAIMessage],
        tools: Sequence[ToolDef] | None = None,
        response_format: type[T],
        params: OpenAIParams | None = None,
    ) -> StructuredStream[T]:
        raise NotImplementedError

    def structured_context_stream(
        self,
        *,
        ctx: Context[DepsT],
        model: OPENAI_REGISTERED_LLMS,
        messages: Sequence[OpenAIMessage],
        tools: Sequence[ToolDef | ContextToolDef[..., Any, DepsT]],
        response_format: type[T],
        params: OpenAIParams | None = None,
    ) -> StructuredStream[T]:
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
        ctx: Context[DepsT],
        model: OPENAI_REGISTERED_LLMS,
        messages: Sequence[OpenAIMessage],
        tools: Sequence[ToolDef | ContextToolDef[..., Any, DepsT]],
        params: OpenAIParams | None = None,
    ) -> AsyncStream:
        raise NotImplementedError

    async def structured_stream_async(
        self,
        *,
        model: OPENAI_REGISTERED_LLMS,
        messages: Sequence[OpenAIMessage],
        tools: Sequence[ToolDef] | None = None,
        response_format: type[T],
        params: OpenAIParams | None = None,
    ) -> AsyncStructuredStream[T]:
        raise NotImplementedError

    async def structured_context_stream_async(
        self,
        *,
        ctx: Context[DepsT],
        model: OPENAI_REGISTERED_LLMS,
        messages: Sequence[OpenAIMessage],
        tools: Sequence[ToolDef | ContextToolDef[..., Any, DepsT]],
        response_format: type[T],
        params: OpenAIParams | None = None,
    ) -> AsyncStructuredStream[T]:
        raise NotImplementedError
