"""The Call module for generating responses using LLMs."""

from dataclasses import dataclass
from typing import Generic, overload

from ..context import Context, DepsT
from ..formatting import FormattableT
from ..prompts import (
    AsyncContextPrompt,
    AsyncPrompt,
    ContextPrompt,
    Prompt,
)
from ..responses import (
    AsyncContextResponse,
    AsyncContextStreamResponse,
    AsyncResponse,
    AsyncStreamResponse,
    ContextResponse,
    ContextStreamResponse,
    Response,
    StreamResponse,
)
from ..tools import (
    AsyncContextToolkit,
    AsyncToolkit,
    ContextToolkit,
    Toolkit,
)
from ..types import P
from .base_call import BaseCall


@dataclass
class Call(BaseCall[P, Prompt[P], Toolkit, FormattableT], Generic[P, FormattableT]):
    """A class for generating responses using LLMs."""

    @overload
    def __call__(
        self: "Call[P, None]", *args: P.args, **kwargs: P.kwargs
    ) -> Response: ...

    @overload
    def __call__(
        self: "Call[P, FormattableT]", *args: P.args, **kwargs: P.kwargs
    ) -> Response[FormattableT]: ...

    def __call__(
        self, *args: P.args, **kwargs: P.kwargs
    ) -> Response | Response[FormattableT]:
        """Generates a response using the LLM."""
        return self.call(*args, **kwargs)

    @overload
    def call(self: "Call[P, None]", *args: P.args, **kwargs: P.kwargs) -> Response: ...

    @overload
    def call(
        self: "Call[P, FormattableT]", *args: P.args, **kwargs: P.kwargs
    ) -> Response[FormattableT]: ...

    def call(
        self, *args: P.args, **kwargs: P.kwargs
    ) -> Response | Response[FormattableT]:
        """Generates a response using the LLM."""
        messages = self.fn(*args, **kwargs)
        return self.model.call(
            messages=messages, tools=self.toolkit, format=self.format
        )

    @overload
    def stream(
        self: "Call[P, None]", *args: P.args, **kwargs: P.kwargs
    ) -> StreamResponse: ...

    @overload
    def stream(
        self: "Call[P, FormattableT]", *args: P.args, **kwargs: P.kwargs
    ) -> StreamResponse[FormattableT]: ...

    def stream(
        self, *args: P.args, **kwargs: P.kwargs
    ) -> StreamResponse | StreamResponse[FormattableT]:
        """Generates a streaming response using the LLM."""
        messages = self.fn(*args, **kwargs)
        return self.model.stream(
            messages=messages, tools=self.toolkit, format=self.format
        )


@dataclass
class AsyncCall(
    BaseCall[P, AsyncPrompt[P], AsyncToolkit, FormattableT],
    Generic[P, FormattableT],
):
    """A class for generating responses using LLMs asynchronously."""

    @overload
    async def __call__(
        self: "AsyncCall[P, None]", *args: P.args, **kwargs: P.kwargs
    ) -> AsyncResponse: ...

    @overload
    async def __call__(
        self: "AsyncCall[P, FormattableT]", *args: P.args, **kwargs: P.kwargs
    ) -> AsyncResponse[FormattableT]: ...

    async def __call__(
        self, *args: P.args, **kwargs: P.kwargs
    ) -> AsyncResponse | AsyncResponse[FormattableT]:
        """Generates a Asyncresponse using the LLM asynchronously."""
        return await self.call(*args, **kwargs)

    @overload
    async def call(
        self: "AsyncCall[P, None]", *args: P.args, **kwargs: P.kwargs
    ) -> AsyncResponse: ...

    @overload
    async def call(
        self: "AsyncCall[P, FormattableT]", *args: P.args, **kwargs: P.kwargs
    ) -> AsyncResponse[FormattableT]: ...

    async def call(
        self, *args: P.args, **kwargs: P.kwargs
    ) -> AsyncResponse | AsyncResponse[FormattableT]:
        """Generates a response using the LLM asynchronously."""
        messages = await self.fn(*args, **kwargs)
        return await self.model.call_async(
            messages=messages, tools=self.toolkit, format=self.format
        )

    @overload
    async def stream(
        self: "AsyncCall[P, None]", *args: P.args, **kwargs: P.kwargs
    ) -> AsyncStreamResponse: ...

    @overload
    async def stream(
        self: "AsyncCall[P, FormattableT]", *args: P.args, **kwargs: P.kwargs
    ) -> AsyncStreamResponse[FormattableT]: ...

    async def stream(
        self, *args: P.args, **kwargs: P.kwargs
    ) -> AsyncStreamResponse[FormattableT] | AsyncStreamResponse:
        """Generates a streaming response using the LLM asynchronously."""
        messages = await self.fn(*args, **kwargs)
        return await self.model.stream_async(
            messages=messages, tools=self.toolkit, format=self.format
        )


