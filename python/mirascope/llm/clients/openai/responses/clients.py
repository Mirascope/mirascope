"""OpenAI Responses API client implementation."""

import os
from collections.abc import Sequence
from contextvars import ContextVar
from functools import lru_cache
from typing import overload
from typing_extensions import Unpack

from openai import AsyncOpenAI, OpenAI

from ....context import Context, DepsT
from ....formatting import Format, FormattableT
from ....messages import Message
from ....responses import (
    AsyncContextResponse,
    AsyncContextStreamResponse,
    AsyncResponse,
    AsyncStreamResponse,
    ContextResponse,
    ContextStreamResponse,
    Response,
    StreamResponse,
)
from ....tools import (
    AsyncContextTool,
    AsyncContextToolkit,
    AsyncTool,
    AsyncToolkit,
    ContextTool,
    ContextToolkit,
    Tool,
    Toolkit,
)
from ...base import BaseClient, Params
from . import _utils
from .model_ids import OpenAIResponsesModelId

OPENAI_RESPONSES_CLIENT_CONTEXT: ContextVar["OpenAIResponsesClient"] = ContextVar(
    "OPENAI_RESPONSES_CLIENT_CONTEXT"
)


@lru_cache(maxsize=256)
def _openai_responses_singleton(
    api_key: str | None, base_url: str | None
) -> "OpenAIResponsesClient":
    """Return a cached `OpenAIResponsesClient` instance for the given parameters."""
    return OpenAIResponsesClient(api_key=api_key, base_url=base_url)


def client(
    *, api_key: str | None = None, base_url: str | None = None
) -> "OpenAIResponsesClient":
    """Return an `OpenAIResponsesClient`."""
    api_key = api_key or os.getenv("OPENAI_API_KEY")
    base_url = base_url or os.getenv("OPENAI_BASE_URL")
    return _openai_responses_singleton(api_key, base_url)


def get_client() -> "OpenAIResponsesClient":
    """Get the current `OpenAIResponsesClient` from context."""
    current_client = OPENAI_RESPONSES_CLIENT_CONTEXT.get(None)
    if current_client is None:
        current_client = client()
        OPENAI_RESPONSES_CLIENT_CONTEXT.set(current_client)
    return current_client


