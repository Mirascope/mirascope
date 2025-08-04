"""Google client implementation."""

from collections.abc import Sequence

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
from .params import GoogleParams
from .registered_llms import GOOGLE_REGISTERED_LLMS


class GoogleClient(BaseClient[GoogleParams, GOOGLE_REGISTERED_LLMS]):
    """The client for the Google LLM model."""

    def call(
        self,
        *,
        model: GOOGLE_REGISTERED_LLMS,
        messages: Sequence[Message],
        tools: Sequence[Tool] | None = None,
        params: GoogleParams | None = None,
    ) -> Response[None]:
        raise NotImplementedError

    def context_call(
        self,
        *,
        ctx: Context[DepsT],
        model: GOOGLE_REGISTERED_LLMS,
        messages: Sequence[Message],
        tools: Sequence[Tool | ContextTool[..., Jsonable, DepsT]],
        params: GoogleParams | None = None,
    ) -> Response[None]:
        raise NotImplementedError

    def structured_call(
        self,
        *,
        model: GOOGLE_REGISTERED_LLMS,
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
        model: GOOGLE_REGISTERED_LLMS,
        messages: Sequence[Message],
        tools: Sequence[Tool | ContextTool[..., Jsonable, DepsT]],
        format: type[FormatT],
        params: GoogleParams | None = None,
    ) -> Response[FormatT]:
        raise NotImplementedError

    async def call_async(
        self,
        *,
        model: GOOGLE_REGISTERED_LLMS,
        messages: Sequence[Message],
        tools: Sequence[AsyncTool] | None = None,
        params: GoogleParams | None = None,
    ) -> Response[None]:
        raise NotImplementedError

    async def context_call_async(
        self,
        *,
        ctx: Context[DepsT],
        model: GOOGLE_REGISTERED_LLMS,
        messages: Sequence[Message],
        tools: Sequence[AsyncTool | AsyncContextTool[..., Jsonable, DepsT]],
        params: GoogleParams | None = None,
    ) -> Response[None]:
        raise NotImplementedError

    async def structured_call_async(
        self,
        *,
        model: GOOGLE_REGISTERED_LLMS,
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
        model: GOOGLE_REGISTERED_LLMS,
        messages: Sequence[Message],
        tools: Sequence[AsyncTool | AsyncContextTool[..., Jsonable, DepsT]],
        format: type[FormatT],
        params: GoogleParams | None = None,
    ) -> Response[FormatT]:
        raise NotImplementedError

    def stream(
        self,
        *,
        model: GOOGLE_REGISTERED_LLMS,
        messages: Sequence[Message],
        tools: Sequence[Tool] | None = None,
        params: GoogleParams | None = None,
    ) -> StreamResponse[Stream, None]:
        raise NotImplementedError

    def context_stream(
        self,
        *,
        ctx: Context[DepsT],
        model: GOOGLE_REGISTERED_LLMS,
        messages: Sequence[Message],
        tools: Sequence[Tool | ContextTool[..., Jsonable, DepsT]],
        params: GoogleParams | None = None,
    ) -> StreamResponse[Stream, None]:
        raise NotImplementedError

    def structured_stream(
        self,
        *,
        model: GOOGLE_REGISTERED_LLMS,
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
        model: GOOGLE_REGISTERED_LLMS,
        messages: Sequence[Message],
        tools: Sequence[Tool | ContextTool[..., Jsonable, DepsT]],
        format: type[FormatT],
        params: GoogleParams | None = None,
    ) -> StreamResponse[Stream, FormatT]:
        raise NotImplementedError

    async def stream_async(
        self,
        *,
        model: GOOGLE_REGISTERED_LLMS,
        messages: Sequence[Message],
        tools: Sequence[AsyncTool] | None = None,
        params: GoogleParams | None = None,
    ) -> StreamResponse[AsyncStream, None]:
        raise NotImplementedError

    async def context_stream_async(
        self,
        *,
        ctx: Context[DepsT],
        model: GOOGLE_REGISTERED_LLMS,
        messages: Sequence[Message],
        tools: Sequence[AsyncTool | AsyncContextTool[..., Jsonable, DepsT]],
        params: GoogleParams | None = None,
    ) -> StreamResponse[AsyncStream, None]:
        raise NotImplementedError

    async def structured_stream_async(
        self,
        *,
        model: GOOGLE_REGISTERED_LLMS,
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
        model: GOOGLE_REGISTERED_LLMS,
        messages: Sequence[Message],
        tools: Sequence[AsyncTool | AsyncContextTool[..., Jsonable, DepsT]],
        format: type[FormatT],
        params: GoogleParams | None = None,
    ) -> StreamResponse[AsyncStream, FormatT]:
        raise NotImplementedError
