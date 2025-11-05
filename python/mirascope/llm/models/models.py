"""The model context manager for the `llm` module."""

from __future__ import annotations

from collections.abc import Iterator, Sequence
from contextlib import contextmanager
from contextvars import ContextVar
from typing import TYPE_CHECKING, overload
from typing_extensions import Unpack

from ..clients import PROVIDERS, get_client
from ..context import Context, DepsT
from ..formatting import Format, FormattableT
from ..messages import Message, UserContent
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
    AsyncContextTool,
    AsyncContextToolkit,
    AsyncTool,
    AsyncToolkit,
    ContextTool,
    ContextToolkit,
    Tool,
    Toolkit,
)

if TYPE_CHECKING:
    from ..clients import (
        ModelId,
        Params,
        Provider,
    )


MODEL_CONTEXT: ContextVar[Model | None] = ContextVar("MODEL_CONTEXT", default=None)


def get_model_from_context() -> Model | None:
    """Get the LLM currently set via context, if any."""
    return MODEL_CONTEXT.get()


class Model:
    """The unified LLM interface that delegates to provider-specific clients.

    This class provides a consistent interface for interacting with language models
    from various providers. It handles the common operations like generating responses,
    streaming, and async variants by delegating to the appropriate client methods.

    **Usage Note:** In most cases, you should use `llm.use_model()` instead of instantiating
    `Model` directly. This preserves the ability to override the model at runtime using
    the `llm.model()` context manager. Only instantiate `Model` directly if you want to
    hardcode a specific model and prevent it from being overridden by context.

    Example (recommended - allows override):

        ```python
        from mirascope import llm

        def recommend_book(genre: str) -> llm.Response:
            # Uses context model if available, otherwise creates default
            model = llm.use_model(provider="openai", model_id="gpt-4o-mini")
            message = llm.messages.user(f"Please recommend a book in {genre}.")
            return model.call(messages=[message])

        # Uses default model
        response = recommend_book("fantasy")

        # Override with different model
        with llm.model(provider="anthropic", model_id="claude-sonnet-4-0"):
            response = recommend_book("fantasy")  # Uses Claude
        ```

    Example (direct instantiation - prevents override):

        ```python
        from mirascope import llm

        def recommend_book(genre: str) -> llm.Response:
            # Hardcoded model, cannot be overridden by context
            model = llm.Model(provider="openai", model_id="gpt-4o-mini")
            message = llm.messages.user(f"Please recommend a book in {genre}.")
            return model.call(messages=[message])
        ```
    """

    provider: Provider
    """The provider being used (e.g. `openai`)."""

    model_id: ModelId
    """The model being used (e.g. `gpt-4o-mini`)."""

    params: Params
    """The default parameters for the model (temperature, max_tokens, etc.)."""

    def __init__(
        self,
        provider: Provider,
        model_id: ModelId,
        **params: Unpack[Params],
    ) -> None:
        """Initialize the Model with provider, model_id, and optional params."""
        if provider not in PROVIDERS:
            raise ValueError(f"Unknown provider: {provider}")
        self.provider = provider
        self.model_id = model_id
        self.params = params

    @overload
    def call(
        self,
        *,
        messages: Sequence[Message],
        tools: Sequence[Tool] | Toolkit | None = None,
        format: None = None,
    ) -> Response:
        """Generate an `llm.Response` without a response format."""
        ...

    @overload
    def call(
        self,
        *,
        messages: Sequence[Message],
        tools: Sequence[Tool] | Toolkit | None = None,
        format: type[FormattableT] | Format[FormattableT],
    ) -> Response[FormattableT]:
        """Generate an `llm.Response` with a response format."""
        ...

    @overload
    def call(
        self,
        *,
        messages: Sequence[Message],
        tools: Sequence[Tool] | Toolkit | None = None,
        format: type[FormattableT] | Format[FormattableT] | None,
    ) -> Response | Response[FormattableT]:
        """Generate an `llm.Response` with an optional response format."""
        ...

    def call(
        self,
        *,
        messages: Sequence[Message],
        tools: Sequence[Tool] | Toolkit | None = None,
        format: type[FormattableT] | Format[FormattableT] | None = None,
    ) -> Response | Response[FormattableT]:
        """Generate an `llm.Response` by synchronously calling this model's LLM provider.

        Args:
            messages: Messages to send to the LLM.
            tools: Optional tools that the model may invoke.
            format: Optional response format specifier.

        Returns:
            An `llm.Response` object containing the LLM-generated content.
        """
        return get_client(self.provider).call(
            model_id=self.model_id,
            messages=messages,
            tools=tools,
            format=format,
            **self.params,
        )

    @overload
    async def call_async(
        self,
        *,
        messages: Sequence[Message],
        tools: Sequence[AsyncTool] | AsyncToolkit | None = None,
        format: None = None,
    ) -> AsyncResponse:
        """Generate an `llm.AsyncResponse` without a response format."""
        ...

    @overload
    async def call_async(
        self,
        *,
        messages: Sequence[Message],
        tools: Sequence[AsyncTool] | AsyncToolkit | None = None,
        format: type[FormattableT] | Format[FormattableT],
    ) -> AsyncResponse[FormattableT]:
        """Generate an `llm.AsyncResponse` with a response format."""
        ...

    @overload
    async def call_async(
        self,
        *,
        messages: Sequence[Message],
        tools: Sequence[AsyncTool] | AsyncToolkit | None = None,
        format: type[FormattableT] | Format[FormattableT] | None,
    ) -> AsyncResponse | AsyncResponse[FormattableT]:
        """Generate an `llm.AsyncResponse` with an optional response format."""
        ...

    async def call_async(
        self,
        *,
        messages: Sequence[Message],
        tools: Sequence[AsyncTool] | AsyncToolkit | None = None,
        format: type[FormattableT] | Format[FormattableT] | None = None,
    ) -> AsyncResponse | AsyncResponse[FormattableT]:
        """Generate an `llm.AsyncResponse` by asynchronously calling this model's LLM provider.

        Args:
            messages: Messages to send to the LLM.
            tools: Optional tools that the model may invoke.
            format: Optional response format specifier.

        Returns:
            An `llm.AsyncResponse` object containing the LLM-generated content.
        """
        return await get_client(self.provider).call_async(
            model_id=self.model_id,
            messages=messages,
            tools=tools,
            **self.params,
            format=format,
        )

    @overload
    def stream(
        self,
        *,
        messages: Sequence[Message],
        tools: Sequence[Tool] | Toolkit | None = None,
        format: None = None,
    ) -> StreamResponse:
        """Stream an `llm.StreamResponse` without a response format."""
        ...

    @overload
    def stream(
        self,
        *,
        messages: Sequence[Message],
        tools: Sequence[Tool] | Toolkit | None = None,
        format: type[FormattableT] | Format[FormattableT],
    ) -> StreamResponse[FormattableT]:
        """Stream an `llm.StreamResponse` with a response format."""
        ...

    @overload
    def stream(
        self,
        *,
        messages: Sequence[Message],
        tools: Sequence[Tool] | Toolkit | None = None,
        format: type[FormattableT] | Format[FormattableT] | None,
    ) -> StreamResponse | StreamResponse[FormattableT]:
        """Stream an `llm.StreamResponse` with an optional response format."""
        ...

    def stream(
        self,
        *,
        messages: Sequence[Message],
        tools: Sequence[Tool] | Toolkit | None = None,
        format: type[FormattableT] | Format[FormattableT] | None = None,
    ) -> StreamResponse | StreamResponse[FormattableT]:
        """Generate an `llm.StreamResponse` by synchronously streaming from this model's LLM provider.

        Args:
            messages: Messages to send to the LLM.
            tools: Optional tools that the model may invoke.
            format: Optional response format specifier.

        Returns:
            An `llm.StreamResponse` object for iterating over the LLM-generated content.
        """
        return get_client(self.provider).stream(
            model_id=self.model_id,
            messages=messages,
            tools=tools,
            format=format,
            **self.params,
        )

    @overload
    async def stream_async(
        self,
        *,
        messages: list[Message],
        tools: Sequence[AsyncTool] | AsyncToolkit | None = None,
        format: None = None,
    ) -> AsyncStreamResponse:
        """Stream an `llm.AsyncStreamResponse` without a response format."""
        ...

    @overload
    async def stream_async(
        self,
        *,
        messages: list[Message],
        tools: Sequence[AsyncTool] | AsyncToolkit | None = None,
        format: type[FormattableT] | Format[FormattableT],
    ) -> AsyncStreamResponse[FormattableT]:
        """Stream an `llm.AsyncStreamResponse` with a response format."""
        ...

    @overload
    async def stream_async(
        self,
        *,
        messages: list[Message],
        tools: Sequence[AsyncTool] | AsyncToolkit | None = None,
        format: type[FormattableT] | Format[FormattableT] | None,
    ) -> AsyncStreamResponse | AsyncStreamResponse[FormattableT]:
        """Stream an `llm.AsyncStreamResponse` with an optional response format."""
        ...

    async def stream_async(
        self,
        *,
        messages: list[Message],
        tools: Sequence[AsyncTool] | AsyncToolkit | None = None,
        format: type[FormattableT] | Format[FormattableT] | None = None,
    ) -> AsyncStreamResponse | AsyncStreamResponse[FormattableT]:
        """Generate an `llm.AsyncStreamResponse` by asynchronously streaming from this model's LLM provider.

        Args:
            messages: Messages to send to the LLM.
            tools: Optional tools that the model may invoke.
            format: Optional response format specifier.

        Returns:
            An `llm.AsyncStreamResponse` object for asynchronously iterating over the LLM-generated content.
        """
        return await get_client(self.provider).stream_async(
            model_id=self.model_id,
            messages=messages,
            tools=tools,
            format=format,
            **self.params,
        )

    @overload
    def context_call(
        self,
        *,
        ctx: Context[DepsT],
        messages: Sequence[Message],
        tools: Sequence[Tool | ContextTool[DepsT]]
        | ContextToolkit[DepsT]
        | None = None,
        format: None = None,
    ) -> ContextResponse[DepsT, None]:
        """Generate an `llm.ContextResponse` without a response format."""
        ...

    @overload
    def context_call(
        self,
        *,
        ctx: Context[DepsT],
        messages: Sequence[Message],
        tools: Sequence[Tool | ContextTool[DepsT]]
        | ContextToolkit[DepsT]
        | None = None,
        format: type[FormattableT] | Format[FormattableT],
    ) -> ContextResponse[DepsT, FormattableT]:
        """Generate an `llm.ContextResponse` with a response format."""
        ...

    @overload
    def context_call(
        self,
        *,
        ctx: Context[DepsT],
        messages: Sequence[Message],
        tools: Sequence[Tool | ContextTool[DepsT]]
        | ContextToolkit[DepsT]
        | None = None,
        format: type[FormattableT] | Format[FormattableT] | None,
    ) -> ContextResponse[DepsT, None] | ContextResponse[DepsT, FormattableT]:
        """Generate an `llm.ContextResponse` with an optional response format."""
        ...

    def context_call(
        self,
        *,
        ctx: Context[DepsT],
        messages: Sequence[Message],
        tools: Sequence[Tool | ContextTool[DepsT]]
        | ContextToolkit[DepsT]
        | None = None,
        format: type[FormattableT] | Format[FormattableT] | None = None,
    ) -> ContextResponse[DepsT, None] | ContextResponse[DepsT, FormattableT]:
        """Generate an `llm.ContextResponse` by synchronously calling this model's LLM provider.

        Args:
            ctx: Context object with dependencies for tools.
            messages: Messages to send to the LLM.
            tools: Optional tools that the model may invoke.
            format: Optional response format specifier.

        Returns:
            An `llm.ContextResponse` object containing the LLM-generated content.
        """
        return get_client(self.provider).context_call(
            ctx=ctx,
            model_id=self.model_id,
            messages=messages,
            tools=tools,
            format=format,
            **self.params,
        )

    @overload
    async def context_call_async(
        self,
        *,
        ctx: Context[DepsT],
        messages: Sequence[Message],
        tools: Sequence[AsyncTool | AsyncContextTool[DepsT]]
        | AsyncContextToolkit[DepsT]
        | None = None,
        format: None = None,
    ) -> AsyncContextResponse[DepsT, None]:
        """Generate an `llm.AsyncContextResponse` without a response format."""
        ...

    @overload
    async def context_call_async(
        self,
        *,
        ctx: Context[DepsT],
        messages: Sequence[Message],
        tools: Sequence[AsyncTool | AsyncContextTool[DepsT]]
        | AsyncContextToolkit[DepsT]
        | None = None,
        format: type[FormattableT] | Format[FormattableT],
    ) -> AsyncContextResponse[DepsT, FormattableT]:
        """Generate an `llm.AsyncContextResponse` with a response format."""
        ...

    @overload
    async def context_call_async(
        self,
        *,
        ctx: Context[DepsT],
        messages: Sequence[Message],
        tools: Sequence[AsyncTool | AsyncContextTool[DepsT]]
        | AsyncContextToolkit[DepsT]
        | None = None,
        format: type[FormattableT] | Format[FormattableT] | None,
    ) -> AsyncContextResponse[DepsT, None] | AsyncContextResponse[DepsT, FormattableT]:
        """Generate an `llm.AsyncContextResponse` with an optional response format."""
        ...

    async def context_call_async(
        self,
        *,
        ctx: Context[DepsT],
        messages: Sequence[Message],
        tools: Sequence[AsyncTool | AsyncContextTool[DepsT]]
        | AsyncContextToolkit[DepsT]
        | None = None,
        format: type[FormattableT] | Format[FormattableT] | None = None,
    ) -> AsyncContextResponse[DepsT, None] | AsyncContextResponse[DepsT, FormattableT]:
        """Generate an `llm.AsyncContextResponse` by asynchronously calling this model's LLM provider.

        Args:
            ctx: Context object with dependencies for tools.
            messages: Messages to send to the LLM.
            tools: Optional tools that the model may invoke.
            format: Optional response format specifier.

        Returns:
            An `llm.AsyncContextResponse` object containing the LLM-generated content.
        """
        return await get_client(self.provider).context_call_async(
            ctx=ctx,
            model_id=self.model_id,
            messages=messages,
            tools=tools,
            format=format,
            **self.params,
        )

    @overload
    def context_stream(
        self,
        *,
        ctx: Context[DepsT],
        messages: Sequence[Message],
        tools: Sequence[Tool | ContextTool[DepsT]]
        | ContextToolkit[DepsT]
        | None = None,
        format: None = None,
    ) -> ContextStreamResponse[DepsT, None]:
        """Stream an `llm.ContextStreamResponse` without a response format."""
        ...

    @overload
    def context_stream(
        self,
        *,
        ctx: Context[DepsT],
        messages: Sequence[Message],
        tools: Sequence[Tool | ContextTool[DepsT]]
        | ContextToolkit[DepsT]
        | None = None,
        format: type[FormattableT] | Format[FormattableT],
    ) -> ContextStreamResponse[DepsT, FormattableT]:
        """Stream an `llm.ContextStreamResponse` with a response format."""
        ...

    @overload
    def context_stream(
        self,
        *,
        ctx: Context[DepsT],
        messages: Sequence[Message],
        tools: Sequence[Tool | ContextTool[DepsT]]
        | ContextToolkit[DepsT]
        | None = None,
        format: type[FormattableT] | Format[FormattableT] | None,
    ) -> (
        ContextStreamResponse[DepsT, None] | ContextStreamResponse[DepsT, FormattableT]
    ):
        """Stream an `llm.ContextStreamResponse` with an optional response format."""
        ...

    def context_stream(
        self,
        *,
        ctx: Context[DepsT],
        messages: Sequence[Message],
        tools: Sequence[Tool | ContextTool[DepsT]]
        | ContextToolkit[DepsT]
        | None = None,
        format: type[FormattableT] | Format[FormattableT] | None = None,
    ) -> (
        ContextStreamResponse[DepsT, None] | ContextStreamResponse[DepsT, FormattableT]
    ):
        """Generate an `llm.ContextStreamResponse` by synchronously streaming from this model's LLM provider.

        Args:
            ctx: Context object with dependencies for tools.
            messages: Messages to send to the LLM.
            tools: Optional tools that the model may invoke.
            format: Optional response format specifier.

        Returns:
            An `llm.ContextStreamResponse` object for iterating over the LLM-generated content.
        """
        return get_client(self.provider).context_stream(
            ctx=ctx,
            model_id=self.model_id,
            messages=messages,
            tools=tools,
            format=format,
            **self.params,
        )

    @overload
    async def context_stream_async(
        self,
        *,
        ctx: Context[DepsT],
        messages: list[Message],
        tools: Sequence[AsyncTool | AsyncContextTool[DepsT]]
        | AsyncContextToolkit[DepsT]
        | None = None,
        format: None = None,
    ) -> AsyncContextStreamResponse[DepsT, None]:
        """Stream an `llm.AsyncContextStreamResponse` without a response format."""
        ...

    @overload
    async def context_stream_async(
        self,
        *,
        ctx: Context[DepsT],
        messages: list[Message],
        tools: Sequence[AsyncTool | AsyncContextTool[DepsT]]
        | AsyncContextToolkit[DepsT]
        | None = None,
        format: type[FormattableT] | Format[FormattableT],
    ) -> AsyncContextStreamResponse[DepsT, FormattableT]:
        """Stream an `llm.AsyncContextStreamResponse` with a response format."""
        ...

    @overload
    async def context_stream_async(
        self,
        *,
        ctx: Context[DepsT],
        messages: list[Message],
        tools: Sequence[AsyncTool | AsyncContextTool[DepsT]]
        | AsyncContextToolkit[DepsT]
        | None = None,
        format: type[FormattableT] | Format[FormattableT] | None,
    ) -> (
        AsyncContextStreamResponse[DepsT, None]
        | AsyncContextStreamResponse[DepsT, FormattableT]
    ):
        """Stream an `llm.AsyncContextStreamResponse` with an optional response format."""
        ...

    async def context_stream_async(
        self,
        *,
        ctx: Context[DepsT],
        messages: list[Message],
        tools: Sequence[AsyncTool | AsyncContextTool[DepsT]]
        | AsyncContextToolkit[DepsT]
        | None = None,
        format: type[FormattableT] | Format[FormattableT] | None = None,
    ) -> (
        AsyncContextStreamResponse[DepsT, None]
        | AsyncContextStreamResponse[DepsT, FormattableT]
    ):
        """Generate an `llm.AsyncContextStreamResponse` by asynchronously streaming from this model's LLM provider.

        Args:
            ctx: Context object with dependencies for tools.
            messages: Messages to send to the LLM.
            tools: Optional tools that the model may invoke.
            format: Optional response format specifier.

        Returns:
            An `llm.AsyncContextStreamResponse` object for asynchronously iterating over the LLM-generated content.
        """
        return await get_client(self.provider).context_stream_async(
            ctx=ctx,
            model_id=self.model_id,
            messages=messages,
            tools=tools,
            format=format,
            **self.params,
        )

    @overload
    def resume(
        self,
        *,
        response: Response,
        content: UserContent,
    ) -> Response:
        """Resume an `llm.Response` without a response format."""
        ...

    @overload
    def resume(
        self,
        *,
        response: Response[FormattableT],
        content: UserContent,
    ) -> Response[FormattableT]:
        """Resume an `llm.Response` with a response format."""
        ...

    @overload
    def resume(
        self,
        *,
        response: Response | Response[FormattableT],
        content: UserContent,
    ) -> Response | Response[FormattableT]:
        """Resume an `llm.Response` with an optional response format."""
        ...

    def resume(
        self,
        *,
        response: Response | Response[FormattableT],
        content: UserContent,
    ) -> Response | Response[FormattableT]:
        """Generate a new `llm.Response` by extending another response's messages with additional user content.

        Uses the previous response's tools and output format, and this model's params.

        Depending on the client, this may be a wrapper around using client call methods
        with the response's messages and the new content, or it may use a provider-specific
        API for resuming an existing interaction.

        Args:
            response: Previous response to extend.
            content: Additional user content to append.

        Returns:
            A new `llm.Response` object containing the extended conversation.
        """
        return get_client(self.provider).resume(
            model_id=self.model_id,
            response=response,
            content=content,
            **self.params,
        )

    @overload
    async def resume_async(
        self,
        *,
        response: AsyncResponse,
        content: UserContent,
    ) -> AsyncResponse:
        """Resume an `llm.AsyncResponse` without a response format."""
        ...

    @overload
    async def resume_async(
        self,
        *,
        response: AsyncResponse[FormattableT],
        content: UserContent,
    ) -> AsyncResponse[FormattableT]:
        """Resume an `llm.AsyncResponse` with a response format."""
        ...

    @overload
    async def resume_async(
        self,
        *,
        response: AsyncResponse | AsyncResponse[FormattableT],
        content: UserContent,
    ) -> AsyncResponse | AsyncResponse[FormattableT]:
        """Resume an `llm.AsyncResponse` with an optional response format."""
        ...

    async def resume_async(
        self,
        *,
        response: AsyncResponse | AsyncResponse[FormattableT],
        content: UserContent,
    ) -> AsyncResponse | AsyncResponse[FormattableT]:
        """Generate a new `llm.AsyncResponse` by extending another response's messages with additional user content.

        Uses the previous response's tools and output format, and this model's params.

        Depending on the client, this may be a wrapper around using client call methods
        with the response's messages and the new content, or it may use a provider-specific
        API for resuming an existing interaction.

        Args:
            response: Previous async response to extend.
            content: Additional user content to append.

        Returns:
            A new `llm.AsyncResponse` object containing the extended conversation.
        """
        return await get_client(self.provider).resume_async(
            model_id=self.model_id,
            response=response,
            content=content,
            **self.params,
        )

    @overload
    def context_resume(
        self,
        *,
        ctx: Context[DepsT],
        response: ContextResponse[DepsT, None],
        content: UserContent,
    ) -> ContextResponse[DepsT, None]:
        """Resume an `llm.ContextResponse` without a response format."""
        ...

    @overload
    def context_resume(
        self,
        *,
        ctx: Context[DepsT],
        response: ContextResponse[DepsT, FormattableT],
        content: UserContent,
    ) -> ContextResponse[DepsT, FormattableT]:
        """Resume an `llm.ContextResponse` with a response format."""
        ...

    @overload
    def context_resume(
        self,
        *,
        ctx: Context[DepsT],
        response: ContextResponse[DepsT, None] | ContextResponse[DepsT, FormattableT],
        content: UserContent,
    ) -> ContextResponse[DepsT, None] | ContextResponse[DepsT, FormattableT]:
        """Resume an `llm.ContextResponse` with an optional response format."""
        ...

    def context_resume(
        self,
        *,
        ctx: Context[DepsT],
        response: ContextResponse[DepsT, None] | ContextResponse[DepsT, FormattableT],
        content: UserContent,
    ) -> ContextResponse[DepsT, None] | ContextResponse[DepsT, FormattableT]:
        """Generate a new `llm.ContextResponse` by extending another response's messages with additional user content.

        Uses the previous response's tools and output format, and this model's params.

        Depending on the client, this may be a wrapper around using client call methods
        with the response's messages and the new content, or it may use a provider-specific
        API for resuming an existing interaction.

        Args:
            ctx: Context object with dependencies for tools.
            response: Previous context response to extend.
            content: Additional user content to append.

        Returns:
            A new `llm.ContextResponse` object containing the extended conversation.
        """
        return get_client(self.provider).context_resume(
            ctx=ctx,
            model_id=self.model_id,
            response=response,
            content=content,
            **self.params,
        )

    @overload
    async def context_resume_async(
        self,
        *,
        ctx: Context[DepsT],
        response: AsyncContextResponse[DepsT, None],
        content: UserContent,
    ) -> AsyncContextResponse[DepsT, None]:
        """Resume an `llm.AsyncContextResponse` without a response format."""
        ...

    @overload
    async def context_resume_async(
        self,
        *,
        ctx: Context[DepsT],
        response: AsyncContextResponse[DepsT, FormattableT],
        content: UserContent,
    ) -> AsyncContextResponse[DepsT, FormattableT]:
        """Resume an `llm.AsyncContextResponse` with a response format."""
        ...

    @overload
    async def context_resume_async(
        self,
        *,
        ctx: Context[DepsT],
        response: AsyncContextResponse[DepsT, None]
        | AsyncContextResponse[DepsT, FormattableT],
        content: UserContent,
    ) -> AsyncContextResponse[DepsT, None] | AsyncContextResponse[DepsT, FormattableT]:
        """Resume an `llm.AsyncContextResponse` with an optional response format."""
        ...

    async def context_resume_async(
        self,
        *,
        ctx: Context[DepsT],
        response: AsyncContextResponse[DepsT, None]
        | AsyncContextResponse[DepsT, FormattableT],
        content: UserContent,
    ) -> AsyncContextResponse[DepsT, None] | AsyncContextResponse[DepsT, FormattableT]:
        """Generate a new `llm.AsyncContextResponse` by extending another response's messages with additional user content.

        Uses the previous response's tools and output format, and this model's params.

        Depending on the client, this may be a wrapper around using client call methods
        with the response's messages and the new content, or it may use a provider-specific
        API for resuming an existing interaction.

        Args:
            ctx: Context object with dependencies for tools.
            response: Previous async context response to extend.
            content: Additional user content to append.

        Returns:
            A new `llm.AsyncContextResponse` object containing the extended conversation.
        """
        return await get_client(self.provider).context_resume_async(
            ctx=ctx,
            model_id=self.model_id,
            response=response,
            content=content,
            **self.params,
        )

    @overload
    def resume_stream(
        self,
        *,
        response: StreamResponse,
        content: UserContent,
    ) -> StreamResponse:
        """Resume an `llm.StreamResponse` without a response format."""
        ...

    @overload
    def resume_stream(
        self,
        *,
        response: StreamResponse[FormattableT],
        content: UserContent,
    ) -> StreamResponse[FormattableT]:
        """Resume an `llm.StreamResponse` with a response format."""
        ...

    @overload
    def resume_stream(
        self,
        *,
        response: StreamResponse | StreamResponse[FormattableT],
        content: UserContent,
    ) -> StreamResponse | StreamResponse[FormattableT]:
        """Resume an `llm.StreamResponse` with an optional response format."""
        ...

    def resume_stream(
        self,
        *,
        response: StreamResponse | StreamResponse[FormattableT],
        content: UserContent,
    ) -> StreamResponse | StreamResponse[FormattableT]:
        """Generate a new `llm.StreamResponse` by extending another response's messages with additional user content.

        Uses the previous response's tools and output format, and this model's params.

        Depending on the client, this may be a wrapper around using client call methods
        with the response's messages and the new content, or it may use a provider-specific
        API for resuming an existing interaction.

        Args:
            response: Previous stream response to extend.
            content: Additional user content to append.

        Returns:
            A new `llm.StreamResponse` object for streaming the extended conversation.
        """
        return get_client(self.provider).resume_stream(
            model_id=self.model_id,
            response=response,
            content=content,
            **self.params,
        )

    @overload
    async def resume_stream_async(
        self,
        *,
        response: AsyncStreamResponse,
        content: UserContent,
    ) -> AsyncStreamResponse:
        """Resume an `llm.AsyncStreamResponse` without a response format."""
        ...

    @overload
    async def resume_stream_async(
        self,
        *,
        response: AsyncStreamResponse[FormattableT],
        content: UserContent,
    ) -> AsyncStreamResponse[FormattableT]:
        """Resume an `llm.AsyncStreamResponse` with a response format."""
        ...

    @overload
    async def resume_stream_async(
        self,
        *,
        response: AsyncStreamResponse | AsyncStreamResponse[FormattableT],
        content: UserContent,
    ) -> AsyncStreamResponse | AsyncStreamResponse[FormattableT]:
        """Resume an `llm.AsyncStreamResponse` with an optional response format."""
        ...

    async def resume_stream_async(
        self,
        *,
        response: AsyncStreamResponse | AsyncStreamResponse[FormattableT],
        content: UserContent,
    ) -> AsyncStreamResponse | AsyncStreamResponse[FormattableT]:
        """Generate a new `llm.AsyncStreamResponse` by extending another response's messages with additional user content.

        Uses the previous response's tools and output format, and this model's params.

        Depending on the client, this may be a wrapper around using client call methods
        with the response's messages and the new content, or it may use a provider-specific
        API for resuming an existing interaction.

        Args:
            response: Previous async stream response to extend.
            content: Additional user content to append.

        Returns:
            A new `llm.AsyncStreamResponse` object for asynchronously streaming the extended conversation.
        """
        return await get_client(self.provider).resume_stream_async(
            model_id=self.model_id,
            response=response,
            content=content,
            **self.params,
        )

    @overload
    def context_resume_stream(
        self,
        *,
        ctx: Context[DepsT],
        response: ContextStreamResponse[DepsT, None],
        content: UserContent,
    ) -> ContextStreamResponse[DepsT, None]:
        """Resume an `llm.ContextStreamResponse` without a response format."""
        ...

    @overload
    def context_resume_stream(
        self,
        *,
        ctx: Context[DepsT],
        response: ContextStreamResponse[DepsT, FormattableT],
        content: UserContent,
    ) -> ContextStreamResponse[DepsT, FormattableT]:
        """Resume an `llm.ContextStreamResponse` with a response format."""
        ...

    @overload
    def context_resume_stream(
        self,
        *,
        ctx: Context[DepsT],
        response: ContextStreamResponse[DepsT, None]
        | ContextStreamResponse[DepsT, FormattableT],
        content: UserContent,
    ) -> (
        ContextStreamResponse[DepsT, None] | ContextStreamResponse[DepsT, FormattableT]
    ):
        """Resume an `llm.ContextStreamResponse` with an optional response format."""
        ...

    def context_resume_stream(
        self,
        *,
        ctx: Context[DepsT],
        response: ContextStreamResponse[DepsT, None]
        | ContextStreamResponse[DepsT, FormattableT],
        content: UserContent,
    ) -> (
        ContextStreamResponse[DepsT, None] | ContextStreamResponse[DepsT, FormattableT]
    ):
        """Generate a new `llm.ContextStreamResponse` by extending another response's messages with additional user content.

        Uses the previous response's tools and output format, and this model's params.

        Depending on the client, this may be a wrapper around using client call methods
        with the response's messages and the new content, or it may use a provider-specific
        API for resuming an existing interaction.

        Args:
            ctx: Context object with dependencies for tools.
            response: Previous context stream response to extend.
            content: Additional user content to append.

        Returns:
            A new `llm.ContextStreamResponse` object for streaming the extended conversation.
        """
        return get_client(self.provider).context_resume_stream(
            ctx=ctx,
            model_id=self.model_id,
            response=response,
            content=content,
            **self.params,
        )

    @overload
    async def context_resume_stream_async(
        self,
        *,
        ctx: Context[DepsT],
        response: AsyncContextStreamResponse[DepsT, None],
        content: UserContent,
    ) -> AsyncContextStreamResponse[DepsT, None]:
        """Resume an `llm.AsyncContextStreamResponse` without a response format."""
        ...

    @overload
    async def context_resume_stream_async(
        self,
        *,
        ctx: Context[DepsT],
        response: AsyncContextStreamResponse[DepsT, FormattableT],
        content: UserContent,
    ) -> AsyncContextStreamResponse[DepsT, FormattableT]:
        """Resume an `llm.AsyncContextStreamResponse` with a response format."""
        ...

    @overload
    async def context_resume_stream_async(
        self,
        *,
        ctx: Context[DepsT],
        response: AsyncContextStreamResponse[DepsT, None]
        | AsyncContextStreamResponse[DepsT, FormattableT],
        content: UserContent,
    ) -> (
        AsyncContextStreamResponse[DepsT, None]
        | AsyncContextStreamResponse[DepsT, FormattableT]
    ):
        """Resume an `llm.AsyncContextStreamResponse` with an optional response format."""
        ...

    async def context_resume_stream_async(
        self,
        *,
        ctx: Context[DepsT],
        response: AsyncContextStreamResponse[DepsT, None]
        | AsyncContextStreamResponse[DepsT, FormattableT],
        content: UserContent,
    ) -> (
        AsyncContextStreamResponse[DepsT, None]
        | AsyncContextStreamResponse[DepsT, FormattableT]
    ):
        """Generate a new `llm.AsyncContextStreamResponse` by extending another response's messages with additional user content.

        Uses the previous response's tools and output format, and this model's params.

        Depending on the client, this may be a wrapper around using client call methods
        with the response's messages and the new content, or it may use a provider-specific
        API for resuming an existing interaction.

        Args:
            ctx: Context object with dependencies for tools.
            response: Previous async context stream response to extend.
            content: Additional user content to append.

        Returns:
            A new `llm.AsyncContextStreamResponse` object for asynchronously streaming the extended conversation.
        """
        return await get_client(self.provider).context_resume_stream_async(
            ctx=ctx,
            model_id=self.model_id,
            response=response,
            content=content,
            **self.params,
        )


