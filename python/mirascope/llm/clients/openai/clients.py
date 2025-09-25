"""OpenAI client implementation."""

import os
from collections.abc import Sequence
from contextvars import ContextVar
from functools import lru_cache
from typing import overload
from typing_extensions import Unpack

from openai import AsyncOpenAI, OpenAI

from ...context import Context, DepsT
from ...formatting import Format, FormattableT
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
    AsyncContextToolkit,
    AsyncTool,
    AsyncToolkit,
    ContextTool,
    ContextToolkit,
    Tool,
    Toolkit,
)
from ..base import BaseClient, Params
from . import _utils
from .model_ids import OpenAIModelId

OPENAI_CLIENT_CONTEXT: ContextVar["OpenAIClient | None"] = ContextVar(
    "OPENAI_CLIENT_CONTEXT", default=None
)


@lru_cache(maxsize=256)
def _openai_singleton(api_key: str | None, base_url: str | None) -> "OpenAIClient":
    """Return a cached OpenAI client instance for the given parameters."""
    return OpenAIClient(api_key=api_key, base_url=base_url)


def client(
    *, api_key: str | None = None, base_url: str | None = None
) -> "OpenAIClient":
    """Create or retrieve an OpenAI client with the given parameters.

    If a client has already been created with these parameters, it will be
    retrieved from cache and returned.

    Args:
        api_key: API key for authentication. If None, uses OPENAI_API_KEY env var.
        base_url: Base URL for the API. If None, uses OPENAI_BASE_URL env var.

    Returns:
        An OpenAI client instance.
    """
    api_key = api_key or os.getenv("OPENAI_API_KEY")
    base_url = base_url or os.getenv("OPENAI_BASE_URL")
    return _openai_singleton(api_key, base_url)


def get_client() -> "OpenAIClient":
    """Retrieve the current OpenAI client from context, or a global default.

    Returns:
        The current OpenAI client from context if available, otherwise
        a global default client based on environment variables.
    """
    ctx_client = OPENAI_CLIENT_CONTEXT.get()
    return ctx_client or client()


