"""Google client implementation."""

from collections.abc import Sequence
from typing import Any, TypeAlias

from google.genai.types import ContentDict, FunctionResponse

from ..clients import BaseParams
from ..context import Context
from ..messages import Message
from ..responses import Response
from ..streams import (
    AsyncStream,
    AsyncStructuredStream,
    Stream,
    StructuredStream,
)
from ..tools import ContextToolDef, ToolDef
from ..types import DepsT, FormatT
from .base import BaseClient
from .register import GOOGLE_REGISTERED_LLMS

GoogleMessage: TypeAlias = Message | ContentDict | FunctionResponse


class GoogleParams(BaseParams, total=False):
    """The parameters for the Google LLM model."""


class GoogleClient(BaseClient[GoogleMessage, GoogleParams, GOOGLE_REGISTERED_LLMS]):
    """The client for the Google LLM model."""

    def call(
        self,
        *,
        model: GOOGLE_REGISTERED_LLMS,
        messages: Sequence[GoogleMessage],
        tools: Sequence[ToolDef] | None = None,
        params: GoogleParams | None = None,
    ) -> Response[None, None]:
        raise NotImplementedError

    def context_call(
        self,
        *,
        ctx: Context[DepsT],
        model: GOOGLE_REGISTERED_LLMS,
        messages: Sequence[GoogleMessage],
        tools: Sequence[ToolDef | ContextToolDef[..., Any, DepsT]],
        params: GoogleParams | None = None,
    ) -> Response[DepsT, None]:
        raise NotImplementedError

    def structured_call(
        self,
        *,
        model: GOOGLE_REGISTERED_LLMS,
        messages: Sequence[GoogleMessage],
        tools: Sequence[ToolDef] | None = None,
        response_format: type[FormatT],
        params: GoogleParams | None = None,
    ) -> Response[None, FormatT]:
        raise NotImplementedError

    def structured_context_call(
        self,
        *,
        ctx: Context[DepsT],
        model: GOOGLE_REGISTERED_LLMS,
        messages: Sequence[GoogleMessage],
        tools: Sequence[ToolDef | ContextToolDef[..., Any, DepsT]],
        response_format: type[FormatT],
        params: GoogleParams | None = None,
    ) -> Response[DepsT, FormatT]:
        raise NotImplementedError

    async def call_async(
        self,
        *,
        model: GOOGLE_REGISTERED_LLMS,
        messages: Sequence[GoogleMessage],
        tools: Sequence[ToolDef] | None = None,
        params: GoogleParams | None = None,
    ) -> Response[None, None]:
        raise NotImplementedError

    async def context_call_async(
        self,
        *,
        ctx: Context[DepsT],
        model: GOOGLE_REGISTERED_LLMS,
        messages: Sequence[GoogleMessage],
        tools: Sequence[ToolDef | ContextToolDef[..., Any, DepsT]],
        params: GoogleParams | None = None,
    ) -> Response[DepsT, None]:
        raise NotImplementedError

    async def structured_call_async(
        self,
        *,
        model: GOOGLE_REGISTERED_LLMS,
        messages: Sequence[GoogleMessage],
        tools: Sequence[ToolDef] | None = None,
        response_format: type[FormatT],
        params: GoogleParams | None = None,
    ) -> Response[None, FormatT]:
        raise NotImplementedError

    async def structured_context_call_async(
        self,
        *,
        ctx: Context[DepsT],
        model: GOOGLE_REGISTERED_LLMS,
        messages: Sequence[GoogleMessage],
        tools: Sequence[ToolDef | ContextToolDef[..., Any, DepsT]],
        response_format: type[FormatT],
        params: GoogleParams | None = None,
    ) -> Response[DepsT, FormatT]:
        raise NotImplementedError

    def stream(
        self,
        *,
        model: GOOGLE_REGISTERED_LLMS,
        messages: Sequence[GoogleMessage],
        tools: Sequence[ToolDef] | None = None,
        params: GoogleParams | None = None,
    ) -> Stream[None]:
        raise NotImplementedError

    def context_stream(
        self,
        *,
        ctx: Context[DepsT],
        model: GOOGLE_REGISTERED_LLMS,
        messages: Sequence[GoogleMessage],
        tools: Sequence[ToolDef | ContextToolDef[..., Any, DepsT]],
        params: GoogleParams | None = None,
    ) -> Stream[DepsT]:
        raise NotImplementedError

    def structured_stream(
        self,
        *,
        model: GOOGLE_REGISTERED_LLMS,
        messages: Sequence[GoogleMessage],
        tools: Sequence[ToolDef] | None = None,
        response_format: type[FormatT],
        params: GoogleParams | None = None,
    ) -> StructuredStream[None, FormatT]:
        raise NotImplementedError

    def structured_context_stream(
        self,
        *,
        ctx: Context[DepsT],
        model: GOOGLE_REGISTERED_LLMS,
        messages: Sequence[GoogleMessage],
        tools: Sequence[ToolDef | ContextToolDef[..., Any, DepsT]],
        response_format: type[FormatT],
        params: GoogleParams | None = None,
    ) -> StructuredStream[DepsT, FormatT]:
        raise NotImplementedError

    async def stream_async(
        self,
        *,
        model: GOOGLE_REGISTERED_LLMS,
        messages: Sequence[GoogleMessage],
        tools: Sequence[ToolDef] | None = None,
        params: GoogleParams | None = None,
    ) -> AsyncStream[None]:
        raise NotImplementedError

    async def context_stream_async(
        self,
        *,
        ctx: Context[DepsT],
        model: GOOGLE_REGISTERED_LLMS,
        messages: Sequence[GoogleMessage],
        tools: Sequence[ToolDef | ContextToolDef[..., Any, DepsT]],
        params: GoogleParams | None = None,
    ) -> AsyncStream[DepsT]:
        raise NotImplementedError

    async def structured_stream_async(
        self,
        *,
        model: GOOGLE_REGISTERED_LLMS,
        messages: Sequence[GoogleMessage],
        tools: Sequence[ToolDef] | None = None,
        response_format: type[FormatT],
        params: GoogleParams | None = None,
    ) -> AsyncStructuredStream[None, FormatT]:
        raise NotImplementedError

    async def structured_context_stream_async(
        self,
        *,
        ctx: Context[DepsT],
        model: GOOGLE_REGISTERED_LLMS,
        messages: Sequence[GoogleMessage],
        tools: Sequence[ToolDef | ContextToolDef[..., Any, DepsT]],
        response_format: type[FormatT],
        params: GoogleParams | None = None,
    ) -> AsyncStructuredStream[DepsT, FormatT]:
        raise NotImplementedError
