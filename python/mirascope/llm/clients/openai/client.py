"""OpenAI client implementation."""

import os
from collections.abc import Sequence
from typing import cast, overload

import httpx
from openai import AsyncOpenAI, OpenAI

from ...context import Context, DepsT
from ...formatting import FormatT
from ...messages import Message
from ...responses import (
    AsyncContextResponse,
    AsyncContextStreamResponse,
    AsyncResponse,
    AsyncStreamResponse,
    ContextResponse,
    ContextStreamResponse,
    Response,
    StreamResponse,
)
from ...tools import (
    AsyncContextTool,
    AsyncTool,
    ContextTool,
    Tool,
)
from ..base import BaseClient
from . import _utils
from .model_ids import OpenAIModelId
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


class OpenAIClient(BaseClient[OpenAIParams, OpenAIModelId, OpenAI]):
    """The client for the OpenAI LLM model."""

    def __init__(
        self, *, api_key: str | None = None, base_url: str | httpx.URL | None = None
    ) -> None:
        """Initialize the OpenAIClient with optional API key.

        If api_key is not set, OpenAI will look for it in env as "OPENAI_API_KEY".
        """
        self.client = OpenAI(api_key=api_key, base_url=base_url)
        self.async_client = AsyncOpenAI(api_key=api_key, base_url=base_url)

    @overload
    def call(
        self,
        *,
        model_id: OpenAIModelId,
        messages: Sequence[Message],
        tools: Sequence[Tool] | None = None,
        format: None = None,
        params: OpenAIParams | None = None,
    ) -> Response: ...

    @overload
    def call(
        self,
        *,
        model_id: OpenAIModelId,
        messages: Sequence[Message],
        tools: Sequence[Tool] | None = None,
        format: type[FormatT],
        params: OpenAIParams | None = None,
    ) -> Response[FormatT]: ...

    @overload
    def call(
        self,
        *,
        model_id: OpenAIModelId,
        messages: Sequence[Message],
        tools: Sequence[Tool] | None = None,
        format: type[FormatT] | None,
        params: OpenAIParams | None = None,
    ) -> Response | Response[FormatT]: ...

    @overload
    def call(
        self,
        *,
        ctx: Context[DepsT],
        model_id: OpenAIModelId,
        messages: Sequence[Message],
        tools: Sequence[Tool | ContextTool[DepsT]] | None = None,
        format: None = None,
        params: OpenAIParams | None = None,
    ) -> ContextResponse[DepsT]: ...

    @overload
    def call(
        self,
        *,
        ctx: Context[DepsT],
        model_id: OpenAIModelId,
        messages: Sequence[Message],
        tools: Sequence[Tool | ContextTool[DepsT]] | None = None,
        format: type[FormatT],
        params: OpenAIParams | None = None,
    ) -> ContextResponse[DepsT, FormatT]: ...

    @overload
    def call(
        self,
        *,
        ctx: Context[DepsT],
        model_id: OpenAIModelId,
        messages: Sequence[Message],
        tools: Sequence[Tool | ContextTool[DepsT]] | None = None,
        format: type[FormatT] | None,
        params: OpenAIParams | None = None,
    ) -> ContextResponse[DepsT] | ContextResponse[DepsT, FormatT]: ...

    def call(
        self,
        *,
        ctx: Context[DepsT] | None = None,
        model_id: OpenAIModelId,
        messages: Sequence[Message],
        tools: Sequence[Tool] | Sequence[Tool | ContextTool[DepsT]] | None = None,
        format: type[FormatT] | None = None,
        params: OpenAIParams | None = None,
    ) -> (
        Response
        | Response[FormatT]
        | ContextResponse[DepsT]
        | ContextResponse[DepsT, FormatT]
    ):
        """Make a call to the OpenAI ChatCompletions API."""
        input_messages, kwargs = _utils.prepare_openai_request(
            model_id=model_id,
            messages=messages,
            tools=tools,
            format=format,
            params=params,
        )

        openai_response = self.client.chat.completions.create(**kwargs)

        assistant_message, finish_reason = _utils.decode_response(openai_response)

        if ctx is not None:
            return ContextResponse(
                raw=openai_response,
                provider="openai",
                model_id=model_id,
                params=params,
                tools=tools,
                input_messages=input_messages,
                assistant_message=assistant_message,
                finish_reason=finish_reason,
                format_type=format,
            )
        else:
            tools = cast(Sequence[Tool] | None, tools)
            return Response(
                raw=openai_response,
                provider="openai",
                model_id=model_id,
                params=params,
                tools=tools,
                input_messages=input_messages,
                assistant_message=assistant_message,
                finish_reason=finish_reason,
                format_type=format,
            )

    @overload
    async def call_async(
        self,
        *,
        model_id: OpenAIModelId,
        messages: Sequence[Message],
        tools: Sequence[AsyncTool] | None = None,
        format: None = None,
        params: OpenAIParams | None = None,
    ) -> AsyncResponse: ...

    @overload
    async def call_async(
        self,
        *,
        model_id: OpenAIModelId,
        messages: Sequence[Message],
        tools: Sequence[AsyncTool] | None = None,
        format: type[FormatT],
        params: OpenAIParams | None = None,
    ) -> AsyncResponse[FormatT]: ...

    @overload
    async def call_async(
        self,
        *,
        model_id: OpenAIModelId,
        messages: Sequence[Message],
        tools: Sequence[AsyncTool] | None = None,
        format: type[FormatT] | None,
        params: OpenAIParams | None = None,
    ) -> AsyncResponse | AsyncResponse[FormatT]: ...

    @overload
    async def call_async(
        self,
        *,
        ctx: Context[DepsT],
        model_id: OpenAIModelId,
        messages: Sequence[Message],
        tools: Sequence[AsyncTool | AsyncContextTool[DepsT]] | None = None,
        format: None = None,
        params: OpenAIParams | None = None,
    ) -> AsyncContextResponse[DepsT]: ...

    @overload
    async def call_async(
        self,
        *,
        ctx: Context[DepsT],
        model_id: OpenAIModelId,
        messages: Sequence[Message],
        tools: Sequence[AsyncTool | AsyncContextTool[DepsT]] | None = None,
        format: type[FormatT],
        params: OpenAIParams | None = None,
    ) -> AsyncContextResponse[DepsT, FormatT]: ...

    @overload
    async def call_async(
        self,
        *,
        ctx: Context[DepsT],
        model_id: OpenAIModelId,
        messages: Sequence[Message],
        tools: Sequence[AsyncTool | AsyncContextTool[DepsT]] | None = None,
        format: type[FormatT] | None,
        params: OpenAIParams | None = None,
    ) -> AsyncContextResponse[DepsT] | AsyncContextResponse[DepsT, FormatT]: ...

    async def call_async(
        self,
        *,
        ctx: Context[DepsT] | None = None,
        model_id: OpenAIModelId,
        messages: Sequence[Message],
        tools: Sequence[AsyncTool]
        | Sequence[AsyncTool | AsyncContextTool[DepsT]]
        | None = None,
        format: type[FormatT] | None = None,
        params: OpenAIParams | None = None,
    ) -> (
        AsyncResponse
        | AsyncResponse[FormatT]
        | AsyncContextResponse[DepsT]
        | AsyncContextResponse[DepsT, FormatT]
    ):
        """Make an async call to the OpenAI ChatCompletions API."""
        input_messages, kwargs = _utils.prepare_openai_request(
            model_id=model_id,
            params=params,
            messages=messages,
            tools=tools,
            format=format,
        )

        openai_response = await self.async_client.chat.completions.create(**kwargs)

        assistant_message, finish_reason = _utils.decode_response(openai_response)

        if ctx is not None:
            return AsyncContextResponse(
                raw=openai_response,
                provider="openai",
                model_id=model_id,
                params=params,
                tools=tools,
                input_messages=input_messages,
                assistant_message=assistant_message,
                finish_reason=finish_reason,
                format_type=format,
            )
        else:
            tools = cast(Sequence[AsyncTool] | None, tools)
            return AsyncResponse(
                raw=openai_response,
                provider="openai",
                model_id=model_id,
                params=params,
                tools=tools,
                input_messages=input_messages,
                assistant_message=assistant_message,
                finish_reason=finish_reason,
                format_type=format,
            )

    @overload
    def stream(
        self,
        *,
        model_id: OpenAIModelId,
        messages: Sequence[Message],
        tools: Sequence[Tool] | None = None,
        format: None = None,
        params: OpenAIParams | None = None,
    ) -> StreamResponse: ...

    @overload
    def stream(
        self,
        *,
        model_id: OpenAIModelId,
        messages: Sequence[Message],
        tools: Sequence[Tool] | None = None,
        format: type[FormatT],
        params: OpenAIParams | None = None,
    ) -> StreamResponse[FormatT]: ...

    @overload
    def stream(
        self,
        *,
        model_id: OpenAIModelId,
        messages: Sequence[Message],
        tools: Sequence[Tool] | None = None,
        format: type[FormatT] | None,
        params: OpenAIParams | None = None,
    ) -> StreamResponse | StreamResponse[FormatT]: ...

    @overload
    def stream(
        self,
        *,
        ctx: Context[DepsT],
        model_id: OpenAIModelId,
        messages: Sequence[Message],
        tools: Sequence[Tool | ContextTool[DepsT]] | None = None,
        format: None = None,
        params: OpenAIParams | None = None,
    ) -> ContextStreamResponse[DepsT]: ...

    @overload
    def stream(
        self,
        *,
        ctx: Context[DepsT],
        model_id: OpenAIModelId,
        messages: Sequence[Message],
        tools: Sequence[Tool | ContextTool[DepsT]] | None = None,
        format: type[FormatT],
        params: OpenAIParams | None = None,
    ) -> ContextStreamResponse[DepsT, FormatT]: ...

    @overload
    def stream(
        self,
        *,
        ctx: Context[DepsT],
        model_id: OpenAIModelId,
        messages: Sequence[Message],
        tools: Sequence[Tool | ContextTool[DepsT]] | None = None,
        format: type[FormatT] | None,
        params: OpenAIParams | None = None,
    ) -> ContextStreamResponse[DepsT] | ContextStreamResponse[DepsT, FormatT]: ...

    def stream(
        self,
        *,
        ctx: Context[DepsT] | None = None,
        model_id: OpenAIModelId,
        messages: Sequence[Message],
        tools: Sequence[Tool] | Sequence[Tool | ContextTool[DepsT]] | None = None,
        format: type[FormatT] | None = None,
        params: OpenAIParams | None = None,
    ) -> (
        StreamResponse
        | StreamResponse[FormatT]
        | ContextStreamResponse[DepsT]
        | ContextStreamResponse[DepsT, FormatT]
    ):
        """Make a streaming call to the OpenAI API."""
        input_messages, kwargs = _utils.prepare_openai_request(
            model_id=model_id,
            messages=messages,
            tools=tools,
            format=format,
            params=params,
        )

        openai_stream = self.client.chat.completions.create(
            **kwargs,
            stream=True,
        )

        chunk_iterator = _utils.convert_openai_stream_to_chunk_iterator(openai_stream)

        if ctx is not None:
            return ContextStreamResponse(
                provider="openai",
                model_id=model_id,
                params=params,
                tools=tools,
                input_messages=input_messages,
                chunk_iterator=chunk_iterator,
                format_type=format,
            )
        else:
            tools = cast(Sequence[Tool] | None, tools)
            return StreamResponse(
                provider="openai",
                model_id=model_id,
                params=params,
                tools=tools,
                input_messages=input_messages,
                chunk_iterator=chunk_iterator,
                format_type=format,
            )

    @overload
    async def stream_async(
        self,
        *,
        model_id: OpenAIModelId,
        messages: Sequence[Message],
        tools: Sequence[AsyncTool] | None = None,
        format: None = None,
        params: OpenAIParams | None = None,
    ) -> AsyncStreamResponse: ...

    @overload
    async def stream_async(
        self,
        *,
        model_id: OpenAIModelId,
        messages: Sequence[Message],
        tools: Sequence[AsyncTool] | None = None,
        format: type[FormatT],
        params: OpenAIParams | None = None,
    ) -> AsyncStreamResponse[FormatT]: ...

    @overload
    async def stream_async(
        self,
        *,
        model_id: OpenAIModelId,
        messages: Sequence[Message],
        tools: Sequence[AsyncTool] | None = None,
        format: type[FormatT] | None,
        params: OpenAIParams | None = None,
    ) -> AsyncStreamResponse | AsyncStreamResponse[FormatT]: ...

    @overload
    async def stream_async(
        self,
        *,
        ctx: Context[DepsT],
        model_id: OpenAIModelId,
        messages: Sequence[Message],
        tools: Sequence[AsyncTool | AsyncContextTool[DepsT]] | None = None,
        format: None = None,
        params: OpenAIParams | None = None,
    ) -> AsyncContextStreamResponse[DepsT]: ...

    @overload
    async def stream_async(
        self,
        *,
        ctx: Context[DepsT],
        model_id: OpenAIModelId,
        messages: Sequence[Message],
        tools: Sequence[AsyncTool | AsyncContextTool[DepsT]] | None = None,
        format: type[FormatT],
        params: OpenAIParams | None = None,
    ) -> AsyncContextStreamResponse[DepsT, FormatT]: ...

    @overload
    async def stream_async(
        self,
        *,
        ctx: Context[DepsT],
        model_id: OpenAIModelId,
        messages: Sequence[Message],
        tools: Sequence[AsyncTool | AsyncContextTool[DepsT]] | None = None,
        format: type[FormatT] | None,
        params: OpenAIParams | None = None,
    ) -> (
        AsyncContextStreamResponse[DepsT] | AsyncContextStreamResponse[DepsT, FormatT]
    ): ...

    async def stream_async(
        self,
        *,
        ctx: Context[DepsT] | None = None,
        model_id: OpenAIModelId,
        messages: Sequence[Message],
        tools: Sequence[AsyncTool]
        | Sequence[AsyncTool | AsyncContextTool[DepsT]]
        | None = None,
        format: type[FormatT] | None = None,
        params: OpenAIParams | None = None,
    ) -> (
        AsyncStreamResponse
        | AsyncStreamResponse[FormatT]
        | AsyncContextStreamResponse[DepsT]
        | AsyncContextStreamResponse[DepsT, FormatT]
    ):
        """Make an async streaming call to the OpenAI API."""
        input_messages, kwargs = _utils.prepare_openai_request(
            model_id=model_id,
            messages=messages,
            tools=tools,
            format=format,
            params=params,
        )

        openai_stream = await self.async_client.chat.completions.create(
            **kwargs,
            stream=True,
        )

        chunk_iterator = _utils.convert_openai_stream_to_async_chunk_iterator(
            openai_stream
        )

        if ctx is not None:
            return AsyncContextStreamResponse(
                provider="openai",
                model_id=model_id,
                params=params,
                tools=tools,
                input_messages=input_messages,
                chunk_iterator=chunk_iterator,
                format_type=format,
            )
        else:
            tools = cast(Sequence[AsyncTool] | None, tools)
            return AsyncStreamResponse(
                provider="openai",
                model_id=model_id,
                params=params,
                tools=tools,
                input_messages=input_messages,
                chunk_iterator=chunk_iterator,
                format_type=format,
            )
