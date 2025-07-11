"""Base abstract interface for provider clients."""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Sequence
from typing import Any, Generic, TypedDict

from typing_extensions import TypeVar

from ..context import Context
from ..response_formatting import FormatT
from ..responses import Response
from ..streams import (
    AsyncStream,
    Stream,
)
from ..tools import ContextToolDef, ToolDef
from ..types import DepsT
from .register import REGISTERED_LLMS

ProviderMessageT = TypeVar("ProviderMessageT")
"""Type variable for an LLM that is usable by a specific LLM provider.

May often be the union of generic `llm.Message` and a provider-specific message representation."""


LLMT = TypeVar("LLMT", bound=REGISTERED_LLMS)
"""Type variable for a registered LLM model. Will be a string of form provider:model_name."""


class BaseParams(TypedDict, total=False):
    """Common parameters shared across LLM providers.

    Note: Each provider may handle these parameters differently or not support them at all.
    Please check provider-specific documentation for parameter support and behavior.
    """

    temperature: float | None
    """Controls randomness in the output (0.0 to 1.0)."""

    max_tokens: int | None
    """Maximum number of tokens to generate."""

    top_p: float | None
    """Nucleus sampling parameter (0.0 to 1.0)."""

    frequency_penalty: float | None
    """Penalizes frequent tokens (-2.0 to 2.0)."""

    presence_penalty: float | None
    """Penalizes tokens based on presence (-2.0 to 2.0)."""

    seed: int | None
    """Random seed for reproducibility."""

    stop: str | list[str] | None
    """Stop sequence(s) to end generation."""


ParamsT = TypeVar("ParamsT", bound="BaseParams")
"""Type variable for LLM parameters. May be provider specific."""


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
        tools: Sequence[ToolDef] | None = None,
        params: ParamsT | None = None,
    ) -> Response[None, None]:
        """Generate a standard response."""
        ...

    @abstractmethod
    def context_call(
        self,
        *,
        ctx: Context[DepsT],
        model: LLMT,
        messages: Sequence[ProviderMessageT],
        tools: Sequence[ToolDef | ContextToolDef[..., Any, DepsT]],
        params: ParamsT | None = None,
    ) -> Response[DepsT, None]:
        """Generate a context response with context tools."""
        ...

    @abstractmethod
    def structured_call(
        self,
        *,
        model: LLMT,
        messages: Sequence[ProviderMessageT],
        tools: Sequence[ToolDef] | None = None,
        response_format: type[FormatT],
        params: ParamsT | None = None,
    ) -> Response[None, FormatT]:
        """Generate a structured response."""
        ...

    @abstractmethod
    def structured_context_call(
        self,
        *,
        ctx: Context[DepsT],
        model: LLMT,
        messages: Sequence[ProviderMessageT],
        tools: Sequence[ToolDef | ContextToolDef[..., Any, DepsT]],
        response_format: type[FormatT],
        params: ParamsT | None = None,
    ) -> Response[DepsT, FormatT]:
        """Generate a structured context response."""
        ...

    @abstractmethod
    async def call_async(
        self,
        *,
        model: LLMT,
        messages: Sequence[ProviderMessageT],
        tools: Sequence[ToolDef] | None = None,
        params: ParamsT | None = None,
    ) -> Response[None, None]:
        """Generate a standard response asynchronously."""
        ...

    @abstractmethod
    async def context_call_async(
        self,
        *,
        ctx: Context[DepsT],
        model: LLMT,
        messages: Sequence[ProviderMessageT],
        tools: Sequence[ToolDef | ContextToolDef[..., Any, DepsT]],
        params: ParamsT | None = None,
    ) -> Response[DepsT, None]:
        """Generate a context response asynchronously."""
        ...

    @abstractmethod
    async def structured_call_async(
        self,
        *,
        model: LLMT,
        messages: Sequence[ProviderMessageT],
        tools: Sequence[ToolDef] | None = None,
        response_format: type[FormatT],
        params: ParamsT | None = None,
    ) -> Response[None, FormatT]:
        """Generate a structured response asynchronously."""
        ...

    @abstractmethod
    async def structured_context_call_async(
        self,
        *,
        ctx: Context[DepsT],
        model: LLMT,
        messages: Sequence[ProviderMessageT],
        tools: Sequence[ToolDef | ContextToolDef[..., Any, DepsT]],
        response_format: type[FormatT],
        params: ParamsT | None = None,
    ) -> Response[DepsT, FormatT]:
        """Generate a structured context response asynchronously."""
        ...

    @abstractmethod
    def stream(
        self,
        *,
        model: LLMT,
        messages: Sequence[ProviderMessageT],
        tools: Sequence[ToolDef] | None = None,
        params: ParamsT | None = None,
    ) -> Stream[None, None]:
        """Stream a standard response."""
        ...

    @abstractmethod
    def context_stream(
        self,
        *,
        ctx: Context[DepsT],
        model: LLMT,
        messages: Sequence[ProviderMessageT],
        tools: Sequence[ToolDef | ContextToolDef[..., Any, DepsT]],
        params: ParamsT | None = None,
    ) -> Stream[DepsT, None]:
        """Stream a context response."""
        ...

    @abstractmethod
    def structured_stream(
        self,
        *,
        model: LLMT,
        messages: Sequence[ProviderMessageT],
        tools: Sequence[ToolDef] | None = None,
        response_format: type[FormatT],
        params: ParamsT | None = None,
    ) -> Stream[None, FormatT]:
        """Stream a structured response."""
        ...

    @abstractmethod
    def structured_context_stream(
        self,
        *,
        ctx: Context[DepsT],
        model: LLMT,
        messages: Sequence[ProviderMessageT],
        tools: Sequence[ToolDef | ContextToolDef[..., Any, DepsT]],
        response_format: type[FormatT],
        params: ParamsT | None = None,
    ) -> Stream[DepsT, FormatT]:
        """Stream a structured context response."""
        ...

    @abstractmethod
    def stream_async(
        self,
        *,
        model: LLMT,
        messages: Sequence[ProviderMessageT],
        tools: Sequence[ToolDef] | None = None,
        params: ParamsT | None = None,
    ) -> AsyncStream[None, None]:
        """Stream a standard response asynchronously."""
        ...

    @abstractmethod
    def context_stream_async(
        self,
        *,
        ctx: Context[DepsT],
        model: LLMT,
        messages: Sequence[ProviderMessageT],
        tools: Sequence[ToolDef | ContextToolDef[..., Any, DepsT]],
        params: ParamsT | None = None,
    ) -> AsyncStream[DepsT, None]:
        """Stream a context response asynchronously."""
        ...

    @abstractmethod
    def structured_stream_async(
        self,
        *,
        model: LLMT,
        messages: Sequence[ProviderMessageT],
        tools: Sequence[ToolDef] | None = None,
        response_format: type[FormatT],
        params: ParamsT | None = None,
    ) -> AsyncStream[None, FormatT]:
        """Stream a structured response asynchronously."""
        ...

    @abstractmethod
    def structured_context_stream_async(
        self,
        *,
        ctx: Context[DepsT],
        model: LLMT,
        messages: Sequence[ProviderMessageT],
        tools: Sequence[ToolDef | ContextToolDef[..., Any, DepsT]],
        response_format: type[FormatT],
        params: ParamsT | None = None,
    ) -> AsyncStream[DepsT, FormatT]:
        """Stream a structured context response asynchronously."""
        ...


ClientT = TypeVar("ClientT", bound=BaseClient)
"""Type variable for an LLM client."""