@contextmanager
def model(
    *,
    provider: Provider,
    model_id: ModelId,
    **params: Unpack[Params],
) -> Iterator[None]:
    """Set a model in context for the duration of the context manager.

    This context manager sets a model that will be used by `llm.use_model()` calls
    within the context. This allows you to override the default model at runtime.

    Args:
        provider: The LLM provider to use (e.g., "openai:completions", "anthropic", "google").
        model_id: The specific model identifier for the chosen provider.
        **params: Additional parameters to configure the model (e.g. temperature). See `llm.Params`.

    Raises:
        ValueError: If the specified provider is not supported.

    Example:

        ```python
        import mirascope.llm as llm

        def recommend_book(genre: str) -> llm.Response:
            model = llm.use_model(provider="openai", model_id="gpt-4o-mini")
            message = llm.messages.user(f"Please recommend a book in {genre}.")
            return model.call(messages=[message])

        # Override the default model at runtime
        with llm.model(provider="anthropic", model_id="claude-sonnet-4-0"):
            response = recommend_book("fantasy")  # Uses Claude instead of GPT
        ```
    """
    token = MODEL_CONTEXT.set(Model(provider, model_id, **params))
    try:
        yield
    finally:
        MODEL_CONTEXT.reset(token)


def use_model(
    *,
    provider: Provider,
    model_id: ModelId,
    **params: Unpack[Params],
) -> Model:
    """Get the model from context if available, otherwise create a new Model.

    This function checks if a model has been set in the context (via `llm.model()`
    context manager). If a model is found in the context, it returns that model.
    Otherwise, it creates and returns a new `llm.Model` instance with the provided
    arguments as defaults.

    This allows you to write functions that work with a default model but can be
    overridden at runtime using the `llm.model()` context manager.

    Args:
        provider: The LLM provider to use (e.g., "openai:completions", "anthropic", "google").
        model_id: The specific model identifier for the chosen provider.
        **params: Additional parameters to configure the model (e.g. temperature). See `llm.Params`.

    Returns:
        An `llm.Model` instance from context or a new instance with the specified settings.

    Raises:
        ValueError: If the specified provider is not supported.

    Example:

        ```python
        import mirascope.llm as llm

        def recommend_book(genre: str) -> llm.Response:
            model = llm.use_model(provider="openai", model_id="gpt-4o-mini")
            message = llm.messages.user(f"Please recommend a book in {genre}.")
            return model.call(messages=[message])

        # Uses the default model (gpt-4o-mini)
        response = recommend_book("fantasy")

        # Override with a different model
        with llm.model(provider="anthropic", model_id="claude-sonnet-4-0"):
            response = recommend_book("fantasy")  # Uses Claude instead
        ```
    """
    context_model = get_model_from_context()
    if context_model is not None:
        return context_model
    return Model(provider, model_id, **params)
