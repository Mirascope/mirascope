"""The base abstract model interfaces for LLM models."""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Sequence
from typing import Any, Generic, overload

from typing_extensions import TypedDict, TypeVar

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
from ..types import Dataclass

T = TypeVar("T", bound=Dataclass | None, default=None)
MessageT = TypeVar("MessageT")
ParamsT = TypeVar("ParamsT", bound="Params")
ClientT = TypeVar("ClientT", bound="Client")
DepsT = TypeVar("DepsT", default=None)


class Params(TypedDict, total=False):
    """The base interface for LLM parameters."""


class Client:
    """The base interface for LLM clients."""


class LLM(Generic[MessageT, ParamsT, ClientT], ABC):
    """The base interface for LLM models.

    This class defines the interface for interacting with language models from
    various providers. It handles the common operations like generating responses,
    streaming, and async variants of these operations.

    Implementations of this class for specific providers should extend it and
    implement the abstract methods for calls and streaming.
    """

    provider: str
    """The provider of the model (e.g., 'google', 'openai', 'anthropic', etc.)."""

    name: str
    """The name of the model (e.g., 'gpt-4', 'claude-3-5-sonnet', 'gemini-2.5-flash')."""

    params: ParamsT
    """The default parameters for the model (temperature, max_tokens, etc.)."""

    client: ClientT
    """The client object used to interact with the model API."""

    @abstractmethod
    def __init__(
        self,
        *,
        provider: str,
        name: str,
        params: ParamsT | None = None,
        client: ClientT | None = None,
    ) -> None:
        """Initializes a `GenerativeModel` instance."""
        ...

    @overload
    def call(
        self,
        *,
        messages: Sequence[MessageT],
        tools: Sequence[ToolDef] | None = None,
        response_format: None = None,
        params: ParamsT | None = None,
    ) -> Response:
        """Overload for standard call."""
        ...

    @overload
    def call(
        self,
        *,
        messages: Sequence[MessageT],
        tools: Sequence[ToolDef | ContextToolDef[..., Any, DepsT]],
        response_format: None = None,
        params: ParamsT | None = None,
    ) -> ContextResponse:
        """Overload for standard context call."""
        ...

    @overload
    def call(
        self,
        *,
        messages: Sequence[MessageT],
        tools: Sequence[ToolDef] | None = None,
        response_format: type[T],
        params: ParamsT | None = None,
    ) -> Response[T]:
        """Overload for calls when a response format is specified."""
        ...

    @overload
    def call(
        self,
        *,
        messages: Sequence[MessageT],
        tools: Sequence[ToolDef | ContextToolDef[..., Any, DepsT]],
        response_format: type[T],
        params: ParamsT | None = None,
    ) -> ContextResponse[T]:
        """Overload for calls when a response format is specified."""
        ...

    @abstractmethod
    def call(
        self,
        *,
        messages: Sequence[MessageT],
        tools: Sequence[ToolDef]
        | Sequence[ToolDef | ContextToolDef[..., Any, DepsT]]
        | None = None,
        response_format: type[T] | None = None,
        params: ParamsT | None = None,
    ) -> Response | Response[T] | ContextResponse | ContextResponse[T]:
        """Generate a response using the model."""
        ...

    @overload
    async def call_async(
        self,
        *,
        messages: Sequence[MessageT],
        tools: Sequence[ToolDef] | None = None,
        response_format: None = None,
        params: ParamsT | None = None,
    ) -> Response:
        """Overload for standard async call."""
        ...

    @overload
    async def call_async(
        self,
        *,
        messages: Sequence[MessageT],
        tools: Sequence[ToolDef | ContextToolDef[..., Any, DepsT]],
        response_format: None = None,
        params: ParamsT | None = None,
    ) -> ContextResponse:
        """Overload for standard async context call."""
        ...

    @overload
    async def call_async(
        self,
        *,
        messages: Sequence[MessageT],
        tools: Sequence[ToolDef] | None = None,
        response_format: type[T],
        params: ParamsT | None = None,
    ) -> Response[T]:
        """Overload for async calls when a response format is specified."""
        ...

    @overload
    async def call_async(
        self,
        *,
        messages: Sequence[MessageT],
        tools: Sequence[ToolDef | ContextToolDef[..., Any, DepsT]],
        response_format: type[T],
        params: ParamsT | None = None,
    ) -> ContextResponse[T]:
        """Overload for async context calls when a response format is specified."""
        ...

    @abstractmethod
    async def call_async(
        self,
        *,
        messages: Sequence[MessageT],
        tools: Sequence[ToolDef]
        | Sequence[ToolDef | ContextToolDef[..., Any, DepsT]]
        | None = None,
        response_format: type[T] | None = None,
        params: ParamsT | None = None,
    ) -> Response | Response[T] | ContextResponse | ContextResponse[T]:
        """Generate a response asynchronously using the model."""
        ...

    @overload
    def stream(
        self,
        *,
        messages: Sequence[MessageT],
        tools: Sequence[ToolDef] | None = None,
        response_format: None = None,
        params: ParamsT | None = None,
    ) -> Stream:
        """Overload for standard streaming."""
        ...

    @overload
    def stream(
        self,
        *,
        messages: Sequence[MessageT],
        tools: Sequence[ToolDef | ContextToolDef[..., Any, DepsT]],
        response_format: None = None,
        params: ParamsT | None = None,
    ) -> ContextStream[DepsT]:
        """Overload for standard context streaming."""
        ...

    @overload
    def stream(
        self,
        *,
        messages: Sequence[MessageT],
        tools: Sequence[ToolDef] | None = None,
        response_format: type[T],
        params: ParamsT | None = None,
    ) -> StructuredStream[T]:
        """Overload for structured streaming."""
        ...

    @overload
    def stream(
        self,
        *,
        messages: Sequence[MessageT],
        tools: Sequence[ToolDef | ContextToolDef[..., Any, DepsT]],
        response_format: type[T],
        params: ParamsT | None = None,
    ) -> ContextStructuredStream[DepsT, T]:
        """Overload for context structured streaming."""
        ...

    @abstractmethod
    def stream(
        self,
        *,
        messages: Sequence[MessageT],
        tools: Sequence[ToolDef]
        | Sequence[ToolDef | ContextToolDef[..., Any, DepsT]]
        | None = None,
        response_format: type[T] | None = None,
        params: ParamsT | None = None,
    ) -> (
        Stream
        | StructuredStream[T]
        | ContextStream[DepsT]
        | ContextStructuredStream[DepsT, T]
    ):
        """Stream a response using the model."""
        ...

    @overload
    async def stream_async(
        self,
        *,
        messages: list[MessageT],
        tools: Sequence[ToolDef] | None = None,
        response_format: None = None,
        params: ParamsT | None = None,
    ) -> AsyncStream:
        """Overload for standard async streaming."""
        ...

    @overload
    async def stream_async(
        self,
        *,
        messages: list[MessageT],
        tools: Sequence[ToolDef | ContextToolDef[..., Any, DepsT]],
        response_format: None = None,
        params: ParamsT | None = None,
    ) -> AsyncContextStream[DepsT]:
        """Overload for standard async context streaming."""
        ...

    @overload
    async def stream_async(
        self,
        *,
        messages: list[MessageT],
        tools: Sequence[ToolDef] | None = None,
        response_format: type[T],
        params: ParamsT | None = None,
    ) -> AsyncStructuredStream[T]:
        """Overload for async structured streaming."""
        ...

    @overload
    async def stream_async(
        self,
        *,
        messages: list[MessageT],
        tools: Sequence[ToolDef | ContextToolDef[..., Any, DepsT]],
        response_format: type[T],
        params: ParamsT | None = None,
    ) -> AsyncContextStructuredStream[DepsT, T]:
        """Overload for async context structured streaming."""
        ...

    @abstractmethod
    async def stream_async(
        self,
        *,
        messages: list[MessageT],
        tools: Sequence[ToolDef]
        | Sequence[ToolDef | ContextToolDef[..., Any, DepsT]]
        | None = None,
        response_format: type[T] | None = None,
        params: ParamsT | None = None,
    ) -> (
        AsyncStream
        | AsyncStructuredStream[T]
        | AsyncContextStream[DepsT]
        | AsyncContextStructuredStream[DepsT, T]
    ):
        """Stream a response asynchronously using the model."""
        ...
