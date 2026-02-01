"""Beta Anthropic provider implementation."""

from __future__ import annotations

from collections.abc import Sequence
from typing import TYPE_CHECKING
from typing_extensions import Unpack

from anthropic import Anthropic, AsyncAnthropic

from ...context import Context, DepsT
from ...formatting import FormatSpec, FormattableT
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
    AsyncContextToolkit,
    AsyncToolkit,
    ContextToolkit,
    Toolkit,
)
from ..base import BaseProvider
from . import _utils
from ._utils import beta_decode, beta_encode
from .model_id import model_name

if TYPE_CHECKING:
    from ...models import Params


class AnthropicBetaProvider(BaseProvider[Anthropic]):
    """Provider using beta Anthropic API."""

    id = "anthropic-beta"
    default_scope = "anthropic-beta/"
    error_map = _utils.ANTHROPIC_ERROR_MAP

    def __init__(
        self, *, api_key: str | None = None, base_url: str | None = None
    ) -> None:
        """Initialize the beta Anthropic client."""
        self.client = Anthropic(api_key=api_key, base_url=base_url)
        self.async_client = AsyncAnthropic(api_key=api_key, base_url=base_url)

    def get_error_status(self, e: Exception) -> int | None:
        """Extract HTTP status code from Anthropic exception."""
        return getattr(e, "status_code", None)

    def _call(
        self,
        *,
        model_id: str,
        messages: Sequence[Message],
        toolkit: Toolkit,
        format: FormatSpec[FormattableT] | None = None,
        **params: Unpack[Params],
    ) -> Response | Response[FormattableT]:
        """Generate an `llm.Response` using the beta Anthropic API."""
        input_messages, resolved_format, kwargs = beta_encode.beta_encode_request(
            model_id=model_id,
            messages=messages,
            tools=toolkit,
            format=format,
            params=params,
        )
        beta_response = self.client.beta.messages.parse(**kwargs)
        include_thoughts = _utils.get_include_thoughts(params)
        assistant_message, finish_reason, usage = beta_decode.beta_decode_response(
            beta_response, model_id, include_thoughts=include_thoughts
        )
        return Response(
            raw=beta_response,
            provider_id="anthropic",
            model_id=model_id,
            provider_model_name=model_name(model_id),
            params=params,
            tools=toolkit,
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
        toolkit: ContextToolkit[DepsT],
        format: FormatSpec[FormattableT] | None = None,
        **params: Unpack[Params],
    ) -> ContextResponse[DepsT, None] | ContextResponse[DepsT, FormattableT]:
        """Generate an `llm.ContextResponse` using the beta Anthropic API."""
        input_messages, resolved_format, kwargs = beta_encode.beta_encode_request(
            model_id=model_id,
            messages=messages,
            tools=toolkit,
            format=format,
            params=params,
        )
        beta_response = self.client.beta.messages.parse(**kwargs)
        include_thoughts = _utils.get_include_thoughts(params)
        assistant_message, finish_reason, usage = beta_decode.beta_decode_response(
            beta_response, model_id, include_thoughts=include_thoughts
        )
        return ContextResponse(
            raw=beta_response,
            provider_id="anthropic",
            model_id=model_id,
            provider_model_name=model_name(model_id),
            params=params,
            tools=toolkit,
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
        toolkit: AsyncToolkit,
        format: FormatSpec[FormattableT] | None = None,
        **params: Unpack[Params],
    ) -> AsyncResponse | AsyncResponse[FormattableT]:
        """Generate an `llm.AsyncResponse` using the beta Anthropic API."""
        input_messages, resolved_format, kwargs = beta_encode.beta_encode_request(
            model_id=model_id,
            messages=messages,
            tools=toolkit,
            format=format,
            params=params,
        )
        beta_response = await self.async_client.beta.messages.parse(**kwargs)
        include_thoughts = _utils.get_include_thoughts(params)
        assistant_message, finish_reason, usage = beta_decode.beta_decode_response(
            beta_response, model_id, include_thoughts=include_thoughts
        )
        return AsyncResponse(
            raw=beta_response,
            provider_id="anthropic",
            model_id=model_id,
            provider_model_name=model_name(model_id),
            params=params,
            tools=toolkit,
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
        toolkit: AsyncContextToolkit[DepsT],
        format: FormatSpec[FormattableT] | None = None,
        **params: Unpack[Params],
    ) -> AsyncContextResponse[DepsT, None] | AsyncContextResponse[DepsT, FormattableT]:
        """Generate an `llm.AsyncContextResponse` using the beta Anthropic API."""
        input_messages, resolved_format, kwargs = beta_encode.beta_encode_request(
            model_id=model_id,
            messages=messages,
            tools=toolkit,
            format=format,
            params=params,
        )
        beta_response = await self.async_client.beta.messages.parse(**kwargs)
        include_thoughts = _utils.get_include_thoughts(params)
        assistant_message, finish_reason, usage = beta_decode.beta_decode_response(
            beta_response, model_id, include_thoughts=include_thoughts
        )
        return AsyncContextResponse(
            raw=beta_response,
            provider_id="anthropic",
            model_id=model_id,
            provider_model_name=model_name(model_id),
            params=params,
            tools=toolkit,
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
        toolkit: Toolkit,
        format: FormatSpec[FormattableT] | None = None,
        **params: Unpack[Params],
    ) -> StreamResponse | StreamResponse[FormattableT]:
        """Generate an `llm.StreamResponse` using the beta Anthropic API."""
        input_messages, resolved_format, kwargs = beta_encode.beta_encode_request(
            model_id=model_id,
            messages=messages,
            tools=toolkit,
            format=format,
            params=params,
        )
        beta_stream = self.client.beta.messages.stream(**kwargs)
        include_thoughts = _utils.get_include_thoughts(params)
        chunk_iterator = beta_decode.beta_decode_stream(
            beta_stream, include_thoughts=include_thoughts
        )
        return StreamResponse(
            provider_id="anthropic",
            model_id=model_id,
            provider_model_name=model_name(model_id),
            params=params,
            tools=toolkit,
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
        toolkit: ContextToolkit[DepsT],
        format: FormatSpec[FormattableT] | None = None,
        **params: Unpack[Params],
    ) -> ContextStreamResponse[DepsT] | ContextStreamResponse[DepsT, FormattableT]:
        """Generate an `llm.ContextStreamResponse` using the beta Anthropic API."""
        input_messages, resolved_format, kwargs = beta_encode.beta_encode_request(
            model_id=model_id,
            messages=messages,
            tools=toolkit,
            format=format,
            params=params,
        )
        beta_stream = self.client.beta.messages.stream(**kwargs)
        include_thoughts = _utils.get_include_thoughts(params)
        chunk_iterator = beta_decode.beta_decode_stream(
            beta_stream, include_thoughts=include_thoughts
        )
        return ContextStreamResponse(
            provider_id="anthropic",
            model_id=model_id,
            provider_model_name=model_name(model_id),
            params=params,
            tools=toolkit,
            input_messages=input_messages,
            chunk_iterator=chunk_iterator,
            format=resolved_format,
        )

    async def _stream_async(
        self,
        *,
        model_id: str,
        messages: Sequence[Message],
        toolkit: AsyncToolkit,
        format: FormatSpec[FormattableT] | None = None,
        **params: Unpack[Params],
    ) -> AsyncStreamResponse | AsyncStreamResponse[FormattableT]:
        """Generate an `llm.AsyncStreamResponse` using the beta Anthropic API."""
        input_messages, resolved_format, kwargs = beta_encode.beta_encode_request(
            model_id=model_id,
            messages=messages,
            tools=toolkit,
            format=format,
            params=params,
        )
        beta_stream = self.async_client.beta.messages.stream(**kwargs)
        include_thoughts = _utils.get_include_thoughts(params)
        chunk_iterator = beta_decode.beta_decode_async_stream(
            beta_stream, include_thoughts=include_thoughts
        )
        return AsyncStreamResponse(
            provider_id="anthropic",
            model_id=model_id,
            provider_model_name=model_name(model_id),
            params=params,
            tools=toolkit,
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
        toolkit: AsyncContextToolkit[DepsT],
        format: FormatSpec[FormattableT] | None = None,
        **params: Unpack[Params],
    ) -> (
        AsyncContextStreamResponse[DepsT]
        | AsyncContextStreamResponse[DepsT, FormattableT]
    ):
        """Generate an `llm.AsyncContextStreamResponse` using the beta Anthropic API."""
        input_messages, resolved_format, kwargs = beta_encode.beta_encode_request(
            model_id=model_id,
            messages=messages,
            tools=toolkit,
            format=format,
            params=params,
        )
        beta_stream = self.async_client.beta.messages.stream(**kwargs)
        include_thoughts = _utils.get_include_thoughts(params)
        chunk_iterator = beta_decode.beta_decode_async_stream(
            beta_stream, include_thoughts=include_thoughts
        )
        return AsyncContextStreamResponse(
            provider_id="anthropic",
            model_id=model_id,
            provider_model_name=model_name(model_id),
            params=params,
            tools=toolkit,
            input_messages=input_messages,
            chunk_iterator=chunk_iterator,
            format=resolved_format,
        )
