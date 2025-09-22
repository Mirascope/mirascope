"""Base abstract interface for provider clients."""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Sequence
from contextvars import ContextVar, Token
from types import TracebackType
from typing import Generic, overload
from typing_extensions import Self, TypeVar

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
    _token: Token | None = None

    @property
    @abstractmethod
    def _context_var(self) -> ContextVar:
        """The ContextVar for this client type."""
        ...

    def __enter__(self) -> Self:
        """Sets the client context and stores the token."""
        self._token = self._context_var.set(self)
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        """Restores the client context to the token from the last setting."""
        if self._token is not None:
            self._context_var.reset(self._token)
            self._token = None

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
        format: type[FormattableT] | Format[FormattableT],
        params: ParamsT | None = None,
    ) -> Response[FormattableT]: ...

    @overload
    @abstractmethod
    def call(
        self,
        *,
        model_id: ModelIdT,
        messages: Sequence[Message],
        tools: Sequence[Tool] | None = None,
        format: type[FormattableT] | Format[FormattableT] | None,
        params: ParamsT | None = None,
    ) -> Response | Response[FormattableT]: ...

    @abstractmethod
    def call(
        self,
        *,
        model_id: ModelIdT,
        messages: Sequence[Message],
        tools: Sequence[Tool] | None = None,
        format: type[FormattableT] | Format[FormattableT] | None = None,
        params: ParamsT | None = None,
    ) -> Response | Response[FormattableT]:
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
        tools: Sequence[Tool | ContextTool[DepsT]] | None = None,
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
        tools: Sequence[Tool | ContextTool[DepsT]] | None = None,
        format: type[FormattableT] | Format[FormattableT],
        params: ParamsT | None = None,
    ) -> ContextResponse[DepsT, FormattableT]: ...

    @overload
    @abstractmethod
    def context_call(
        self,
        *,
        ctx: Context[DepsT],
        model_id: ModelIdT,
        messages: Sequence[Message],
        tools: Sequence[Tool | ContextTool[DepsT]] | None = None,
        format: type[FormattableT] | Format[FormattableT] | None,
        params: ParamsT | None = None,
    ) -> ContextResponse[DepsT, None] | ContextResponse[DepsT, FormattableT]: ...

    @abstractmethod
    def context_call(
        self,
        *,
        ctx: Context[DepsT],
        model_id: ModelIdT,
        messages: Sequence[Message],
        tools: Sequence[Tool | ContextTool[DepsT]] | None = None,
        format: type[FormattableT] | Format[FormattableT] | None = None,
        params: ParamsT | None = None,
    ) -> ContextResponse[DepsT, None] | ContextResponse[DepsT, FormattableT]:
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
        format: type[FormattableT] | Format[FormattableT],
        params: ParamsT | None = None,
    ) -> AsyncResponse[FormattableT]: ...

    @overload
    @abstractmethod
    async def call_async(
        self,
        *,
        model_id: ModelIdT,
        messages: Sequence[Message],
        tools: Sequence[AsyncTool] | None = None,
        format: type[FormattableT] | Format[FormattableT] | None,
        params: ParamsT | None = None,
    ) -> AsyncResponse | AsyncResponse[FormattableT]: ...

    @abstractmethod
    async def call_async(
        self,
        *,
        model_id: ModelIdT,
        messages: Sequence[Message],
        tools: Sequence[AsyncTool] | None = None,
        format: type[FormattableT] | Format[FormattableT] | None = None,
        params: ParamsT | None = None,
    ) -> AsyncResponse | AsyncResponse[FormattableT]:
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
        tools: Sequence[AsyncTool | AsyncContextTool[DepsT]] | None = None,
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
        tools: Sequence[AsyncTool | AsyncContextTool[DepsT]] | None = None,
        format: type[FormattableT] | Format[FormattableT],
        params: ParamsT | None = None,
    ) -> AsyncContextResponse[DepsT, FormattableT]: ...

    @overload
    @abstractmethod
    async def context_call_async(
        self,
        *,
        ctx: Context[DepsT],
        model_id: ModelIdT,
        messages: Sequence[Message],
        tools: Sequence[AsyncTool | AsyncContextTool[DepsT]] | None = None,
        format: type[FormattableT] | Format[FormattableT] | None,
        params: ParamsT | None = None,
    ) -> (
        AsyncContextResponse[DepsT, None] | AsyncContextResponse[DepsT, FormattableT]
    ): ...

    @abstractmethod
    async def context_call_async(
        self,
        *,
        ctx: Context[DepsT],
        model_id: ModelIdT,
        messages: Sequence[Message],
        tools: Sequence[AsyncTool | AsyncContextTool[DepsT]] | None = None,
        format: type[FormattableT] | Format[FormattableT] | None = None,
        params: ParamsT | None = None,
    ) -> AsyncContextResponse[DepsT, None] | AsyncContextResponse[DepsT, FormattableT]:
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
        format: type[FormattableT] | Format[FormattableT],
        params: ParamsT | None = None,
    ) -> StreamResponse[FormattableT]: ...

    @overload
    @abstractmethod
    def stream(
        self,
        *,
        model_id: ModelIdT,
        messages: Sequence[Message],
        tools: Sequence[Tool] | None = None,
        format: type[FormattableT] | Format[FormattableT] | None,
        params: ParamsT | None = None,
    ) -> StreamResponse | StreamResponse[FormattableT]: ...

    @abstractmethod
    def stream(
        self,
        *,
        model_id: ModelIdT,
        messages: Sequence[Message],
        tools: Sequence[Tool] | None = None,
        format: type[FormattableT] | Format[FormattableT] | None = None,
        params: ParamsT | None = None,
    ) -> StreamResponse | StreamResponse[FormattableT]:
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
        tools: Sequence[Tool | ContextTool[DepsT]] | None = None,
        format: None = None,
        params: ParamsT | None = None,
    ) -> ContextStreamResponse[DepsT, None]: ...

    @overload
    @abstractmethod
    def context_stream(
        self,
        *,
        ctx: Context[DepsT],
        model_id: ModelIdT,
        messages: Sequence[Message],
        tools: Sequence[Tool | ContextTool[DepsT]] | None = None,
        format: type[FormattableT] | Format[FormattableT],
        params: ParamsT | None = None,
    ) -> ContextStreamResponse[DepsT, FormattableT]: ...

    @overload
    @abstractmethod
    def context_stream(
        self,
        *,
        ctx: Context[DepsT],
        model_id: ModelIdT,
        messages: Sequence[Message],
        tools: Sequence[Tool | ContextTool[DepsT]] | None = None,
        format: type[FormattableT] | Format[FormattableT] | None,
        params: ParamsT | None = None,
    ) -> (
        ContextStreamResponse[DepsT, None] | ContextStreamResponse[DepsT, FormattableT]
    ): ...

    @abstractmethod
    def context_stream(
        self,
        *,
        ctx: Context[DepsT],
        model_id: ModelIdT,
        messages: Sequence[Message],
        tools: Sequence[Tool | ContextTool[DepsT]] | None = None,
        format: type[FormattableT] | Format[FormattableT] | None = None,
        params: ParamsT | None = None,
    ) -> (
        ContextStreamResponse[DepsT, None] | ContextStreamResponse[DepsT, FormattableT]
    ):
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
        format: type[FormattableT] | Format[FormattableT],
        params: ParamsT | None = None,
    ) -> AsyncStreamResponse[FormattableT]: ...

    @overload
    @abstractmethod
    async def stream_async(
        self,
        *,
        model_id: ModelIdT,
        messages: Sequence[Message],
        tools: Sequence[AsyncTool] | None = None,
        format: type[FormattableT] | Format[FormattableT] | None,
        params: ParamsT | None = None,
    ) -> AsyncStreamResponse | AsyncStreamResponse[FormattableT]: ...

    @abstractmethod
    async def stream_async(
        self,
        *,
        model_id: ModelIdT,
        messages: Sequence[Message],
        tools: Sequence[AsyncTool] | None = None,
        format: type[FormattableT] | Format[FormattableT] | None = None,
        params: ParamsT | None = None,
    ) -> AsyncStreamResponse | AsyncStreamResponse[FormattableT]:
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
        tools: Sequence[AsyncTool | AsyncContextTool[DepsT]] | None = None,
        format: None = None,
        params: ParamsT | None = None,
    ) -> AsyncContextStreamResponse[DepsT, None]: ...

    @overload
    @abstractmethod
    async def context_stream_async(
        self,
        *,
        ctx: Context[DepsT],
        model_id: ModelIdT,
        messages: Sequence[Message],
        tools: Sequence[AsyncTool | AsyncContextTool[DepsT]] | None = None,
        format: type[FormattableT] | Format[FormattableT],
        params: ParamsT | None = None,
    ) -> AsyncContextStreamResponse[DepsT, FormattableT]: ...

    @overload
    @abstractmethod
    async def context_stream_async(
        self,
        *,
        ctx: Context[DepsT],
        model_id: ModelIdT,
        messages: Sequence[Message],
        tools: Sequence[AsyncTool | AsyncContextTool[DepsT]] | None = None,
        format: type[FormattableT] | Format[FormattableT] | None,
        params: ParamsT | None = None,
    ) -> (
        AsyncContextStreamResponse[DepsT, None]
        | AsyncContextStreamResponse[DepsT, FormattableT]
    ): ...

    @abstractmethod
    async def context_stream_async(
        self,
        *,
        ctx: Context[DepsT],
        model_id: ModelIdT,
        messages: Sequence[Message],
        tools: Sequence[AsyncTool | AsyncContextTool[DepsT]] | None = None,
        format: type[FormattableT] | Format[FormattableT] | None = None,
        params: ParamsT | None = None,
    ) -> (
        AsyncContextStreamResponse[DepsT, None]
        | AsyncContextStreamResponse[DepsT, FormattableT]
    ):
        """Stream a context response asynchronously."""
        ...
