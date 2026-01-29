"""Concrete Prompt classes for generating messages with tools and formatting."""

from collections.abc import Callable, Sequence
from dataclasses import dataclass, field
from typing import Any, Generic, TypeVar, overload

from ..._utils import copy_function_metadata
from ..context import Context, DepsT
from ..formatting import FormatSpec, FormattableT
from ..messages import Message, promote_to_messages
from ..models import Model
from ..providers import ModelId
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
from ..tools import AsyncContextToolkit, AsyncToolkit, ContextToolkit, Toolkit
from ..types import P
from .protocols import (
    AsyncContextMessageTemplate,
    AsyncMessageTemplate,
    ContextMessageTemplate,
    MessageTemplate,
)

FunctionT = TypeVar("FunctionT", bound=Callable[..., Any])


@dataclass(kw_only=True)
class BasePrompt(Generic[FunctionT]):
    """Base class for all Prompt types with shared metadata functionality."""

    fn: FunctionT
    """The underlying prompt function that generates message content."""

    __name__: str = field(init=False, repr=False, default="")
    """The name of the underlying function (preserved for decorator stacking)."""

    def __post_init__(self) -> None:
        """Preserve standard function attributes for decorator stacking."""
        copy_function_metadata(self, self.fn)


@dataclass
class Prompt(BasePrompt[MessageTemplate[P]], Generic[P, FormattableT]):
    """A prompt that can be called with a model to generate a response.

    Created by decorating a `MessageTemplate` with `llm.prompt`. The decorated
    function becomes callable with a `Model` to generate LLM responses.

    A `Prompt` is essentially: `MessageTemplate` + tools + format.
    It can be invoked with a model: `prompt(model, *args, **kwargs)`.
    """

    toolkit: Toolkit
    """The toolkit containing this prompt's tools."""

    format: FormatSpec[FormattableT] | None
    """The response format for the generated response."""

    def messages(self, *args: P.args, **kwargs: P.kwargs) -> Sequence[Message]:
        """Return the `Messages` from invoking this prompt."""
        return promote_to_messages(self.fn(*args, **kwargs))

    @overload
    def __call__(
        self: "Prompt[P, None]",
        model: Model | ModelId,
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> Response: ...

    @overload
    def __call__(
        self: "Prompt[P, FormattableT]",
        model: Model | ModelId,
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> Response[FormattableT]: ...

    def __call__(
        self, model: Model | ModelId, *args: P.args, **kwargs: P.kwargs
    ) -> Response | Response[FormattableT]:
        """Generates a response using the provided model."""
        return self.call(model, *args, **kwargs)

    @overload
    def call(
        self: "Prompt[P, None]",
        model: Model | ModelId,
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> Response: ...

    @overload
    def call(
        self: "Prompt[P, FormattableT]",
        model: Model | ModelId,
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> Response[FormattableT]: ...

    def call(
        self, model: Model | ModelId, *args: P.args, **kwargs: P.kwargs
    ) -> Response | Response[FormattableT]:
        """Generates a response using the provided model."""
        if isinstance(model, str):
            model = Model(model)
        messages = self.messages(*args, **kwargs)
        return model.call(messages, tools=self.toolkit, format=self.format)

    @overload
    def stream(
        self: "Prompt[P, None]",
        model: Model | ModelId,
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> StreamResponse: ...

    @overload
    def stream(
        self: "Prompt[P, FormattableT]",
        model: Model | ModelId,
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> StreamResponse[FormattableT]: ...

    def stream(
        self, model: Model | ModelId, *args: P.args, **kwargs: P.kwargs
    ) -> StreamResponse | StreamResponse[FormattableT]:
        """Generates a streaming response using the provided model."""
        if isinstance(model, str):
            model = Model(model)
        messages = self.messages(*args, **kwargs)
        return model.stream(messages, tools=self.toolkit, format=self.format)


@dataclass
class AsyncPrompt(BasePrompt[AsyncMessageTemplate[P]], Generic[P, FormattableT]):
    """An async prompt that can be called with a model to generate a response.

    Created by decorating an async `MessageTemplate` with `llm.prompt`. The decorated
    async function becomes callable with a `Model` to generate LLM responses asynchronously.

    An `AsyncPrompt` is essentially: async `MessageTemplate` + tools + format.
    It can be invoked with a model: `await prompt(model, *args, **kwargs)`.
    """

    toolkit: AsyncToolkit
    """The toolkit containing this prompt's async tools."""

    format: FormatSpec[FormattableT] | None
    """The response format for the generated response."""

    async def messages(self, *args: P.args, **kwargs: P.kwargs) -> Sequence[Message]:
        """Return the `Messages` from invoking this prompt."""
        return promote_to_messages(await self.fn(*args, **kwargs))

    @overload
    async def __call__(
        self: "AsyncPrompt[P, None]",
        model: Model | ModelId,
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> AsyncResponse: ...

    @overload
    async def __call__(
        self: "AsyncPrompt[P, FormattableT]",
        model: Model | ModelId,
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> AsyncResponse[FormattableT]: ...

    async def __call__(
        self, model: Model | ModelId, *args: P.args, **kwargs: P.kwargs
    ) -> AsyncResponse | AsyncResponse[FormattableT]:
        """Generates a response using the provided model asynchronously."""
        return await self.call(model, *args, **kwargs)

    @overload
    async def call(
        self: "AsyncPrompt[P, None]",
        model: Model | ModelId,
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> AsyncResponse: ...

    @overload
    async def call(
        self: "AsyncPrompt[P, FormattableT]",
        model: Model | ModelId,
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> AsyncResponse[FormattableT]: ...

    async def call(
        self, model: Model | ModelId, *args: P.args, **kwargs: P.kwargs
    ) -> AsyncResponse | AsyncResponse[FormattableT]:
        """Generates a response using the provided model asynchronously."""
        if isinstance(model, str):
            model = Model(model)
        messages = await self.messages(*args, **kwargs)
        return await model.call_async(messages, tools=self.toolkit, format=self.format)

    @overload
    async def stream(
        self: "AsyncPrompt[P, None]",
        model: Model | ModelId,
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> AsyncStreamResponse: ...

    @overload
    async def stream(
        self: "AsyncPrompt[P, FormattableT]",
        model: Model | ModelId,
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> AsyncStreamResponse[FormattableT]: ...

    async def stream(
        self, model: Model | ModelId, *args: P.args, **kwargs: P.kwargs
    ) -> AsyncStreamResponse | AsyncStreamResponse[FormattableT]:
        """Generates a streaming response using the provided model asynchronously."""
        if isinstance(model, str):
            model = Model(model)
        messages = await self.messages(*args, **kwargs)
        return await model.stream_async(
            messages, tools=self.toolkit, format=self.format
        )


@dataclass
class ContextPrompt(
    BasePrompt[ContextMessageTemplate[P, DepsT]], Generic[P, DepsT, FormattableT]
):
    """A context-aware prompt that can be called with a model to generate a response.

    Created by decorating a `ContextMessageTemplate` with `llm.prompt`. The decorated
    function (with first parameter `'ctx'` of type `Context[DepsT]`) becomes callable
    with a `Model` to generate LLM responses with context dependencies.

    A `ContextPrompt` is essentially: `ContextMessageTemplate` + tools + format.
    It can be invoked with a model: `prompt(model, ctx, *args, **kwargs)`.
    """

    toolkit: ContextToolkit[DepsT]
    """The toolkit containing this prompt's context-aware tools."""

    format: FormatSpec[FormattableT] | None
    """The response format for the generated response."""

    def messages(
        self, ctx: Context[DepsT], *args: P.args, **kwargs: P.kwargs
    ) -> Sequence[Message]:
        """Return the `Messages` from invoking this prompt."""
        return promote_to_messages(self.fn(ctx, *args, **kwargs))

    @overload
    def __call__(
        self: "ContextPrompt[P, DepsT, None]",
        model: Model | ModelId,
        ctx: Context[DepsT],
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> ContextResponse[DepsT, None]: ...

    @overload
    def __call__(
        self: "ContextPrompt[P, DepsT, FormattableT]",
        model: Model | ModelId,
        ctx: Context[DepsT],
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> ContextResponse[DepsT, FormattableT]: ...

    def __call__(
        self,
        model: Model | ModelId,
        ctx: Context[DepsT],
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> ContextResponse[DepsT, None] | ContextResponse[DepsT, FormattableT]:
        """Generates a response using the provided model."""
        return self.call(model, ctx, *args, **kwargs)

    @overload
    def call(
        self: "ContextPrompt[P, DepsT, None]",
        model: Model | ModelId,
        ctx: Context[DepsT],
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> ContextResponse[DepsT, None]: ...

    @overload
    def call(
        self: "ContextPrompt[P, DepsT, FormattableT]",
        model: Model | ModelId,
        ctx: Context[DepsT],
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> ContextResponse[DepsT, FormattableT]: ...

    def call(
        self,
        model: Model | ModelId,
        ctx: Context[DepsT],
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> ContextResponse[DepsT, None] | ContextResponse[DepsT, FormattableT]:
        """Generates a response using the provided model."""
        if isinstance(model, str):
            model = Model(model)
        messages = self.messages(ctx, *args, **kwargs)
        return model.context_call(
            messages, ctx=ctx, tools=self.toolkit, format=self.format
        )

    @overload
    def stream(
        self: "ContextPrompt[P, DepsT, None]",
        model: Model | ModelId,
        ctx: Context[DepsT],
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> ContextStreamResponse[DepsT, None]: ...

    @overload
    def stream(
        self: "ContextPrompt[P, DepsT, FormattableT]",
        model: Model | ModelId,
        ctx: Context[DepsT],
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> ContextStreamResponse[DepsT, FormattableT]: ...

    def stream(
        self,
        model: Model | ModelId,
        ctx: Context[DepsT],
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> (
        ContextStreamResponse[DepsT, None] | ContextStreamResponse[DepsT, FormattableT]
    ):
        """Generates a streaming response using the provided model."""
        if isinstance(model, str):
            model = Model(model)
        messages = self.messages(ctx, *args, **kwargs)
        return model.context_stream(
            messages, ctx=ctx, tools=self.toolkit, format=self.format
        )


@dataclass
class AsyncContextPrompt(
    BasePrompt[AsyncContextMessageTemplate[P, DepsT]], Generic[P, DepsT, FormattableT]
):
    """An async context-aware prompt that can be called with a model to generate a response.

    Created by decorating an async `ContextMessageTemplate` with `llm.prompt`. The decorated
    async function (with first parameter `'ctx'` of type `Context[DepsT]`) becomes callable
    with a `Model` to generate LLM responses asynchronously with context dependencies.

    An `AsyncContextPrompt` is essentially: async `ContextMessageTemplate` + tools + format.
    It can be invoked with a model: `await prompt(model, ctx, *args, **kwargs)`.
    """

    toolkit: AsyncContextToolkit[DepsT]
    """The toolkit containing this prompt's async context-aware tools."""

    format: FormatSpec[FormattableT] | None
    """The response format for the generated response."""

    async def messages(
        self, ctx: Context[DepsT], *args: P.args, **kwargs: P.kwargs
    ) -> Sequence[Message]:
        """Return the `Messages` from invoking this prompt."""
        return promote_to_messages(await self.fn(ctx, *args, **kwargs))

    @overload
    async def __call__(
        self: "AsyncContextPrompt[P, DepsT, None]",
        model: Model | ModelId,
        ctx: Context[DepsT],
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> AsyncContextResponse[DepsT, None]: ...

    @overload
    async def __call__(
        self: "AsyncContextPrompt[P, DepsT, FormattableT]",
        model: Model | ModelId,
        ctx: Context[DepsT],
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> AsyncContextResponse[DepsT, FormattableT]: ...

    async def __call__(
        self,
        model: Model | ModelId,
        ctx: Context[DepsT],
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> AsyncContextResponse[DepsT, None] | AsyncContextResponse[DepsT, FormattableT]:
        """Generates a response using the provided model asynchronously."""
        return await self.call(model, ctx, *args, **kwargs)

    @overload
    async def call(
        self: "AsyncContextPrompt[P, DepsT, None]",
        model: Model | ModelId,
        ctx: Context[DepsT],
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> AsyncContextResponse[DepsT, None]: ...

    @overload
    async def call(
        self: "AsyncContextPrompt[P, DepsT, FormattableT]",
        model: Model | ModelId,
        ctx: Context[DepsT],
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> AsyncContextResponse[DepsT, FormattableT]: ...

    async def call(
        self,
        model: Model | ModelId,
        ctx: Context[DepsT],
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> AsyncContextResponse[DepsT, None] | AsyncContextResponse[DepsT, FormattableT]:
        """Generates a response using the provided model asynchronously."""
        if isinstance(model, str):
            model = Model(model)
        messages = await self.messages(ctx, *args, **kwargs)
        return await model.context_call_async(
            messages, ctx=ctx, tools=self.toolkit, format=self.format
        )

    @overload
    async def stream(
        self: "AsyncContextPrompt[P, DepsT, None]",
        model: Model | ModelId,
        ctx: Context[DepsT],
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> AsyncContextStreamResponse[DepsT, None]: ...

    @overload
    async def stream(
        self: "AsyncContextPrompt[P, DepsT, FormattableT]",
        model: Model | ModelId,
        ctx: Context[DepsT],
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> AsyncContextStreamResponse[DepsT, FormattableT]: ...

    async def stream(
        self,
        model: Model | ModelId,
        ctx: Context[DepsT],
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> (
        AsyncContextStreamResponse[DepsT, None]
        | AsyncContextStreamResponse[DepsT, FormattableT]
    ):
        """Generates a streaming response using the provided model asynchronously."""
        if isinstance(model, str):
            model = Model(model)
        messages = await self.messages(ctx, *args, **kwargs)
        return await model.context_stream_async(
            messages, ctx=ctx, tools=self.toolkit, format=self.format
        )
