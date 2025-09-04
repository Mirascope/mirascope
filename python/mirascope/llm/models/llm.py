"""The base model interfaces for LLM models."""

from __future__ import annotations

from collections.abc import Sequence
from contextvars import ContextVar, Token
from types import TracebackType
from typing import TYPE_CHECKING, Generic, overload

from ..clients import ClientT, ParamsT
from ..context import Context
from ..messages import Message
from ..responses import AsyncResponse, AsyncStreamResponse, Response, StreamResponse
from ..tools import AsyncContextTool, AsyncTool, ContextTool, Tool

if TYPE_CHECKING:
    from ..clients import Model, Provider

from ..context import DepsT
from ..formatting import FormatT

LLM_CONTEXT: ContextVar[LLM | None] = ContextVar("LLM_CONTEXT", default=None)


def get_model_from_context() -> LLM | None:
    """Get the LLM currently set via context, if any."""
    return LLM_CONTEXT.get()


class LLM(Generic[ClientT, ParamsT]):
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
            model="gpt-5",
        )
        def answer_question(question: str) -> str:
            return f"Answer this question: {question}"

        # Run the call with a different model from the default
        with llm.model(provider="anthropic", model="claude-4-sonnet"):
            response: llm.Response = answer_question("What is the capital of France?")
            print(response.content)
        ```
    """

    _token: Token[LLM | None] | None = None
    """The token returned when setting the LLM context."""

    provider: Provider
    """The provider being used (e.g. `openai`)."""

    model: Model
    """The model being used (e.g. `gpt-4o-mini`)."""

    client: ClientT
    """The client object used to interact with the model API."""

    params: ParamsT | None
    """The default parameters for the model (temperature, max_tokens, etc.)."""

    def __init__(self) -> None:
        """LLM is not created via `__init__`; use `llm.model(...)` instead."""
        raise TypeError("Use `llm.model(...)` instead")

    def __enter__(self) -> LLM[ClientT, ParamsT]:
        """Sets LLM_CONTEXT with this LLM and stores the token."""
        self._token = LLM_CONTEXT.set(self)
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        """Restores LLM_CONTEXT to the token returned from the last setting."""
        if self._token is not None:
            LLM_CONTEXT.reset(self._token)
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

    def call(
        self,
        *,
        messages: Sequence[Message],
        tools: Sequence[Tool] | None = None,
        format: type[FormatT] | None = None,
    ) -> Response | Response[FormatT]:
        """Generate a response using the model."""
        kwargs = {
            "model": self.model,
            "messages": messages,
            "tools": tools,
            "params": self.params,
        }
        if format is not None:
            kwargs["format"] = format
        return self.client.call(**kwargs)

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

    async def call_async(
        self,
        *,
        messages: Sequence[Message],
        tools: Sequence[AsyncTool] | None = None,
        format: type[FormatT] | None = None,
    ) -> AsyncResponse | AsyncResponse[FormatT]:
        """Generate a response asynchronously using the model."""
        kwargs = {
            "model": self.model,
            "messages": messages,
            "tools": tools,
            "params": self.params,
        }
        if format is not None:
            kwargs["format"] = format
        return await self.client.call_async(**kwargs)

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

    def stream(
        self,
        *,
        messages: Sequence[Message],
        tools: Sequence[Tool] | None = None,
        format: type[FormatT] | None = None,
    ) -> StreamResponse | StreamResponse[FormatT]:
        """Stream a response using the model."""
        kwargs = {
            "model": self.model,
            "messages": messages,
            "tools": tools,
            "params": self.params,
        }
        if format is not None:
            kwargs["format"] = format
        return self.client.stream(**kwargs)

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

    async def stream_async(
        self,
        *,
        messages: list[Message],
        tools: Sequence[AsyncTool] | None = None,
        format: type[FormatT] | None = None,
    ) -> AsyncStreamResponse | AsyncStreamResponse[FormatT]:
        """Stream a response asynchronously using the model."""
        kwargs = {
            "model": self.model,
            "messages": messages,
            "tools": tools,
            "params": self.params,
        }
        if format is not None:
            kwargs["format"] = format
        return await self.client.stream_async(**kwargs)

    @overload
    def context_call(
        self,
        *,
        ctx: Context[DepsT],
        messages: Sequence[Message],
        tools: Sequence[Tool | ContextTool[DepsT]] | None = None,
        format: None = None,
    ) -> Response: ...

    @overload
    def context_call(
        self,
        *,
        ctx: Context[DepsT],
        messages: Sequence[Message],
        tools: Sequence[Tool | ContextTool[DepsT]] | None = None,
        format: type[FormatT],
    ) -> Response[FormatT]: ...

    def context_call(
        self,
        *,
        ctx: Context[DepsT],
        messages: Sequence[Message],
        tools: Sequence[Tool | ContextTool[DepsT]] | None = None,
        format: type[FormatT] | None = None,
    ) -> Response | Response[FormatT]:
        """Generate a response using the model."""
        raise NotImplementedError()

    @overload
    async def context_call_async(
        self,
        *,
        ctx: Context[DepsT],
        messages: Sequence[Message],
        tools: Sequence[AsyncTool | AsyncContextTool[DepsT]] | None = None,
        format: None = None,
    ) -> Response: ...

    @overload
    async def context_call_async(
        self,
        *,
        ctx: Context[DepsT],
        messages: Sequence[Message],
        tools: Sequence[AsyncTool | AsyncContextTool[DepsT]] | None = None,
        format: type[FormatT],
    ) -> Response[FormatT]: ...

    async def context_call_async(
        self,
        *,
        ctx: Context[DepsT],
        messages: Sequence[Message],
        tools: Sequence[AsyncTool | AsyncContextTool[DepsT]] | None = None,
        format: type[FormatT] | None = None,
    ) -> Response | Response[FormatT]:
        """Generate a response asynchronously using the model."""
        raise NotImplementedError()

    @overload
    def context_stream(
        self,
        *,
        ctx: Context[DepsT],
        messages: Sequence[Message],
        tools: Sequence[Tool | ContextTool[DepsT]] | None = None,
        format: None = None,
    ) -> StreamResponse: ...

    @overload
    def context_stream(
        self,
        *,
        ctx: Context[DepsT],
        messages: Sequence[Message],
        tools: Sequence[Tool | ContextTool[DepsT]] | None = None,
        format: type[FormatT],
    ) -> StreamResponse[FormatT]: ...

    def context_stream(
        self,
        *,
        ctx: Context[DepsT],
        messages: Sequence[Message],
        tools: Sequence[Tool | ContextTool[DepsT]] | None = None,
        format: type[FormatT] | None = None,
    ) -> StreamResponse | StreamResponse[FormatT]:
        """Stream a response using the model."""
        raise NotImplementedError()

    @overload
    async def context_stream_async(
        self,
        *,
        ctx: Context[DepsT],
        messages: list[Message],
        tools: Sequence[AsyncTool | AsyncContextTool[DepsT]] | None = None,
        format: None = None,
    ) -> AsyncStreamResponse: ...

    @overload
    async def context_stream_async(
        self,
        *,
        ctx: Context[DepsT],
        messages: list[Message],
        tools: Sequence[AsyncTool | AsyncContextTool[DepsT]] | None = None,
        format: type[FormatT],
    ) -> AsyncStreamResponse[FormatT]: ...

    async def context_stream_async(
        self,
        *,
        ctx: Context[DepsT],
        messages: list[Message],
        tools: Sequence[AsyncTool | AsyncContextTool[DepsT]] | None = None,
        format: type[FormatT] | None = None,
    ) -> AsyncStreamResponse | AsyncStreamResponse[FormatT]:
        """Stream a response asynchronously using the model."""
        raise NotImplementedError()
