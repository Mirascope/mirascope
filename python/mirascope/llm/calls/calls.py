"""The Call module for generating responses using LLMs."""

from dataclasses import dataclass
from typing import Generic, overload

from ..context import Context, DepsT
from ..formatting import FormattableT
from ..models import Model, use_model
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
from ..types import P


@dataclass
class BaseCall:
    """Base class for all Call types with shared model functionality."""

    default_model: Model
    """The default model that will be used if no model is set in context."""

    @property
    def model(self) -> Model:
        """The model used for generating responses. May be overwritten via `with llm.model(...)`."""
        return use_model(self.default_model)


@dataclass
class Call(BaseCall, Generic[P, FormattableT]):
    """A call that directly generates LLM responses without requiring a model argument.

    Created by decorating a `MessageTemplate` with `llm.call`. The decorated function
    becomes directly callable to generate responses, with the `Model` bundled in.

    A `Call` is essentially: `MessageTemplate` + tools + format + `Model`.
    It can be invoked directly: `call(*args, **kwargs)` (no model argument needed).

    The model can be overridden at runtime using `with llm.model(...)` context manager.
    """

    prompt: Prompt[P, FormattableT]
    """The underlying Prompt instance that generates messages with tools and format."""

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
        return self.prompt.call(self.model, *args, **kwargs)

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
        return self.prompt.stream(self.model, *args, **kwargs)


@dataclass
class AsyncCall(BaseCall, Generic[P, FormattableT]):
    """An async call that directly generates LLM responses without requiring a model argument.

    Created by decorating an async `MessageTemplate` with `llm.call`. The decorated async
    function becomes directly callable to generate responses asynchronously, with the `Model` bundled in.

    An `AsyncCall` is essentially: async `MessageTemplate` + tools + format + `Model`.
    It can be invoked directly: `await call(*args, **kwargs)` (no model argument needed).

    The model can be overridden at runtime using `with llm.model(...)` context manager.
    """

    prompt: AsyncPrompt[P, FormattableT]
    """The underlying AsyncPrompt instance that generates messages with tools and format."""

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
        """Generates a response using the LLM asynchronously."""
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
        return await self.prompt.call(self.model, *args, **kwargs)

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
        return await self.prompt.stream(self.model, *args, **kwargs)


@dataclass
class ContextCall(BaseCall, Generic[P, DepsT, FormattableT]):
    """A context-aware call that directly generates LLM responses without requiring a model argument.

    Created by decorating a `ContextMessageTemplate` with `llm.call`. The decorated function
    (with first parameter `'ctx'` of type `Context[DepsT]`) becomes directly callable to generate
    responses with context dependencies, with the `Model` bundled in.

    A `ContextCall` is essentially: `ContextMessageTemplate` + tools + format + `Model`.
    It can be invoked directly: `call(ctx, *args, **kwargs)` (no model argument needed).

    The model can be overridden at runtime using `with llm.model(...)` context manager.
    """

    prompt: ContextPrompt[P, DepsT, FormattableT]
    """The underlying ContextPrompt instance that generates messages with tools and format."""

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
        return self.prompt.call(self.model, ctx, *args, **kwargs)

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
        return self.prompt.stream(self.model, ctx, *args, **kwargs)


@dataclass
class AsyncContextCall(BaseCall, Generic[P, DepsT, FormattableT]):
    """An async context-aware call that directly generates LLM responses without requiring a model argument.

    Created by decorating an async `ContextMessageTemplate` with `llm.call`. The decorated async
    function (with first parameter `'ctx'` of type `Context[DepsT]`) becomes directly callable to generate
    responses asynchronously with context dependencies, with the `Model` bundled in.

    An `AsyncContextCall` is essentially: async `ContextMessageTemplate` + tools + format + `Model`.
    It can be invoked directly: `await call(ctx, *args, **kwargs)` (no model argument needed).

    The model can be overridden at runtime using `with llm.model(...)` context manager.
    """

    prompt: AsyncContextPrompt[P, DepsT, FormattableT]
    """The underlying AsyncContextPrompt instance that generates messages with tools and format."""

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
        return await self.prompt.call(self.model, ctx, *args, **kwargs)

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
        return await self.prompt.stream(self.model, ctx, *args, **kwargs)
