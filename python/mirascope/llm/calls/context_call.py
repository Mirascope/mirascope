"""The ContextCall module for generating responses using LLMs with context."""

from dataclasses import dataclass
from typing import Generic

from ..context import Context, DepsT
from ..formatting import FormatT
from ..prompts import Prompt
from ..responses import (
    AsyncContextResponse,
    AsyncContextStreamResponse,
    ContextResponse,
    ContextStreamResponse,
)
from ..tools import AsyncContextToolkit, ContextToolkit
from ..types import P
from .base_call import BaseCall


@dataclass
class ContextCall(
    BaseCall[P, Prompt, ContextToolkit[DepsT], FormatT],
    Generic[P, DepsT, FormatT],
):
    """A class for generating responses using LLMs."""

    def __call__(
        self, ctx: Context[DepsT], *args: P.args, **kwargs: P.kwargs
    ) -> ContextResponse[DepsT, FormatT]:
        """Generates a response using the LLM."""
        raise NotImplementedError()

    def call(
        self, ctx: Context[DepsT], *args: P.args, **kwargs: P.kwargs
    ) -> ContextResponse[DepsT, FormatT]:
        """Generates a response using the LLM."""
        raise NotImplementedError()

    def stream(
        self, ctx: Context[DepsT], *args: P.args, **kwargs: P.kwargs
    ) -> ContextStreamResponse[DepsT, FormatT]:
        """Generates a streaming response using the LLM."""
        raise NotImplementedError()


@dataclass
class AsyncContextCall(
    BaseCall[P, Prompt, AsyncContextToolkit[DepsT], FormatT],
    Generic[P, DepsT, FormatT],
):
    """A class for generating responses using LLMs asynchronously."""

    async def __call__(
        self, ctx: Context[DepsT], *args: P.args, **kwargs: P.kwargs
    ) -> AsyncContextResponse[DepsT, FormatT]:
        """Generates a response using the LLM asynchronously."""
        raise NotImplementedError()

    async def call(
        self, ctx: Context[DepsT], *args: P.args, **kwargs: P.kwargs
    ) -> AsyncContextResponse[DepsT, FormatT]:
        """Generates a response using the LLM asynchronously."""
        raise NotImplementedError()

    async def stream(
        self, ctx: Context[DepsT], *args: P.args, **kwargs: P.kwargs
    ) -> AsyncContextStreamResponse[DepsT, FormatT]:
        """Generates a streaming response using the LLM asynchronously."""
        raise NotImplementedError()
