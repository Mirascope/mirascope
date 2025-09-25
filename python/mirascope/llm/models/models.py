"""The model context manager for the `llm` module."""

from __future__ import annotations

from collections.abc import Sequence
from contextvars import ContextVar, Token
from types import TracebackType
from typing import TYPE_CHECKING, Literal, overload
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
from ..tools import AsyncContextTool, AsyncTool, ContextTool, Tool

if TYPE_CHECKING:
    from ..clients import (
        AnthropicModelId,
        GoogleModelId,
        ModelId,
        OpenAIModelId,
        Params,
        Provider,
    )


MODEL_CONTEXT: ContextVar[Model | None] = ContextVar("MODEL_CONTEXT", default=None)


def get_model_from_context() -> Model | None:
    """Get the LLM currently set via context, if any."""
    return MODEL_CONTEXT.get()


class Model:
    """The unified LLM interface that delegates to provider-specific clients.

    NOTE: this class cannot be instantiated directly and must be created using the
    `llm.model` factory method.

    This class provides a consistent interface for interacting with language models
    from various providers. It handles the common operations like generating responses,
    streaming, and async variants by delegating to the appropriate client methods.

    This class can also operate as a context manager, which will set this LLM as the
    model in context for any call to a function decorated with `@llm.call`, which will
    first attempt to use a model set in the context, if any. If no model is set in the
    context, the default model will be used for that function.

    This is useful for overriding the default model at runtime.

    Example:

        ```python
        from mirascope import llm

        @llm.call(
            provider="openai",
            model_id="gpt-5",
        )
        def answer_question(question: str) -> str:
            return f"Answer this question: {question}"

        # Run the call with a different model from the default
        with llm.model(provider="anthropic", model_id="claude-4-sonnet"):
            response: llm.Response = answer_question("What is the capital of France?")
            print(response.content)
        ```
    """

    _token: Token[Model | None] | None = None
    """The token returned when setting the LLM context."""

    provider: Provider
    """The provider being used (e.g. `openai`)."""

    model_id: ModelId
    """The model being used (e.g. `gpt-4o-mini`)."""

    params: Params | None
    """The default parameters for the model (temperature, max_tokens, etc.)."""

    def __init__(
        self,
        provider: Provider,
        model_id: ModelId,
        params: Params | None = None,
    ) -> None:
        """Initialize the Model with provider, model_id, and optional params."""
        if provider not in PROVIDERS:
            raise ValueError(f"Unknown provider: {provider}")
        self.provider = provider
        self.model_id = model_id
        self.params = params

    def __enter__(self) -> Model:
        """Sets MODEL_CONTEXT with this LLM and stores the token."""
        self._token = MODEL_CONTEXT.set(self)
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        """Restores MODEL_CONTEXT to the token returned from the last setting."""
        if self._token is not None:
            MODEL_CONTEXT.reset(self._token)
            self._token = None

    @overload
    def call(
        self,
        *,
        messages: Sequence[Message],
        tools: Sequence[Tool] | None = None,
        format: None = None,
    ) -> Response: ...

    @overload
    def call(
        self,
        *,
        messages: Sequence[Message],
        tools: Sequence[Tool] | None = None,
        format: type[FormattableT] | Format[FormattableT],
    ) -> Response[FormattableT]: ...

    @overload
    def call(
        self,
        *,
        messages: Sequence[Message],
        tools: Sequence[Tool] | None = None,
        format: type[FormattableT] | Format[FormattableT] | None,
    ) -> Response | Response[FormattableT]: ...

    def call(
        self,
        *,
        messages: Sequence[Message],
        tools: Sequence[Tool] | None = None,
        format: type[FormattableT] | Format[FormattableT] | None = None,
    ) -> Response | Response[FormattableT]:
        """Generate a response using the model."""
        return get_client(self.provider).call(
            model_id=self.model_id,
            messages=messages,
            tools=tools,
            format=format,
            params=self.params,
        )

    @overload
    async def call_async(
        self,
        *,
        messages: Sequence[Message],
        tools: Sequence[AsyncTool] | None = None,
        format: None = None,
    ) -> AsyncResponse: ...

    @overload
    async def call_async(
        self,
        *,
        messages: Sequence[Message],
        tools: Sequence[AsyncTool] | None = None,
        format: type[FormattableT] | Format[FormattableT],
    ) -> AsyncResponse[FormattableT]: ...

    @overload
    async def call_async(
        self,
        *,
        messages: Sequence[Message],
        tools: Sequence[AsyncTool] | None = None,
        format: type[FormattableT] | Format[FormattableT] | None,
    ) -> AsyncResponse | AsyncResponse[FormattableT]: ...

    async def call_async(
        self,
        *,
        messages: Sequence[Message],
        tools: Sequence[AsyncTool] | None = None,
        format: type[FormattableT] | Format[FormattableT] | None = None,
    ) -> AsyncResponse | AsyncResponse[FormattableT]:
        """Generate a response asynchronously using the model."""
        return await get_client(self.provider).call_async(
            model_id=self.model_id,
            messages=messages,
            tools=tools,
            params=self.params,
            format=format,
        )

    @overload
    def stream(
        self,
        *,
        messages: Sequence[Message],
        tools: Sequence[Tool] | None = None,
        format: None = None,
    ) -> StreamResponse: ...

    @overload
    def stream(
        self,
        *,
        messages: Sequence[Message],
        tools: Sequence[Tool] | None = None,
        format: type[FormattableT] | Format[FormattableT],
    ) -> StreamResponse[FormattableT]: ...

    @overload
    def stream(
        self,
        *,
        messages: Sequence[Message],
        tools: Sequence[Tool] | None = None,
        format: type[FormattableT] | Format[FormattableT] | None,
    ) -> StreamResponse | StreamResponse[FormattableT]: ...

    def stream(
        self,
        *,
        messages: Sequence[Message],
        tools: Sequence[Tool] | None = None,
        format: type[FormattableT] | Format[FormattableT] | None = None,
    ) -> StreamResponse | StreamResponse[FormattableT]:
        """Stream a response using the model."""
        return get_client(self.provider).stream(
            model_id=self.model_id,
            messages=messages,
            tools=tools,
            format=format,
            params=self.params,
        )

    @overload
    async def stream_async(
        self,
        *,
        messages: list[Message],
        tools: Sequence[AsyncTool] | None = None,
        format: None = None,
    ) -> AsyncStreamResponse: ...

    @overload
    async def stream_async(
        self,
        *,
        messages: list[Message],
        tools: Sequence[AsyncTool] | None = None,
        format: type[FormattableT] | Format[FormattableT],
    ) -> AsyncStreamResponse[FormattableT]: ...

    @overload
    async def stream_async(
        self,
        *,
        messages: list[Message],
        tools: Sequence[AsyncTool] | None = None,
        format: type[FormattableT] | Format[FormattableT] | None,
    ) -> AsyncStreamResponse | AsyncStreamResponse[FormattableT]: ...

    async def stream_async(
        self,
        *,
        messages: list[Message],
        tools: Sequence[AsyncTool] | None = None,
        format: type[FormattableT] | Format[FormattableT] | None = None,
    ) -> AsyncStreamResponse | AsyncStreamResponse[FormattableT]:
        """Stream a response asynchronously using the model."""
        return await get_client(self.provider).stream_async(
            model_id=self.model_id,
            messages=messages,
            tools=tools,
            format=format,
            params=self.params,
        )

    @overload
    def context_call(
        self,
        *,
        ctx: Context[DepsT],
        messages: Sequence[Message],
        tools: Sequence[Tool | ContextTool[DepsT]] | None = None,
        format: None = None,
    ) -> ContextResponse[DepsT, None]: ...

    @overload
    def context_call(
        self,
        *,
        ctx: Context[DepsT],
        messages: Sequence[Message],
        tools: Sequence[Tool | ContextTool[DepsT]] | None = None,
        format: type[FormattableT] | Format[FormattableT],
    ) -> ContextResponse[DepsT, FormattableT]: ...

    @overload
    def context_call(
        self,
        *,
        ctx: Context[DepsT],
        messages: Sequence[Message],
        tools: Sequence[Tool | ContextTool[DepsT]] | None = None,
        format: type[FormattableT] | Format[FormattableT] | None,
    ) -> ContextResponse[DepsT, None] | ContextResponse[DepsT, FormattableT]: ...

    def context_call(
        self,
        *,
        ctx: Context[DepsT],
        messages: Sequence[Message],
        tools: Sequence[Tool | ContextTool[DepsT]] | None = None,
        format: type[FormattableT] | Format[FormattableT] | None = None,
    ) -> ContextResponse[DepsT, None] | ContextResponse[DepsT, FormattableT]:
        """Generate a response using the model."""
        return get_client(self.provider).context_call(
            ctx=ctx,
            model_id=self.model_id,
            messages=messages,
            tools=tools,
            format=format,
            params=self.params,
        )

    @overload
    async def context_call_async(
        self,
        *,
        ctx: Context[DepsT],
        messages: Sequence[Message],
        tools: Sequence[AsyncTool | AsyncContextTool[DepsT]] | None = None,
        format: None = None,
    ) -> AsyncContextResponse[DepsT, None]: ...

    @overload
    async def context_call_async(
        self,
        *,
        ctx: Context[DepsT],
        messages: Sequence[Message],
        tools: Sequence[AsyncTool | AsyncContextTool[DepsT]] | None = None,
        format: type[FormattableT] | Format[FormattableT],
    ) -> AsyncContextResponse[DepsT, FormattableT]: ...

    @overload
    async def context_call_async(
        self,
        *,
        ctx: Context[DepsT],
        messages: Sequence[Message],
        tools: Sequence[AsyncTool | AsyncContextTool[DepsT]] | None = None,
        format: type[FormattableT] | Format[FormattableT] | None,
    ) -> (
        AsyncContextResponse[DepsT, None] | AsyncContextResponse[DepsT, FormattableT]
    ): ...

    async def context_call_async(
        self,
        *,
        ctx: Context[DepsT],
        messages: Sequence[Message],
        tools: Sequence[AsyncTool | AsyncContextTool[DepsT]] | None = None,
        format: type[FormattableT] | Format[FormattableT] | None = None,
    ) -> AsyncContextResponse[DepsT, None] | AsyncContextResponse[DepsT, FormattableT]:
        """Generate a response asynchronously using the model."""
        return await get_client(self.provider).context_call_async(
            ctx=ctx,
            model_id=self.model_id,
            messages=messages,
            tools=tools,
            format=format,
            params=self.params,
        )

    @overload
    def context_stream(
        self,
        *,
        ctx: Context[DepsT],
        messages: Sequence[Message],
        tools: Sequence[Tool | ContextTool[DepsT]] | None = None,
        format: None = None,
    ) -> ContextStreamResponse[DepsT, None]: ...

    @overload
    def context_stream(
        self,
        *,
        ctx: Context[DepsT],
        messages: Sequence[Message],
        tools: Sequence[Tool | ContextTool[DepsT]] | None = None,
        format: type[FormattableT] | Format[FormattableT],
    ) -> ContextStreamResponse[DepsT, FormattableT]: ...

    @overload
    def context_stream(
        self,
        *,
        ctx: Context[DepsT],
        messages: Sequence[Message],
        tools: Sequence[Tool | ContextTool[DepsT]] | None = None,
        format: type[FormattableT] | Format[FormattableT] | None,
    ) -> (
        ContextStreamResponse[DepsT, None] | ContextStreamResponse[DepsT, FormattableT]
    ): ...

    def context_stream(
        self,
        *,
        ctx: Context[DepsT],
        messages: Sequence[Message],
        tools: Sequence[Tool | ContextTool[DepsT]] | None = None,
        format: type[FormattableT] | Format[FormattableT] | None = None,
    ) -> (
        ContextStreamResponse[DepsT, None] | ContextStreamResponse[DepsT, FormattableT]
    ):
        """Stream a response using the model."""
        return get_client(self.provider).context_stream(
            ctx=ctx,
            model_id=self.model_id,
            messages=messages,
            tools=tools,
            format=format,
            params=self.params,
        )

    @overload
    async def context_stream_async(
        self,
        *,
        ctx: Context[DepsT],
        messages: list[Message],
        tools: Sequence[AsyncTool | AsyncContextTool[DepsT]] | None = None,
        format: None = None,
    ) -> AsyncContextStreamResponse[DepsT, None]: ...

    @overload
    async def context_stream_async(
        self,
        *,
        ctx: Context[DepsT],
        messages: list[Message],
        tools: Sequence[AsyncTool | AsyncContextTool[DepsT]] | None = None,
        format: type[FormattableT] | Format[FormattableT],
    ) -> AsyncContextStreamResponse[DepsT, FormattableT]: ...

    @overload
    async def context_stream_async(
        self,
        *,
        ctx: Context[DepsT],
        messages: list[Message],
        tools: Sequence[AsyncTool | AsyncContextTool[DepsT]] | None = None,
        format: type[FormattableT] | Format[FormattableT] | None,
    ) -> (
        AsyncContextStreamResponse[DepsT, None]
        | AsyncContextStreamResponse[DepsT, FormattableT]
    ): ...

    async def context_stream_async(
        self,
        *,
        ctx: Context[DepsT],
        messages: list[Message],
        tools: Sequence[AsyncTool | AsyncContextTool[DepsT]] | None = None,
        format: type[FormattableT] | Format[FormattableT] | None = None,
    ) -> (
        AsyncContextStreamResponse[DepsT, None]
        | AsyncContextStreamResponse[DepsT, FormattableT]
    ):
        """Stream a response asynchronously using the model."""
        return await get_client(self.provider).context_stream_async(
            ctx=ctx,
            model_id=self.model_id,
            messages=messages,
            tools=tools,
            format=format,
            params=self.params,
        )

    @overload
    def resume(
        self,
        *,
        response: Response,
        content: UserContent,
    ) -> Response: ...

    @overload
    def resume(
        self,
        *,
        response: Response[FormattableT],
        content: UserContent,
    ) -> Response[FormattableT]: ...

    @overload
    def resume(
        self,
        *,
        response: Response | Response[FormattableT],
        content: UserContent,
    ) -> Response | Response[FormattableT]: ...

    def resume(
        self,
        *,
        response: Response | Response[FormattableT],
        content: UserContent,
    ) -> Response | Response[FormattableT]:
        """Generate a new `Response` by extending another `Response`'s messages with additional user content.

        Uses the other response's tools and output format.
        """
        return get_client(self.provider).resume(
            model_id=self.model_id,
            response=response,
            content=content,
            params=self.params,
        )

    @overload
    async def resume_async(
        self,
        *,
        response: AsyncResponse,
        content: UserContent,
    ) -> AsyncResponse: ...

    @overload
    async def resume_async(
        self,
        *,
        response: AsyncResponse[FormattableT],
        content: UserContent,
    ) -> AsyncResponse[FormattableT]: ...

    @overload
    async def resume_async(
        self,
        *,
        response: AsyncResponse | AsyncResponse[FormattableT],
        content: UserContent,
    ) -> AsyncResponse | AsyncResponse[FormattableT]: ...

    async def resume_async(
        self,
        *,
        response: AsyncResponse | AsyncResponse[FormattableT],
        content: UserContent,
    ) -> AsyncResponse | AsyncResponse[FormattableT]:
        """Generate a new `AsyncResponse` by extending another `AsyncResponse`'s messages with additional user content.

        Uses the other response's tools and output format.
        """
        return await get_client(self.provider).resume_async(
            model_id=self.model_id,
            response=response,
            content=content,
            params=self.params,
        )

    @overload
    def context_resume(
        self,
        *,
        ctx: Context[DepsT],
        response: ContextResponse[DepsT, None],
        content: UserContent,
    ) -> ContextResponse[DepsT, None]: ...

    @overload
    def context_resume(
        self,
        *,
        ctx: Context[DepsT],
        response: ContextResponse[DepsT, FormattableT],
        content: UserContent,
    ) -> ContextResponse[DepsT, FormattableT]: ...

    @overload
    def context_resume(
        self,
        *,
        ctx: Context[DepsT],
        response: ContextResponse[DepsT, None] | ContextResponse[DepsT, FormattableT],
        content: UserContent,
    ) -> ContextResponse[DepsT, None] | ContextResponse[DepsT, FormattableT]: ...

    def context_resume(
        self,
        *,
        ctx: Context[DepsT],
        response: ContextResponse[DepsT, None] | ContextResponse[DepsT, FormattableT],
        content: UserContent,
    ) -> ContextResponse[DepsT, None] | ContextResponse[DepsT, FormattableT]:
        """Generate a new `ContextResponse` by extending another `ContextResponse`'s messages with additional user content.

        Uses the other response's tools and output format.
        """
        return get_client(self.provider).context_resume(
            ctx=ctx,
            model_id=self.model_id,
            response=response,
            content=content,
            params=self.params,
        )

    @overload
    async def context_resume_async(
        self,
        *,
        ctx: Context[DepsT],
        response: AsyncContextResponse[DepsT, None],
        content: UserContent,
    ) -> AsyncContextResponse[DepsT, None]: ...

    @overload
    async def context_resume_async(
        self,
        *,
        ctx: Context[DepsT],
        response: AsyncContextResponse[DepsT, FormattableT],
        content: UserContent,
    ) -> AsyncContextResponse[DepsT, FormattableT]: ...

    @overload
    async def context_resume_async(
        self,
        *,
        ctx: Context[DepsT],
        response: AsyncContextResponse[DepsT, None]
        | AsyncContextResponse[DepsT, FormattableT],
        content: UserContent,
    ) -> (
        AsyncContextResponse[DepsT, None] | AsyncContextResponse[DepsT, FormattableT]
    ): ...

    async def context_resume_async(
        self,
        *,
        ctx: Context[DepsT],
        response: AsyncContextResponse[DepsT, None]
        | AsyncContextResponse[DepsT, FormattableT],
        content: UserContent,
    ) -> AsyncContextResponse[DepsT, None] | AsyncContextResponse[DepsT, FormattableT]:
        """Generate a new `AsyncContextResponse` by extending another `AsyncContextResponse`'s messages with additional user content.

        Uses the other response's tools and output format.
        """
        return await get_client(self.provider).context_resume_async(
            ctx=ctx,
            model_id=self.model_id,
            response=response,
            content=content,
            params=self.params,
        )

    @overload
    def resume_stream(
        self,
        *,
        response: StreamResponse,
        content: UserContent,
    ) -> StreamResponse: ...

    @overload
    def resume_stream(
        self,
        *,
        response: StreamResponse[FormattableT],
        content: UserContent,
    ) -> StreamResponse[FormattableT]: ...

    @overload
    def resume_stream(
        self,
        *,
        response: StreamResponse | StreamResponse[FormattableT],
        content: UserContent,
    ) -> StreamResponse | StreamResponse[FormattableT]: ...

    def resume_stream(
        self,
        *,
        response: StreamResponse | StreamResponse[FormattableT],
        content: UserContent,
    ) -> StreamResponse | StreamResponse[FormattableT]:
        """Generate a new `StreamResponse` by extending another `StreamResponse`'s messages with additional user content.

        Uses the other response's tools and output format.
        """
        return get_client(self.provider).resume_stream(
            model_id=self.model_id,
            response=response,
            content=content,
            params=self.params,
        )

    @overload
    async def resume_stream_async(
        self,
        *,
        response: AsyncStreamResponse,
        content: UserContent,
    ) -> AsyncStreamResponse: ...

    @overload
    async def resume_stream_async(
        self,
        *,
        response: AsyncStreamResponse[FormattableT],
        content: UserContent,
    ) -> AsyncStreamResponse[FormattableT]: ...

    @overload
    async def resume_stream_async(
        self,
        *,
        response: AsyncStreamResponse | AsyncStreamResponse[FormattableT],
        content: UserContent,
    ) -> AsyncStreamResponse | AsyncStreamResponse[FormattableT]: ...

    async def resume_stream_async(
        self,
        *,
        response: AsyncStreamResponse | AsyncStreamResponse[FormattableT],
        content: UserContent,
    ) -> AsyncStreamResponse | AsyncStreamResponse[FormattableT]:
        """Generate a new `AsyncStreamResponse` by extending another `AsyncStreamResponse`'s messages with additional user content.

        Uses the other response's tools and output format.
        """
        return await get_client(self.provider).resume_stream_async(
            model_id=self.model_id,
            response=response,
            content=content,
            params=self.params,
        )

    @overload
    def context_resume_stream(
        self,
        *,
        ctx: Context[DepsT],
        response: ContextStreamResponse[DepsT, None],
        content: UserContent,
    ) -> ContextStreamResponse[DepsT, None]: ...

    @overload
    def context_resume_stream(
        self,
        *,
        ctx: Context[DepsT],
        response: ContextStreamResponse[DepsT, FormattableT],
        content: UserContent,
    ) -> ContextStreamResponse[DepsT, FormattableT]: ...

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
    ): ...

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
        """Generate a new `ContextStreamResponse` by extending another `ContextStreamResponse`'s messages with additional user content.

        Uses the other response's tools and output format.
        """
        return get_client(self.provider).context_resume_stream(
            ctx=ctx,
            model_id=self.model_id,
            response=response,
            content=content,
            params=self.params,
        )

    @overload
    async def context_resume_stream_async(
        self,
        *,
        ctx: Context[DepsT],
        response: AsyncContextStreamResponse[DepsT, None],
        content: UserContent,
    ) -> AsyncContextStreamResponse[DepsT, None]: ...

    @overload
    async def context_resume_stream_async(
        self,
        *,
        ctx: Context[DepsT],
        response: AsyncContextStreamResponse[DepsT, FormattableT],
        content: UserContent,
    ) -> AsyncContextStreamResponse[DepsT, FormattableT]: ...

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
    ): ...

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
        """Generate a new `AsyncContextStreamResponse` by extending another `AsyncContextStreamResponse`'s messages with additional user content.

        Uses the other response's tools and output format.
        """
        return await get_client(self.provider).context_resume_stream_async(
            ctx=ctx,
            model_id=self.model_id,
            response=response,
            content=content,
            params=self.params,
        )


@overload
def model(
    *,
    provider: Literal["anthropic"],
    model_id: AnthropicModelId,
    **params: Unpack[Params],
) -> Model:
    """Overload for Anthropic models."""
    ...


@overload
def model(
    *,
    provider: Literal["google"],
    model_id: GoogleModelId,
    **params: Unpack[Params],
) -> Model:
    """Overload for Google models."""
    ...


@overload
def model(
    *,
    provider: Literal["openai"],
    model_id: OpenAIModelId,
    **params: Unpack[Params],
) -> Model:
    """Overload for OpenAI models."""
    ...


@overload
def model(
    *,
    provider: Provider,
    model_id: ModelId,
    **params: Unpack[Params],
) -> Model:
    """Cross-provider overload."""
    ...


def model(
    *,
    provider: Provider,
    model_id: ModelId,
    **params: Unpack[Params],
) -> Model:
    """Returns an `LLM` instance with the given settings."""
    return Model(provider, model_id, params)
