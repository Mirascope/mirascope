"""Google client implementation."""

from collections.abc import Sequence
from typing import Any, TypeAlias

from google.genai.types import ContentDict, FunctionResponse

from ..messages import Message
from ..models.base import BaseParams
from ..responses import (
    AsyncContextStream,
    AsyncContextStructuredStream,
    AsyncStream,
    AsyncStructuredStream,
    ContextResponse,
    ContextStream,
    ContextStructuredStream,
    Response,
    Stream,
    StructuredStream,
)
from ..tools import ContextToolDef, ToolDef
from .base import BaseClient
from .register import GOOGLE_REGISTERED_LLMS

GoogleMessage: TypeAlias = Message | ContentDict | FunctionResponse


class GoogleClient(BaseClient[GoogleMessage, BaseParams, GOOGLE_REGISTERED_LLMS]):
    """The client for the Google LLM model."""
    
    def call(
        self,
        *,
        model: GOOGLE_REGISTERED_LLMS,
        messages: Sequence[GoogleMessage],
        tools: Sequence[ToolDef] | None = None,
        params: BaseParams | None = None,
    ) -> Response:
        raise NotImplementedError
    
    def context_call(
        self,
        *,
        model: GOOGLE_REGISTERED_LLMS,
        messages: Sequence[GoogleMessage],
        tools: Sequence[ToolDef | ContextToolDef[..., Any, Any]],
        params: BaseParams | None = None,
    ) -> ContextResponse:
        raise NotImplementedError
    
    def structured_call(
        self,
        *,
        model: GOOGLE_REGISTERED_LLMS,
        messages: Sequence[GoogleMessage],
        tools: Sequence[ToolDef] | None = None,
        response_format: type,
        params: BaseParams | None = None,
    ) -> Response:
        raise NotImplementedError
    
    def structured_context_call(
        self,
        *,
        model: GOOGLE_REGISTERED_LLMS,
        messages: Sequence[GoogleMessage],
        tools: Sequence[ToolDef | ContextToolDef[..., Any, Any]],
        response_format: type,
        params: BaseParams | None = None,
    ) -> ContextResponse:
        raise NotImplementedError
    
    async def call_async(
        self,
        *,
        model: GOOGLE_REGISTERED_LLMS,
        messages: Sequence[GoogleMessage],
        tools: Sequence[ToolDef] | None = None,
        params: BaseParams | None = None,
    ) -> Response:
        raise NotImplementedError
    
    async def context_call_async(
        self,
        *,
        model: GOOGLE_REGISTERED_LLMS,
        messages: Sequence[GoogleMessage],
        tools: Sequence[ToolDef | ContextToolDef[..., Any, Any]],
        params: BaseParams | None = None,
    ) -> ContextResponse:
        raise NotImplementedError
    
    async def structured_call_async(
        self,
        *,
        model: GOOGLE_REGISTERED_LLMS,
        messages: Sequence[GoogleMessage],
        tools: Sequence[ToolDef] | None = None,
        response_format: type,
        params: BaseParams | None = None,
    ) -> Response:
        raise NotImplementedError
    
    async def structured_context_call_async(
        self,
        *,
        model: GOOGLE_REGISTERED_LLMS,
        messages: Sequence[GoogleMessage],
        tools: Sequence[ToolDef | ContextToolDef[..., Any, Any]],
        response_format: type,
        params: BaseParams | None = None,
    ) -> ContextResponse:
        raise NotImplementedError
    
    def stream(
        self,
        *,
        model: GOOGLE_REGISTERED_LLMS,
        messages: Sequence[GoogleMessage],
        tools: Sequence[ToolDef] | None = None,
        params: BaseParams | None = None,
    ) -> Stream:
        raise NotImplementedError
    
    def context_stream(
        self,
        *,
        model: GOOGLE_REGISTERED_LLMS,
        messages: Sequence[GoogleMessage],
        tools: Sequence[ToolDef | ContextToolDef[..., Any, Any]],
        params: BaseParams | None = None,
    ) -> ContextStream:
        raise NotImplementedError
    
    def structured_stream(
        self,
        *,
        model: GOOGLE_REGISTERED_LLMS,
        messages: Sequence[GoogleMessage],
        tools: Sequence[ToolDef] | None = None,
        response_format: type,
        params: BaseParams | None = None,
    ) -> StructuredStream:
        raise NotImplementedError
    
    def structured_context_stream(
        self,
        *,
        model: GOOGLE_REGISTERED_LLMS,
        messages: Sequence[GoogleMessage],
        tools: Sequence[ToolDef | ContextToolDef[..., Any, Any]],
        response_format: type,
        params: BaseParams | None = None,
    ) -> ContextStructuredStream:
        raise NotImplementedError
    
    async def stream_async(
        self,
        *,
        model: GOOGLE_REGISTERED_LLMS,
        messages: Sequence[GoogleMessage],
        tools: Sequence[ToolDef] | None = None,
        params: BaseParams | None = None,
    ) -> AsyncStream:
        raise NotImplementedError
    
    async def context_stream_async(
        self,
        *,
        model: GOOGLE_REGISTERED_LLMS,
        messages: Sequence[GoogleMessage],
        tools: Sequence[ToolDef | ContextToolDef[..., Any, Any]],
        params: BaseParams | None = None,
    ) -> AsyncContextStream:
        raise NotImplementedError
    
    async def structured_stream_async(
        self,
        *,
        model: GOOGLE_REGISTERED_LLMS,
        messages: Sequence[GoogleMessage],
        tools: Sequence[ToolDef] | None = None,
        response_format: type,
        params: BaseParams | None = None,
    ) -> AsyncStructuredStream:
        raise NotImplementedError
    
    async def structured_context_stream_async(
        self,
        *,
        model: GOOGLE_REGISTERED_LLMS,
        messages: Sequence[GoogleMessage],
        tools: Sequence[ToolDef | ContextToolDef[..., Any, Any]],
        response_format: type,
        params: BaseParams | None = None,
    ) -> AsyncContextStructuredStream:
        raise NotImplementedError


class GoogleParams(BaseParams, total=False):
    """The parameters for the Google LLM model."""