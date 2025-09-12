"""Google client implementation."""

import os
from collections.abc import Sequence
from typing import overload

from google.genai import Client
from google.genai.types import HttpOptions

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
    AsyncToolkit,
    ContextTool,
    Tool,
    Toolkit,
)
from ..base import BaseClient
from . import _utils
from .model_ids import GoogleModelId
from .params import GoogleParams

_global_client: "GoogleClient | None" = None


def get_google_client() -> "GoogleClient":
    """Get a global Google client instance.

    Returns:
        A Google client instance. Multiple calls return the same instance.
    """
    global _global_client
    if _global_client is None:
        api_key = os.getenv("GOOGLE_API_KEY")
        _global_client = GoogleClient(api_key=api_key)
    return _global_client


class GoogleClient(BaseClient[GoogleParams, GoogleModelId, Client]):
    """The client for the Google LLM model."""

    def __init__(
        self, *, api_key: str | None = None, base_url: str | None = None
    ) -> None:
        """Initialize the GoogleClient with optional API key and base URL.

        If api_key is not set, Google will look for it in env as "GOOGLE_API_KEY".
        """
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
        format: type[FormatT],
        params: GoogleParams | None = None,
    ) -> Response[FormatT]: ...

    @overload
    def call(
        self,
        *,
        model_id: GoogleModelId,
        messages: Sequence[Message],
        tools: Sequence[Tool] | None = None,
        format: type[FormatT] | None,
        params: GoogleParams | None = None,
    ) -> Response | Response[FormatT]: ...

    def call(
        self,
        *,
        model_id: GoogleModelId,
        messages: Sequence[Message],
        tools: Sequence[Tool] | None = None,
        format: type[FormatT] | None = None,
        params: GoogleParams | None = None,
    ) -> Response | Response[FormatT]:
        """Make a call to the Google GenAI API."""
        if params:
            raise NotImplementedError("param use not yet supported")

        input_messages, contents, config = _utils.prepare_google_request(
            messages, tools, format
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
        model_id: GoogleModelId,
        messages: Sequence[Message],
        tools: Sequence[Tool | ContextTool[DepsT]],
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
        tools: Sequence[Tool | ContextTool[DepsT]],
        format: type[FormatT],
        params: GoogleParams | None = None,
    ) -> ContextResponse[DepsT, FormatT]: ...

    @overload
    def context_call(
        self,
        *,
        ctx: Context[DepsT],
        model_id: GoogleModelId,
        messages: Sequence[Message],
        tools: Sequence[Tool | ContextTool[DepsT]],
        format: type[FormatT] | None,
        params: GoogleParams | None = None,
    ) -> ContextResponse[DepsT, None] | ContextResponse[DepsT, FormatT]: ...

    def context_call(
        self,
        *,
        ctx: Context[DepsT],
        model_id: GoogleModelId,
        messages: Sequence[Message],
        tools: Sequence[Tool | ContextTool[DepsT]],
        format: type[FormatT] | None = None,
        params: GoogleParams | None = None,
    ) -> ContextResponse[DepsT, None] | ContextResponse[DepsT, FormatT]:
        raise NotImplementedError

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
        format: type[FormatT],
        params: GoogleParams | None = None,
    ) -> AsyncResponse[FormatT]: ...

    @overload
    async def call_async(
        self,
        *,
        model_id: GoogleModelId,
        messages: Sequence[Message],
        tools: Sequence[AsyncTool] | None = None,
        format: type[FormatT] | None,
        params: GoogleParams | None = None,
    ) -> AsyncResponse | AsyncResponse[FormatT]: ...

    async def call_async(
        self,
        *,
        model_id: GoogleModelId,
        messages: Sequence[Message],
        tools: Sequence[AsyncTool] | None = None,
        format: type[FormatT] | None = None,
        params: GoogleParams | None = None,
    ) -> AsyncResponse | AsyncResponse[FormatT]:
        """Make an async call to the Google GenAI API."""
        if params:
            raise NotImplementedError("param use not yet supported")

        input_messages, contents, config = _utils.prepare_google_request(
            messages, tools, format
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
            toolkit=AsyncToolkit(tools=tools),
            input_messages=input_messages,
            assistant_message=assistant_message,
            finish_reason=finish_reason,
            format_type=format,
        )

    @overload
    async def context_call_async(
        self,
        *,
        ctx: Context[DepsT],
        model_id: GoogleModelId,
        messages: Sequence[Message],
        tools: Sequence[AsyncTool | AsyncContextTool[DepsT]],
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
        tools: Sequence[AsyncTool | AsyncContextTool[DepsT]],
        format: type[FormatT],
        params: GoogleParams | None = None,
    ) -> AsyncContextResponse[DepsT, FormatT]: ...

    @overload
    async def context_call_async(
        self,
        *,
        ctx: Context[DepsT],
        model_id: GoogleModelId,
        messages: Sequence[Message],
        tools: Sequence[AsyncTool | AsyncContextTool[DepsT]],
        format: type[FormatT] | None,
        params: GoogleParams | None = None,
    ) -> AsyncContextResponse[DepsT, None] | AsyncContextResponse[DepsT, FormatT]: ...

    async def context_call_async(
        self,
        *,
        ctx: Context[DepsT],
        model_id: GoogleModelId,
        messages: Sequence[Message],
        tools: Sequence[AsyncTool | AsyncContextTool[DepsT]],
        format: type[FormatT] | None = None,
        params: GoogleParams | None = None,
    ) -> AsyncContextResponse[DepsT, None] | AsyncContextResponse[DepsT, FormatT]:
        raise NotImplementedError

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
        format: type[FormatT],
        params: GoogleParams | None = None,
    ) -> StreamResponse[FormatT]: ...

    @overload
    def stream(
        self,
        *,
        model_id: GoogleModelId,
        messages: Sequence[Message],
        tools: Sequence[Tool] | None = None,
        format: type[FormatT] | None,
        params: GoogleParams | None = None,
    ) -> StreamResponse | StreamResponse[FormatT]: ...

    def stream(
        self,
        *,
        model_id: GoogleModelId,
        messages: Sequence[Message],
        tools: Sequence[Tool] | None = None,
        format: type[FormatT] | None = None,
        params: GoogleParams | None = None,
    ) -> StreamResponse | StreamResponse[FormatT]:
        if params:
            raise NotImplementedError("param use not yet supported")

        input_messages, contents, config = _utils.prepare_google_request(
            messages, tools, format
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
        model_id: GoogleModelId,
        messages: Sequence[Message],
        tools: Sequence[Tool | ContextTool[DepsT]],
        format: None = None,
        params: GoogleParams | None = None,
    ) -> ContextStreamResponse: ...

    @overload
    def context_stream(
        self,
        *,
        ctx: Context[DepsT],
        model_id: GoogleModelId,
        messages: Sequence[Message],
        tools: Sequence[Tool | ContextTool[DepsT]],
        format: type[FormatT],
        params: GoogleParams | None = None,
    ) -> ContextStreamResponse[FormatT]: ...

    @overload
    def context_stream(
        self,
        *,
        ctx: Context[DepsT],
        model_id: GoogleModelId,
        messages: Sequence[Message],
        tools: Sequence[Tool | ContextTool[DepsT]],
        format: type[FormatT] | None,
        params: GoogleParams | None = None,
    ) -> ContextStreamResponse | ContextStreamResponse[FormatT]: ...

    def context_stream(
        self,
        *,
        ctx: Context[DepsT],
        model_id: GoogleModelId,
        messages: Sequence[Message],
        tools: Sequence[Tool | ContextTool[DepsT]],
        format: type[FormatT] | None = None,
        params: GoogleParams | None = None,
    ) -> ContextStreamResponse | ContextStreamResponse[FormatT]:
        raise NotImplementedError

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
        format: type[FormatT],
        params: GoogleParams | None = None,
    ) -> AsyncStreamResponse[FormatT]: ...

    @overload
    async def stream_async(
        self,
        *,
        model_id: GoogleModelId,
        messages: Sequence[Message],
        tools: Sequence[AsyncTool] | None = None,
        format: type[FormatT] | None,
        params: GoogleParams | None = None,
    ) -> AsyncStreamResponse | AsyncStreamResponse[FormatT]: ...

    async def stream_async(
        self,
        *,
        model_id: GoogleModelId,
        messages: Sequence[Message],
        tools: Sequence[AsyncTool] | None = None,
        format: type[FormatT] | None = None,
        params: GoogleParams | None = None,
    ) -> AsyncStreamResponse | AsyncStreamResponse[FormatT]:
        """Make an async streaming call to the Google GenAI API."""
        if params:
            raise NotImplementedError("param use not yet supported")

        input_messages, contents, config = _utils.prepare_google_request(
            messages, tools, format
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
            toolkit=AsyncToolkit(tools=tools),
            input_messages=input_messages,
            chunk_iterator=chunk_iterator,
            format_type=format,
        )

    @overload
    async def context_stream_async(
        self,
        *,
        ctx: Context[DepsT],
        model_id: GoogleModelId,
        messages: Sequence[Message],
        tools: Sequence[AsyncTool | AsyncContextTool[DepsT]],
        format: None = None,
        params: GoogleParams | None = None,
    ) -> AsyncContextStreamResponse: ...

    @overload
    async def context_stream_async(
        self,
        *,
        ctx: Context[DepsT],
        model_id: GoogleModelId,
        messages: Sequence[Message],
        tools: Sequence[AsyncTool | AsyncContextTool[DepsT]],
        format: type[FormatT],
        params: GoogleParams | None = None,
    ) -> AsyncContextStreamResponse[FormatT]: ...

    @overload
    async def context_stream_async(
        self,
        *,
        ctx: Context[DepsT],
        model_id: GoogleModelId,
        messages: Sequence[Message],
        tools: Sequence[AsyncTool | AsyncContextTool[DepsT]],
        format: type[FormatT] | None,
        params: GoogleParams | None = None,
    ) -> AsyncContextStreamResponse | AsyncContextStreamResponse[FormatT]: ...

    async def context_stream_async(
        self,
        *,
        ctx: Context[DepsT],
        model_id: GoogleModelId,
        messages: Sequence[Message],
        tools: Sequence[AsyncTool | AsyncContextTool[DepsT]],
        format: type[FormatT] | None = None,
        params: GoogleParams | None = None,
    ) -> AsyncContextStreamResponse | AsyncContextStreamResponse[FormatT]:
        raise NotImplementedError
