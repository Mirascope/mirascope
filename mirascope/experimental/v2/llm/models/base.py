"""The base abstract model interfaces for LLM models."""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Sequence
from typing import Generic, TypeVar, overload

from typing_extensions import TypedDict

from ..messages import Message
from ..response_formatting import ResponseFormat
from ..responses import (
    AsyncStream,
    AsyncStructuredStream,
    Response,
    Stream,
    StructuredStream,
)
from ..tools import ToolDef

T = TypeVar("T")
ParamsT = TypeVar("ParamsT", bound="Params")
ClientT = TypeVar("ClientT", bound="Client")


class Params(TypedDict, total=False):
    """The base interface for LLM parameters."""


class Client:
    """The base interface for LLM clients."""


class LLM(Generic[ParamsT, ClientT], ABC):
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
        messages: list[Message],
        tools: Sequence[ToolDef] | None = None,
        response_format: None = None,
        params: ParamsT | None = None,
    ) -> Response:
        """Overload for call when there's no response format specified."""
        ...

    @overload
    def call(
        self,
        *,
        messages: list[Message],
        tools: Sequence[ToolDef] | None = None,
        response_format: ResponseFormat[T],
        params: ParamsT | None = None,
    ) -> Response[T]:
        """Overload for calls when a response format is specified."""
        ...

    @abstractmethod
    def call(
        self,
        *,
        messages: list[Message],
        tools: Sequence[ToolDef] | None = None,
        response_format: ResponseFormat[T] | None = None,
        params: ParamsT | None = None,
    ) -> Response | Response[T]:
        """Generate a response using the model."""
        ...

    @overload
    async def call_async(
        self,
        *,
        messages: list[Message],
        tools: Sequence[ToolDef] | None = None,
        response_format: None = None,
        params: ParamsT | None = None,
    ) -> Response:
        """Overload for async calls when there's no response format specified."""
        ...

    @overload
    async def call_async(
        self,
        *,
        messages: list[Message],
        tools: Sequence[ToolDef] | None = None,
        response_format: ResponseFormat[T],
        params: ParamsT | None = None,
    ) -> Response[T]:
        """Overload for async calls when a response format is specified."""
        ...

    @abstractmethod
    async def call_async(
        self,
        *,
        messages: list[Message],
        tools: Sequence[ToolDef] | None = None,
        response_format: ResponseFormat[T] | None = None,
        params: ParamsT | None = None,
    ) -> Response | Response[T]:
        """Generate a response asynchronously using the model."""
        ...

    @overload
    def stream(
        self,
        *,
        messages: list[Message],
        tools: Sequence[ToolDef] | None = None,
        response_format: None = None,
        params: ParamsT | None = None,
    ) -> Stream:
        """Overload for streaming when there's no response format specified."""
        ...

    @overload
    def stream(
        self,
        *,
        messages: list[Message],
        tools: Sequence[ToolDef] | None = None,
        response_format: ResponseFormat[T],
        params: ParamsT | None = None,
    ) -> StructuredStream[T]:
        """Overload for streaming when a response format is specified."""
        ...

    @abstractmethod
    def stream(
        self,
        *,
        messages: list[Message],
        tools: Sequence[ToolDef] | None = None,
        response_format: ResponseFormat[T] | None = None,
        params: ParamsT | None = None,
    ) -> Stream | StructuredStream[T]:
        """Stream a response using the model."""
        ...

    @overload
    async def stream_async(
        self,
        *,
        messages: list[Message],
        tools: Sequence[ToolDef] | None = None,
        response_format: None = None,
        params: ParamsT | None = None,
    ) -> AsyncStream:
        """Overload for async streaming when there's no response format specified."""
        ...

    @overload
    async def stream_async(
        self,
        *,
        messages: list[Message],
        tools: Sequence[ToolDef] | None = None,
        response_format: ResponseFormat[T],
        params: ParamsT | None = None,
    ) -> AsyncStructuredStream[T]:
        """Overload for async streaming when a response format is specified."""
        ...

    @abstractmethod
    async def stream_async(
        self,
        messages: list[Message],
        tools: Sequence[ToolDef] | None = None,
        response_format: ResponseFormat[T] | None = None,
        params: ParamsT | None = None,
    ) -> AsyncStream | AsyncStructuredStream[T]:
        """Stream a response asynchronously using the model."""
        ...
