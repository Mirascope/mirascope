"""Google client implementation."""

import os
from collections.abc import Sequence
from contextvars import ContextVar
from functools import lru_cache
from typing import overload

from google.genai import Client
from google.genai.types import HttpOptions

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
    AsyncTool,
    ContextTool,
    Tool,
)
from ..base import BaseClient
from . import _utils
from .model_ids import GoogleModelId
from .params import GoogleParams

GOOGLE_CLIENT_CONTEXT: ContextVar["GoogleClient | None"] = ContextVar(
    "GOOGLE_CLIENT_CONTEXT", default=None
)


@lru_cache(maxsize=256)
def _google_singleton(api_key: str | None, base_url: str | None) -> "GoogleClient":
    """Return a cached Google client instance for the given parameters."""
    return GoogleClient(api_key=api_key, base_url=base_url)


def client(
    *, api_key: str | None = None, base_url: str | None = None
) -> "GoogleClient":
    """Create or retrieve a Google client with the given parameters.

    If a client has already been created with these parameters, it will be
    retrieved from cache and returned.

    Args:
        api_key: API key for authentication. If None, uses GOOGLE_API_KEY env var.
        base_url: Base URL for the API. If None, uses GOOGLE_BASE_URL env var.

    Returns:
        A Google client instance.
    """
    api_key = api_key or os.getenv("GOOGLE_API_KEY")
    base_url = base_url or os.getenv("GOOGLE_BASE_URL")
    return _google_singleton(api_key, base_url)


def get_client() -> "GoogleClient":
    """Retrieve the current Google client from context, or a global default.

    Returns:
        The current Google client from context if available, otherwise
        a global default client based on environment variables.
    """
    ctx_client = GOOGLE_CLIENT_CONTEXT.get()
    return ctx_client or client()


