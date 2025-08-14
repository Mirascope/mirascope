"""The base model interfaces for LLM models."""

from __future__ import annotations

from collections.abc import Sequence
from typing import TYPE_CHECKING, Generic, overload

from ..clients import ClientT, ParamsT
from ..context import Context
from ..messages import Message
from ..responses import AsyncStreamResponse, Response, StreamResponse
from ..tools import AsyncContextTool, AsyncTool, ContextTool, Tool

if TYPE_CHECKING:
    from ..clients import Model, Provider

from ..context import DepsT
from ..formatting import FormatT


class LLM(Generic[ClientT, ParamsT]):
    """The unified LLM interface that delegates to provider-specific clients.

    This class provides a consistent interface for interacting with language models
    from various providers. It handles the common operations like generating responses,
    streaming, and async variants by delegating to the appropriate client methods.
    """

    provider: Provider
    """The provider being used (e.g. `openai`)."""

    model: Model
    """The model being used (e.g. `gpt-4o-mini`)."""

    client: ClientT
    """The client object used to interact with the model API."""

    params: ParamsT
    """The default parameters for the model (temperature, max_tokens, etc.)."""

    def __init__(
        self,
        *,
        provider: str,
        name: str,
        client: ClientT | None = None,
        params: ParamsT | None = None,
    ) -> None:
        """Initializes an `LLM` instance."""
        raise NotImplementedError()

    @overload
    def call(
        self,
        *,
        messages: Sequence[Message],
        tools: Sequence[Tool] | None = None,
        format: None = None,
    ) -> Response: ...

    @overload
    def call(
        self,
        *,
        messages: Sequence[Message],
        tools: Sequence[Tool] | None = None,
        format: type[FormatT],
    ) -> Response[FormatT]: ...

    def call(
        self,
        *,
        messages: Sequence[Message],
        tools: Sequence[Tool] | None = None,
        format: type[FormatT] | None = None,
    ) -> Response | Response[FormatT]:
        """Generate a response using the model."""
        raise NotImplementedError()

    @overload
    async def call_async(
        self,
        *,
        messages: Sequence[Message],
        tools: Sequence[AsyncTool] | None = None,
        format: None = None,
    ) -> Response: ...

    @overload
    async def call_async(
        self,
        *,
        messages: Sequence[Message],
        tools: Sequence[AsyncTool] | None = None,
        format: type[FormatT],
    ) -> Response[FormatT]: ...

    async def call_async(
        self,
        *,
        messages: Sequence[Message],
        tools: Sequence[AsyncTool] | None = None,
        format: type[FormatT] | None = None,
    ) -> Response | Response[FormatT]:
        """Generate a response asynchronously using the model."""
        raise NotImplementedError()

    @overload
    def stream(
        self,
        *,
        messages: Sequence[Message],
        tools: Sequence[Tool] | None = None,
        format: None = None,
    ) -> StreamResponse: ...

    @overload
    def stream(
        self,
        *,
        messages: Sequence[Message],
        tools: Sequence[Tool] | None = None,
        format: type[FormatT],
    ) -> StreamResponse[FormatT]: ...

    def stream(
        self,
        *,
        messages: Sequence[Message],
        tools: Sequence[Tool] | None = None,
        format: type[FormatT] | None = None,
    ) -> StreamResponse | StreamResponse[FormatT]:
        """Stream a response using the model."""
        raise NotImplementedError()

    @overload
    async def stream_async(
        self,
        *,
        messages: list[Message],
        tools: Sequence[AsyncTool] | None = None,
        format: None = None,
    ) -> AsyncStreamResponse: ...

    @overload
    async def stream_async(
        self,
        *,
        messages: list[Message],
        tools: Sequence[AsyncTool] | None = None,
        format: type[FormatT],
    ) -> AsyncStreamResponse[FormatT]: ...

    async def stream_async(
        self,
        *,
        messages: list[Message],
        tools: Sequence[AsyncTool] | None = None,
        format: type[FormatT] | None = None,
    ) -> AsyncStreamResponse | AsyncStreamResponse[FormatT]:
        """Stream a response asynchronously using the model."""
        raise NotImplementedError()

    @overload
    def context_call(
        self,
        *,
        ctx: Context[DepsT],
        messages: Sequence[Message],
        tools: Sequence[Tool | ContextTool[DepsT]] | None = None,
        format: None = None,
    ) -> Response: ...

    @overload
    def context_call(
        self,
        *,
        ctx: Context[DepsT],
        messages: Sequence[Message],
        tools: Sequence[Tool | ContextTool[DepsT]] | None = None,
        format: type[FormatT],
    ) -> Response[FormatT]: ...

    def context_call(
        self,
        *,
        ctx: Context[DepsT],
        messages: Sequence[Message],
        tools: Sequence[Tool | ContextTool[DepsT]] | None = None,
        format: type[FormatT] | None = None,
    ) -> Response | Response[FormatT]:
        """Generate a response using the model."""
        raise NotImplementedError()

    @overload
    async def context_call_async(
        self,
        *,
        ctx: Context[DepsT],
        messages: Sequence[Message],
        tools: Sequence[AsyncTool | AsyncContextTool[DepsT]] | None = None,
        format: None = None,
    ) -> Response: ...

    @overload
    async def context_call_async(
        self,
        *,
        ctx: Context[DepsT],
        messages: Sequence[Message],
        tools: Sequence[AsyncTool | AsyncContextTool[DepsT]] | None = None,
        format: type[FormatT],
    ) -> Response[FormatT]: ...

    async def context_call_async(
        self,
        *,
        ctx: Context[DepsT],
        messages: Sequence[Message],
        tools: Sequence[AsyncTool | AsyncContextTool[DepsT]] | None = None,
        format: type[FormatT] | None = None,
    ) -> Response | Response[FormatT]:
        """Generate a response asynchronously using the model."""
        raise NotImplementedError()

    @overload
    def context_stream(
        self,
        *,
        ctx: Context[DepsT],
        messages: Sequence[Message],
        tools: Sequence[Tool | ContextTool[DepsT]] | None = None,
        format: None = None,
    ) -> StreamResponse: ...

    @overload
    def context_stream(
        self,
        *,
        ctx: Context[DepsT],
        messages: Sequence[Message],
        tools: Sequence[Tool | ContextTool[DepsT]] | None = None,
        format: type[FormatT],
    ) -> StreamResponse[FormatT]: ...

    def context_stream(
        self,
        *,
        ctx: Context[DepsT],
        messages: Sequence[Message],
        tools: Sequence[Tool | ContextTool[DepsT]] | None = None,
        format: type[FormatT] | None = None,
    ) -> StreamResponse | StreamResponse[FormatT]:
        """Stream a response using the model."""
        raise NotImplementedError()

    @overload
    async def context_stream_async(
        self,
        *,
        ctx: Context[DepsT],
        messages: list[Message],
        tools: Sequence[AsyncTool | AsyncContextTool[DepsT]] | None = None,
        format: None = None,
    ) -> AsyncStreamResponse: ...

    @overload
    async def context_stream_async(
        self,
        *,
        ctx: Context[DepsT],
        messages: list[Message],
        tools: Sequence[AsyncTool | AsyncContextTool[DepsT]] | None = None,
        format: type[FormatT],
    ) -> AsyncStreamResponse[FormatT]: ...

    async def context_stream_async(
        self,
        *,
        ctx: Context[DepsT],
        messages: list[Message],
        tools: Sequence[AsyncTool | AsyncContextTool[DepsT]] | None = None,
        format: type[FormatT] | None = None,
    ) -> AsyncStreamResponse | AsyncStreamResponse[FormatT]:
        """Stream a response asynchronously using the model."""
        raise NotImplementedError()
