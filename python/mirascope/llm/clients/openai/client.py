"""OpenAI client implementation."""

import os
from collections.abc import Sequence
from typing import overload

import httpx
from openai import OpenAI

from ...context import Context, DepsT
from ...formatting import FormatT
from ...messages import Message
from ...responses import (
    AsyncContextResponse,
    AsyncResponse,
    AsyncStreamResponse,
    ContextResponse,
    Response,
    StreamResponse,
)
from ...tools import AsyncContextTool, AsyncTool, ContextTool, Tool, Toolkit
from ..base import BaseClient
from . import _utils
from .models import OpenAIModel
from .params import OpenAIParams

_global_client: "OpenAIClient | None" = None


def get_openai_client() -> "OpenAIClient":
    """Get a global OpenAI client instance.

    Returns:
        An OpenAI client instance. Multiple calls return the same instance.
    """
    global _global_client
    if _global_client is None:
        api_key = os.getenv("OPENAI_API_KEY")
        _global_client = OpenAIClient(api_key=api_key)
    return _global_client


class OpenAIClient(BaseClient[OpenAIParams, OpenAIModel, OpenAI]):
    """The client for the OpenAI LLM model."""

    def __init__(
        self, *, api_key: str | None = None, base_url: str | httpx.URL | None = None
    ) -> None:
        """Initialize the OpenAIClient with optional API key.

        If api_key is not set, OpenAI will look for it in env as "OPENAI_API_KEY".
        """
        self.client = OpenAI(api_key=api_key, base_url=base_url)

    @overload
    def call(
        self,
        *,
        model: OpenAIModel,
        messages: Sequence[Message],
        tools: Sequence[Tool] | None = None,
        params: OpenAIParams | None = None,
        format: None = None,
    ) -> Response: ...

    @overload
    def call(
        self,
        *,
        model: OpenAIModel,
        messages: Sequence[Message],
        tools: Sequence[Tool] | None = None,
        params: OpenAIParams | None = None,
        format: type[FormatT],
    ) -> Response[FormatT]: ...

    def call(
        self,
        *,
        model: OpenAIModel,
        messages: Sequence[Message],
        tools: Sequence[Tool] | None = None,
        params: OpenAIParams | None = None,
        format: type[FormatT] | None = None,
    ) -> Response | Response[FormatT]:
        """Make a call to the OpenAI ChatCompletions API."""
        if params:
            raise NotImplementedError("param use not yet supported")

        input_messages, message_params, tool_params, response_format = (
            _utils.prepare_openai_request(
                model=model, messages=messages, tools=tools, format=format
            )
        )

        openai_response = self.client.chat.completions.create(
            model=model,
            messages=message_params,
            tools=tool_params,
            response_format=response_format,
        )

        assistant_message, finish_reason = _utils.decode_response(openai_response)

        return Response(
            raw=openai_response,
            provider="openai",
            model=model,
            params=params,
            toolkit=Toolkit(tools=tools),
            input_messages=input_messages,
            assistant_message=assistant_message,
            finish_reason=finish_reason,
            format_type=format,
        )

    @overload
    def context_call(
        self,
        *,
        ctx: Context[DepsT],
        model: OpenAIModel,
        messages: Sequence[Message],
        tools: Sequence[Tool | ContextTool[DepsT]],
        params: OpenAIParams | None = None,
        format: None = None,
    ) -> ContextResponse[DepsT, None]: ...

    @overload
    def context_call(
        self,
        *,
        ctx: Context[DepsT],
        model: OpenAIModel,
        messages: Sequence[Message],
        tools: Sequence[Tool | ContextTool[DepsT]],
        params: OpenAIParams | None = None,
        format: type[FormatT],
    ) -> ContextResponse[DepsT, FormatT]: ...

    def context_call(
        self,
        *,
        ctx: Context[DepsT],
        model: OpenAIModel,
        messages: Sequence[Message],
        tools: Sequence[Tool | ContextTool[DepsT]],
        params: OpenAIParams | None = None,
        format: type[FormatT] | None = None,
    ) -> ContextResponse[DepsT, None] | ContextResponse[DepsT, FormatT]:
        raise NotImplementedError

    @overload
    async def call_async(
        self,
        *,
        model: OpenAIModel,
        messages: Sequence[Message],
        tools: Sequence[AsyncTool] | None = None,
        params: OpenAIParams | None = None,
        format: None = None,
    ) -> AsyncResponse: ...

    @overload
    async def call_async(
        self,
        *,
        model: OpenAIModel,
        messages: Sequence[Message],
        tools: Sequence[AsyncTool] | None = None,
        params: OpenAIParams | None = None,
        format: type[FormatT],
    ) -> AsyncResponse[FormatT]: ...

    async def call_async(
        self,
        *,
        model: OpenAIModel,
        messages: Sequence[Message],
        tools: Sequence[AsyncTool] | None = None,
        params: OpenAIParams | None = None,
        format: type[FormatT] | None = None,
    ) -> AsyncResponse | AsyncResponse[FormatT]:
        raise NotImplementedError

    @overload
    async def context_call_async(
        self,
        *,
        ctx: Context[DepsT],
        model: OpenAIModel,
        messages: Sequence[Message],
        tools: Sequence[AsyncTool | AsyncContextTool[DepsT]],
        params: OpenAIParams | None = None,
        format: None = None,
    ) -> AsyncContextResponse[DepsT, None]: ...

    @overload
    async def context_call_async(
        self,
        *,
        ctx: Context[DepsT],
        model: OpenAIModel,
        messages: Sequence[Message],
        tools: Sequence[AsyncTool | AsyncContextTool[DepsT]],
        params: OpenAIParams | None = None,
        format: type[FormatT],
    ) -> AsyncContextResponse[DepsT, FormatT]: ...

    async def context_call_async(
        self,
        *,
        ctx: Context[DepsT],
        model: OpenAIModel,
        messages: Sequence[Message],
        tools: Sequence[AsyncTool | AsyncContextTool[DepsT]],
        params: OpenAIParams | None = None,
        format: type[FormatT] | None = None,
    ) -> AsyncContextResponse[DepsT, None] | AsyncContextResponse[DepsT, FormatT]:
        raise NotImplementedError

    @overload
    def stream(
        self,
        *,
        model: OpenAIModel,
        messages: Sequence[Message],
        tools: Sequence[Tool] | None = None,
        params: OpenAIParams | None = None,
        format: None = None,
    ) -> StreamResponse: ...

    @overload
    def stream(
        self,
        *,
        model: OpenAIModel,
        messages: Sequence[Message],
        tools: Sequence[Tool] | None = None,
        params: OpenAIParams | None = None,
        format: type[FormatT],
    ) -> StreamResponse[FormatT]: ...

    def stream(
        self,
        *,
        model: OpenAIModel,
        messages: Sequence[Message],
        tools: Sequence[Tool] | None = None,
        params: OpenAIParams | None = None,
        format: type[FormatT] | None = None,
    ) -> StreamResponse | StreamResponse[FormatT]:
        """Make a streaming call to the OpenAI API."""
        if params:
            raise NotImplementedError("param use not yet supported")

        input_messages, message_params, tool_params, response_format = (
            _utils.prepare_openai_request(
                model=model, messages=messages, tools=tools, format=format
            )
        )

        openai_stream = self.client.chat.completions.create(
            model=model,
            messages=message_params,
            tools=tool_params,
            response_format=response_format,
            stream=True,
        )

        chunk_iterator = _utils.convert_openai_stream_to_chunk_iterator(openai_stream)

        return StreamResponse(
            provider="openai",
            model=model,
            params=params,
            toolkit=Toolkit(tools=tools),
            input_messages=input_messages,
            chunk_iterator=chunk_iterator,
            format_type=format,
        )

    @overload
    def context_stream(
        self,
        *,
        ctx: Context[DepsT],
        model: OpenAIModel,
        messages: Sequence[Message],
        tools: Sequence[Tool | ContextTool[DepsT]],
        params: OpenAIParams | None = None,
        format: None = None,
    ) -> StreamResponse: ...

    @overload
    def context_stream(
        self,
        *,
        ctx: Context[DepsT],
        model: OpenAIModel,
        messages: Sequence[Message],
        tools: Sequence[Tool | ContextTool[DepsT]],
        params: OpenAIParams | None = None,
        format: type[FormatT],
    ) -> StreamResponse[FormatT]: ...

    def context_stream(
        self,
        *,
        ctx: Context[DepsT],
        model: OpenAIModel,
        messages: Sequence[Message],
        tools: Sequence[Tool | ContextTool[DepsT]],
        params: OpenAIParams | None = None,
        format: type[FormatT] | None = None,
    ) -> StreamResponse | StreamResponse[FormatT]:
        raise NotImplementedError

    @overload
    async def stream_async(
        self,
        *,
        model: OpenAIModel,
        messages: Sequence[Message],
        tools: Sequence[AsyncTool] | None = None,
        params: OpenAIParams | None = None,
        format: None = None,
    ) -> AsyncStreamResponse: ...

    @overload
    async def stream_async(
        self,
        *,
        model: OpenAIModel,
        messages: Sequence[Message],
        tools: Sequence[AsyncTool] | None = None,
        params: OpenAIParams | None = None,
        format: type[FormatT],
    ) -> AsyncStreamResponse[FormatT]: ...

    async def stream_async(
        self,
        *,
        model: OpenAIModel,
        messages: Sequence[Message],
        tools: Sequence[AsyncTool] | None = None,
        params: OpenAIParams | None = None,
        format: type[FormatT] | None = None,
    ) -> AsyncStreamResponse | AsyncStreamResponse[FormatT]:
        raise NotImplementedError

    @overload
    async def context_stream_async(
        self,
        *,
        ctx: Context[DepsT],
        model: OpenAIModel,
        messages: Sequence[Message],
        tools: Sequence[AsyncTool | AsyncContextTool[DepsT]],
        params: OpenAIParams | None = None,
        format: None = None,
    ) -> AsyncStreamResponse: ...

    @overload
    async def context_stream_async(
        self,
        *,
        ctx: Context[DepsT],
        model: OpenAIModel,
        messages: Sequence[Message],
        tools: Sequence[AsyncTool | AsyncContextTool[DepsT]],
        params: OpenAIParams | None = None,
        format: type[FormatT],
    ) -> AsyncStreamResponse[FormatT]: ...

    async def context_stream_async(
        self,
        *,
        ctx: Context[DepsT],
        model: OpenAIModel,
        messages: Sequence[Message],
        tools: Sequence[AsyncTool | AsyncContextTool[DepsT]],
        params: OpenAIParams | None = None,
        format: type[FormatT] | None = None,
    ) -> AsyncStreamResponse | AsyncStreamResponse[FormatT]:
        raise NotImplementedError
