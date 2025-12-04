"""Concrete Prompt classes for generating messages with tools and formatting."""

from dataclasses import dataclass
from typing import Generic, overload

from ..context import Context, DepsT
from ..formatting import Format, FormattableT
from ..models import Model
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
from . import _utils
from .protocols import (
    AsyncContextMessageTemplate,
    AsyncMessageTemplate,
    ContextMessageTemplate,
    MessageTemplate,
)


@dataclass
class Prompt(Generic[P, FormattableT]):
    """A prompt that can be called with a model to generate a response.

    Created by decorating a `MessageTemplate` with `llm.prompt`. The decorated
    function becomes callable with a `Model` to generate LLM responses.

    A `Prompt` is essentially: `MessageTemplate` + tools + format.
    It can be invoked with a model: `prompt(model, *args, **kwargs)`.
    """

    fn: MessageTemplate[P]
    """The underlying prompt function that generates message content."""

    toolkit: Toolkit
    """The toolkit containing this prompt's tools."""

    format: type[FormattableT] | Format[FormattableT] | None
    """The response format for the generated response."""

    @overload
    def __call__(
        self: "Prompt[P, None]", model: Model, *args: P.args, **kwargs: P.kwargs
    ) -> Response: ...

    @overload
    def __call__(
        self: "Prompt[P, FormattableT]", model: Model, *args: P.args, **kwargs: P.kwargs
    ) -> Response[FormattableT]: ...

    def __call__(
        self, model: Model, *args: P.args, **kwargs: P.kwargs
    ) -> Response | Response[FormattableT]:
        """Generates a response using the provided model."""
        return self.call(model, *args, **kwargs)

    @overload
    def call(
        self: "Prompt[P, None]", model: Model, *args: P.args, **kwargs: P.kwargs
    ) -> Response: ...

    @overload
    def call(
        self: "Prompt[P, FormattableT]", model: Model, *args: P.args, **kwargs: P.kwargs
    ) -> Response[FormattableT]: ...

    def call(
        self, model: Model, *args: P.args, **kwargs: P.kwargs
    ) -> Response | Response[FormattableT]:
        """Generates a response using the provided model."""
        result = self.fn(*args, **kwargs)
        messages = _utils.promote_to_messages(result)
        return model.call(messages=messages, tools=self.toolkit, format=self.format)

    @overload
    def stream(
        self: "Prompt[P, None]", model: Model, *args: P.args, **kwargs: P.kwargs
    ) -> StreamResponse: ...

    @overload
    def stream(
        self: "Prompt[P, FormattableT]", model: Model, *args: P.args, **kwargs: P.kwargs
    ) -> StreamResponse[FormattableT]: ...

    def stream(
        self, model: Model, *args: P.args, **kwargs: P.kwargs
    ) -> StreamResponse | StreamResponse[FormattableT]:
        """Generates a streaming response using the provided model."""
        result = self.fn(*args, **kwargs)
        messages = _utils.promote_to_messages(result)
        return model.stream(messages=messages, tools=self.toolkit, format=self.format)


