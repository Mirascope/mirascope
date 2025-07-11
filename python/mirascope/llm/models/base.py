"""The base model interfaces for LLM models."""

from __future__ import annotations

from collections.abc import Sequence
from typing import TYPE_CHECKING, Any, Generic, overload

from ..context import Context
from ..responses import Response
from ..streams import (
    AsyncStream,
    AsyncStructuredStream,
    Stream,
    StructuredStream,
)
from ..tools import ContextToolDef, ToolDef
from ..types import ClientT, ParamsT, ProviderMessageT

if TYPE_CHECKING:
    from ..clients import REGISTERED_LLMS


from ..types import DepsT, FormatT


class LLM(Generic[ProviderMessageT, ParamsT, ClientT]):
    """The unified LLM interface that delegates to provider-specific clients.

    This class provides a consistent interface for interacting with language models
    from various providers. It handles the common operations like generating responses,
    streaming, and async variants by delegating to the appropriate client methods.
    """

    model: REGISTERED_LLMS
    """The model being used (e.g. `openai:gpt-4o-mini`)"""

    params: ParamsT
    """The default parameters for the model (temperature, max_tokens, etc.)."""

    client: ClientT
    """The client object used to interact with the model API."""

    def __init__(
        self,
        *,
        provider: str,
        name: str,
        params: ParamsT | None = None,
        client: ClientT | None = None,
    ) -> None:
        """Initializes an `LLM` instance."""
        ...

    @overload
    def call(
        self,
        *,
        ctx: None = None,
        messages: Sequence[ProviderMessageT],
        tools: Sequence[ToolDef] | None = None,
        response_format: None = None,
        params: ParamsT | None = None,
    ) -> Response[None, None]:
        """Overload for standard call."""
        ...

    @overload
    def call(
        self,
        *,
        ctx: Context[DepsT],
        messages: Sequence[ProviderMessageT],
        tools: Sequence[ToolDef | ContextToolDef[..., Any, DepsT]],
        response_format: None = None,
        params: ParamsT | None = None,
    ) -> Response[DepsT, None]:
        """Overload for standard context call."""
        ...

    @overload
    def call(
        self,
        *,
        ctx: None = None,
        messages: Sequence[ProviderMessageT],
        tools: Sequence[ToolDef] | None = None,
        response_format: type[FormatT],
        params: ParamsT | None = None,
    ) -> Response[None, FormatT]:
        """Overload for calls when a response format is specified."""
        ...

    @overload
    def call(
        self,
        *,
        ctx: Context[DepsT],
        messages: Sequence[ProviderMessageT],
        tools: Sequence[ToolDef | ContextToolDef[..., Any, DepsT]],
        response_format: type[FormatT],
        params: ParamsT | None = None,
    ) -> Response[DepsT, FormatT]:
        """Overload for calls when a response format is specified."""
        ...

    def call(
        self,
        *,
        ctx: Context[DepsT] | None = None,
        messages: Sequence[ProviderMessageT],
        tools: Sequence[ToolDef]
        | Sequence[ToolDef | ContextToolDef[..., Any, DepsT]]
        | None = None,
        response_format: type[FormatT] | None = None,
        params: ParamsT | None = None,
    ) -> Response[DepsT, FormatT]:
        """Generate a response using the model."""
        ...

    @overload
    async def call_async(
        self,
        *,
        ctx: None = None,
        messages: Sequence[ProviderMessageT],
        tools: Sequence[ToolDef] | None = None,
        response_format: None = None,
        params: ParamsT | None = None,
    ) -> Response[None, None]:
        """Overload for standard async call."""
        ...

    @overload
    async def call_async(
        self,
        *,
        ctx: Context[DepsT],
        messages: Sequence[ProviderMessageT],
        tools: Sequence[ToolDef | ContextToolDef[..., Any, DepsT]],
        response_format: None = None,
        params: ParamsT | None = None,
    ) -> Response[DepsT, None]:
        """Overload for standard async context call."""
        ...

    @overload
    async def call_async(
        self,
        *,
        ctx: None = None,
        messages: Sequence[ProviderMessageT],
        tools: Sequence[ToolDef] | None = None,
        response_format: type[FormatT],
        params: ParamsT | None = None,
    ) -> Response[None, FormatT]:
        """Overload for async calls when a response format is specified."""
        ...

    @overload
    async def call_async(
        self,
        *,
        ctx: Context[DepsT],
        messages: Sequence[ProviderMessageT],
        tools: Sequence[ToolDef | ContextToolDef[..., Any, DepsT]],
        response_format: type[FormatT],
        params: ParamsT | None = None,
    ) -> Response[DepsT, FormatT]:
        """Overload for async context calls when a response format is specified."""
        ...

    async def call_async(
        self,
        *,
        ctx: Context[DepsT] | None = None,
        messages: Sequence[ProviderMessageT],
        tools: Sequence[ToolDef]
        | Sequence[ToolDef | ContextToolDef[..., Any, DepsT]]
        | None = None,
        response_format: type[FormatT] | None = None,
        params: ParamsT | None = None,
    ) -> Response[DepsT, FormatT]:
        """Generate a response asynchronously using the model."""
        ...

    @overload
    def stream(
        self,
        *,
        ctx: None = None,
        messages: Sequence[ProviderMessageT],
        tools: Sequence[ToolDef] | None = None,
        response_format: None = None,
        params: ParamsT | None = None,
    ) -> Stream[None]:
        """Overload for standard streaming."""
        ...

    @overload
    def stream(
        self,
        *,
        ctx: Context[DepsT],
        messages: Sequence[ProviderMessageT],
        tools: Sequence[ToolDef | ContextToolDef[..., Any, DepsT]],
        response_format: None = None,
        params: ParamsT | None = None,
    ) -> Stream[DepsT]:
        """Overload for standard context streaming."""
        ...

    @overload
    def stream(
        self,
        *,
        ctx: None = None,
        messages: Sequence[ProviderMessageT],
        tools: Sequence[ToolDef] | None = None,
        response_format: type[FormatT],
        params: ParamsT | None = None,
    ) -> StructuredStream[None, FormatT]:
        """Overload for structured streaming."""
        ...

    @overload
    def stream(
        self,
        *,
        ctx: Context[DepsT],
        messages: Sequence[ProviderMessageT],
        tools: Sequence[ToolDef | ContextToolDef[..., Any, DepsT]],
        response_format: type[FormatT],
        params: ParamsT | None = None,
    ) -> StructuredStream[DepsT, FormatT]:
        """Overload for context structured streaming."""
        ...

    def stream(
        self,
        *,
        ctx: Context[DepsT] | None = None,
        messages: Sequence[ProviderMessageT],
        tools: Sequence[ToolDef]
        | Sequence[ToolDef | ContextToolDef[..., Any, DepsT]]
        | None = None,
        response_format: type[FormatT] | None = None,
        params: ParamsT | None = None,
    ) -> Stream[DepsT] | StructuredStream[DepsT, FormatT]:
        """Stream a response using the model."""
        ...

    @overload
    async def stream_async(
        self,
        *,
        ctx: None = None,
        messages: list[ProviderMessageT],
        tools: Sequence[ToolDef] | None = None,
        response_format: None = None,
        params: ParamsT | None = None,
    ) -> AsyncStream[None]:
        """Overload for standard async streaming."""
        ...

    @overload
    async def stream_async(
        self,
        *,
        ctx: Context[DepsT],
        messages: list[ProviderMessageT],
        tools: Sequence[ToolDef | ContextToolDef[..., Any, DepsT]],
        response_format: None = None,
        params: ParamsT | None = None,
    ) -> AsyncStream[DepsT]:
        """Overload for standard async context streaming."""
        ...

    @overload
    async def stream_async(
        self,
        *,
        ctx: None = None,
        messages: list[ProviderMessageT],
        tools: Sequence[ToolDef] | None = None,
        response_format: type[FormatT],
        params: ParamsT | None = None,
    ) -> AsyncStructuredStream[None, FormatT]:
        """Overload for async structured streaming."""
        ...

    @overload
    async def stream_async(
        self,
        *,
        ctx: Context[DepsT],
        messages: list[ProviderMessageT],
        tools: Sequence[ToolDef | ContextToolDef[..., Any, DepsT]],
        response_format: type[FormatT],
        params: ParamsT | None = None,
    ) -> AsyncStructuredStream[DepsT, FormatT]:
        """Overload for async context structured streaming."""
        ...

    async def stream_async(
        self,
        *,
        ctx: Context[DepsT] | None = None,
        messages: list[ProviderMessageT],
        tools: Sequence[ToolDef]
        | Sequence[ToolDef | ContextToolDef[..., Any, DepsT]]
        | None = None,
        response_format: type[FormatT] | None = None,
        params: ParamsT | None = None,
    ) -> AsyncStream[DepsT] | AsyncStructuredStream[DepsT, FormatT]:
        """Stream a response asynchronously using the model."""
        ...
