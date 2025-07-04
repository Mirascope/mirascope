"""Google client implementation."""

from collections.abc import Sequence
from typing import Any, TypeAlias

from google.genai.types import ContentDict, FunctionResponse
from typing_extensions import TypeVar

from ..context import Context
from ..messages import Message
from ..models.base import BaseParams
from ..responses import (
    AsyncStream,
    AsyncStructuredStream,
    Response,
    Stream,
    StructuredStream,
)
from ..tools import ContextToolDef, ToolDef
from .base import BaseClient
from .register import GOOGLE_REGISTERED_LLMS

T = TypeVar("T", bound=object | None, default=None)
DepsT = TypeVar("DepsT", default=None)

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
    ) -> Response:
        raise NotImplementedError

    def context_call(
        self,
        *,
        model: GOOGLE_REGISTERED_LLMS,
        messages: Sequence[GoogleMessage],
        tools: Sequence[ToolDef | ContextToolDef[..., Any, DepsT]],
        params: GoogleParams | None = None,
        ctx: Context[DepsT],
    ) -> Response:
        raise NotImplementedError

    def structured_call(
        self,
        *,
        model: GOOGLE_REGISTERED_LLMS,
        messages: Sequence[GoogleMessage],
        tools: Sequence[ToolDef] | None = None,
        response_format: type[T],
        params: GoogleParams | None = None,
    ) -> Response[T]:
        raise NotImplementedError

    def structured_context_call(
        self,
        *,
        model: GOOGLE_REGISTERED_LLMS,
        messages: Sequence[GoogleMessage],
        tools: Sequence[ToolDef | ContextToolDef[..., Any, DepsT]],
        response_format: type[T],
        params: GoogleParams | None = None,
        ctx: Context[DepsT],
    ) -> Response[T]:
        raise NotImplementedError

    async def call_async(
        self,
        *,
        model: GOOGLE_REGISTERED_LLMS,
        messages: Sequence[GoogleMessage],
        tools: Sequence[ToolDef] | None = None,
        params: GoogleParams | None = None,
    ) -> Response:
        raise NotImplementedError

    async def context_call_async(
        self,
        *,
        model: GOOGLE_REGISTERED_LLMS,
        messages: Sequence[GoogleMessage],
        tools: Sequence[ToolDef | ContextToolDef[..., Any, DepsT]],
        params: GoogleParams | None = None,
        ctx: Context[DepsT],
    ) -> Response:
        raise NotImplementedError

    async def structured_call_async(
        self,
        *,
        model: GOOGLE_REGISTERED_LLMS,
        messages: Sequence[GoogleMessage],
        tools: Sequence[ToolDef] | None = None,
        response_format: type[T],
        params: GoogleParams | None = None,
    ) -> Response[T]:
        raise NotImplementedError

    async def structured_context_call_async(
        self,
        *,
        model: GOOGLE_REGISTERED_LLMS,
        messages: Sequence[GoogleMessage],
        tools: Sequence[ToolDef | ContextToolDef[..., Any, DepsT]],
        response_format: type[T],
        params: GoogleParams | None = None,
        ctx: Context[DepsT],
    ) -> Response[T]:
        raise NotImplementedError

    def stream(
        self,
        *,
        model: GOOGLE_REGISTERED_LLMS,
        messages: Sequence[GoogleMessage],
        tools: Sequence[ToolDef] | None = None,
        params: GoogleParams | None = None,
    ) -> Stream:
        raise NotImplementedError

    def context_stream(
        self,
        *,
        model: GOOGLE_REGISTERED_LLMS,
        messages: Sequence[GoogleMessage],
        tools: Sequence[ToolDef | ContextToolDef[..., Any, DepsT]],
        params: GoogleParams | None = None,
        ctx: Context[DepsT],
    ) -> Stream:
        raise NotImplementedError

    def structured_stream(
        self,
        *,
        model: GOOGLE_REGISTERED_LLMS,
        messages: Sequence[GoogleMessage],
        tools: Sequence[ToolDef] | None = None,
        response_format: type[T],
        params: GoogleParams | None = None,
    ) -> StructuredStream[T]:
        raise NotImplementedError

    def structured_context_stream(
        self,
        *,
        model: GOOGLE_REGISTERED_LLMS,
        messages: Sequence[GoogleMessage],
        tools: Sequence[ToolDef | ContextToolDef[..., Any, DepsT]],
        response_format: type[T],
        params: GoogleParams | None = None,
        ctx: Context[DepsT],
    ) -> StructuredStream[T]:
        raise NotImplementedError

    async def stream_async(
        self,
        *,
        model: GOOGLE_REGISTERED_LLMS,
        messages: Sequence[GoogleMessage],
        tools: Sequence[ToolDef] | None = None,
        params: GoogleParams | None = None,
    ) -> AsyncStream:
        raise NotImplementedError

    async def context_stream_async(
        self,
        *,
        model: GOOGLE_REGISTERED_LLMS,
        messages: Sequence[GoogleMessage],
        tools: Sequence[ToolDef | ContextToolDef[..., Any, DepsT]],
        params: GoogleParams | None = None,
        ctx: Context[DepsT],
    ) -> AsyncStream:
        raise NotImplementedError

    async def structured_stream_async(
        self,
        *,
        model: GOOGLE_REGISTERED_LLMS,
        messages: Sequence[GoogleMessage],
        tools: Sequence[ToolDef] | None = None,
        response_format: type[T],
        params: GoogleParams | None = None,
    ) -> AsyncStructuredStream[T]:
        raise NotImplementedError

    async def structured_context_stream_async(
        self,
        *,
        model: GOOGLE_REGISTERED_LLMS,
        messages: Sequence[GoogleMessage],
        tools: Sequence[ToolDef | ContextToolDef[..., Any, DepsT]],
        response_format: type[T],
        params: GoogleParams | None = None,
        ctx: Context[DepsT],
    ) -> AsyncStructuredStream[T]:
        raise NotImplementedError
