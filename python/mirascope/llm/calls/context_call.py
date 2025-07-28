"""The ContextCall module for generating responses using LLMs with context."""

from dataclasses import dataclass
from typing import Generic

from ..context import Context, DepsT
from ..formatting import FormatT
from ..messages import UserMessagePromotable
from ..prompts import Prompt
from ..responses import Response
from ..streams import AsyncStream, BaseStream, Stream
from ..tools import ContextToolT
from ..types import P
from .base_call import BaseContextCall


@dataclass
class ContextCall(
    BaseContextCall[P, Prompt, ContextToolT, FormatT, DepsT],
    Generic[P, ContextToolT, DepsT, FormatT],
):
    """A class for generating responses using LLMs."""

    def __call__(
        self, ctx: Context[DepsT], *args: P.args, **kwargs: P.kwargs
    ) -> Response[FormatT]:
        """Generates a response using the LLM."""
        raise NotImplementedError()

    def call(
        self, ctx: Context[DepsT], *args: P.args, **kwargs: P.kwargs
    ) -> Response[FormatT]:
        """Generates a response using the LLM."""
        raise NotImplementedError()

    def stream(
        self, ctx: Context[DepsT], *args: P.args, **kwargs: P.kwargs
    ) -> Stream[FormatT]:
        """Generates a streaming response using the LLM."""
        raise NotImplementedError()

    def resume(
        self,
        ctx: Context[DepsT],
        output: Response[FormatT] | BaseStream[FormatT],
        content: UserMessagePromotable,
    ) -> Response[FormatT]:
        """Generate a new response by continuing from a previous output, plus new user content."""
        raise NotImplementedError()

    def resume_stream(
        self,
        ctx: Context[DepsT],
        output: Response[FormatT] | BaseStream[FormatT],
        content: UserMessagePromotable,
    ) -> Stream[FormatT]:
        """Generate a new stream by continuing from a previous output, plus new user content."""
        raise NotImplementedError()


@dataclass
class AsyncContextCall(
    BaseContextCall[P, Prompt, ContextToolT, FormatT, DepsT],
    Generic[P, ContextToolT, DepsT, FormatT],
):
    """A class for generating responses using LLMs asynchronously."""

    async def __call__(
        self, ctx: Context[DepsT], *args: P.args, **kwargs: P.kwargs
    ) -> Response[FormatT]:
        """Generates a response using the LLM asynchronously."""
        raise NotImplementedError()

    async def call(
        self, ctx: Context[DepsT], *args: P.args, **kwargs: P.kwargs
    ) -> Response[FormatT]:
        """Generates a response using the LLM asynchronously."""
        raise NotImplementedError()

    async def stream(
        self, ctx: Context[DepsT], *args: P.args, **kwargs: P.kwargs
    ) -> AsyncStream[FormatT]:
        """Generates a streaming response using the LLM asynchronously."""
        raise NotImplementedError()

    async def resume(
        self,
        ctx: Context[DepsT],
        output: Response[FormatT] | BaseStream[FormatT],
        content: UserMessagePromotable,
    ) -> Response[FormatT]:
        """Generate a new response by continuing from a previous output, plus new user content."""
        raise NotImplementedError()

    async def resume_stream(
        self,
        ctx: Context[DepsT],
        output: Response[FormatT] | BaseStream[FormatT],
        content: UserMessagePromotable,
    ) -> AsyncStream[FormatT]:
        """Generate a new stream by continuing from a previous output, plus new user content."""
        raise NotImplementedError()