@dataclass
class ContextCall(
    BaseCall[P, ContextPrompt[P, DepsT], ContextToolkit[DepsT], FormattableT],
    Generic[P, DepsT, FormattableT],
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
        self: "ContextCall[P, DepsT, FormattableT]",
        ctx: Context[DepsT],
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> ContextResponse[DepsT, FormattableT]: ...

    def __call__(
        self, ctx: Context[DepsT], *args: P.args, **kwargs: P.kwargs
    ) -> ContextResponse[DepsT, None] | ContextResponse[DepsT, FormattableT]:
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
        self: "ContextCall[P, DepsT, FormattableT]",
        ctx: Context[DepsT],
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> ContextResponse[DepsT, FormattableT]: ...

    def call(
        self, ctx: Context[DepsT], *args: P.args, **kwargs: P.kwargs
    ) -> ContextResponse[DepsT, None] | ContextResponse[DepsT, FormattableT]:
        """Generates a response using the LLM."""
        messages = self.fn(ctx, *args, **kwargs)
        return self.model.context_call(
            ctx=ctx, messages=messages, tools=self.toolkit, format=self.format
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
        self: "ContextCall[P, DepsT, FormattableT]",
        ctx: Context[DepsT],
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> ContextStreamResponse[DepsT, FormattableT]: ...

    def stream(
        self, ctx: Context[DepsT], *args: P.args, **kwargs: P.kwargs
    ) -> (
        ContextStreamResponse[DepsT, None] | ContextStreamResponse[DepsT, FormattableT]
    ):
        """Generates a streaming response using the LLM."""
        messages = self.fn(ctx, *args, **kwargs)
        return self.model.context_stream(
            ctx=ctx, messages=messages, tools=self.toolkit, format=self.format
        )


@dataclass
class AsyncContextCall(
    BaseCall[P, AsyncContextPrompt[P, DepsT], AsyncContextToolkit[DepsT], FormattableT],
    Generic[P, DepsT, FormattableT],
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
        self: "AsyncContextCall[P, DepsT, FormattableT]",
        ctx: Context[DepsT],
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> AsyncContextResponse[DepsT, FormattableT]: ...

    async def __call__(
        self, ctx: Context[DepsT], *args: P.args, **kwargs: P.kwargs
    ) -> AsyncContextResponse[DepsT, None] | AsyncContextResponse[DepsT, FormattableT]:
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
        self: "AsyncContextCall[P, DepsT, FormattableT]",
        ctx: Context[DepsT],
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> AsyncContextResponse[DepsT, FormattableT]: ...

    async def call(
        self, ctx: Context[DepsT], *args: P.args, **kwargs: P.kwargs
    ) -> AsyncContextResponse[DepsT, None] | AsyncContextResponse[DepsT, FormattableT]:
        """Generates a response using the LLM asynchronously."""
        messages = await self.fn(ctx, *args, **kwargs)
        return await self.model.context_call_async(
            ctx=ctx, messages=messages, tools=self.toolkit, format=self.format
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
        self: "AsyncContextCall[P, DepsT, FormattableT]",
        ctx: Context[DepsT],
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> AsyncContextStreamResponse[DepsT, FormattableT]: ...

    async def stream(
        self, ctx: Context[DepsT], *args: P.args, **kwargs: P.kwargs
    ) -> (
        AsyncContextStreamResponse[DepsT, None]
        | AsyncContextStreamResponse[DepsT, FormattableT]
    ):
        """Generates a streaming response using the LLM asynchronously."""
        messages = await self.fn(ctx, *args, **kwargs)
        return await self.model.context_stream_async(
            ctx=ctx, messages=messages, tools=self.toolkit, format=self.format
        )
