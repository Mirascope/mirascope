"""Base abstract interface for provider clients."""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Sequence
from typing import TYPE_CHECKING, Generic

from typing_extensions import TypeVar

from ...context import Context, DepsT
from ...formatting import FormatT
from ...responses import (
    Response,
    StreamResponse,
)
from ...streams import AsyncStream, Stream
from ...tools import AsyncContextTool, AsyncTool, ContextTool, Tool
from ...types import Jsonable
from .params import ParamsT

if TYPE_CHECKING:
    from ..registered_llms import LLMT
else:
    # Use a string bound to avoid circular import at runtime
    LLMT = TypeVar("LLMT", bound=str)

ClientT = TypeVar("ClientT", bound="BaseClient")
"""Type variable for an LLM client."""


ProviderMessageT = TypeVar("ProviderMessageT")
"""Type variable for an LLM that is usable by a specific LLM provider.

May often be the union of generic `llm.Message` and a provider-specific message representation.
"""


class BaseClient(Generic[ProviderMessageT, ParamsT, LLMT], ABC):
    """Base abstract client for provider-specific implementations.

    This class defines explicit methods for each type of call, eliminating
    the need for complex overloads in provider implementations.
    """

    @abstractmethod
    def call(
        self,
        *,
        model: LLMT,
        messages: Sequence[ProviderMessageT],
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
        model: LLMT,
        messages: Sequence[ProviderMessageT],
        tools: Sequence[Tool | ContextTool[..., Jsonable, DepsT]],
        params: ParamsT | None = None,
    ) -> Response[None]:
        """Generate a context response with context tools."""
        ...

    @abstractmethod
    def structured_call(
        self,
        *,
        model: LLMT,
        messages: Sequence[ProviderMessageT],
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
        model: LLMT,
        messages: Sequence[ProviderMessageT],
        tools: Sequence[Tool | ContextTool[..., Jsonable, DepsT]],
        format: type[FormatT],
        params: ParamsT | None = None,
    ) -> Response[FormatT]:
        """Generate a structured context response."""
        ...

    @abstractmethod
    async def call_async(
        self,
        *,
        model: LLMT,
        messages: Sequence[ProviderMessageT],
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
        model: LLMT,
        messages: Sequence[ProviderMessageT],
        tools: Sequence[AsyncTool | AsyncContextTool[..., Jsonable, DepsT]],
        params: ParamsT | None = None,
    ) -> Response[None]:
        """Generate a context response asynchronously."""
        ...

    @abstractmethod
    async def structured_call_async(
        self,
        *,
        model: LLMT,
        messages: Sequence[ProviderMessageT],
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
        model: LLMT,
        messages: Sequence[ProviderMessageT],
        tools: Sequence[AsyncTool | AsyncContextTool[..., Jsonable, DepsT]],
        format: type[FormatT],
        params: ParamsT | None = None,
    ) -> Response[FormatT]:
        """Generate a structured context response asynchronously."""
        ...

    @abstractmethod
    def stream(
        self,
        *,
        model: LLMT,
        messages: Sequence[ProviderMessageT],
        tools: Sequence[Tool] | None = None,
        params: ParamsT | None = None,
    ) -> StreamResponse[Stream, None]:
        """Stream a standard response."""
        ...

    @abstractmethod
    def context_stream(
        self,
        *,
        ctx: Context[DepsT],
        model: LLMT,
        messages: Sequence[ProviderMessageT],
        tools: Sequence[Tool | ContextTool[..., Jsonable, DepsT]],
        params: ParamsT | None = None,
    ) -> StreamResponse[Stream, None]:
        """Stream a context response."""
        ...

    @abstractmethod
    def structured_stream(
        self,
        *,
        model: LLMT,
        messages: Sequence[ProviderMessageT],
        tools: Sequence[Tool] | None = None,
        format: type[FormatT],
        params: ParamsT | None = None,
    ) -> StreamResponse[Stream, FormatT]:
        """Stream a structured response."""
        ...

    @abstractmethod
    def structured_context_stream(
        self,
        *,
        ctx: Context[DepsT],
        model: LLMT,
        messages: Sequence[ProviderMessageT],
        tools: Sequence[Tool | ContextTool[..., Jsonable, DepsT]],
        format: type[FormatT],
        params: ParamsT | None = None,
    ) -> StreamResponse[Stream, FormatT]:
        """Stream a structured context response."""
        ...

    @abstractmethod
    async def stream_async(
        self,
        *,
        model: LLMT,
        messages: Sequence[ProviderMessageT],
        tools: Sequence[AsyncTool] | None = None,
        params: ParamsT | None = None,
    ) -> StreamResponse[AsyncStream, None]:
        """Stream a standard response asynchronously."""
        ...

    @abstractmethod
    async def context_stream_async(
        self,
        *,
        ctx: Context[DepsT],
        model: LLMT,
        messages: Sequence[ProviderMessageT],
        tools: Sequence[AsyncTool | AsyncContextTool[..., Jsonable, DepsT]],
        params: ParamsT | None = None,
    ) -> StreamResponse[AsyncStream, None]:
        """Stream a context response asynchronously."""
        ...

    @abstractmethod
    async def structured_stream_async(
        self,
        *,
        model: LLMT,
        messages: Sequence[ProviderMessageT],
        tools: Sequence[AsyncTool] | None = None,
        format: type[FormatT],
        params: ParamsT | None = None,
    ) -> StreamResponse[AsyncStream, FormatT]:
        """Stream a structured response asynchronously."""
        ...

    @abstractmethod
    async def structured_context_stream_async(
        self,
        *,
        ctx: Context[DepsT],
        model: LLMT,
        messages: Sequence[ProviderMessageT],
        tools: Sequence[AsyncTool | AsyncContextTool[..., Jsonable, DepsT]],
        format: type[FormatT],
        params: ParamsT | None = None,
    ) -> StreamResponse[AsyncStream, FormatT]:
        """Stream a structured context response asynchronously."""
        ...
