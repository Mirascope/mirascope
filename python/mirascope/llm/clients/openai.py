"""OpenAI client implementation."""

from collections.abc import Sequence
from typing import TypeAlias

from openai.types.chat import ChatCompletionMessageParam

from ..clients import BaseParams
from ..context import Context, DepsT
from ..formatting import FormatT
from ..messages import Message
from ..responses import Response
from ..streams import (
    AsyncStream,
    Stream,
)
from ..tools import AsyncContextTool, AsyncTool, ContextTool, Tool
from ..types import Jsonable
from .base import BaseClient
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
        tools: Sequence[Tool] | None = None,
        params: OpenAIParams | None = None,
    ) -> Response[None, None]:
        raise NotImplementedError

    def context_call(
        self,
        *,
        ctx: Context[DepsT],
        model: OPENAI_REGISTERED_LLMS,
        messages: Sequence[OpenAIMessage],
        tools: Sequence[Tool | ContextTool[..., Jsonable, DepsT]],
        params: OpenAIParams | None = None,
    ) -> Response[DepsT, None]:
        raise NotImplementedError

    def structured_call(
        self,
        *,
        model: OPENAI_REGISTERED_LLMS,
        messages: Sequence[OpenAIMessage],
        tools: Sequence[Tool] | None = None,
        format: type[FormatT],
        params: OpenAIParams | None = None,
    ) -> Response[None, FormatT]:
        raise NotImplementedError

    def structured_context_call(
        self,
        *,
        ctx: Context[DepsT],
        model: OPENAI_REGISTERED_LLMS,
        messages: Sequence[OpenAIMessage],
        tools: Sequence[Tool | ContextTool[..., Jsonable, DepsT]],
        format: type[FormatT],
        params: OpenAIParams | None = None,
    ) -> Response[DepsT, FormatT]:
        raise NotImplementedError

    async def call_async(
        self,
        *,
        model: OPENAI_REGISTERED_LLMS,
        messages: Sequence[OpenAIMessage],
        tools: Sequence[AsyncTool] | None = None,
        params: OpenAIParams | None = None,
    ) -> Response[None, None]:
        raise NotImplementedError

    async def context_call_async(
        self,
        *,
        ctx: Context[DepsT],
        model: OPENAI_REGISTERED_LLMS,
        messages: Sequence[OpenAIMessage],
        tools: Sequence[AsyncTool | AsyncContextTool[..., Jsonable, DepsT]],
        params: OpenAIParams | None = None,
    ) -> Response[DepsT, None]:
        raise NotImplementedError

    async def structured_call_async(
        self,
        *,
        model: OPENAI_REGISTERED_LLMS,
        messages: Sequence[OpenAIMessage],
        tools: Sequence[AsyncTool] | None = None,
        format: type[FormatT],
        params: OpenAIParams | None = None,
    ) -> Response[None, FormatT]:
        raise NotImplementedError

    async def structured_context_call_async(
        self,
        *,
        ctx: Context[DepsT],
        model: OPENAI_REGISTERED_LLMS,
        messages: Sequence[OpenAIMessage],
        tools: Sequence[AsyncTool | AsyncContextTool[..., Jsonable, DepsT]],
        format: type[FormatT],
        params: OpenAIParams | None = None,
    ) -> Response[DepsT, FormatT]:
        raise NotImplementedError

    def stream(
        self,
        *,
        model: OPENAI_REGISTERED_LLMS,
        messages: Sequence[OpenAIMessage],
        tools: Sequence[Tool] | None = None,
        params: OpenAIParams | None = None,
    ) -> Stream[None, None]:
        raise NotImplementedError

    def context_stream(
        self,
        *,
        ctx: Context[DepsT],
        model: OPENAI_REGISTERED_LLMS,
        messages: Sequence[OpenAIMessage],
        tools: Sequence[Tool | ContextTool[..., Jsonable, DepsT]],
        params: OpenAIParams | None = None,
    ) -> Stream[DepsT, None]:
        raise NotImplementedError

    def structured_stream(
        self,
        *,
        model: OPENAI_REGISTERED_LLMS,
        messages: Sequence[OpenAIMessage],
        tools: Sequence[Tool] | None = None,
        format: type[FormatT],
        params: OpenAIParams | None = None,
    ) -> Stream[None, FormatT]:
        raise NotImplementedError

    def structured_context_stream(
        self,
        *,
        ctx: Context[DepsT],
        model: OPENAI_REGISTERED_LLMS,
        messages: Sequence[OpenAIMessage],
        tools: Sequence[Tool | ContextTool[..., Jsonable, DepsT]],
        format: type[FormatT],
        params: OpenAIParams | None = None,
    ) -> Stream[DepsT, FormatT]:
        raise NotImplementedError

    async def stream_async(
        self,
        *,
        model: OPENAI_REGISTERED_LLMS,
        messages: Sequence[OpenAIMessage],
        tools: Sequence[AsyncTool] | None = None,
        params: OpenAIParams | None = None,
    ) -> AsyncStream[None, None]:
        raise NotImplementedError

    async def context_stream_async(
        self,
        *,
        ctx: Context[DepsT],
        model: OPENAI_REGISTERED_LLMS,
        messages: Sequence[OpenAIMessage],
        tools: Sequence[AsyncTool | AsyncContextTool[..., Jsonable, DepsT]],
        params: OpenAIParams | None = None,
    ) -> AsyncStream[DepsT, None]:
        raise NotImplementedError

    async def structured_stream_async(
        self,
        *,
        model: OPENAI_REGISTERED_LLMS,
        messages: Sequence[OpenAIMessage],
        tools: Sequence[AsyncTool] | None = None,
        format: type[FormatT],
        params: OpenAIParams | None = None,
    ) -> AsyncStream[None, FormatT]:
        raise NotImplementedError

    async def structured_context_stream_async(
        self,
        *,
        ctx: Context[DepsT],
        model: OPENAI_REGISTERED_LLMS,
        messages: Sequence[OpenAIMessage],
        tools: Sequence[AsyncTool | AsyncContextTool[..., Jsonable, DepsT]],
        format: type[FormatT],
        params: OpenAIParams | None = None,
    ) -> AsyncStream[DepsT, FormatT]:
        raise NotImplementedError
