"""The ContextCall module for generating responses using LLMs with context."""

from dataclasses import dataclass
from typing import Generic, overload

from ..context import Context, DepsT
from ..formatting import FormatT
from ..prompts import AsyncContextPrompt, ContextPrompt, context_prompt
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
    BaseCall[P, ContextPrompt, ContextToolkit[DepsT], FormatT],
    Generic[P, DepsT, FormatT],
):
    """A class for generating responses using LLMs."""

    @overload
    def __call__(
        self: "ContextCall[P, DepsT, None]",
        ctx: Context[DepsT],
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> ContextResponse[DepsT, None]: ...

    @overload
    def __call__(
        self: "ContextCall[P, DepsT, FormatT]",
        ctx: Context[DepsT],
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> ContextResponse[DepsT, FormatT]: ...

    def __call__(
        self, ctx: Context[DepsT], *args: P.args, **kwargs: P.kwargs
    ) -> ContextResponse[DepsT, None] | ContextResponse[DepsT, FormatT]:
        """Generates a response using the LLM."""
        return self.call(ctx, *args, **kwargs)

    @overload
    def call(
        self: "ContextCall[P, DepsT, None]",
        ctx: Context[DepsT],
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> ContextResponse[DepsT, None]: ...

    @overload
    def call(
        self: "ContextCall[P, DepsT, FormatT]",
        ctx: Context[DepsT],
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> ContextResponse[DepsT, FormatT]: ...

    def call(
        self, ctx: Context[DepsT], *args: P.args, **kwargs: P.kwargs
    ) -> ContextResponse[DepsT, None] | ContextResponse[DepsT, FormatT]:
        """Generates a response using the LLM."""
        messages = context_prompt(self.fn)(ctx, *args, **kwargs)
        return self.model.context_call(
            ctx=ctx, messages=messages, tools=self.toolkit.tools, format=self.format
        )

    @overload
    def stream(
        self: "ContextCall[P, DepsT, None]",
        ctx: Context[DepsT],
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> ContextStreamResponse[DepsT, None]: ...

    @overload
    def stream(
        self: "ContextCall[P, DepsT, FormatT]",
        ctx: Context[DepsT],
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> ContextStreamResponse[DepsT, FormatT]: ...

    def stream(
        self, ctx: Context[DepsT], *args: P.args, **kwargs: P.kwargs
    ) -> ContextStreamResponse[DepsT, None] | ContextStreamResponse[DepsT, FormatT]:
        """Generates a streaming response using the LLM."""
        messages = context_prompt(self.fn)(ctx, *args, **kwargs)
        return self.model.context_stream(
            ctx=ctx, messages=messages, tools=self.toolkit.tools, format=self.format
        )


@dataclass
class AsyncContextCall(
    BaseCall[P, AsyncContextPrompt, AsyncContextToolkit[DepsT], FormatT],
    Generic[P, DepsT, FormatT],
):
    """A class for generating responses using LLMs asynchronously."""

    @overload
    async def __call__(
        self: "AsyncContextCall[P, DepsT, None]",
        ctx: Context[DepsT],
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> AsyncContextResponse[DepsT, None]: ...

    @overload
    async def __call__(
        self: "AsyncContextCall[P, DepsT, FormatT]",
        ctx: Context[DepsT],
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> AsyncContextResponse[DepsT, FormatT]: ...

    async def __call__(
        self, ctx: Context[DepsT], *args: P.args, **kwargs: P.kwargs
    ) -> AsyncContextResponse[DepsT, None] | AsyncContextResponse[DepsT, FormatT]:
        """Generates a response using the LLM asynchronously."""
        return await self.call(ctx, *args, **kwargs)

    @overload
    async def call(
        self: "AsyncContextCall[P, DepsT, None]",
        ctx: Context[DepsT],
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> AsyncContextResponse[DepsT, None]: ...

    @overload
    async def call(
        self: "AsyncContextCall[P, DepsT, FormatT]",
        ctx: Context[DepsT],
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> AsyncContextResponse[DepsT, FormatT]: ...

    async def call(
        self, ctx: Context[DepsT], *args: P.args, **kwargs: P.kwargs
    ) -> AsyncContextResponse[DepsT, None] | AsyncContextResponse[DepsT, FormatT]:
        """Generates a response using the LLM asynchronously."""
        messages = await context_prompt(self.fn)(ctx, *args, **kwargs)
        return await self.model.context_call_async(
            ctx=ctx, messages=messages, tools=self.toolkit.tools, format=self.format
        )

    @overload
    async def stream(
        self: "AsyncContextCall[P, DepsT, None]",
        ctx: Context[DepsT],
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> AsyncContextStreamResponse[DepsT, None]: ...

    @overload
    async def stream(
        self: "AsyncContextCall[P, DepsT, FormatT]",
        ctx: Context[DepsT],
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> AsyncContextStreamResponse[DepsT, FormatT]: ...

    async def stream(
        self, ctx: Context[DepsT], *args: P.args, **kwargs: P.kwargs
    ) -> (
        AsyncContextStreamResponse[DepsT, None]
        | AsyncContextStreamResponse[DepsT, FormatT]
    ):
        """Generates a streaming response using the LLM asynchronously."""
        messages = await context_prompt(self.fn)(ctx, *args, **kwargs)
        return await self.model.context_stream_async(
            ctx=ctx, messages=messages, tools=self.toolkit.tools, format=self.format
        )
