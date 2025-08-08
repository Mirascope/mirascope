"""Google client implementation."""

from collections.abc import Sequence

from google.genai import Client
from google.genai.types import HttpOptions

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
from . import _utils
from .model import GoogleModel
from .params import GoogleParams


class GoogleClient(BaseClient[GoogleParams, GoogleModel, Client]):
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

    def call(
        self,
        *,
        model: GoogleModel,
        messages: Sequence[Message],
        tools: Sequence[Tool] | None = None,
        params: GoogleParams | None = None,
    ) -> Response[None]:
        """Make a call to the Google GenAI API."""
        if tools:
            raise NotImplementedError("tool use not yet supported")
        if params:
            raise NotImplementedError("param use not yet supported")

        contents, config = _utils.prepare_google_request(messages)

        google_response = self.client.models.generate_content(
            model=model,
            contents=contents,
            config=config,
        )

        assistant_message, finish_reason = _utils.decode_response(google_response)

        return Response(
            provider="google",
            model=model,
            raw=google_response,
            input_messages=messages,
            assistant_message=assistant_message,
            finish_reason=finish_reason,
        )

    def context_call(
        self,
        *,
        ctx: Context[DepsT],
        model: GoogleModel,
        messages: Sequence[Message],
        tools: Sequence[Tool | ContextTool[..., Jsonable, DepsT]],
        params: GoogleParams | None = None,
    ) -> Response[None]:
        raise NotImplementedError

    def structured_call(
        self,
        *,
        model: GoogleModel,
        messages: Sequence[Message],
        tools: Sequence[Tool] | None = None,
        format: type[FormatT],
        params: GoogleParams | None = None,
    ) -> Response[FormatT]:
        raise NotImplementedError

    def structured_context_call(
        self,
        *,
        ctx: Context[DepsT],
        model: GoogleModel,
        messages: Sequence[Message],
        tools: Sequence[Tool | ContextTool[..., Jsonable, DepsT]],
        format: type[FormatT],
        params: GoogleParams | None = None,
    ) -> Response[FormatT]:
        raise NotImplementedError

    async def call_async(
        self,
        *,
        model: GoogleModel,
        messages: Sequence[Message],
        tools: Sequence[AsyncTool] | None = None,
        params: GoogleParams | None = None,
    ) -> Response[None]:
        raise NotImplementedError

    async def context_call_async(
        self,
        *,
        ctx: Context[DepsT],
        model: GoogleModel,
        messages: Sequence[Message],
        tools: Sequence[AsyncTool | AsyncContextTool[..., Jsonable, DepsT]],
        params: GoogleParams | None = None,
    ) -> Response[None]:
        raise NotImplementedError

    async def structured_call_async(
        self,
        *,
        model: GoogleModel,
        messages: Sequence[Message],
        tools: Sequence[AsyncTool] | None = None,
        format: type[FormatT],
        params: GoogleParams | None = None,
    ) -> Response[FormatT]:
        raise NotImplementedError

    async def structured_context_call_async(
        self,
        *,
        ctx: Context[DepsT],
        model: GoogleModel,
        messages: Sequence[Message],
        tools: Sequence[AsyncTool | AsyncContextTool[..., Jsonable, DepsT]],
        format: type[FormatT],
        params: GoogleParams | None = None,
    ) -> Response[FormatT]:
        raise NotImplementedError

    def stream(
        self,
        *,
        model: GoogleModel,
        messages: Sequence[Message],
        tools: Sequence[Tool] | None = None,
        params: GoogleParams | None = None,
    ) -> StreamResponse[Stream, None]:
        if tools:
            raise NotImplementedError("tool use not yet supported")
        if params:
            raise NotImplementedError("param use not yet supported")

        contents, config = _utils.prepare_google_request(messages)

        google_stream = self.client.models.generate_content_stream(
            model=model,
            contents=contents,
            config=config,
        )

        chunk_iterator = _utils.convert_google_stream_to_chunk_iterator(google_stream)

        return StreamResponse(
            provider="google",
            model=model,
            input_messages=messages,
            chunk_iterator=chunk_iterator,
        )

    def context_stream(
        self,
        *,
        ctx: Context[DepsT],
        model: GoogleModel,
        messages: Sequence[Message],
        tools: Sequence[Tool | ContextTool[..., Jsonable, DepsT]],
        params: GoogleParams | None = None,
    ) -> StreamResponse[Stream, None]:
        raise NotImplementedError

    def structured_stream(
        self,
        *,
        model: GoogleModel,
        messages: Sequence[Message],
        tools: Sequence[Tool] | None = None,
        format: type[FormatT],
        params: GoogleParams | None = None,
    ) -> StreamResponse[Stream, FormatT]:
        raise NotImplementedError

    def structured_context_stream(
        self,
        *,
        ctx: Context[DepsT],
        model: GoogleModel,
        messages: Sequence[Message],
        tools: Sequence[Tool | ContextTool[..., Jsonable, DepsT]],
        format: type[FormatT],
        params: GoogleParams | None = None,
    ) -> StreamResponse[Stream, FormatT]:
        raise NotImplementedError

    async def stream_async(
        self,
        *,
        model: GoogleModel,
        messages: Sequence[Message],
        tools: Sequence[AsyncTool] | None = None,
        params: GoogleParams | None = None,
    ) -> StreamResponse[AsyncStream, None]:
        raise NotImplementedError

    async def context_stream_async(
        self,
        *,
        ctx: Context[DepsT],
        model: GoogleModel,
        messages: Sequence[Message],
        tools: Sequence[AsyncTool | AsyncContextTool[..., Jsonable, DepsT]],
        params: GoogleParams | None = None,
    ) -> StreamResponse[AsyncStream, None]:
        raise NotImplementedError

    async def structured_stream_async(
        self,
        *,
        model: GoogleModel,
        messages: Sequence[Message],
        tools: Sequence[AsyncTool] | None = None,
        format: type[FormatT],
        params: GoogleParams | None = None,
    ) -> StreamResponse[AsyncStream, FormatT]:
        raise NotImplementedError

    async def structured_context_stream_async(
        self,
        *,
        ctx: Context[DepsT],
        model: GoogleModel,
        messages: Sequence[Message],
        tools: Sequence[AsyncTool | AsyncContextTool[..., Jsonable, DepsT]],
        format: type[FormatT],
        params: GoogleParams | None = None,
    ) -> StreamResponse[AsyncStream, FormatT]:
        raise NotImplementedError
