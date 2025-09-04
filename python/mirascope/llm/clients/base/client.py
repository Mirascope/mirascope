"""Base abstract interface for provider clients."""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Sequence
from typing import Generic, overload
from typing_extensions import TypeVar

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
from ...tools import AsyncContextTool, AsyncTool, ContextTool, Tool
from .params import ParamsT

ModelIdT = TypeVar("ModelIdT", bound=str)
ProviderClientT = TypeVar("ProviderClientT")

ClientT = TypeVar("ClientT", bound="BaseClient")
"""Type variable for an LLM client."""


class BaseClient(Generic[ParamsT, ModelIdT, ProviderClientT], ABC):
    """Base abstract client for provider-specific implementations.

    This class defines explicit methods for each type of call, eliminating
    the need for complex overloads in provider implementations.
    """

    client: ProviderClientT

    @overload
    @abstractmethod
    def call(
        self,
        *,
        model_id: ModelIdT,
        messages: Sequence[Message],
        tools: Sequence[Tool] | None = None,
        format: None = None,
        params: ParamsT | None = None,
    ) -> Response: ...

    @overload
    @abstractmethod
    def call(
        self,
        *,
        model_id: ModelIdT,
        messages: Sequence[Message],
        tools: Sequence[Tool] | None = None,
        format: type[FormatT],
        params: ParamsT | None = None,
    ) -> Response[FormatT]: ...

    @abstractmethod
    def call(
        self,
        *,
        model_id: ModelIdT,
        messages: Sequence[Message],
        tools: Sequence[Tool] | None = None,
        format: type[FormatT] | None = None,
        params: ParamsT | None = None,
    ) -> Response | Response[FormatT]:
        """Generate a response."""
        ...

    @overload
    @abstractmethod
    def context_call(
        self,
        *,
        ctx: Context[DepsT],
        model_id: ModelIdT,
        messages: Sequence[Message],
        tools: Sequence[Tool | ContextTool[DepsT]],
        format: None = None,
        params: ParamsT | None = None,
    ) -> ContextResponse[DepsT, None]: ...

    @overload
    @abstractmethod
    def context_call(
        self,
        *,
        ctx: Context[DepsT],
        model_id: ModelIdT,
        messages: Sequence[Message],
        tools: Sequence[Tool | ContextTool[DepsT]],
        format: type[FormatT],
        params: ParamsT | None = None,
    ) -> ContextResponse[DepsT, FormatT]: ...

    @abstractmethod
    def context_call(
        self,
        *,
        ctx: Context[DepsT],
        model_id: ModelIdT,
        messages: Sequence[Message],
        tools: Sequence[Tool | ContextTool[DepsT]],
        format: type[FormatT] | None = None,
        params: ParamsT | None = None,
    ) -> ContextResponse[DepsT, None] | ContextResponse[DepsT, FormatT]:
        """Generate a context response."""
        ...

    @overload
    @abstractmethod
    async def call_async(
        self,
        *,
        model_id: ModelIdT,
        messages: Sequence[Message],
        tools: Sequence[AsyncTool] | None = None,
        format: None = None,
        params: ParamsT | None = None,
    ) -> AsyncResponse: ...

    @overload
    @abstractmethod
    async def call_async(
        self,
        *,
        model_id: ModelIdT,
        messages: Sequence[Message],
        tools: Sequence[AsyncTool] | None = None,
        format: type[FormatT],
        params: ParamsT | None = None,
    ) -> AsyncResponse[FormatT]: ...

    @abstractmethod
    async def call_async(
        self,
        *,
        model_id: ModelIdT,
        messages: Sequence[Message],
        tools: Sequence[AsyncTool] | None = None,
        format: type[FormatT] | None = None,
        params: ParamsT | None = None,
    ) -> AsyncResponse | AsyncResponse[FormatT]:
        """Generate a response asynchronously."""
        ...

    @overload
    @abstractmethod
    async def context_call_async(
        self,
        *,
        ctx: Context[DepsT],
        model_id: ModelIdT,
        messages: Sequence[Message],
        tools: Sequence[AsyncTool | AsyncContextTool[DepsT]],
        format: None = None,
        params: ParamsT | None = None,
    ) -> AsyncContextResponse[DepsT, None]: ...

    @overload
    @abstractmethod
    async def context_call_async(
        self,
        *,
        ctx: Context[DepsT],
        model_id: ModelIdT,
        messages: Sequence[Message],
        tools: Sequence[AsyncTool | AsyncContextTool[DepsT]],
        format: type[FormatT],
        params: ParamsT | None = None,
    ) -> AsyncContextResponse[DepsT, FormatT]: ...

    @abstractmethod
    async def context_call_async(
        self,
        *,
        ctx: Context[DepsT],
        model_id: ModelIdT,
        messages: Sequence[Message],
        tools: Sequence[AsyncTool | AsyncContextTool[DepsT]],
        format: type[FormatT] | None = None,
        params: ParamsT | None = None,
    ) -> AsyncContextResponse[DepsT, None] | AsyncContextResponse[DepsT, FormatT]:
        """Generate a context response asynchronously."""
        ...

    @overload
    @abstractmethod
    def stream(
        self,
        *,
        model_id: ModelIdT,
        messages: Sequence[Message],
        tools: Sequence[Tool] | None = None,
        format: None = None,
        params: ParamsT | None = None,
    ) -> StreamResponse: ...

    @overload
    @abstractmethod
    def stream(
        self,
        *,
        model_id: ModelIdT,
        messages: Sequence[Message],
        tools: Sequence[Tool] | None = None,
        format: type[FormatT],
        params: ParamsT | None = None,
    ) -> StreamResponse[FormatT]: ...

    @abstractmethod
    def stream(
        self,
        *,
        model_id: ModelIdT,
        messages: Sequence[Message],
        tools: Sequence[Tool] | None = None,
        format: type[FormatT] | None = None,
        params: ParamsT | None = None,
    ) -> StreamResponse | StreamResponse[FormatT]:
        """Stream a response."""
        ...

    @overload
    @abstractmethod
    def context_stream(
        self,
        *,
        ctx: Context[DepsT],
        model_id: ModelIdT,
        messages: Sequence[Message],
        tools: Sequence[Tool | ContextTool[DepsT]],
        format: None = None,
        params: ParamsT | None = None,
    ) -> StreamResponse: ...

    @overload
    @abstractmethod
    def context_stream(
        self,
        *,
        ctx: Context[DepsT],
        model_id: ModelIdT,
        messages: Sequence[Message],
        tools: Sequence[Tool | ContextTool[DepsT]],
        format: type[FormatT],
        params: ParamsT | None = None,
    ) -> StreamResponse[FormatT]: ...

    @abstractmethod
    def context_stream(
        self,
        *,
        ctx: Context[DepsT],
        model_id: ModelIdT,
        messages: Sequence[Message],
        tools: Sequence[Tool | ContextTool[DepsT]],
        format: type[FormatT] | None = None,
        params: ParamsT | None = None,
    ) -> StreamResponse | StreamResponse[FormatT]:
        """Stream a context response."""
        ...

    @overload
    @abstractmethod
    async def stream_async(
        self,
        *,
        model_id: ModelIdT,
        messages: Sequence[Message],
        tools: Sequence[AsyncTool] | None = None,
        format: None = None,
        params: ParamsT | None = None,
    ) -> AsyncStreamResponse: ...

    @overload
    @abstractmethod
    async def stream_async(
        self,
        *,
        model_id: ModelIdT,
        messages: Sequence[Message],
        tools: Sequence[AsyncTool] | None = None,
        format: type[FormatT],
        params: ParamsT | None = None,
    ) -> AsyncStreamResponse[FormatT]: ...

    @abstractmethod
    async def stream_async(
        self,
        *,
        model_id: ModelIdT,
        messages: Sequence[Message],
        tools: Sequence[AsyncTool] | None = None,
        format: type[FormatT] | None = None,
        params: ParamsT | None = None,
    ) -> AsyncStreamResponse | AsyncStreamResponse[FormatT]:
        """Stream a response asynchronously."""
        ...

    @overload
    @abstractmethod
    async def context_stream_async(
        self,
        *,
        ctx: Context[DepsT],
        model_id: ModelIdT,
        messages: Sequence[Message],
        tools: Sequence[AsyncTool | AsyncContextTool[DepsT]],
        format: None = None,
        params: ParamsT | None = None,
    ) -> AsyncStreamResponse: ...

    @overload
    @abstractmethod
    async def context_stream_async(
        self,
        *,
        ctx: Context[DepsT],
        model_id: ModelIdT,
        messages: Sequence[Message],
        tools: Sequence[AsyncTool | AsyncContextTool[DepsT]],
        format: type[FormatT],
        params: ParamsT | None = None,
    ) -> AsyncStreamResponse[FormatT]: ...

    @abstractmethod
    async def context_stream_async(
        self,
        *,
        ctx: Context[DepsT],
        model_id: ModelIdT,
        messages: Sequence[Message],
        tools: Sequence[AsyncTool | AsyncContextTool[DepsT]],
        format: type[FormatT] | None = None,
        params: ParamsT | None = None,
    ) -> AsyncStreamResponse | AsyncStreamResponse[FormatT]:
        """Stream a context response asynchronously."""
        ...
