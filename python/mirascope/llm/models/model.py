"""The model context manager for the `llm` module."""

from __future__ import annotations

from collections.abc import Sequence
from contextvars import ContextVar, Token
from types import TracebackType
from typing import TYPE_CHECKING, Generic, Literal, overload
from typing_extensions import Unpack

from ..clients import ClientT, ParamsT, get_client
from ..context import Context, DepsT
from ..formatting import FormatT
from ..messages import Message
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
        AnthropicClient,
        AnthropicModelId,
        AnthropicParams,
        BaseParams,
        GoogleClient,
        GoogleModelId,
        GoogleParams,
        ModelId,
        OpenAIClient,
        OpenAIModelId,
        OpenAIParams,
        Provider,
    )


MODEL_CONTEXT: ContextVar[Model | None] = ContextVar("MODEL_CONTEXT", default=None)


def get_model_from_context() -> Model | None:
    """Get the LLM currently set via context, if any."""
    return MODEL_CONTEXT.get()


class Model(Generic[ClientT, ParamsT]):
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

    client: ClientT
    """The client object used to interact with the model API."""

    params: ParamsT | None
    """The default parameters for the model (temperature, max_tokens, etc.)."""

    def __init__(self) -> None:
        """LLM is not created via `__init__`; use `llm.model(...)` instead."""
        raise TypeError("Use `llm.model(...)` instead")

    def __enter__(self) -> Model[ClientT, ParamsT]:
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
        format: type[FormatT],
    ) -> Response[FormatT]: ...

    @overload
    def call(
        self,
        *,
        messages: Sequence[Message],
        tools: Sequence[Tool] | None = None,
        format: type[FormatT] | None,
    ) -> Response | Response[FormatT]: ...

    def call(
        self,
        *,
        messages: Sequence[Message],
        tools: Sequence[Tool] | None = None,
        format: type[FormatT] | None = None,
    ) -> Response | Response[FormatT]:
        """Generate a response using the model."""
        return self.client.call(
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
        format: type[FormatT],
    ) -> AsyncResponse[FormatT]: ...

    @overload
    async def call_async(
        self,
        *,
        messages: Sequence[Message],
        tools: Sequence[AsyncTool] | None = None,
        format: type[FormatT] | None,
    ) -> AsyncResponse | AsyncResponse[FormatT]: ...

    async def call_async(
        self,
        *,
        messages: Sequence[Message],
        tools: Sequence[AsyncTool] | None = None,
        format: type[FormatT] | None = None,
    ) -> AsyncResponse | AsyncResponse[FormatT]:
        """Generate a response asynchronously using the model."""
        return await self.client.call_async(
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
        format: type[FormatT],
    ) -> StreamResponse[FormatT]: ...

    @overload
    def stream(
        self,
        *,
        messages: Sequence[Message],
        tools: Sequence[Tool] | None = None,
        format: type[FormatT] | None,
    ) -> StreamResponse | StreamResponse[FormatT]: ...

    def stream(
        self,
        *,
        messages: Sequence[Message],
        tools: Sequence[Tool] | None = None,
        format: type[FormatT] | None = None,
    ) -> StreamResponse | StreamResponse[FormatT]:
        """Stream a response using the model."""
        return self.client.stream(
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
        format: type[FormatT],
    ) -> AsyncStreamResponse[FormatT]: ...

    @overload
    async def stream_async(
        self,
        *,
        messages: list[Message],
        tools: Sequence[AsyncTool] | None = None,
        format: type[FormatT] | None,
    ) -> AsyncStreamResponse | AsyncStreamResponse[FormatT]: ...

    async def stream_async(
        self,
        *,
        messages: list[Message],
        tools: Sequence[AsyncTool] | None = None,
        format: type[FormatT] | None = None,
    ) -> AsyncStreamResponse | AsyncStreamResponse[FormatT]:
        """Stream a response asynchronously using the model."""
        return await self.client.stream_async(
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
        format: type[FormatT],
    ) -> ContextResponse[DepsT, FormatT]: ...

    @overload
    def context_call(
        self,
        *,
        ctx: Context[DepsT],
        messages: Sequence[Message],
        tools: Sequence[Tool | ContextTool[DepsT]] | None = None,
        format: type[FormatT] | None,
    ) -> ContextResponse[DepsT, None] | ContextResponse[DepsT, FormatT]: ...

    def context_call(
        self,
        *,
        ctx: Context[DepsT],
        messages: Sequence[Message],
        tools: Sequence[Tool | ContextTool[DepsT]] | None = None,
        format: type[FormatT] | None = None,
    ) -> ContextResponse[DepsT, None] | ContextResponse[DepsT, FormatT]:
        """Generate a response using the model."""
        return self.client.context_call(
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
        format: type[FormatT],
    ) -> AsyncContextResponse[DepsT, FormatT]: ...

    @overload
    async def context_call_async(
        self,
        *,
        ctx: Context[DepsT],
        messages: Sequence[Message],
        tools: Sequence[AsyncTool | AsyncContextTool[DepsT]] | None = None,
        format: type[FormatT] | None,
    ) -> AsyncContextResponse[DepsT, None] | AsyncContextResponse[DepsT, FormatT]: ...

    async def context_call_async(
        self,
        *,
        ctx: Context[DepsT],
        messages: Sequence[Message],
        tools: Sequence[AsyncTool | AsyncContextTool[DepsT]] | None = None,
        format: type[FormatT] | None = None,
    ) -> AsyncContextResponse[DepsT, None] | AsyncContextResponse[DepsT, FormatT]:
        """Generate a response asynchronously using the model."""
        return await self.client.context_call_async(
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
        format: type[FormatT],
    ) -> ContextStreamResponse[DepsT, FormatT]: ...

    @overload
    def context_stream(
        self,
        *,
        ctx: Context[DepsT],
        messages: Sequence[Message],
        tools: Sequence[Tool | ContextTool[DepsT]] | None = None,
        format: type[FormatT] | None,
    ) -> ContextStreamResponse[DepsT, None] | ContextStreamResponse[DepsT, FormatT]: ...

    def context_stream(
        self,
        *,
        ctx: Context[DepsT],
        messages: Sequence[Message],
        tools: Sequence[Tool | ContextTool[DepsT]] | None = None,
        format: type[FormatT] | None = None,
    ) -> ContextStreamResponse[DepsT, None] | ContextStreamResponse[DepsT, FormatT]:
        """Stream a response using the model."""
        return self.client.context_stream(
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
        format: type[FormatT],
    ) -> AsyncContextStreamResponse[DepsT, FormatT]: ...

    @overload
    async def context_stream_async(
        self,
        *,
        ctx: Context[DepsT],
        messages: list[Message],
        tools: Sequence[AsyncTool | AsyncContextTool[DepsT]] | None = None,
        format: type[FormatT] | None,
    ) -> (
        AsyncContextStreamResponse[DepsT, None]
        | AsyncContextStreamResponse[DepsT, FormatT]
    ): ...

    async def context_stream_async(
        self,
        *,
        ctx: Context[DepsT],
        messages: list[Message],
        tools: Sequence[AsyncTool | AsyncContextTool[DepsT]] | None = None,
        format: type[FormatT] | None = None,
    ) -> (
        AsyncContextStreamResponse[DepsT, None]
        | AsyncContextStreamResponse[DepsT, FormatT]
    ):
        """Stream a response asynchronously using the model."""
        return await self.client.context_stream_async(
            ctx=ctx,
            model_id=self.model_id,
            messages=messages,
            tools=tools,
            format=format,
            params=self.params,
        )


