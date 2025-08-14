"""The base model interfaces for LLM models."""

from __future__ import annotations

from collections.abc import Sequence
from typing import TYPE_CHECKING, Generic, Literal, overload

from ..clients import ClientT, ParamsT, get_client
from ..context import Context
from ..messages import Message
from ..responses import AsyncStreamResponse, Response, StreamResponse
from ..tools import AsyncContextTool, AsyncTool, ContextTool, Tool

if TYPE_CHECKING:
    from ..clients import (
        AnthropicClient,
        AnthropicModel,
        AnthropicParams,
        GoogleClient,
        GoogleModel,
        GoogleParams,
        Model,
        OpenAIClient,
        OpenAIModel,
        OpenAIParams,
        Provider,
    )
from ..context import DepsT
from ..formatting import FormatT


class LLM(Generic[ClientT, ParamsT]):
    """The unified LLM interface that delegates to provider-specific clients.

    This class provides a consistent interface for interacting with language models
    from various providers. It handles the common operations like generating responses,
    streaming, and async variants by delegating to the appropriate client methods.
    """

    provider: Provider
    """The provider being used (e.g. `openai`)."""

    model: Model
    """The model being used (e.g. `gpt-4o-mini`)."""

    client: ClientT
    """The client object used to interact with the model API."""

    params: ParamsT | None
    """The default parameters for the model (temperature, max_tokens, etc.)."""

    @overload
    @classmethod
    def create(
        cls: type[LLM[AnthropicClient, AnthropicParams]],
        *,
        provider: Literal["anthropic"],
        model: AnthropicModel,
        client: AnthropicClient | None = None,
        params: AnthropicParams | None = None,
    ) -> LLM[AnthropicClient, AnthropicParams]:
        """Create an Anthropic LLM"""
        ...

    @overload
    @classmethod
    def create(
        cls: type[LLM[GoogleClient, GoogleParams]],
        *,
        provider: Literal["google"],
        model: GoogleModel,
        client: GoogleClient | None = None,
        params: GoogleParams | None = None,
    ) -> LLM[GoogleClient, GoogleParams]:
        """Create a Google LLM"""
        ...

    @overload
    @classmethod
    def create(
        cls: type[LLM[OpenAIClient, OpenAIParams]],
        *,
        provider: Literal["openai"],
        model: OpenAIModel,
        client: OpenAIClient | None = None,
        params: OpenAIParams | None = None,
    ) -> LLM[OpenAIClient, OpenAIParams]:
        """Create an OpenAI LLM"""
        ...

    @classmethod
    def create(
        cls: type[
            LLM[AnthropicClient, AnthropicParams]
            | LLM[GoogleClient, GoogleParams]
            | LLM[OpenAIClient, OpenAIParams]
        ],
        *,
        provider: Provider,
        model: Model,
        client: AnthropicClient | GoogleClient | OpenAIClient | None = None,
        params: AnthropicParams | GoogleParams | OpenAIParams | None = None,
    ) -> (
        LLM[AnthropicClient, AnthropicParams]
        | LLM[GoogleClient, GoogleParams]
        | LLM[OpenAIClient, OpenAIParams]
    ):
        instance = cls.__new__(cls)
        instance.provider = provider
        instance.model = model
        instance.client = client or get_client(provider)  # pyright: ignore[reportAttributeAccessIssue]
        instance.params = params
        return instance

    def __init__(self) -> None:
        """LLM is not created via `__init__`; use `LLM.create(...)` instead."""
        raise TypeError("Use `LLM.create(...)` instead")

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
        if format:
            return self.client.structured_call(
                model=self.model,
                messages=messages,
                tools=tools,
                format=format,
                params=self.params,
            )
        else:
            return self.client.call(
                model=self.model, messages=messages, tools=tools, params=self.params
            )

    @overload
    async def call_async(
        self,
        *,
        messages: Sequence[Message],
        tools: Sequence[AsyncTool] | None = None,
        format: None = None,
    ) -> Response: ...

    @overload
    async def call_async(
        self,
        *,
        messages: Sequence[Message],
        tools: Sequence[AsyncTool] | None = None,
        format: type[FormatT],
    ) -> Response[FormatT]: ...

    async def call_async(
        self,
        *,
        messages: Sequence[Message],
        tools: Sequence[AsyncTool] | None = None,
        format: type[FormatT] | None = None,
    ) -> Response | Response[FormatT]:
        """Generate a response asynchronously using the model."""
        if format:
            return await self.client.structured_call_async(
                model=self.model,
                messages=messages,
                tools=tools,
                format=format,
                params=self.params,
            )
        else:
            return await self.client.call_async(
                model=self.model, messages=messages, tools=tools, params=self.params
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

    def stream(
        self,
        *,
        messages: Sequence[Message],
        tools: Sequence[Tool] | None = None,
        format: type[FormatT] | None = None,
    ) -> StreamResponse | StreamResponse[FormatT]:
        """Stream a response using the model."""
        if format:
            return self.client.structured_stream(
                model=self.model,
                messages=messages,
                tools=tools,
                format=format,
                params=self.params,
            )
        else:
            return self.client.stream(
                model=self.model, messages=messages, tools=tools, params=self.params
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

    async def stream_async(
        self,
        *,
        messages: list[Message],
        tools: Sequence[AsyncTool] | None = None,
        format: type[FormatT] | None = None,
    ) -> AsyncStreamResponse | AsyncStreamResponse[FormatT]:
        """Stream a response asynchronously using the model."""
        if format:
            return await self.client.structured_stream_async(
                model=self.model,
                messages=messages,
                tools=tools,
                format=format,
                params=self.params,
            )
        else:
            return await self.client.stream_async(
                model=self.model, messages=messages, tools=tools, params=self.params
            )

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
