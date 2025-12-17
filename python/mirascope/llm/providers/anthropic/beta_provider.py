"""Beta Anthropic provider implementation."""

from collections.abc import Sequence
from typing_extensions import Unpack

from anthropic import Anthropic, AsyncAnthropic

from ...context import Context, DepsT
from ...formatting import Format, FormattableT
from ...messages import Message
from ...responses import (
    AsyncContextResponse,
    AsyncContextStreamResponse,
    AsyncResponse,
    AsyncStreamResponse,
    ContextResponse,
    ContextStreamResponse,
    Response,
    StreamResponse,
)
from ...tools import (
    AsyncContextTool,
    AsyncContextToolkit,
    AsyncTool,
    AsyncToolkit,
    ContextTool,
    ContextToolkit,
    Tool,
    Toolkit,
)
from ..base import BaseProvider, Params
from ._utils import beta_decode, beta_encode
from .model_id import model_name


class AnthropicBetaProvider(BaseProvider[Anthropic]):
    """Provider using beta Anthropic API."""

    id = "anthropic-beta"
    default_scope = "anthropic-beta/"

    def __init__(
        self, *, api_key: str | None = None, base_url: str | None = None
    ) -> None:
        """Initialize the beta Anthropic client."""
        self.client = Anthropic(api_key=api_key, base_url=base_url)
        self.async_client = AsyncAnthropic(api_key=api_key, base_url=base_url)

    def _call(
        self,
        *,
        model_id: str,
        messages: Sequence[Message],
        tools: Sequence[Tool] | Toolkit | None = None,
        format: type[FormattableT] | Format[FormattableT] | None = None,
        **params: Unpack[Params],
    ) -> Response | Response[FormattableT]:
        """Generate an `llm.Response` using the beta Anthropic API."""
        input_messages, resolved_format, kwargs = beta_encode.beta_encode_request(
            model_id=model_id,
            messages=messages,
            tools=tools,
            format=format,
            params=params,
        )
        beta_response = self.client.beta.messages.parse(**kwargs)
        assistant_message, finish_reason, usage = beta_decode.beta_decode_response(
            beta_response, model_id
        )
        return Response(
            raw=beta_response,
            provider_id="anthropic",
            model_id=model_id,
            provider_model_name=model_name(model_id),
            params=params,
            tools=tools,
            input_messages=input_messages,
            assistant_message=assistant_message,
            finish_reason=finish_reason,
            usage=usage,
            format=resolved_format,
        )

    def _context_call(
        self,
        *,
        ctx: Context[DepsT],
        model_id: str,
        messages: Sequence[Message],
        tools: Sequence[Tool | ContextTool[DepsT]]
        | ContextToolkit[DepsT]
        | None = None,
        format: type[FormattableT] | Format[FormattableT] | None = None,
        **params: Unpack[Params],
    ) -> ContextResponse[DepsT, None] | ContextResponse[DepsT, FormattableT]:
        """Generate an `llm.ContextResponse` using the beta Anthropic API."""
        input_messages, resolved_format, kwargs = beta_encode.beta_encode_request(
            model_id=model_id,
            messages=messages,
            tools=tools,
            format=format,
            params=params,
        )
        beta_response = self.client.beta.messages.parse(**kwargs)
        assistant_message, finish_reason, usage = beta_decode.beta_decode_response(
            beta_response, model_id
        )
        return ContextResponse(
            raw=beta_response,
            provider_id="anthropic",
            model_id=model_id,
            provider_model_name=model_name(model_id),
            params=params,
            tools=tools,
            input_messages=input_messages,
            assistant_message=assistant_message,
            finish_reason=finish_reason,
            usage=usage,
            format=resolved_format,
        )

    async def _call_async(
        self,
        *,
        model_id: str,
        messages: Sequence[Message],
        tools: Sequence[AsyncTool] | AsyncToolkit | None = None,
        format: type[FormattableT] | Format[FormattableT] | None = None,
        **params: Unpack[Params],
    ) -> AsyncResponse | AsyncResponse[FormattableT]:
        """Generate an `llm.AsyncResponse` using the beta Anthropic API."""
        input_messages, resolved_format, kwargs = beta_encode.beta_encode_request(
            model_id=model_id,
            messages=messages,
            tools=tools,
            format=format,
            params=params,
        )
        beta_response = await self.async_client.beta.messages.parse(**kwargs)
        assistant_message, finish_reason, usage = beta_decode.beta_decode_response(
            beta_response, model_id
        )
        return AsyncResponse(
            raw=beta_response,
            provider_id="anthropic",
            model_id=model_id,
            provider_model_name=model_name(model_id),
            params=params,
            tools=tools,
            input_messages=input_messages,
            assistant_message=assistant_message,
            finish_reason=finish_reason,
            usage=usage,
            format=resolved_format,
        )

    async def _context_call_async(
        self,
        *,
        ctx: Context[DepsT],
        model_id: str,
        messages: Sequence[Message],
        tools: Sequence[AsyncTool | AsyncContextTool[DepsT]]
        | AsyncContextToolkit[DepsT]
        | None = None,
        format: type[FormattableT] | Format[FormattableT] | None = None,
        **params: Unpack[Params],
    ) -> AsyncContextResponse[DepsT, None] | AsyncContextResponse[DepsT, FormattableT]:
        """Generate an `llm.AsyncContextResponse` using the beta Anthropic API."""
        input_messages, resolved_format, kwargs = beta_encode.beta_encode_request(
            model_id=model_id,
            messages=messages,
            tools=tools,
            format=format,
            params=params,
        )
        beta_response = await self.async_client.beta.messages.parse(**kwargs)
        assistant_message, finish_reason, usage = beta_decode.beta_decode_response(
            beta_response, model_id
        )
        return AsyncContextResponse(
            raw=beta_response,
            provider_id="anthropic",
            model_id=model_id,
            provider_model_name=model_name(model_id),
            params=params,
            tools=tools,
            input_messages=input_messages,
            assistant_message=assistant_message,
            finish_reason=finish_reason,
            usage=usage,
            format=resolved_format,
        )

    def _stream(
        self,
        *,
        model_id: str,
        messages: Sequence[Message],
        tools: Sequence[Tool] | Toolkit | None = None,
        format: type[FormattableT] | Format[FormattableT] | None = None,
        **params: Unpack[Params],
    ) -> StreamResponse | StreamResponse[FormattableT]:
        """Generate an `llm.StreamResponse` using the beta Anthropic API."""
        input_messages, resolved_format, kwargs = beta_encode.beta_encode_request(
            model_id=model_id,
            messages=messages,
            tools=tools,
            format=format,
            params=params,
        )
        beta_stream = self.client.beta.messages.stream(**kwargs)
        chunk_iterator = beta_decode.beta_decode_stream(beta_stream)
        return StreamResponse(
            provider_id="anthropic",
            model_id=model_id,
            provider_model_name=model_name(model_id),
            params=params,
            tools=tools,
            input_messages=input_messages,
            chunk_iterator=chunk_iterator,
            format=resolved_format,
        )

    def _context_stream(
        self,
        *,
        ctx: Context[DepsT],
        model_id: str,
        messages: Sequence[Message],
        tools: Sequence[Tool | ContextTool[DepsT]]
        | ContextToolkit[DepsT]
        | None = None,
        format: type[FormattableT] | Format[FormattableT] | None = None,
        **params: Unpack[Params],
    ) -> ContextStreamResponse[DepsT] | ContextStreamResponse[DepsT, FormattableT]:
        """Generate an `llm.ContextStreamResponse` using the beta Anthropic API."""
        input_messages, resolved_format, kwargs = beta_encode.beta_encode_request(
            model_id=model_id,
            messages=messages,
            tools=tools,
            format=format,
            params=params,
        )
        beta_stream = self.client.beta.messages.stream(**kwargs)
        chunk_iterator = beta_decode.beta_decode_stream(beta_stream)
        return ContextStreamResponse(
            provider_id="anthropic",
            model_id=model_id,
            provider_model_name=model_name(model_id),
            params=params,
            tools=tools,
            input_messages=input_messages,
            chunk_iterator=chunk_iterator,
            format=resolved_format,
        )

    async def _stream_async(
        self,
        *,
        model_id: str,
        messages: Sequence[Message],
        tools: Sequence[AsyncTool] | AsyncToolkit | None = None,
        format: type[FormattableT] | Format[FormattableT] | None = None,
        **params: Unpack[Params],
    ) -> AsyncStreamResponse | AsyncStreamResponse[FormattableT]:
        """Generate an `llm.AsyncStreamResponse` using the beta Anthropic API."""
        input_messages, resolved_format, kwargs = beta_encode.beta_encode_request(
            model_id=model_id,
            messages=messages,
            tools=tools,
            format=format,
            params=params,
        )
        beta_stream = self.async_client.beta.messages.stream(**kwargs)
        chunk_iterator = beta_decode.beta_decode_async_stream(beta_stream)
        return AsyncStreamResponse(
            provider_id="anthropic",
            model_id=model_id,
            provider_model_name=model_name(model_id),
            params=params,
            tools=tools,
            input_messages=input_messages,
            chunk_iterator=chunk_iterator,
            format=resolved_format,
        )

    async def _context_stream_async(
        self,
        *,
        ctx: Context[DepsT],
        model_id: str,
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
        """Generate an `llm.AsyncContextStreamResponse` using the beta Anthropic API."""
        input_messages, resolved_format, kwargs = beta_encode.beta_encode_request(
            model_id=model_id,
            messages=messages,
            tools=tools,
            format=format,
            params=params,
        )
        beta_stream = self.async_client.beta.messages.stream(**kwargs)
        chunk_iterator = beta_decode.beta_decode_async_stream(beta_stream)
        return AsyncContextStreamResponse(
            provider_id="anthropic",
            model_id=model_id,
            provider_model_name=model_name(model_id),
            params=params,
            tools=tools,
            input_messages=input_messages,
            chunk_iterator=chunk_iterator,
            format=resolved_format,
        )