class OpenAIResponsesClient(
    BaseClient[OpenAIResponsesModelId, OpenAI, "OpenAIResponsesClient"]
):
    """The client for the OpenAI Responses API."""

    @property
    def _context_var(self) -> ContextVar["OpenAIResponsesClient"]:
        return OPENAI_RESPONSES_CLIENT_CONTEXT

    def __init__(
        self, *, api_key: str | None = None, base_url: str | None = None
    ) -> None:
        """Initialize the OpenAI Responses client."""
        self.client = OpenAI(api_key=api_key, base_url=base_url)
        self.async_client = AsyncOpenAI(api_key=api_key, base_url=base_url)

    @overload
    def call(
        self,
        *,
        model_id: OpenAIResponsesModelId,
        messages: Sequence[Message],
        tools: Sequence[Tool] | Toolkit | None = None,
        format: None = None,
        **params: Unpack[Params],
    ) -> Response:
        """Generate an `llm.Response` without a response format."""
        ...

    @overload
    def call(
        self,
        *,
        model_id: OpenAIResponsesModelId,
        messages: Sequence[Message],
        tools: Sequence[Tool] | Toolkit | None = None,
        format: type[FormattableT] | Format[FormattableT],
        **params: Unpack[Params],
    ) -> Response[FormattableT]:
        """Generate an `llm.Response` with a response format."""
        ...

    @overload
    def call(
        self,
        *,
        model_id: OpenAIResponsesModelId,
        messages: Sequence[Message],
        tools: Sequence[Tool] | Toolkit | None = None,
        format: type[FormattableT] | Format[FormattableT] | None = None,
        **params: Unpack[Params],
    ) -> Response | Response[FormattableT]:
        """Generate an `llm.Response` with optional response format."""
        ...

    def call(
        self,
        *,
        model_id: OpenAIResponsesModelId,
        messages: Sequence[Message],
        tools: Sequence[Tool] | Toolkit | None = None,
        format: type[FormattableT] | Format[FormattableT] | None = None,
        **params: Unpack[Params],
    ) -> Response | Response[FormattableT]:
        """Generate an `llm.Response` by synchronously calling the OpenAI Responses API.

        Args:
            model_id: Model identifier to use.
            messages: Messages to send to the LLM.
            tools: Optional tools that the model may invoke.
            format: Optional response format specifier.
            **params: Additional parameters to configure output (e.g. temperature). See `llm.Params`.

        Returns:
            An `llm.Response` object containing the LLM-generated content.
        """
        messages, format, kwargs = _utils.encode_request(
            model_id=model_id,
            messages=messages,
            tools=tools,
            format=format,
            params=params,
        )

        openai_response = self.client.responses.create(**kwargs)

        assistant_message, finish_reason = _utils.decode_response(
            openai_response, model_id
        )
        provider_model_id = _utils.get_provider_model_id(model_id)

        return Response(
            raw=openai_response,
            provider="openai:responses",
            model_id=model_id,
            provider_model_id=provider_model_id,
            params=params,
            tools=tools,
            input_messages=messages,
            assistant_message=assistant_message,
            finish_reason=finish_reason,
            format=format,
        )

    @overload
    async def call_async(
        self,
        *,
        model_id: OpenAIResponsesModelId,
        messages: Sequence[Message],
        tools: Sequence[AsyncTool] | AsyncToolkit | None = None,
        format: None = None,
        **params: Unpack[Params],
    ) -> AsyncResponse:
        """Generate an `llm.AsyncResponse` without a response format."""
        ...

    @overload
    async def call_async(
        self,
        *,
        model_id: OpenAIResponsesModelId,
        messages: Sequence[Message],
        tools: Sequence[AsyncTool] | AsyncToolkit | None = None,
        format: type[FormattableT] | Format[FormattableT],
        **params: Unpack[Params],
    ) -> AsyncResponse[FormattableT]:
        """Generate an `llm.AsyncResponse` with a response format."""
        ...

    @overload
    async def call_async(
        self,
        *,
        model_id: OpenAIResponsesModelId,
        messages: Sequence[Message],
        tools: Sequence[AsyncTool] | AsyncToolkit | None = None,
        format: type[FormattableT] | Format[FormattableT] | None = None,
        **params: Unpack[Params],
    ) -> AsyncResponse | AsyncResponse[FormattableT]:
        """Generate an `llm.AsyncResponse` with optional response format."""
        ...

    async def call_async(
        self,
        *,
        model_id: OpenAIResponsesModelId,
        messages: Sequence[Message],
        tools: Sequence[AsyncTool] | AsyncToolkit | None = None,
        format: type[FormattableT] | Format[FormattableT] | None = None,
        **params: Unpack[Params],
    ) -> AsyncResponse | AsyncResponse[FormattableT]:
        """Generate an `llm.AsyncResponse` by asynchronously calling the OpenAI Responses API.

        Args:
            model_id: Model identifier to use.
            messages: Messages to send to the LLM.
            tools: Optional tools that the model may invoke.
            format: Optional response format specifier.
            **params: Additional parameters to configure output (e.g. temperature). See `llm.Params`.

        Returns:
            An `llm.AsyncResponse` object containing the LLM-generated content.
        """
        messages, format, kwargs = _utils.encode_request(
            model_id=model_id,
            messages=messages,
            tools=tools,
            format=format,
            params=params,
        )

        openai_response = await self.async_client.responses.create(**kwargs)

        assistant_message, finish_reason = _utils.decode_response(
            openai_response, model_id
        )
        provider_model_id = _utils.get_provider_model_id(model_id)

        return AsyncResponse(
            raw=openai_response,
            provider="openai:responses",
            model_id=model_id,
            provider_model_id=provider_model_id,
            params=params,
            tools=tools,
            input_messages=messages,
            assistant_message=assistant_message,
            finish_reason=finish_reason,
            format=format,
        )

    @overload
    def stream(
        self,
        *,
        model_id: OpenAIResponsesModelId,
        messages: Sequence[Message],
        tools: Sequence[Tool] | Toolkit | None = None,
        format: None = None,
        **params: Unpack[Params],
    ) -> StreamResponse:
        """Generate a `llm.StreamResponse` without a response format."""
        ...

    @overload
    def stream(
        self,
        *,
        model_id: OpenAIResponsesModelId,
        messages: Sequence[Message],
        tools: Sequence[Tool] | Toolkit | None = None,
        format: type[FormattableT] | Format[FormattableT],
        **params: Unpack[Params],
    ) -> StreamResponse[FormattableT]:
        """Generate a `llm.StreamResponse` with a response format."""
        ...

    @overload
    def stream(
        self,
        *,
        model_id: OpenAIResponsesModelId,
        messages: Sequence[Message],
        tools: Sequence[Tool] | Toolkit | None = None,
        format: type[FormattableT] | Format[FormattableT] | None = None,
        **params: Unpack[Params],
    ) -> StreamResponse | StreamResponse[FormattableT]:
        """Generate a `llm.StreamResponse` with optional response format."""
        ...

    def stream(
        self,
        *,
        model_id: OpenAIResponsesModelId,
        messages: Sequence[Message],
        tools: Sequence[Tool] | Toolkit | None = None,
        format: type[FormattableT] | Format[FormattableT] | None = None,
        **params: Unpack[Params],
    ) -> StreamResponse | StreamResponse[FormattableT]:
        """Generate a `llm.StreamResponse` by synchronously streaming from the OpenAI Responses API.

        Args:
            model_id: Model identifier to use.
            messages: Messages to send to the LLM.
            tools: Optional tools that the model may invoke.
            format: Optional response format specifier.
            **params: Additional parameters to configure output (e.g. temperature). See `llm.Params`.

        Returns:
            A `llm.StreamResponse` object containing the LLM-generated content stream.
        """
        messages, format, kwargs = _utils.encode_request(
            model_id=model_id,
            messages=messages,
            tools=tools,
            format=format,
            params=params,
        )

        openai_stream = self.client.responses.create(
            **kwargs,
            stream=True,
        )

        chunk_iterator = _utils.decode_stream(
            openai_stream,
        )
        provider_model_id = _utils.get_provider_model_id(model_id)

        return StreamResponse(
            provider="openai:responses",
            model_id=model_id,
            provider_model_id=provider_model_id,
            params=params,
            tools=tools,
            input_messages=messages,
            chunk_iterator=chunk_iterator,
            format=format,
        )

    @overload
    async def stream_async(
        self,
        *,
        model_id: OpenAIResponsesModelId,
        messages: Sequence[Message],
        tools: Sequence[AsyncTool] | AsyncToolkit | None = None,
        format: None = None,
        **params: Unpack[Params],
    ) -> AsyncStreamResponse:
        """Generate a `llm.AsyncStreamResponse` without a response format."""
        ...

    @overload
    async def stream_async(
        self,
        *,
        model_id: OpenAIResponsesModelId,
        messages: Sequence[Message],
        tools: Sequence[AsyncTool] | AsyncToolkit | None = None,
        format: type[FormattableT] | Format[FormattableT],
        **params: Unpack[Params],
    ) -> AsyncStreamResponse[FormattableT]:
        """Generate a `llm.AsyncStreamResponse` with a response format."""
        ...

    @overload
    async def stream_async(
        self,
        *,
        model_id: OpenAIResponsesModelId,
        messages: Sequence[Message],
        tools: Sequence[AsyncTool] | AsyncToolkit | None = None,
        format: type[FormattableT] | Format[FormattableT] | None = None,
        **params: Unpack[Params],
    ) -> AsyncStreamResponse | AsyncStreamResponse[FormattableT]:
        """Generate a `llm.AsyncStreamResponse` with optional response format."""
        ...

    async def stream_async(
        self,
        *,
        model_id: OpenAIResponsesModelId,
        messages: Sequence[Message],
        tools: Sequence[AsyncTool] | AsyncToolkit | None = None,
        format: type[FormattableT] | Format[FormattableT] | None = None,
        **params: Unpack[Params],
    ) -> AsyncStreamResponse | AsyncStreamResponse[FormattableT]:
        """Generate a `llm.AsyncStreamResponse` by asynchronously streaming from the OpenAI Responses API.

        Args:
            model_id: Model identifier to use.
            messages: Messages to send to the LLM.
            tools: Optional tools that the model may invoke.
            format: Optional response format specifier.
            **params: Additional parameters to configure output (e.g. temperature). See `llm.Params`.

        Returns:
            A `llm.AsyncStreamResponse` object containing the LLM-generated content stream.
        """
        messages, format, kwargs = _utils.encode_request(
            model_id=model_id,
            messages=messages,
            tools=tools,
            format=format,
            params=params,
        )

        openai_stream = await self.async_client.responses.create(
            **kwargs,
            stream=True,
        )

        chunk_iterator = _utils.decode_async_stream(
            openai_stream,
        )
        provider_model_id = _utils.get_provider_model_id(model_id)

        return AsyncStreamResponse(
            provider="openai:responses",
            model_id=model_id,
            provider_model_id=provider_model_id,
            params=params,
            tools=tools,
            input_messages=messages,
            chunk_iterator=chunk_iterator,
            format=format,
        )

    @overload
    def context_call(
        self,
        *,
        ctx: Context[DepsT],
        model_id: OpenAIResponsesModelId,
        messages: Sequence[Message],
        tools: Sequence[Tool | ContextTool[DepsT]]
        | ContextToolkit[DepsT]
        | None = None,
        format: None = None,
        **params: Unpack[Params],
    ) -> ContextResponse[DepsT]:
        """Generate a `llm.ContextResponse` without a response format."""
        ...

    @overload
    def context_call(
        self,
        *,
        ctx: Context[DepsT],
        model_id: OpenAIResponsesModelId,
        messages: Sequence[Message],
        tools: Sequence[Tool | ContextTool[DepsT]]
        | ContextToolkit[DepsT]
        | None = None,
        format: type[FormattableT] | Format[FormattableT],
        **params: Unpack[Params],
    ) -> ContextResponse[DepsT, FormattableT]:
        """Generate a `llm.ContextResponse` with a response format."""
        ...

    @overload
    def context_call(
        self,
        *,
        ctx: Context[DepsT],
        model_id: OpenAIResponsesModelId,
        messages: Sequence[Message],
        tools: Sequence[Tool | ContextTool[DepsT]]
        | ContextToolkit[DepsT]
        | None = None,
        format: type[FormattableT] | Format[FormattableT] | None = None,
        **params: Unpack[Params],
    ) -> ContextResponse[DepsT] | ContextResponse[DepsT, FormattableT]:
        """Generate a `llm.ContextResponse` with optional response format."""
        ...

    def context_call(
        self,
        *,
        ctx: Context[DepsT],
        model_id: OpenAIResponsesModelId,
        messages: Sequence[Message],
        tools: Sequence[Tool | ContextTool[DepsT]]
        | ContextToolkit[DepsT]
        | None = None,
        format: type[FormattableT] | Format[FormattableT] | None = None,
        **params: Unpack[Params],
    ) -> ContextResponse[DepsT] | ContextResponse[DepsT, FormattableT]:
        """Generate a `llm.ContextResponse` by synchronously calling the OpenAI Responses API with context.

        Args:
            ctx: The context object containing dependencies.
            model_id: Model identifier to use.
            messages: Messages to send to the LLM.
            tools: Optional tools that the model may invoke.
            format: Optional response format specifier.
            **params: Additional parameters to configure output (e.g. temperature). See `llm.Params`.

        Returns:
            A `llm.ContextResponse` object containing the LLM-generated content and context.
        """
        messages, format, kwargs = _utils.encode_request(
            model_id=model_id,
            messages=messages,
            tools=tools,
            format=format,
            params=params,
        )

        openai_response = self.client.responses.create(**kwargs)

        assistant_message, finish_reason = _utils.decode_response(
            openai_response, model_id
        )
        provider_model_id = _utils.get_provider_model_id(model_id)

        return ContextResponse(
            raw=openai_response,
            provider="openai:responses",
            model_id=model_id,
            provider_model_id=provider_model_id,
            params=params,
            tools=tools,
            input_messages=messages,
            assistant_message=assistant_message,
            finish_reason=finish_reason,
            format=format,
        )

    @overload
    async def context_call_async(
        self,
        *,
        ctx: Context[DepsT],
        model_id: OpenAIResponsesModelId,
        messages: Sequence[Message],
        tools: Sequence[AsyncTool | AsyncContextTool[DepsT]]
        | AsyncContextToolkit[DepsT]
        | None = None,
        format: None = None,
        **params: Unpack[Params],
    ) -> AsyncContextResponse[DepsT]:
        """Generate a `llm.AsyncContextResponse` without a response format."""
        ...

    @overload
    async def context_call_async(
        self,
        *,
        ctx: Context[DepsT],
        model_id: OpenAIResponsesModelId,
        messages: Sequence[Message],
        tools: Sequence[AsyncTool | AsyncContextTool[DepsT]]
        | AsyncContextToolkit[DepsT]
        | None = None,
        format: type[FormattableT] | Format[FormattableT],
        **params: Unpack[Params],
    ) -> AsyncContextResponse[DepsT, FormattableT]:
        """Generate a `llm.AsyncContextResponse` with a response format."""
        ...

    @overload
    async def context_call_async(
        self,
        *,
        ctx: Context[DepsT],
        model_id: OpenAIResponsesModelId,
        messages: Sequence[Message],
        tools: Sequence[AsyncTool | AsyncContextTool[DepsT]]
        | AsyncContextToolkit[DepsT]
        | None = None,
        format: type[FormattableT] | Format[FormattableT] | None = None,
        **params: Unpack[Params],
    ) -> AsyncContextResponse[DepsT] | AsyncContextResponse[DepsT, FormattableT]:
        """Generate a `llm.AsyncContextResponse` with optional response format."""
        ...

    async def context_call_async(
        self,
        *,
        ctx: Context[DepsT],
        model_id: OpenAIResponsesModelId,
        messages: Sequence[Message],
        tools: Sequence[AsyncTool | AsyncContextTool[DepsT]]
        | AsyncContextToolkit[DepsT]
        | None = None,
        format: type[FormattableT] | Format[FormattableT] | None = None,
        **params: Unpack[Params],
    ) -> AsyncContextResponse[DepsT] | AsyncContextResponse[DepsT, FormattableT]:
        """Generate a `llm.AsyncContextResponse` by asynchronously calling the OpenAI Responses API with context.

        Args:
            ctx: The context object containing dependencies.
            model_id: Model identifier to use.
            messages: Messages to send to the LLM.
            tools: Optional tools that the model may invoke.
            format: Optional response format specifier.
            **params: Additional parameters to configure output (e.g. temperature). See `llm.Params`.

        Returns:
            A `llm.AsyncContextResponse` object containing the LLM-generated content and context.
        """
        messages, format, kwargs = _utils.encode_request(
            model_id=model_id,
            messages=messages,
            tools=tools,
            format=format,
            params=params,
        )

        openai_response = await self.async_client.responses.create(**kwargs)

        assistant_message, finish_reason = _utils.decode_response(
            openai_response, model_id
        )
        provider_model_id = _utils.get_provider_model_id(model_id)

        return AsyncContextResponse(
            raw=openai_response,
            provider="openai:responses",
            model_id=model_id,
            provider_model_id=provider_model_id,
            params=params,
            tools=tools,
            input_messages=messages,
            assistant_message=assistant_message,
            finish_reason=finish_reason,
            format=format,
        )

    @overload
    def context_stream(
        self,
        *,
        ctx: Context[DepsT],
        model_id: OpenAIResponsesModelId,
        messages: Sequence[Message],
        tools: Sequence[Tool | ContextTool[DepsT]]
        | ContextToolkit[DepsT]
        | None = None,
        format: None = None,
        **params: Unpack[Params],
    ) -> ContextStreamResponse[DepsT]:
        """Generate a `llm.ContextStreamResponse` without a response format."""
        ...

    @overload
    def context_stream(
        self,
        *,
        ctx: Context[DepsT],
        model_id: OpenAIResponsesModelId,
        messages: Sequence[Message],
        tools: Sequence[Tool | ContextTool[DepsT]]
        | ContextToolkit[DepsT]
        | None = None,
        format: type[FormattableT] | Format[FormattableT],
        **params: Unpack[Params],
    ) -> ContextStreamResponse[DepsT, FormattableT]:
        """Generate a `llm.ContextStreamResponse` with a response format."""
        ...

    @overload
    def context_stream(
        self,
        *,
        ctx: Context[DepsT],
        model_id: OpenAIResponsesModelId,
        messages: Sequence[Message],
        tools: Sequence[Tool | ContextTool[DepsT]]
        | ContextToolkit[DepsT]
        | None = None,
        format: type[FormattableT] | Format[FormattableT] | None = None,
        **params: Unpack[Params],
    ) -> ContextStreamResponse[DepsT] | ContextStreamResponse[DepsT, FormattableT]:
        """Generate a `llm.ContextStreamResponse` with optional response format."""
        ...

    def context_stream(
        self,
        *,
        ctx: Context[DepsT],
        model_id: OpenAIResponsesModelId,
        messages: Sequence[Message],
        tools: Sequence[Tool | ContextTool[DepsT]]
        | ContextToolkit[DepsT]
        | None = None,
        format: type[FormattableT] | Format[FormattableT] | None = None,
        **params: Unpack[Params],
    ) -> ContextStreamResponse[DepsT] | ContextStreamResponse[DepsT, FormattableT]:
        """Generate a `llm.ContextStreamResponse` by synchronously streaming from the OpenAI Responses API with context.

        Args:
            ctx: The context object containing dependencies.
            model_id: Model identifier to use.
            messages: Messages to send to the LLM.
            tools: Optional tools that the model may invoke.
            format: Optional response format specifier.
            **params: Additional parameters to configure output (e.g. temperature). See `llm.Params`.

        Returns:
            A `llm.ContextStreamResponse` object containing the LLM-generated content stream and context.
        """
        messages, format, kwargs = _utils.encode_request(
            model_id=model_id,
            messages=messages,
            tools=tools,
            format=format,
            params=params,
        )

        openai_stream = self.client.responses.create(
            **kwargs,
            stream=True,
        )

        chunk_iterator = _utils.decode_stream(
            openai_stream,
        )
        provider_model_id = _utils.get_provider_model_id(model_id)

        return ContextStreamResponse(
            provider="openai:responses",
            model_id=model_id,
            provider_model_id=provider_model_id,
            params=params,
            tools=tools,
            input_messages=messages,
            chunk_iterator=chunk_iterator,
            format=format,
        )

    @overload
    async def context_stream_async(
        self,
        *,
        ctx: Context[DepsT],
        model_id: OpenAIResponsesModelId,
        messages: Sequence[Message],
        tools: Sequence[AsyncTool | AsyncContextTool[DepsT]]
        | AsyncContextToolkit[DepsT]
        | None = None,
        format: None = None,
        **params: Unpack[Params],
    ) -> AsyncContextStreamResponse[DepsT]:
        """Generate a `llm.AsyncContextStreamResponse` without a response format."""
        ...

    @overload
    async def context_stream_async(
        self,
        *,
        ctx: Context[DepsT],
        model_id: OpenAIResponsesModelId,
        messages: Sequence[Message],
        tools: Sequence[AsyncTool | AsyncContextTool[DepsT]]
        | AsyncContextToolkit[DepsT]
        | None = None,
        format: type[FormattableT] | Format[FormattableT],
        **params: Unpack[Params],
    ) -> AsyncContextStreamResponse[DepsT, FormattableT]:
        """Generate a `llm.AsyncContextStreamResponse` with a response format."""
        ...

    @overload
    async def context_stream_async(
        self,
        *,
        ctx: Context[DepsT],
        model_id: OpenAIResponsesModelId,
        messages: Sequence[Message],
        tools: Sequence[AsyncTool | AsyncContextTool[DepsT]]
        | AsyncContextToolkit[DepsT]
        | None = None,
        format: type[FormattableT] | Format[FormattableT] | None = None,
        **params: Unpack[Params],
    ) -> (
        AsyncContextStreamResponse[DepsT]
        | AsyncContextStreamResponse[DepsT, FormattableT]
    ):
        """Generate a `llm.AsyncContextStreamResponse` with optional response format."""
        ...

    async def context_stream_async(
        self,
        *,
        ctx: Context[DepsT],
        model_id: OpenAIResponsesModelId,
        messages: Sequence[Message],
        tools: Sequence[AsyncTool | AsyncContextTool[DepsT]]
        | AsyncContextToolkit[DepsT]
        | None = None,
        format: type[FormattableT] | Format[FormattableT] | None = None,
        **params: Unpack[Params],
    ) -> (
        AsyncContextStreamResponse[DepsT]
        | AsyncContextStreamResponse[DepsT, FormattableT]
    ):
        """Generate a `llm.AsyncContextStreamResponse` by asynchronously streaming from the OpenAI Responses API with context.

        Args:
            ctx: The context object containing dependencies.
            model_id: Model identifier to use.
            messages: Messages to send to the LLM.
            tools: Optional tools that the model may invoke.
            format: Optional response format specifier.
            **params: Additional parameters to configure output (e.g. temperature). See `llm.Params`.

        Returns:
            A `llm.AsyncContextStreamResponse` object containing the LLM-generated content stream and context.
        """
        messages, format, kwargs = _utils.encode_request(
            model_id=model_id,
            messages=messages,
            tools=tools,
            format=format,
            params=params,
        )

        openai_stream = await self.async_client.responses.create(
            **kwargs,
            stream=True,
        )

        chunk_iterator = _utils.decode_async_stream(
            openai_stream,
        )
        provider_model_id = _utils.get_provider_model_id(model_id)

        return AsyncContextStreamResponse(
            provider="openai:responses",
            model_id=model_id,
            provider_model_id=provider_model_id,
            params=params,
            tools=tools,
            input_messages=messages,
            chunk_iterator=chunk_iterator,
            format=format,
        )
