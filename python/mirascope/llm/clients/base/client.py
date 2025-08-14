"""Base abstract interface for provider clients."""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Sequence
from typing import Generic

from typing_extensions import TypeVar

from ...context import Context, DepsT
from ...formatting import FormatT
from ...messages import Message
from ...responses import AsyncStreamResponse, Response, StreamResponse
from ...tools import AsyncContextTool, AsyncTool, ContextTool, Tool
from .params import ParamsT

ModelT = TypeVar("ModelT", bound=str)
ProviderClientT = TypeVar("ProviderClientT")

ClientT = TypeVar("ClientT", bound="BaseClient")
"""Type variable for an LLM client."""


class BaseClient(Generic[ParamsT, ModelT, ProviderClientT], ABC):
    """Base abstract client for provider-specific implementations.

    This class defines explicit methods for each type of call, eliminating
    the need for complex overloads in provider implementations.
    """

    client: ProviderClientT

    @abstractmethod
    def call(
        self,
        *,
        model: ModelT,
        messages: Sequence[Message],
        tools: Sequence[Tool] | None = None,
        params: ParamsT | None = None,
    ) -> Response[None]:
        """Generate a standard response."""
        ...

    @abstractmethod
    def context_call(
        self,
        *,
        ctx: Context[DepsT],
        model: ModelT,
        messages: Sequence[Message],
        tools: Sequence[Tool | ContextTool[DepsT]],
        params: ParamsT | None = None,
    ) -> Response[None]:
        """Generate a context response with context tools."""
        ...

    @abstractmethod
    def structured_call(
        self,
        *,
        model: ModelT,
        messages: Sequence[Message],
        tools: Sequence[Tool] | None = None,
        format: type[FormatT],
        params: ParamsT | None = None,
    ) -> Response[FormatT]:
        """Generate a structured response."""
        ...

    @abstractmethod
    def structured_context_call(
        self,
        *,
        ctx: Context[DepsT],
        model: ModelT,
        messages: Sequence[Message],
        tools: Sequence[Tool | ContextTool[DepsT]],
        format: type[FormatT],
        params: ParamsT | None = None,
    ) -> Response[FormatT]:
        """Generate a structured context response."""
        ...

    @abstractmethod
    async def call_async(
        self,
        *,
        model: ModelT,
        messages: Sequence[Message],
        tools: Sequence[AsyncTool] | None = None,
        params: ParamsT | None = None,
    ) -> Response[None]:
        """Generate a standard response asynchronously."""
        ...

    @abstractmethod
    async def context_call_async(
        self,
        *,
        ctx: Context[DepsT],
        model: ModelT,
        messages: Sequence[Message],
        tools: Sequence[AsyncTool | AsyncContextTool[DepsT]],
        params: ParamsT | None = None,
    ) -> Response[None]:
        """Generate a context response asynchronously."""
        ...

    @abstractmethod
    async def structured_call_async(
        self,
        *,
        model: ModelT,
        messages: Sequence[Message],
        tools: Sequence[AsyncTool] | None = None,
        format: type[FormatT],
        params: ParamsT | None = None,
    ) -> Response[FormatT]:
        """Generate a structured response asynchronously."""
        ...

    @abstractmethod
    async def structured_context_call_async(
        self,
        *,
        ctx: Context[DepsT],
        model: ModelT,
        messages: Sequence[Message],
        tools: Sequence[AsyncTool | AsyncContextTool[DepsT]],
        format: type[FormatT],
        params: ParamsT | None = None,
    ) -> Response[FormatT]:
        """Generate a structured context response asynchronously."""
        ...

    @abstractmethod
    def stream(
        self,
        *,
        model: ModelT,
        messages: Sequence[Message],
        tools: Sequence[Tool] | None = None,
        params: ParamsT | None = None,
    ) -> StreamResponse:
        """Stream a standard response."""
        ...

    @abstractmethod
    def context_stream(
        self,
        *,
        ctx: Context[DepsT],
        model: ModelT,
        messages: Sequence[Message],
        tools: Sequence[Tool | ContextTool[DepsT]],
        params: ParamsT | None = None,
    ) -> StreamResponse:
        """Stream a context response."""
        ...

    @abstractmethod
    def structured_stream(
        self,
        *,
        model: ModelT,
        messages: Sequence[Message],
        tools: Sequence[Tool] | None = None,
        format: type[FormatT],
        params: ParamsT | None = None,
    ) -> StreamResponse[FormatT]:
        """Stream a structured response."""
        ...

    @abstractmethod
    def structured_context_stream(
        self,
        *,
        ctx: Context[DepsT],
        model: ModelT,
        messages: Sequence[Message],
        tools: Sequence[Tool | ContextTool[DepsT]],
        format: type[FormatT],
        params: ParamsT | None = None,
    ) -> StreamResponse[FormatT]:
        """Stream a structured context response."""
        ...

    @abstractmethod
    async def stream_async(
        self,
        *,
        model: ModelT,
        messages: Sequence[Message],
        tools: Sequence[AsyncTool] | None = None,
        params: ParamsT | None = None,
    ) -> AsyncStreamResponse:
        """Stream a standard response asynchronously."""
        ...

    @abstractmethod
    async def context_stream_async(
        self,
        *,
        ctx: Context[DepsT],
        model: ModelT,
        messages: Sequence[Message],
        tools: Sequence[AsyncTool | AsyncContextTool[DepsT]],
        params: ParamsT | None = None,
    ) -> AsyncStreamResponse:
        """Stream a context response asynchronously."""
        ...

    @abstractmethod
    async def structured_stream_async(
        self,
        *,
        model: ModelT,
        messages: Sequence[Message],
        tools: Sequence[AsyncTool] | None = None,
        format: type[FormatT],
        params: ParamsT | None = None,
    ) -> AsyncStreamResponse[FormatT]:
        """Stream a structured response asynchronously."""
        ...

    @abstractmethod
    async def structured_context_stream_async(
        self,
        *,
        ctx: Context[DepsT],
        model: ModelT,
        messages: Sequence[Message],
        tools: Sequence[AsyncTool | AsyncContextTool[DepsT]],
        format: type[FormatT],
        params: ParamsT | None = None,
    ) -> AsyncStreamResponse[FormatT]:
        """Stream a structured context response asynchronously."""
        ...
