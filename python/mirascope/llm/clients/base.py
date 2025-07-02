"""Base abstract interface for provider clients."""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Sequence
from typing import Any, Generic, TypedDict, TypeVar

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
from .register import REGISTERED_LLMS

T = TypeVar("T", bound=object | None)
MessageT = TypeVar("MessageT")
ParamsT = TypeVar("ParamsT", bound="BaseParams")
DepsT = TypeVar("DepsT")
LLMT = TypeVar("LLMT", bound=REGISTERED_LLMS)


class BaseParams(TypedDict, total=False):
    """The base interface for LLM parameters."""

    temperature: float
    """Controls randomness in response generation. Lower values (closer to 0) make responses more deterministic, higher values (closer to 1) make them more creative."""
    
    max_tokens: int
    """Maximum number of tokens to generate in the response."""


class BaseClient(Generic[MessageT, ParamsT, LLMT], ABC):
    """Base abstract client for provider-specific implementations.

    This class defines explicit methods for each type of call, eliminating
    the need for complex overloads in provider implementations.
    """

    @abstractmethod
    def call(
        self,
        *,
        model: LLMT,
        messages: Sequence[MessageT],
        tools: Sequence[ToolDef] | None = None,
        params: ParamsT | None = None,
    ) -> Response:
        """Generate a standard response."""
        ...

    @abstractmethod
    def context_call(
        self,
        *,
        model: LLMT,
        messages: Sequence[MessageT],
        tools: Sequence[ToolDef | ContextToolDef[..., Any, DepsT]],
        params: ParamsT | None = None,
    ) -> ContextResponse:
        """Generate a context response with context tools."""
        ...

    @abstractmethod
    def structured_call(
        self,
        *,
        model: LLMT,
        messages: Sequence[MessageT],
        tools: Sequence[ToolDef] | None = None,
        response_format: type[T],
        params: ParamsT | None = None,
    ) -> Response[T]:
        """Generate a structured response."""
        ...

    @abstractmethod
    def structured_context_call(
        self,
        *,
        model: LLMT,
        messages: Sequence[MessageT],
        tools: Sequence[ToolDef | ContextToolDef[..., Any, DepsT]],
        response_format: type[T],
        params: ParamsT | None = None,
    ) -> ContextResponse[T]:
        """Generate a structured context response."""
        ...

    @abstractmethod
    async def call_async(
        self,
        *,
        model: LLMT,
        messages: Sequence[MessageT],
        tools: Sequence[ToolDef] | None = None,
        params: ParamsT | None = None,
    ) -> Response:
        """Generate a standard response asynchronously."""
        ...

    @abstractmethod
    async def context_call_async(
        self,
        *,
        model: LLMT,
        messages: Sequence[MessageT],
        tools: Sequence[ToolDef | ContextToolDef[..., Any, DepsT]],
        params: ParamsT | None = None,
    ) -> ContextResponse:
        """Generate a context response asynchronously."""
        ...

    @abstractmethod
    async def structured_call_async(
        self,
        *,
        model: LLMT,
        messages: Sequence[MessageT],
        tools: Sequence[ToolDef] | None = None,
        response_format: type[T],
        params: ParamsT | None = None,
    ) -> Response[T]:
        """Generate a structured response asynchronously."""
        ...

    @abstractmethod
    async def structured_context_call_async(
        self,
        *,
        model: LLMT,
        messages: Sequence[MessageT],
        tools: Sequence[ToolDef | ContextToolDef[..., Any, DepsT]],
        response_format: type[T],
        params: ParamsT | None = None,
    ) -> ContextResponse[T]:
        """Generate a structured context response asynchronously."""
        ...

    @abstractmethod
    def stream(
        self,
        *,
        model: LLMT,
        messages: Sequence[MessageT],
        tools: Sequence[ToolDef] | None = None,
        params: ParamsT | None = None,
    ) -> Stream:
        """Stream a standard response."""
        ...

    @abstractmethod
    def context_stream(
        self,
        *,
        model: LLMT,
        messages: Sequence[MessageT],
        tools: Sequence[ToolDef | ContextToolDef[..., Any, DepsT]],
        params: ParamsT | None = None,
    ) -> ContextStream[DepsT]:
        """Stream a context response."""
        ...

    @abstractmethod
    def structured_stream(
        self,
        *,
        model: LLMT,
        messages: Sequence[MessageT],
        tools: Sequence[ToolDef] | None = None,
        response_format: type[T],
        params: ParamsT | None = None,
    ) -> StructuredStream[T]:
        """Stream a structured response."""
        ...

    @abstractmethod
    def structured_context_stream(
        self,
        *,
        model: LLMT,
        messages: Sequence[MessageT],
        tools: Sequence[ToolDef | ContextToolDef[..., Any, DepsT]],
        response_format: type[T],
        params: ParamsT | None = None,
    ) -> ContextStructuredStream[DepsT, T]:
        """Stream a structured context response."""
        ...

    @abstractmethod
    async def stream_async(
        self,
        *,
        model: LLMT,
        messages: Sequence[MessageT],
        tools: Sequence[ToolDef] | None = None,
        params: ParamsT | None = None,
    ) -> AsyncStream:
        """Stream a standard response asynchronously."""
        ...

    @abstractmethod
    async def context_stream_async(
        self,
        *,
        model: LLMT,
        messages: Sequence[MessageT],
        tools: Sequence[ToolDef | ContextToolDef[..., Any, DepsT]],
        params: ParamsT | None = None,
    ) -> AsyncContextStream[DepsT]:
        """Stream a context response asynchronously."""
        ...

    @abstractmethod
    async def structured_stream_async(
        self,
        *,
        model: LLMT,
        messages: Sequence[MessageT],
        tools: Sequence[ToolDef] | None = None,
        response_format: type[T],
        params: ParamsT | None = None,
    ) -> AsyncStructuredStream[T]:
        """Stream a structured response asynchronously."""
        ...

    @abstractmethod
    async def structured_context_stream_async(
        self,
        *,
        model: LLMT,
        messages: Sequence[MessageT],
        tools: Sequence[ToolDef | ContextToolDef[..., Any, DepsT]],
        response_format: type[T],
        params: ParamsT | None = None,
    ) -> AsyncContextStructuredStream[DepsT, T]:
        """Stream a structured context response asynchronously."""
        ...