class GoogleClient(BaseClient[GoogleParams, GoogleModelId, Client]):
    """The client for the Google LLM model."""

    @property
    def _context_var(self) -> ContextVar["GoogleClient | None"]:
        return GOOGLE_CLIENT_CONTEXT

    def __init__(
        self, *, api_key: str | None = None, base_url: str | None = None
    ) -> None:
        """Initialize the Google client."""
        http_options = None
        if base_url:
            http_options = HttpOptions(base_url=base_url)

        self.client = Client(api_key=api_key, http_options=http_options)

    @overload
    def call(
        self,
        *,
        model_id: GoogleModelId,
        messages: Sequence[Message],
        tools: Sequence[Tool] | None = None,
        format: None = None,
        params: GoogleParams | None = None,
    ) -> Response: ...

    @overload
    def call(
        self,
        *,
        model_id: GoogleModelId,
        messages: Sequence[Message],
        tools: Sequence[Tool] | None = None,
        format: type[FormattableT] | Format[FormattableT],
        params: GoogleParams | None = None,
    ) -> Response[FormattableT]: ...

    @overload
    def call(
        self,
        *,
        model_id: GoogleModelId,
        messages: Sequence[Message],
        tools: Sequence[Tool] | None = None,
        format: type[FormattableT] | Format[FormattableT] | None,
        params: GoogleParams | None = None,
    ) -> Response | Response[FormattableT]: ...

    def call(
        self,
        *,
        model_id: GoogleModelId,
        messages: Sequence[Message],
        tools: Sequence[Tool] | None = None,
        format: type[FormattableT] | Format[FormattableT] | None = None,
        params: GoogleParams | None = None,
    ) -> Response | Response[FormattableT]:
        """Make a call to the Google GenAI API."""
        input_messages, format, contents, config = _utils.prepare_google_request(
            model_id, messages, tools, format, params=params
        )

        google_response = self.client.models.generate_content(
            model=model_id,
            contents=contents,
            config=config,
        )

        assistant_message, finish_reason = _utils.decode_response(google_response)

        return Response(
            raw=google_response,
            provider="google",
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
        model_id: GoogleModelId,
        messages: Sequence[Message],
        tools: Sequence[Tool | ContextTool[DepsT]] | None = None,
        format: None = None,
        params: GoogleParams | None = None,
    ) -> ContextResponse[DepsT, None]: ...

    @overload
    def context_call(
        self,
        *,
        ctx: Context[DepsT],
        model_id: GoogleModelId,
        messages: Sequence[Message],
        tools: Sequence[Tool | ContextTool[DepsT]] | None = None,
        format: type[FormattableT] | Format[FormattableT],
        params: GoogleParams | None = None,
    ) -> ContextResponse[DepsT, FormattableT]: ...

    @overload
    def context_call(
        self,
        *,
        ctx: Context[DepsT],
        model_id: GoogleModelId,
        messages: Sequence[Message],
        tools: Sequence[Tool | ContextTool[DepsT]] | None = None,
        format: type[FormattableT] | Format[FormattableT] | None,
        params: GoogleParams | None = None,
    ) -> ContextResponse[DepsT, None] | ContextResponse[DepsT, FormattableT]: ...

    def context_call(
        self,
        *,
        ctx: Context[DepsT],
        model_id: GoogleModelId,
        messages: Sequence[Message],
        tools: Sequence[Tool | ContextTool[DepsT]] | None = None,
        format: type[FormattableT] | Format[FormattableT] | None = None,
        params: GoogleParams | None = None,
    ) -> ContextResponse[DepsT, None] | ContextResponse[DepsT, FormattableT]:
        """Make a call to the Google GenAI API."""
        input_messages, format, contents, config = _utils.prepare_google_request(
            model_id, messages, tools, format, params=params
        )

        google_response = self.client.models.generate_content(
            model=model_id,
            contents=contents,
            config=config,
        )

        assistant_message, finish_reason = _utils.decode_response(google_response)

        return ContextResponse(
            raw=google_response,
            provider="google",
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
        model_id: GoogleModelId,
        messages: Sequence[Message],
        tools: Sequence[AsyncTool] | None = None,
        format: None = None,
        params: GoogleParams | None = None,
    ) -> AsyncResponse: ...

    @overload
    async def call_async(
        self,
        *,
        model_id: GoogleModelId,
        messages: Sequence[Message],
        tools: Sequence[AsyncTool] | None = None,
        format: type[FormattableT] | Format[FormattableT],
        params: GoogleParams | None = None,
    ) -> AsyncResponse[FormattableT]: ...

    @overload
    async def call_async(
        self,
        *,
        model_id: GoogleModelId,
        messages: Sequence[Message],
        tools: Sequence[AsyncTool] | None = None,
        format: type[FormattableT] | Format[FormattableT] | None,
        params: GoogleParams | None = None,
    ) -> AsyncResponse | AsyncResponse[FormattableT]: ...

    async def call_async(
        self,
        *,
        model_id: GoogleModelId,
        messages: Sequence[Message],
        tools: Sequence[AsyncTool] | None = None,
        format: type[FormattableT] | Format[FormattableT] | None = None,
        params: GoogleParams | None = None,
    ) -> AsyncResponse | AsyncResponse[FormattableT]:
        """Make an async call to the Google GenAI API."""
        input_messages, format, contents, config = _utils.prepare_google_request(
            model_id, messages, tools, format, params=params
        )

        google_response = await self.client.aio.models.generate_content(
            model=model_id,
            contents=contents,
            config=config,
        )

        assistant_message, finish_reason = _utils.decode_response(google_response)

        return AsyncResponse(
            raw=google_response,
            provider="google",
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
        model_id: GoogleModelId,
        messages: Sequence[Message],
        tools: Sequence[AsyncTool | AsyncContextTool[DepsT]] | None = None,
        format: None = None,
        params: GoogleParams | None = None,
    ) -> AsyncContextResponse[DepsT, None]: ...

    @overload
    async def context_call_async(
        self,
        *,
        ctx: Context[DepsT],
        model_id: GoogleModelId,
        messages: Sequence[Message],
        tools: Sequence[AsyncTool | AsyncContextTool[DepsT]] | None = None,
        format: type[FormattableT] | Format[FormattableT],
        params: GoogleParams | None = None,
    ) -> AsyncContextResponse[DepsT, FormattableT]: ...

    @overload
    async def context_call_async(
        self,
        *,
        ctx: Context[DepsT],
        model_id: GoogleModelId,
        messages: Sequence[Message],
        tools: Sequence[AsyncTool | AsyncContextTool[DepsT]] | None = None,
        format: type[FormattableT] | Format[FormattableT] | None,
        params: GoogleParams | None = None,
    ) -> (
        AsyncContextResponse[DepsT, None] | AsyncContextResponse[DepsT, FormattableT]
    ): ...

    async def context_call_async(
        self,
        *,
        ctx: Context[DepsT],
        model_id: GoogleModelId,
        messages: Sequence[Message],
        tools: Sequence[AsyncTool | AsyncContextTool[DepsT]] | None = None,
        format: type[FormattableT] | Format[FormattableT] | None = None,
        params: GoogleParams | None = None,
    ) -> AsyncContextResponse[DepsT, None] | AsyncContextResponse[DepsT, FormattableT]:
        """Make an async call to the Google GenAI API."""
        input_messages, format, contents, config = _utils.prepare_google_request(
            model_id, messages, tools, format, params=params
        )

        google_response = await self.client.aio.models.generate_content(
            model=model_id,
            contents=contents,
            config=config,
        )

        assistant_message, finish_reason = _utils.decode_response(google_response)

        return AsyncContextResponse(
            raw=google_response,
            provider="google",
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
        model_id: GoogleModelId,
        messages: Sequence[Message],
        tools: Sequence[Tool] | None = None,
        format: None = None,
        params: GoogleParams | None = None,
    ) -> StreamResponse: ...

    @overload
    def stream(
        self,
        *,
        model_id: GoogleModelId,
        messages: Sequence[Message],
        tools: Sequence[Tool] | None = None,
        format: type[FormattableT] | Format[FormattableT],
        params: GoogleParams | None = None,
    ) -> StreamResponse[FormattableT]: ...

    @overload
    def stream(
        self,
        *,
        model_id: GoogleModelId,
        messages: Sequence[Message],
        tools: Sequence[Tool] | None = None,
        format: type[FormattableT] | Format[FormattableT] | None,
        params: GoogleParams | None = None,
    ) -> StreamResponse | StreamResponse[FormattableT]: ...

    def stream(
        self,
        *,
        model_id: GoogleModelId,
        messages: Sequence[Message],
        tools: Sequence[Tool] | None = None,
        format: type[FormattableT] | Format[FormattableT] | None = None,
        params: GoogleParams | None = None,
    ) -> StreamResponse | StreamResponse[FormattableT]:
        """Make a streaming call to the Google GenAI API."""
        input_messages, format, contents, config = _utils.prepare_google_request(
            model_id, messages, tools, format, params=params
        )

        google_stream = self.client.models.generate_content_stream(
            model=model_id,
            contents=contents,
            config=config,
        )

        chunk_iterator = _utils.convert_google_stream_to_chunk_iterator(google_stream)

        return StreamResponse(
            provider="google",
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
        model_id: GoogleModelId,
        messages: Sequence[Message],
        tools: Sequence[Tool | ContextTool[DepsT]] | None = None,
        format: None = None,
        params: GoogleParams | None = None,
    ) -> ContextStreamResponse[DepsT]: ...

    @overload
    def context_stream(
        self,
        *,
        ctx: Context[DepsT],
        model_id: GoogleModelId,
        messages: Sequence[Message],
        tools: Sequence[Tool | ContextTool[DepsT]] | None = None,
        format: type[FormattableT] | Format[FormattableT],
        params: GoogleParams | None = None,
    ) -> ContextStreamResponse[DepsT, FormattableT]: ...

    @overload
    def context_stream(
        self,
        *,
        ctx: Context[DepsT],
        model_id: GoogleModelId,
        messages: Sequence[Message],
        tools: Sequence[Tool | ContextTool[DepsT]] | None = None,
        format: type[FormattableT] | Format[FormattableT] | None,
        params: GoogleParams | None = None,
    ) -> ContextStreamResponse[DepsT] | ContextStreamResponse[DepsT, FormattableT]: ...

    def context_stream(
        self,
        *,
        ctx: Context[DepsT],
        model_id: GoogleModelId,
        messages: Sequence[Message],
        tools: Sequence[Tool | ContextTool[DepsT]] | None = None,
        format: type[FormattableT] | Format[FormattableT] | None = None,
        params: GoogleParams | None = None,
    ) -> ContextStreamResponse[DepsT] | ContextStreamResponse[DepsT, FormattableT]:
        """Make a streaming call to the Google GenAI API."""
        input_messages, format, contents, config = _utils.prepare_google_request(
            model_id, messages, tools, format, params=params
        )

        google_stream = self.client.models.generate_content_stream(
            model=model_id,
            contents=contents,
            config=config,
        )

        chunk_iterator = _utils.convert_google_stream_to_chunk_iterator(google_stream)

        return ContextStreamResponse(
            provider="google",
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
        model_id: GoogleModelId,
        messages: Sequence[Message],
        tools: Sequence[AsyncTool] | None = None,
        format: None = None,
        params: GoogleParams | None = None,
    ) -> AsyncStreamResponse: ...

    @overload
    async def stream_async(
        self,
        *,
        model_id: GoogleModelId,
        messages: Sequence[Message],
        tools: Sequence[AsyncTool] | None = None,
        format: type[FormattableT] | Format[FormattableT],
        params: GoogleParams | None = None,
    ) -> AsyncStreamResponse[FormattableT]: ...

    @overload
    async def stream_async(
        self,
        *,
        model_id: GoogleModelId,
        messages: Sequence[Message],
        tools: Sequence[AsyncTool] | None = None,
        format: type[FormattableT] | Format[FormattableT] | None,
        params: GoogleParams | None = None,
    ) -> AsyncStreamResponse | AsyncStreamResponse[FormattableT]: ...

    async def stream_async(
        self,
        *,
        model_id: GoogleModelId,
        messages: Sequence[Message],
        tools: Sequence[AsyncTool] | None = None,
        format: type[FormattableT] | Format[FormattableT] | None = None,
        params: GoogleParams | None = None,
    ) -> AsyncStreamResponse | AsyncStreamResponse[FormattableT]:
        """Make an async streaming call to the Google GenAI API."""
        input_messages, format, contents, config = _utils.prepare_google_request(
            model_id, messages, tools, format, params=params
        )

        google_stream = await self.client.aio.models.generate_content_stream(
            model=model_id,
            contents=contents,
            config=config,
        )

        chunk_iterator = _utils.convert_google_stream_to_async_chunk_iterator(
            google_stream
        )

        return AsyncStreamResponse(
            provider="google",
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
        model_id: GoogleModelId,
        messages: Sequence[Message],
        tools: Sequence[AsyncTool | AsyncContextTool[DepsT]] | None = None,
        format: None = None,
        params: GoogleParams | None = None,
    ) -> AsyncContextStreamResponse[DepsT]: ...

    @overload
    async def context_stream_async(
        self,
        *,
        ctx: Context[DepsT],
        model_id: GoogleModelId,
        messages: Sequence[Message],
        tools: Sequence[AsyncTool | AsyncContextTool[DepsT]] | None = None,
        format: type[FormattableT] | Format[FormattableT],
        params: GoogleParams | None = None,
    ) -> AsyncContextStreamResponse[DepsT, FormattableT]: ...

    @overload
    async def context_stream_async(
        self,
        *,
        ctx: Context[DepsT],
        model_id: GoogleModelId,
        messages: Sequence[Message],
        tools: Sequence[AsyncTool | AsyncContextTool[DepsT]] | None = None,
        format: type[FormattableT] | Format[FormattableT] | None,
        params: GoogleParams | None = None,
    ) -> (
        AsyncContextStreamResponse | AsyncContextStreamResponse[DepsT, FormattableT]
    ): ...

    async def context_stream_async(
        self,
        *,
        ctx: Context[DepsT],
        model_id: GoogleModelId,
        messages: Sequence[Message],
        tools: Sequence[AsyncTool | AsyncContextTool[DepsT]] | None = None,
        format: type[FormattableT] | Format[FormattableT] | None = None,
        params: GoogleParams | None = None,
    ) -> AsyncContextStreamResponse | AsyncContextStreamResponse[DepsT, FormattableT]:
        """Make an async streaming call to the Google GenAI API."""
        input_messages, format, contents, config = _utils.prepare_google_request(
            model_id, messages, tools, format, params=params
        )

        google_stream = await self.client.aio.models.generate_content_stream(
            model=model_id,
            contents=contents,
            config=config,
        )

        chunk_iterator = _utils.convert_google_stream_to_async_chunk_iterator(
            google_stream
        )

        return AsyncContextStreamResponse(
            provider="google",
            model_id=model_id,
            params=params,
            tools=tools,
            input_messages=input_messages,
            chunk_iterator=chunk_iterator,
            format=format,
        )