@dataclass
class AsyncPrompt(Generic[P, FormattableT]):
    """An async prompt that can be called with a model to generate a response.

    Created by decorating an async `MessageTemplate` with `llm.prompt`. The decorated
    async function becomes callable with a `Model` to generate LLM responses asynchronously.

    An `AsyncPrompt` is essentially: async `MessageTemplate` + tools + format.
    It can be invoked with a model: `await prompt(model, *args, **kwargs)`.
    """

    fn: AsyncMessageTemplate[P]
    """The underlying async prompt function that generates message content."""

    toolkit: AsyncToolkit
    """The toolkit containing this prompt's async tools."""

    format: type[FormattableT] | Format[FormattableT] | None
    """The response format for the generated response."""

    @overload
    async def __call__(
        self: "AsyncPrompt[P, None]", model: Model, *args: P.args, **kwargs: P.kwargs
    ) -> AsyncResponse: ...

    @overload
    async def __call__(
        self: "AsyncPrompt[P, FormattableT]",
        model: Model,
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> AsyncResponse[FormattableT]: ...

    async def __call__(
        self, model: Model, *args: P.args, **kwargs: P.kwargs
    ) -> AsyncResponse | AsyncResponse[FormattableT]:
        """Generates a response using the provided model asynchronously."""
        return await self.call(model, *args, **kwargs)

    @overload
    async def call(
        self: "AsyncPrompt[P, None]", model: Model, *args: P.args, **kwargs: P.kwargs
    ) -> AsyncResponse: ...

    @overload
    async def call(
        self: "AsyncPrompt[P, FormattableT]",
        model: Model,
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> AsyncResponse[FormattableT]: ...

    async def call(
        self, model: Model, *args: P.args, **kwargs: P.kwargs
    ) -> AsyncResponse | AsyncResponse[FormattableT]:
        """Generates a response using the provided model asynchronously."""
        result = await self.fn(*args, **kwargs)
        messages = _utils.promote_to_messages(result)
        return await model.call_async(
            messages=messages, tools=self.toolkit, format=self.format
        )

    @overload
    async def stream(
        self: "AsyncPrompt[P, None]", model: Model, *args: P.args, **kwargs: P.kwargs
    ) -> AsyncStreamResponse: ...

    @overload
    async def stream(
        self: "AsyncPrompt[P, FormattableT]",
        model: Model,
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> AsyncStreamResponse[FormattableT]: ...

    async def stream(
        self, model: Model, *args: P.args, **kwargs: P.kwargs
    ) -> AsyncStreamResponse | AsyncStreamResponse[FormattableT]:
        """Generates a streaming response using the provided model asynchronously."""
        result = await self.fn(*args, **kwargs)
        messages = _utils.promote_to_messages(result)
        return await model.stream_async(
            messages=messages, tools=self.toolkit, format=self.format
        )


@dataclass
class ContextPrompt(Generic[P, DepsT, FormattableT]):
    """A context-aware prompt that can be called with a model to generate a response.

    Created by decorating a `ContextMessageTemplate` with `llm.prompt`. The decorated
    function (with first parameter `'ctx'` of type `Context[DepsT]`) becomes callable
    with a `Model` to generate LLM responses with context dependencies.

    A `ContextPrompt` is essentially: `ContextMessageTemplate` + tools + format.
    It can be invoked with a model: `prompt(model, ctx, *args, **kwargs)`.
    """

    fn: ContextMessageTemplate[P, DepsT]
    """The underlying context-aware prompt function that generates message content."""

    toolkit: ContextToolkit[DepsT]
    """The toolkit containing this prompt's context-aware tools."""

    format: type[FormattableT] | Format[FormattableT] | None
    """The response format for the generated response."""

    @overload
    def __call__(
        self: "ContextPrompt[P, DepsT, None]",
        model: Model,
        ctx: Context[DepsT],
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> ContextResponse[DepsT, None]: ...

    @overload
    def __call__(
        self: "ContextPrompt[P, DepsT, FormattableT]",
        model: Model,
        ctx: Context[DepsT],
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> ContextResponse[DepsT, FormattableT]: ...

    def __call__(
        self,
        model: Model,
        ctx: Context[DepsT],
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> ContextResponse[DepsT, None] | ContextResponse[DepsT, FormattableT]:
        """Generates a response using the provided model."""
        return self.call(model, ctx, *args, **kwargs)

    @overload
    def call(
        self: "ContextPrompt[P, DepsT, None]",
        model: Model,
        ctx: Context[DepsT],
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> ContextResponse[DepsT, None]: ...

    @overload
    def call(
        self: "ContextPrompt[P, DepsT, FormattableT]",
        model: Model,
        ctx: Context[DepsT],
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> ContextResponse[DepsT, FormattableT]: ...

    def call(
        self,
        model: Model,
        ctx: Context[DepsT],
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> ContextResponse[DepsT, None] | ContextResponse[DepsT, FormattableT]:
        """Generates a response using the provided model."""
        result = self.fn(ctx, *args, **kwargs)
        messages = _utils.promote_to_messages(result)
        return model.context_call(
            ctx=ctx, messages=messages, tools=self.toolkit, format=self.format
        )

    @overload
    def stream(
        self: "ContextPrompt[P, DepsT, None]",
        model: Model,
        ctx: Context[DepsT],
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> ContextStreamResponse[DepsT, None]: ...

    @overload
    def stream(
        self: "ContextPrompt[P, DepsT, FormattableT]",
        model: Model,
        ctx: Context[DepsT],
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> ContextStreamResponse[DepsT, FormattableT]: ...

    def stream(
        self,
        model: Model,
        ctx: Context[DepsT],
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> (
        ContextStreamResponse[DepsT, None] | ContextStreamResponse[DepsT, FormattableT]
    ):
        """Generates a streaming response using the provided model."""
        result = self.fn(ctx, *args, **kwargs)
        messages = _utils.promote_to_messages(result)
        return model.context_stream(
            ctx=ctx, messages=messages, tools=self.toolkit, format=self.format
        )


@dataclass
class AsyncContextPrompt(Generic[P, DepsT, FormattableT]):
    """An async context-aware prompt that can be called with a model to generate a response.

    Created by decorating an async `ContextMessageTemplate` with `llm.prompt`. The decorated
    async function (with first parameter `'ctx'` of type `Context[DepsT]`) becomes callable
    with a `Model` to generate LLM responses asynchronously with context dependencies.

    An `AsyncContextPrompt` is essentially: async `ContextMessageTemplate` + tools + format.
    It can be invoked with a model: `await prompt(model, ctx, *args, **kwargs)`.
    """

    fn: AsyncContextMessageTemplate[P, DepsT]
    """The underlying async context-aware prompt function that generates message content."""

    toolkit: AsyncContextToolkit[DepsT]
    """The toolkit containing this prompt's async context-aware tools."""

    format: type[FormattableT] | Format[FormattableT] | None
    """The response format for the generated response."""

    @overload
    async def __call__(
        self: "AsyncContextPrompt[P, DepsT, None]",
        model: Model,
        ctx: Context[DepsT],
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> AsyncContextResponse[DepsT, None]: ...

    @overload
    async def __call__(
        self: "AsyncContextPrompt[P, DepsT, FormattableT]",
        model: Model,
        ctx: Context[DepsT],
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> AsyncContextResponse[DepsT, FormattableT]: ...

    async def __call__(
        self,
        model: Model,
        ctx: Context[DepsT],
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> AsyncContextResponse[DepsT, None] | AsyncContextResponse[DepsT, FormattableT]:
        """Generates a response using the provided model asynchronously."""
        return await self.call(model, ctx, *args, **kwargs)

    @overload
    async def call(
        self: "AsyncContextPrompt[P, DepsT, None]",
        model: Model,
        ctx: Context[DepsT],
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> AsyncContextResponse[DepsT, None]: ...

    @overload
    async def call(
        self: "AsyncContextPrompt[P, DepsT, FormattableT]",
        model: Model,
        ctx: Context[DepsT],
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> AsyncContextResponse[DepsT, FormattableT]: ...

    async def call(
        self,
        model: Model,
        ctx: Context[DepsT],
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> AsyncContextResponse[DepsT, None] | AsyncContextResponse[DepsT, FormattableT]:
        """Generates a response using the provided model asynchronously."""
        result = await self.fn(ctx, *args, **kwargs)
        messages = _utils.promote_to_messages(result)
        return await model.context_call_async(
            ctx=ctx, messages=messages, tools=self.toolkit, format=self.format
        )

    @overload
    async def stream(
        self: "AsyncContextPrompt[P, DepsT, None]",
        model: Model,
        ctx: Context[DepsT],
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> AsyncContextStreamResponse[DepsT, None]: ...

    @overload
    async def stream(
        self: "AsyncContextPrompt[P, DepsT, FormattableT]",
        model: Model,
        ctx: Context[DepsT],
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> AsyncContextStreamResponse[DepsT, FormattableT]: ...

    async def stream(
        self,
        model: Model,
        ctx: Context[DepsT],
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> (
        AsyncContextStreamResponse[DepsT, None]
        | AsyncContextStreamResponse[DepsT, FormattableT]
    ):
        """Generates a streaming response using the provided model asynchronously."""
        result = await self.fn(ctx, *args, **kwargs)
        messages = _utils.promote_to_messages(result)
        return await model.context_stream_async(
            ctx=ctx, messages=messages, tools=self.toolkit, format=self.format
        )
