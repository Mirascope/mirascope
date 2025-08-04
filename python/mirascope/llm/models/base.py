"""The base model interfaces for LLM models."""

from __future__ import annotations

from collections.abc import Sequence
from typing import TYPE_CHECKING, Generic

from ..clients import ClientT, ParamsT
from ..context import Context
from ..messages import Message
from ..responses import (
    Response,
    StreamResponse,
)
from ..streams import AsyncStream, Stream
from ..tools import AsyncContextTool, AsyncTool, ContextTool, Tool

if TYPE_CHECKING:
    from ..clients import REGISTERED_LLMS

from ..context import DepsT
from ..formatting import FormatT
from ..types import Jsonable


class LLM(Generic[ParamsT, ClientT]):
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

    def call(
        self,
        *,
        ctx: Context[DepsT] | None = None,
        messages: Sequence[Message],
        tools: Sequence[Tool]
        | Sequence[Tool | ContextTool[..., Jsonable, DepsT]]
        | None = None,
        format: type[FormatT] | None = None,
        params: ParamsT | None = None,
    ) -> Response[FormatT]:
        """Generate a response using the model."""
        ...

    async def call_async(
        self,
        *,
        ctx: Context[DepsT] | None = None,
        messages: Sequence[Message],
        tools: Sequence[AsyncTool]
        | Sequence[AsyncTool | AsyncContextTool[..., Jsonable, DepsT]]
        | None = None,
        format: type[FormatT] | None = None,
        params: ParamsT | None = None,
    ) -> Response[FormatT]:
        """Generate a response asynchronously using the model."""
        ...

    def stream(
        self,
        *,
        ctx: Context[DepsT] | None = None,
        messages: Sequence[Message],
        tools: Sequence[Tool]
        | Sequence[Tool | ContextTool[..., Jsonable, DepsT]]
        | None = None,
        format: type[FormatT] | None = None,
        params: ParamsT | None = None,
    ) -> StreamResponse[Stream, FormatT]:
        """Stream a response using the model."""
        ...

    async def stream_async(
        self,
        *,
        ctx: Context[DepsT] | None = None,
        messages: list[Message],
        tools: Sequence[AsyncTool]
        | Sequence[AsyncTool | AsyncContextTool[..., Jsonable, DepsT]]
        | None = None,
        format: type[FormatT] | None = None,
        params: ParamsT | None = None,
    ) -> StreamResponse[AsyncStream, FormatT]:
        """Stream a response asynchronously using the model."""
        ...