@overload
def model(
    *,
    provider: Literal["anthropic"],
    model_id: AnthropicModelId,
    client: AnthropicClient | None = None,
    **params: Unpack[AnthropicParams],
) -> Model[AnthropicClient, AnthropicParams]:
    """Overload for Anthropic models."""
    ...


@overload
def model(
    *,
    provider: Literal["google"],
    model_id: GoogleModelId,
    client: GoogleClient | None = None,
    **params: Unpack[GoogleParams],
) -> Model[GoogleClient, GoogleParams]:
    """Overload for Google models."""
    ...


@overload
def model(
    *,
    provider: Literal["openai"],
    model_id: OpenAIModelId,
    client: OpenAIClient | None = None,
    **params: Unpack[OpenAIParams],
) -> Model[OpenAIClient, OpenAIParams]:
    """Overload for OpenAI models."""
    ...


def model(
    *,
    provider: Provider,
    model_id: ModelId,
    client: AnthropicClient | GoogleClient | OpenAIClient | None = None,
    **params: Unpack[BaseParams],
) -> (
    Model[AnthropicClient, AnthropicParams]
    | Model[GoogleClient, GoogleParams]
    | Model[OpenAIClient, OpenAIParams]
):
    """Returns an `LLM` instance with the given settings."""
    llm = Model.__new__(Model)
    llm.provider = provider
    llm.model_id = model_id
    llm.client = client or get_client(provider)
    llm.params = params
    return llm
