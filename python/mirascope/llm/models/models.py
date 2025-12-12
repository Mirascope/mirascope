"""The model context manager for the `llm` module."""

from __future__ import annotations

from collections.abc import Sequence
from contextvars import ContextVar, Token
from types import TracebackType
from typing import overload
from typing_extensions import Unpack

from ..context import Context, DepsT
from ..formatting import Format, FormattableT
from ..messages import Message, UserContent
from ..providers import (
    ModelId,
    Params,
    Provider,
    ProviderId,
    get_provider_for_model,
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
    AsyncContextTool,
    AsyncContextToolkit,
    AsyncTool,
    AsyncToolkit,
    ContextTool,
    ContextToolkit,
    Tool,
    Toolkit,
)

MODEL_CONTEXT: ContextVar[Model | None] = ContextVar("MODEL_CONTEXT", default=None)


def model_from_context() -> Model | None:
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
            model = llm.use_model("openai/gpt-5-mini")
            message = llm.messages.user(f"Please recommend a book in {genre}.")
            return model.call(messages=[message])

        # Uses default model
        response = recommend_book("fantasy")

        # Override with different model
        with llm.model(provider="anthropic", model_id="anthropic/claude-sonnet-4-5"):
            response = recommend_book("fantasy")  # Uses Claude
        ```

    Example (direct instantiation - prevents override):

        ```python
        from mirascope import llm

        def recommend_book(genre: str) -> llm.Response:
            # Hardcoded model, cannot be overridden by context
            model = llm.Model("openai/gpt-5-mini")
            message = llm.messages.user(f"Please recommend a book in {genre}.")
            return model.call(messages=[message])
        ```
    """

    model_id: ModelId
    """The model being used (e.g. `"openai/gpt-4o-mini"`)."""

    params: Params
    """The default parameters for the model (temperature, max_tokens, etc.)."""

    def __init__(
        self,
        model_id: ModelId,
        **params: Unpack[Params],
    ) -> None:
        """Initialize the Model with model_id and optional params."""
        if "/" not in model_id:
            raise ValueError(
                "Invalid model_id format. Expected format: 'provider/model-name' "
                f"(e.g., 'openai/gpt-4'). Got: '{model_id}'"
            )
        self.model_id = model_id
        self.params = params
        self._token_stack: list[Token[Model | None]] = []

    @property
    def provider(self) -> Provider:
        """The provider being used (e.g. an `OpenAIProvider`).

        This property dynamically looks up the provider from the registry based on
        the current model_id. This allows provider overrides via `llm.register_provider()`
        to take effect even after the model instance is created.

        Raises:
            NoRegisteredProviderError: If no provider is available for the model_id
        """
        return get_provider_for_model(self.model_id)

    @property
    def provider_id(self) -> ProviderId:
        """The string id of the provider being used (e.g. `"openai"`).

        This property returns the `id` field of the dynamically resolved provider.

        Raises:
            NoRegisteredProviderError: If no provider is available for the model_id
        """
        return self.provider.id

    def __enter__(self) -> Model:
        """Enter the context manager, setting this model in context."""
        token = MODEL_CONTEXT.set(self)
        self._token_stack.append(token)
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        """Exit the context manager, resetting the model context."""
        if self._token_stack:
            token = self._token_stack.pop()
            MODEL_CONTEXT.reset(token)

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
        return self.provider.call(
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
        return await self.provider.call_async(
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
        return self.provider.stream(
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
        messages: Sequence[Message],
        tools: Sequence[AsyncTool] | AsyncToolkit | None = None,
        format: None = None,
    ) -> AsyncStreamResponse:
        """Stream an `llm.AsyncStreamResponse` without a response format."""
        ...

    @overload
    async def stream_async(
        self,
        *,
        messages: Sequence[Message],
        tools: Sequence[AsyncTool] | AsyncToolkit | None = None,
        format: type[FormattableT] | Format[FormattableT],
    ) -> AsyncStreamResponse[FormattableT]:
        """Stream an `llm.AsyncStreamResponse` with a response format."""
        ...

    @overload
    async def stream_async(
        self,
        *,
        messages: Sequence[Message],
        tools: Sequence[AsyncTool] | AsyncToolkit | None = None,
        format: type[FormattableT] | Format[FormattableT] | None,
    ) -> AsyncStreamResponse | AsyncStreamResponse[FormattableT]:
        """Stream an `llm.AsyncStreamResponse` with an optional response format."""
        ...

    async def stream_async(
        self,
        *,
        messages: Sequence[Message],
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
        return await self.provider.stream_async(
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
        return self.provider.context_call(
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
        return await self.provider.context_call_async(
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
        return self.provider.context_stream(
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
        messages: Sequence[Message],
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
        messages: Sequence[Message],
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
        messages: Sequence[Message],
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
        messages: Sequence[Message],
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
        return await self.provider.context_stream_async(
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
        return self.provider.resume(
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
        return await self.provider.resume_async(
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
        return self.provider.context_resume(
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
        return await self.provider.context_resume_async(
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
        return self.provider.resume_stream(
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
        return await self.provider.resume_stream_async(
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
        return self.provider.context_resume_stream(
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
        return await self.provider.context_resume_stream_async(
            ctx=ctx,
            model_id=self.model_id,
            response=response,
            content=content,
            **self.params,
        )


def model(
    model_id: ModelId,
    **params: Unpack[Params],
) -> Model:
    """Helper for creating a `Model` instance (which may be used as a context manager).

    This is just an alias for the `Model` constructor, added for convenience.

    This function returns a `Model` instance that implements the context manager protocol.
    When used with a `with` statement, the model will be set in context and used by both
    `llm.use_model()` and `llm.call()` within that context. This allows you to override
    the default model at runtime without modifying function definitions.

    The returned `Model` instance can also be stored and reused:

    ```python
    m = llm.model("openai/gpt-4o")
    # Use directly
    response = m.call(messages=[...])
    # Or use as context manager
    with m:
        response = recommend_book("fantasy")
    ```

    When a model is set in context, it completely overrides any model ID or parameters
    specified in `llm.use_model()` or `llm.call()`. The context model's parameters take
    precedence, and any unset parameters use default values.

    Args:
        model_id: A model ID string (e.g., "openai/gpt-4").
        **params: Additional parameters to configure the model (e.g. temperature). See `llm.Params`.

    Returns:
        A Model instance that can be used as a context manager.

    Raises:
        ValueError: If the specified provider is not supported.

    Example:
        With `llm.use_model()`

        ```python
        import mirascope.llm as llm

        def recommend_book(genre: str) -> llm.Response:
            model = llm.use_model("openai/gpt-5-mini")
            message = llm.messages.user(f"Please recommend a book in {genre}.")
            return model.call(messages=[message])

        # Override the default model at runtime
        with llm.model("anthropic/claude-sonnet-4-5"):
           response = recommend_book("fantasy")  # Uses Claude instead of GPT
        ```

    Example:
        With `llm.call()`

        ```python
        import mirascope.llm as llm

        @llm.call("openai/gpt-5-mini")
        def recommend_book(genre: str):
            return f"Please recommend a {genre} book."

        # Override the decorated model at runtime
        with llm.model("anthropic/claude-sonnet-4-0"):
            response = recommend_book("fantasy")  # Uses Claude instead of GPT
        ```

    Example:
        Storing and reusing Model instances

        ```python
        import mirascope.llm as llm

        # Create and store a model
        m = llm.model("openai/gpt-4o")

        # Use it directly
        response = m.call(messages=[llm.messages.user("Hello!")])

        # Or use it as a context manager
        with m:
            response = recommend_book("fantasy")
        ```
    """
    return Model(model_id, **params)


@overload
def use_model(
    model: ModelId,
    **params: Unpack[Params],
) -> Model:
    """Get the model from context if available, otherwise create a new `Model`.

    This overload accepts a model ID string and allows additional params.
    """
    ...


@overload
def use_model(
    model: Model,
) -> Model:
    """Get the model from context if available, otherwise use the provided `Model`.

    This overload accepts a `Model` instance and does not allow additional params.
    """
    ...


def use_model(
    model: Model | ModelId,
    **params: Unpack[Params],
) -> Model:
    """Get the model from context if available, otherwise create a new `Model`.

    This function checks if a model has been set in the context (via `llm.model()`
    context manager). If a model is found in the context, it returns that model,
    ignoring any model ID or parameters passed to this function. Otherwise, it creates
    and returns a new `llm.Model` instance with the provided arguments.

    This allows you to write functions that work with a default model but can be
    overridden at runtime using the `llm.model()` context manager.

    Args:
        model: A model ID string (e.g., "openai/gpt-4") or a Model instance
        **params: Additional parameters to configure the model (e.g. temperature). See `llm.Params`.
            Only available when passing a model ID string

    Returns:
        An `llm.Model` instance from context (if set) or a new instance with the specified settings.

    Raises:
        ValueError: If the specified provider is not supported.

    Example:

        ```python
        import mirascope.llm as llm

        def recommend_book(genre: str) -> llm.Response:
            model = llm.use_model("openai/gpt-5-mini")
            message = llm.messages.user(f"Please recommend a book in {genre}.")
            return model.call(messages=[message])

        # Uses the default model (gpt-5-mini)
        response = recommend_book("fantasy")

        # Override with a different model
        with llm.model(provider="anthropic", model_id="anthropic/claude-sonnet-4-5"):
            response = recommend_book("fantasy")  # Uses Claude instead
        ```
    """
    context_model = model_from_context()
    if context_model is not None:
        return context_model
    if isinstance(model, str):
        return Model(model, **params)
    return model