class OpenAIClient(BaseClient[OpenAIModelId, OpenAI]):
    """The client for the OpenAI LLM model."""

    @property
    def _context_var(self) -> ContextVar["OpenAIClient | None"]:
        return OPENAI_CLIENT_CONTEXT

    def __init__(
        self, *, api_key: str | None = None, base_url: str | None = None
    ) -> None:
        """Initialize the OpenAI client."""
        self.client = OpenAI(api_key=api_key, base_url=base_url)
        self.async_client = AsyncOpenAI(api_key=api_key, base_url=base_url)

    @overload
    def call(
        self,
        *,
        model_id: OpenAIModelId,
        messages: Sequence[Message],
        tools: Sequence[Tool] | Toolkit | None = None,
        format: None = None,
        **params: Unpack[Params],
    ) -> Response: ...

    @overload
    def call(
        self,
        *,
        model_id: OpenAIModelId,
        messages: Sequence[Message],
        tools: Sequence[Tool] | Toolkit | None = None,
        format: type[FormattableT] | Format[FormattableT],
        **params: Unpack[Params],
    ) -> Response[FormattableT]: ...

    @overload
    def call(
        self,
        *,
        model_id: OpenAIModelId,
        messages: Sequence[Message],
        tools: Sequence[Tool] | Toolkit | None = None,
        format: type[FormattableT] | Format[FormattableT] | None,
        **params: Unpack[Params],
    ) -> Response | Response[FormattableT]: ...

    def call(
        self,
        *,
        model_id: OpenAIModelId,
        messages: Sequence[Message],
        tools: Sequence[Tool] | Toolkit | None = None,
        format: type[FormattableT] | Format[FormattableT] | None = None,
        **params: Unpack[Params],
    ) -> Response | Response[FormattableT]:
        """Make a call to the OpenAI ChatCompletions API."""
        input_messages, format, kwargs = _utils.prepare_openai_request(
            model_id=model_id,
            messages=messages,
            tools=tools,
            format=format,
            params=params,
        )

        openai_response = self.client.chat.completions.create(**kwargs)

        assistant_message, finish_reason = _utils.decode_response(openai_response)

        return Response(
            raw=openai_response,
            provider="openai",
            model_id=model_id,
            params=params,
            tools=tools,
            input_messages=input_messages,
            assistant_message=assistant_message,
            finish_reason=finish_reason,
            format=format,
        )

    @overload
    def context_call(
        self,
        *,
        ctx: Context[DepsT],
        model_id: OpenAIModelId,
        messages: Sequence[Message],
        tools: Sequence[Tool | ContextTool[DepsT]]
        | ContextToolkit[DepsT]
        | None = None,
        format: None = None,
        **params: Unpack[Params],
    ) -> ContextResponse[DepsT, None]: ...

    @overload
    def context_call(
        self,
        *,
        ctx: Context[DepsT],
        model_id: OpenAIModelId,
        messages: Sequence[Message],
        tools: Sequence[Tool | ContextTool[DepsT]]
        | ContextToolkit[DepsT]
        | None = None,
        format: type[FormattableT] | Format[FormattableT],
        **params: Unpack[Params],
    ) -> ContextResponse[DepsT, FormattableT]: ...

    @overload
    def context_call(
        self,
        *,
        ctx: Context[DepsT],
        model_id: OpenAIModelId,
        messages: Sequence[Message],
        tools: Sequence[Tool | ContextTool[DepsT]]
        | ContextToolkit[DepsT]
        | None = None,
        format: type[FormattableT] | Format[FormattableT] | None,
        **params: Unpack[Params],
    ) -> ContextResponse[DepsT, None] | ContextResponse[DepsT, FormattableT]: ...

    def context_call(
        self,
        *,
        ctx: Context[DepsT],
        model_id: OpenAIModelId,
        messages: Sequence[Message],
        tools: Sequence[Tool | ContextTool[DepsT]]
        | ContextToolkit[DepsT]
        | None = None,
        format: type[FormattableT] | Format[FormattableT] | None = None,
        **params: Unpack[Params],
    ) -> ContextResponse[DepsT, None] | ContextResponse[DepsT, FormattableT]:
        """Make a call to the OpenAI ChatCompletions API."""
        input_messages, format, kwargs = _utils.prepare_openai_request(
            model_id=model_id,
            messages=messages,
            tools=tools,
            format=format,
            params=params,
        )

        openai_response = self.client.chat.completions.create(**kwargs)

        assistant_message, finish_reason = _utils.decode_response(openai_response)

        return ContextResponse(
            raw=openai_response,
            provider="openai",
            model_id=model_id,
            params=params,
            tools=tools,
            input_messages=input_messages,
            assistant_message=assistant_message,
            finish_reason=finish_reason,
            format=format,
        )

    @overload
    async def call_async(
        self,
        *,
        model_id: OpenAIModelId,
        messages: Sequence[Message],
        tools: Sequence[AsyncTool] | AsyncToolkit | None = None,
        format: None = None,
        **params: Unpack[Params],
    ) -> AsyncResponse: ...

    @overload
    async def call_async(
        self,
        *,
        model_id: OpenAIModelId,
        messages: Sequence[Message],
        tools: Sequence[AsyncTool] | AsyncToolkit | None = None,
        format: type[FormattableT] | Format[FormattableT],
        **params: Unpack[Params],
    ) -> AsyncResponse[FormattableT]: ...

    @overload
    async def call_async(
        self,
        *,
        model_id: OpenAIModelId,
        messages: Sequence[Message],
        tools: Sequence[AsyncTool] | AsyncToolkit | None = None,
        format: type[FormattableT] | Format[FormattableT] | None,
        **params: Unpack[Params],
    ) -> AsyncResponse | AsyncResponse[FormattableT]: ...

    async def call_async(
        self,
        *,
        model_id: OpenAIModelId,
        messages: Sequence[Message],
        tools: Sequence[AsyncTool] | AsyncToolkit | None = None,
        format: type[FormattableT] | Format[FormattableT] | None = None,
        **params: Unpack[Params],
    ) -> AsyncResponse | AsyncResponse[FormattableT]:
        """Make an async call to the OpenAI ChatCompletions API."""
        input_messages, format, kwargs = _utils.prepare_openai_request(
            model_id=model_id,
            params=params,
            messages=messages,
            tools=tools,
            format=format,
        )

        openai_response = await self.async_client.chat.completions.create(**kwargs)

        assistant_message, finish_reason = _utils.decode_response(openai_response)

        return AsyncResponse(
            raw=openai_response,
            provider="openai",
            model_id=model_id,
            params=params,
            tools=tools,
            input_messages=input_messages,
            assistant_message=assistant_message,
            finish_reason=finish_reason,
            format=format,
        )

    @overload
    async def context_call_async(
        self,
        *,
        ctx: Context[DepsT],
        model_id: OpenAIModelId,
        messages: Sequence[Message],
        tools: Sequence[AsyncTool | AsyncContextTool[DepsT]]
        | AsyncContextToolkit[DepsT]
        | None = None,
        format: None = None,
        **params: Unpack[Params],
    ) -> AsyncContextResponse[DepsT, None]: ...

    @overload
    async def context_call_async(
        self,
        *,
        ctx: Context[DepsT],
        model_id: OpenAIModelId,
        messages: Sequence[Message],
        tools: Sequence[AsyncTool | AsyncContextTool[DepsT]]
        | AsyncContextToolkit[DepsT]
        | None = None,
        format: type[FormattableT] | Format[FormattableT],
        **params: Unpack[Params],
    ) -> AsyncContextResponse[DepsT, FormattableT]: ...

    @overload
    async def context_call_async(
        self,
        *,
        ctx: Context[DepsT],
        model_id: OpenAIModelId,
        messages: Sequence[Message],
        tools: Sequence[AsyncTool | AsyncContextTool[DepsT]]
        | AsyncContextToolkit[DepsT]
        | None = None,
        format: type[FormattableT] | Format[FormattableT] | None,
        **params: Unpack[Params],
    ) -> (
        AsyncContextResponse[DepsT, None] | AsyncContextResponse[DepsT, FormattableT]
    ): ...

    async def context_call_async(
        self,
        *,
        ctx: Context[DepsT],
        model_id: OpenAIModelId,
        messages: Sequence[Message],
        tools: Sequence[AsyncTool | AsyncContextTool[DepsT]]
        | AsyncContextToolkit[DepsT]
        | None = None,
        format: type[FormattableT] | Format[FormattableT] | None = None,
        **params: Unpack[Params],
    ) -> AsyncContextResponse[DepsT, None] | AsyncContextResponse[DepsT, FormattableT]:
        """Make an async call to the OpenAI ChatCompletions API."""
        input_messages, format, kwargs = _utils.prepare_openai_request(
            model_id=model_id,
            params=params,
            messages=messages,
            tools=tools,
            format=format,
        )

        openai_response = await self.async_client.chat.completions.create(**kwargs)

        assistant_message, finish_reason = _utils.decode_response(openai_response)

        return AsyncContextResponse(
            raw=openai_response,
            provider="openai",
            model_id=model_id,
            params=params,
            tools=tools,
            input_messages=input_messages,
            assistant_message=assistant_message,
            finish_reason=finish_reason,
            format=format,
        )

    @overload
    def stream(
        self,
        *,
        model_id: OpenAIModelId,
        messages: Sequence[Message],
        tools: Sequence[Tool] | Toolkit | None = None,
        format: None = None,
        **params: Unpack[Params],
    ) -> StreamResponse: ...

    @overload
    def stream(
        self,
        *,
        model_id: OpenAIModelId,
        messages: Sequence[Message],
        tools: Sequence[Tool] | Toolkit | None = None,
        format: type[FormattableT] | Format[FormattableT],
        **params: Unpack[Params],
    ) -> StreamResponse[FormattableT]: ...

    @overload
    def stream(
        self,
        *,
        model_id: OpenAIModelId,
        messages: Sequence[Message],
        tools: Sequence[Tool] | Toolkit | None = None,
        format: type[FormattableT] | Format[FormattableT] | None,
        **params: Unpack[Params],
    ) -> StreamResponse | StreamResponse[FormattableT]: ...

    def stream(
        self,
        *,
        model_id: OpenAIModelId,
        messages: Sequence[Message],
        tools: Sequence[Tool] | Toolkit | None = None,
        format: type[FormattableT] | Format[FormattableT] | None = None,
        **params: Unpack[Params],
    ) -> StreamResponse | StreamResponse[FormattableT]:
        """Make a streaming call to the OpenAI API."""
        input_messages, format, kwargs = _utils.prepare_openai_request(
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

        return StreamResponse(
            provider="openai",
            model_id=model_id,
            params=params,
            tools=tools,
            input_messages=input_messages,
            chunk_iterator=chunk_iterator,
            format=format,
        )

    @overload
    def context_stream(
        self,
        *,
        ctx: Context[DepsT],
        model_id: OpenAIModelId,
        messages: Sequence[Message],
        tools: Sequence[Tool | ContextTool[DepsT]]
        | ContextToolkit[DepsT]
        | None = None,
        format: None = None,
        **params: Unpack[Params],
    ) -> ContextStreamResponse[DepsT]: ...

    @overload
    def context_stream(
        self,
        *,
        ctx: Context[DepsT],
        model_id: OpenAIModelId,
        messages: Sequence[Message],
        tools: Sequence[Tool | ContextTool[DepsT]]
        | ContextToolkit[DepsT]
        | None = None,
        format: type[FormattableT] | Format[FormattableT],
        **params: Unpack[Params],
    ) -> ContextStreamResponse[DepsT, FormattableT]: ...

    @overload
    def context_stream(
        self,
        *,
        ctx: Context[DepsT],
        model_id: OpenAIModelId,
        messages: Sequence[Message],
        tools: Sequence[Tool | ContextTool[DepsT]]
        | ContextToolkit[DepsT]
        | None = None,
        format: type[FormattableT] | Format[FormattableT] | None,
        **params: Unpack[Params],
    ) -> ContextStreamResponse[DepsT] | ContextStreamResponse[DepsT, FormattableT]: ...

    def context_stream(
        self,
        *,
        ctx: Context[DepsT],
        model_id: OpenAIModelId,
        messages: Sequence[Message],
        tools: Sequence[Tool | ContextTool[DepsT]]
        | ContextToolkit[DepsT]
        | None = None,
        format: type[FormattableT] | Format[FormattableT] | None = None,
        **params: Unpack[Params],
    ) -> ContextStreamResponse[DepsT] | ContextStreamResponse[DepsT, FormattableT]:
        """Make a streaming call to the OpenAI API."""
        input_messages, format, kwargs = _utils.prepare_openai_request(
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

        return ContextStreamResponse(
            provider="openai",
            model_id=model_id,
            params=params,
            tools=tools,
            input_messages=input_messages,
            chunk_iterator=chunk_iterator,
            format=format,
        )

    @overload
    async def stream_async(
        self,
        *,
        model_id: OpenAIModelId,
        messages: Sequence[Message],
        tools: Sequence[AsyncTool] | AsyncToolkit | None = None,
        format: None = None,
        **params: Unpack[Params],
    ) -> AsyncStreamResponse: ...

    @overload
    async def stream_async(
        self,
        *,
        model_id: OpenAIModelId,
        messages: Sequence[Message],
        tools: Sequence[AsyncTool] | AsyncToolkit | None = None,
        format: type[FormattableT] | Format[FormattableT],
        **params: Unpack[Params],
    ) -> AsyncStreamResponse[FormattableT]: ...

    @overload
    async def stream_async(
        self,
        *,
        model_id: OpenAIModelId,
        messages: Sequence[Message],
        tools: Sequence[AsyncTool] | AsyncToolkit | None = None,
        format: type[FormattableT] | Format[FormattableT] | None,
        **params: Unpack[Params],
    ) -> AsyncStreamResponse | AsyncStreamResponse[FormattableT]: ...

    async def stream_async(
        self,
        *,
        model_id: OpenAIModelId,
        messages: Sequence[Message],
        tools: Sequence[AsyncTool] | AsyncToolkit | None = None,
        format: type[FormattableT] | Format[FormattableT] | None = None,
        **params: Unpack[Params],
    ) -> AsyncStreamResponse | AsyncStreamResponse[FormattableT]:
        """Make an async streaming call to the OpenAI API."""
        input_messages, format, kwargs = _utils.prepare_openai_request(
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

        return AsyncStreamResponse(
            provider="openai",
            model_id=model_id,
            params=params,
            tools=tools,
            input_messages=input_messages,
            chunk_iterator=chunk_iterator,
            format=format,
        )

    @overload
    async def context_stream_async(
        self,
        *,
        ctx: Context[DepsT],
        model_id: OpenAIModelId,
        messages: Sequence[Message],
        tools: Sequence[AsyncTool | AsyncContextTool[DepsT]]
        | AsyncContextToolkit[DepsT]
        | None = None,
        format: None = None,
        **params: Unpack[Params],
    ) -> AsyncContextStreamResponse[DepsT]: ...

    @overload
    async def context_stream_async(
        self,
        *,
        ctx: Context[DepsT],
        model_id: OpenAIModelId,
        messages: Sequence[Message],
        tools: Sequence[AsyncTool | AsyncContextTool[DepsT]]
        | AsyncContextToolkit[DepsT]
        | None = None,
        format: type[FormattableT] | Format[FormattableT],
        **params: Unpack[Params],
    ) -> AsyncContextStreamResponse[DepsT, FormattableT]: ...

    @overload
    async def context_stream_async(
        self,
        *,
        ctx: Context[DepsT],
        model_id: OpenAIModelId,
        messages: Sequence[Message],
        tools: Sequence[AsyncTool | AsyncContextTool[DepsT]]
        | AsyncContextToolkit[DepsT]
        | None = None,
        format: type[FormattableT] | Format[FormattableT] | None,
        **params: Unpack[Params],
    ) -> (
        AsyncContextStreamResponse | AsyncContextStreamResponse[DepsT, FormattableT]
    ): ...

    async def context_stream_async(
        self,
        *,
        ctx: Context[DepsT],
        model_id: OpenAIModelId,
        messages: Sequence[Message],
        tools: Sequence[AsyncTool | AsyncContextTool[DepsT]]
        | AsyncContextToolkit[DepsT]
        | None = None,
        format: type[FormattableT] | Format[FormattableT] | None = None,
        **params: Unpack[Params],
    ) -> AsyncContextStreamResponse | AsyncContextStreamResponse[DepsT, FormattableT]:
        """Make an async streaming call to the OpenAI API."""
        input_messages, format, kwargs = _utils.prepare_openai_request(
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

        return AsyncContextStreamResponse(
            provider="openai",
            model_id=model_id,
            params=params,
            tools=tools,
            input_messages=input_messages,
            chunk_iterator=chunk_iterator,
            format=format,
        )
