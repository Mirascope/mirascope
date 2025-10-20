"""Base OpenAI Responses client implementation."""

from abc import abstractmethod
from collections.abc import Sequence
from typing import Literal, Protocol, overload, runtime_checkable
from typing_extensions import TypeVar, Unpack

from openai.resources.responses.responses import AsyncResponses, Responses

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
from ...base import BaseClient, ClientT, Params
from . import _utils
from .model_ids import OpenAIResponsesModelId


@runtime_checkable
class OpenAICompatibleClient(Protocol):
    """Protocol for OpenAI-compatible sync clients."""

    @property
    def responses(self) -> Responses: ...


@runtime_checkable
class AsyncOpenAICompatibleClient(Protocol):
    """Protocol for OpenAI-compatible async clients."""

    @property
    def responses(self) -> AsyncResponses: ...


ProviderClientT = TypeVar("ProviderClientT", bound=OpenAICompatibleClient)
AsyncProviderClientT = TypeVar(
    "AsyncProviderClientT", bound=AsyncOpenAICompatibleClient
)


class BaseOpenAIResponsesClient(
    BaseClient[OpenAIResponsesModelId, ProviderClientT, AsyncProviderClientT, ClientT],
):
    """Base client for OpenAI-compatible Responses APIs.

    This class implements all the API call logic that is shared between
    OpenAI and Azure OpenAI. Subclasses only need to define `_context_var`,
    `provider`, and `__init__`.

    Type parameters:
        ProviderClientT: The sync provider client type (OpenAI or AzureOpenAI).
        AsyncProviderClientT: The async provider client type (AsyncOpenAI or AsyncAzureOpenAI).
        ClientT: The concrete client type (for ContextVar typing).
    """

    @property
    @abstractmethod
    def provider(
        self,
    ) -> Literal["openai:responses", "openai", "azure-openai:responses"]:
        """Return the provider name for OpenAI-compatible Responses clients."""
        ...

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
        format: type[FormattableT] | Format[FormattableT] | None,
        **params: Unpack[Params],
    ) -> Response | Response[FormattableT]:
        """Generate an `llm.Response` with an optional response format."""
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
            provider=self.provider,
        )

        openai_response = self.client.responses.create(**kwargs)

        assistant_message, finish_reason = _utils.decode_response(
            openai_response, model_id, self.provider
        )

        return Response(
            raw=openai_response,
            provider=self.provider,
            model_id=model_id,
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
        format: type[FormattableT] | Format[FormattableT] | None,
        **params: Unpack[Params],
    ) -> AsyncResponse | AsyncResponse[FormattableT]:
        """Generate an `llm.AsyncResponse` with an optional response format."""
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
            provider=self.provider,
        )

        openai_response = await self.async_client.responses.create(**kwargs)

        assistant_message, finish_reason = _utils.decode_response(
            openai_response, model_id, self.provider
        )

        return AsyncResponse(
            raw=openai_response,
            provider=self.provider,
            model_id=model_id,
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
        format: type[FormattableT] | Format[FormattableT] | None,
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
            provider=self.provider,
        )

        openai_stream = self.client.responses.create(
            **kwargs,
            stream=True,
        )

        chunk_iterator = _utils.decode_stream(
            openai_stream,
        )

        return StreamResponse(
            provider=self.provider,
            model_id=model_id,
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
        format: type[FormattableT] | Format[FormattableT] | None,
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
            provider=self.provider,
        )

        openai_stream = await self.async_client.responses.create(
            **kwargs,
            stream=True,
        )

        chunk_iterator = _utils.decode_async_stream(
            openai_stream,
        )

        return AsyncStreamResponse(
            provider=self.provider,
            model_id=model_id,
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
            provider=self.provider,
        )

        openai_response = self.client.responses.create(**kwargs)

        assistant_message, finish_reason = _utils.decode_response(
            openai_response, model_id, self.provider
        )

        return ContextResponse(
            raw=openai_response,
            provider=self.provider,
            model_id=model_id,
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
            provider=self.provider,
        )

        openai_response = await self.async_client.responses.create(**kwargs)

        assistant_message, finish_reason = _utils.decode_response(
            openai_response, model_id, self.provider
        )

        return AsyncContextResponse(
            raw=openai_response,
            provider=self.provider,
            model_id=model_id,
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
            provider=self.provider,
        )

        openai_stream = self.client.responses.create(
            **kwargs,
            stream=True,
        )

        chunk_iterator = _utils.decode_stream(
            openai_stream,
        )

        return ContextStreamResponse(
            provider=self.provider,
            model_id=model_id,
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
            provider=self.provider,
        )

        openai_stream = await self.async_client.responses.create(
            **kwargs,
            stream=True,
        )

        chunk_iterator = _utils.decode_async_stream(
            openai_stream,
        )

        return AsyncContextStreamResponse(
            provider=self.provider,
            model_id=model_id,
            params=params,
            tools=tools,
            input_messages=messages,
            chunk_iterator=chunk_iterator,
            format=format,
        )
