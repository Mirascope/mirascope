"""OpenAI client implementation."""

from collections.abc import Sequence

import httpx
from openai import OpenAI

from ...context import Context, DepsT
from ...formatting import FormatT
from ...messages import Message
from ...responses import (
    Response,
    StreamResponse,
)
from ...streams import AsyncStream, Stream
from ...tools import AsyncContextTool, AsyncTool, ContextTool, Tool
from ...types import Jsonable
from ..base import BaseClient
from ._utils import _decode_response, _encode_messages
from .models import OpenAIModel
from .params import OpenAIParams


class OpenAIClient(BaseClient[OpenAIParams, OpenAIModel, OpenAI]):
    """The client for the OpenAI LLM model."""

    def __init__(
        self, *, api_key: str | None = None, base_url: str | httpx.URL | None = None
    ) -> None:
        """Initialize the OpenAIClient with optional API key.

        If api_key is not set, OpenAI will look for it in env as "OPENAI_API_KEY".
        """
        self.client = OpenAI(api_key=api_key, base_url=base_url)

    def call(
        self,
        *,
        model: OpenAIModel,
        messages: Sequence[Message],
        tools: Sequence[Tool] | None = None,
        params: OpenAIParams | None = None,
    ) -> Response[None]:
        """Make a call to the OpenAI ChatCompletions API."""
        if tools:
            raise NotImplementedError("tool use not yet supported")
        if params:
            raise NotImplementedError("param use not yet supported")

        openai_response = self.client.chat.completions.create(
            model=model,
            messages=_encode_messages(messages),
        )

        assistant_message, finish_reason = _decode_response(openai_response)

        return Response(
            provider="openai",
            model=model,
            raw=openai_response,
            input_messages=messages,
            assistant_message=assistant_message,
            finish_reason=finish_reason,
        )

    def context_call(
        self,
        *,
        ctx: Context[DepsT],
        model: OpenAIModel,
        messages: Sequence[Message],
        tools: Sequence[Tool | ContextTool[..., Jsonable, DepsT]],
        params: OpenAIParams | None = None,
    ) -> Response[None]:
        raise NotImplementedError

    def structured_call(
        self,
        *,
        model: OpenAIModel,
        messages: Sequence[Message],
        tools: Sequence[Tool] | None = None,
        format: type[FormatT],
        params: OpenAIParams | None = None,
    ) -> Response[FormatT]:
        raise NotImplementedError

    def structured_context_call(
        self,
        *,
        ctx: Context[DepsT],
        model: OpenAIModel,
        messages: Sequence[Message],
        tools: Sequence[Tool | ContextTool[..., Jsonable, DepsT]],
        format: type[FormatT],
        params: OpenAIParams | None = None,
    ) -> Response[FormatT]:
        raise NotImplementedError

    async def call_async(
        self,
        *,
        model: OpenAIModel,
        messages: Sequence[Message],
        tools: Sequence[AsyncTool] | None = None,
        params: OpenAIParams | None = None,
    ) -> Response[None]:
        raise NotImplementedError

    async def context_call_async(
        self,
        *,
        ctx: Context[DepsT],
        model: OpenAIModel,
        messages: Sequence[Message],
        tools: Sequence[AsyncTool | AsyncContextTool[..., Jsonable, DepsT]],
        params: OpenAIParams | None = None,
    ) -> Response[None]:
        raise NotImplementedError

    async def structured_call_async(
        self,
        *,
        model: OpenAIModel,
        messages: Sequence[Message],
        tools: Sequence[AsyncTool] | None = None,
        format: type[FormatT],
        params: OpenAIParams | None = None,
    ) -> Response[FormatT]:
        raise NotImplementedError

    async def structured_context_call_async(
        self,
        *,
        ctx: Context[DepsT],
        model: OpenAIModel,
        messages: Sequence[Message],
        tools: Sequence[AsyncTool | AsyncContextTool[..., Jsonable, DepsT]],
        format: type[FormatT],
        params: OpenAIParams | None = None,
    ) -> Response[FormatT]:
        raise NotImplementedError

    def stream(
        self,
        *,
        model: OpenAIModel,
        messages: Sequence[Message],
        tools: Sequence[Tool] | None = None,
        params: OpenAIParams | None = None,
    ) -> StreamResponse[Stream, None]:
        raise NotImplementedError

    def context_stream(
        self,
        *,
        ctx: Context[DepsT],
        model: OpenAIModel,
        messages: Sequence[Message],
        tools: Sequence[Tool | ContextTool[..., Jsonable, DepsT]],
        params: OpenAIParams | None = None,
    ) -> StreamResponse[Stream, None]:
        raise NotImplementedError

    def structured_stream(
        self,
        *,
        model: OpenAIModel,
        messages: Sequence[Message],
        tools: Sequence[Tool] | None = None,
        format: type[FormatT],
        params: OpenAIParams | None = None,
    ) -> StreamResponse[Stream, FormatT]:
        raise NotImplementedError

    def structured_context_stream(
        self,
        *,
        ctx: Context[DepsT],
        model: OpenAIModel,
        messages: Sequence[Message],
        tools: Sequence[Tool | ContextTool[..., Jsonable, DepsT]],
        format: type[FormatT],
        params: OpenAIParams | None = None,
    ) -> StreamResponse[Stream, FormatT]:
        raise NotImplementedError

    async def stream_async(
        self,
        *,
        model: OpenAIModel,
        messages: Sequence[Message],
        tools: Sequence[AsyncTool] | None = None,
        params: OpenAIParams | None = None,
    ) -> StreamResponse[AsyncStream, None]:
        raise NotImplementedError

    async def context_stream_async(
        self,
        *,
        ctx: Context[DepsT],
        model: OpenAIModel,
        messages: Sequence[Message],
        tools: Sequence[AsyncTool | AsyncContextTool[..., Jsonable, DepsT]],
        params: OpenAIParams | None = None,
    ) -> StreamResponse[AsyncStream, None]:
        raise NotImplementedError

    async def structured_stream_async(
        self,
        *,
        model: OpenAIModel,
        messages: Sequence[Message],
        tools: Sequence[AsyncTool] | None = None,
        format: type[FormatT],
        params: OpenAIParams | None = None,
    ) -> StreamResponse[AsyncStream, FormatT]:
        raise NotImplementedError

    async def structured_context_stream_async(
        self,
        *,
        ctx: Context[DepsT],
        model: OpenAIModel,
        messages: Sequence[Message],
        tools: Sequence[AsyncTool | AsyncContextTool[..., Jsonable, DepsT]],
        format: type[FormatT],
        params: OpenAIParams | None = None,
    ) -> StreamResponse[AsyncStream, FormatT]:
        raise NotImplementedError
