"""Anthropic client implementation."""

from __future__ import annotations

from collections.abc import Sequence
from typing import TYPE_CHECKING
from typing_extensions import Unpack

from anthropic import Anthropic, AsyncAnthropic

from ...context import Context, DepsT
from ...formatting import FormatSpec, FormattableT, resolve_format
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
    AnyToolSchema,
    AsyncContextToolkit,
    AsyncToolkit,
    BaseToolkit,
    ContextToolkit,
    Toolkit,
)
from ..base import BaseProvider, _utils as _base_utils
from . import _utils
from .beta_provider import AnthropicBetaProvider
from .model_id import AnthropicModelId, model_name
from .model_info import MODELS_WITHOUT_STRICT_STRUCTURED_OUTPUTS

if TYPE_CHECKING:
    from ...models import Params


def _should_use_beta(
    model_id: AnthropicModelId,
    format: FormatSpec[FormattableT] | None,
    tools: BaseToolkit[AnyToolSchema],
) -> bool:
    """Determine whether to use the beta API based on format mode or strict tools.

    If the format resolves to strict mode, or any tools have strict=True,
    and the model plausibly has strict structured output support, then we
    will use the beta provider.
    """
    if model_name(model_id) in MODELS_WITHOUT_STRICT_STRUCTURED_OUTPUTS:
        return False

    # Check if format requires strict mode
    resolved = resolve_format(format, default_mode=_utils.DEFAULT_FORMAT_MODE)
    if resolved is not None and resolved.mode == "strict":
        return True

    return _base_utils.has_strict_tools(tools.tools)


class AnthropicProvider(BaseProvider[Anthropic]):
    """The client for the Anthropic LLM model."""

    id = "anthropic"
    default_scope = "anthropic/"
    error_map = _utils.ANTHROPIC_ERROR_MAP
    _beta_provider: AnthropicBetaProvider

    def __init__(
        self, *, api_key: str | None = None, base_url: str | None = None
    ) -> None:
        """Initialize the Anthropic client."""
        self.client = Anthropic(api_key=api_key, base_url=base_url)
        self.async_client = AsyncAnthropic(api_key=api_key, base_url=base_url)
        self._beta_provider = AnthropicBetaProvider(api_key=api_key, base_url=base_url)

    def get_error_status(self, e: Exception) -> int | None:
        """Extract HTTP status code from Anthropic exception."""
        return getattr(e, "status_code", None)

    def _call(
        self,
        *,
        model_id: AnthropicModelId,
        messages: Sequence[Message],
        toolkit: Toolkit,
        format: FormatSpec[FormattableT] | None = None,
        **params: Unpack[Params],
    ) -> Response | Response[FormattableT]:
        """Generate an `llm.Response` by synchronously calling the Anthropic Messages API."""
        if _should_use_beta(model_id, format, toolkit):
            return self._beta_provider.call(
                model_id=model_id,
                messages=messages,
                toolkit=toolkit,
                format=format,
                **params,
            )

        input_messages, resolved_format, kwargs = _utils.encode_request(
            model_id=model_id,
            messages=messages,
            tools=toolkit,
            format=format,
            params=params,
        )
        anthropic_response = self.client.messages.create(**kwargs)
        include_thoughts = _utils.get_include_thoughts(params)
        assistant_message, finish_reason, usage = _utils.decode_response(
            anthropic_response, model_id, include_thoughts=include_thoughts
        )
        return Response(
            raw=anthropic_response,
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
        model_id: AnthropicModelId,
        messages: Sequence[Message],
        toolkit: ContextToolkit[DepsT],
        format: FormatSpec[FormattableT] | None = None,
        **params: Unpack[Params],
    ) -> ContextResponse[DepsT, None] | ContextResponse[DepsT, FormattableT]:
        """Generate an `llm.ContextResponse` by synchronously calling the Anthropic Messages API."""
        if _should_use_beta(model_id, format, toolkit):
            return self._beta_provider.context_call(
                ctx=ctx,
                model_id=model_id,
                messages=messages,
                toolkit=toolkit,
                format=format,
                **params,
            )

        input_messages, resolved_format, kwargs = _utils.encode_request(
            model_id=model_id,
            messages=messages,
            tools=toolkit,
            format=format,
            params=params,
        )
        anthropic_response = self.client.messages.create(**kwargs)
        include_thoughts = _utils.get_include_thoughts(params)
        assistant_message, finish_reason, usage = _utils.decode_response(
            anthropic_response, model_id, include_thoughts=include_thoughts
        )
        return ContextResponse(
            raw=anthropic_response,
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
        model_id: AnthropicModelId,
        messages: Sequence[Message],
        toolkit: AsyncToolkit,
        format: FormatSpec[FormattableT] | None = None,
        **params: Unpack[Params],
    ) -> AsyncResponse | AsyncResponse[FormattableT]:
        """Generate an `llm.AsyncResponse` by asynchronously calling the Anthropic Messages API."""
        if _should_use_beta(model_id, format, toolkit):
            return await self._beta_provider.call_async(
                model_id=model_id,
                messages=messages,
                toolkit=toolkit,
                format=format,
                **params,
            )

        input_messages, resolved_format, kwargs = _utils.encode_request(
            model_id=model_id,
            messages=messages,
            tools=toolkit,
            format=format,
            params=params,
        )
        anthropic_response = await self.async_client.messages.create(**kwargs)
        include_thoughts = _utils.get_include_thoughts(params)
        assistant_message, finish_reason, usage = _utils.decode_response(
            anthropic_response, model_id, include_thoughts=include_thoughts
        )
        return AsyncResponse(
            raw=anthropic_response,
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
        model_id: AnthropicModelId,
        messages: Sequence[Message],
        toolkit: AsyncContextToolkit[DepsT],
        format: FormatSpec[FormattableT] | None = None,
        **params: Unpack[Params],
    ) -> AsyncContextResponse[DepsT, None] | AsyncContextResponse[DepsT, FormattableT]:
        """Generate an `llm.AsyncContextResponse` by asynchronously calling the Anthropic Messages API."""
        if _should_use_beta(model_id, format, toolkit):
            return await self._beta_provider.context_call_async(
                ctx=ctx,
                model_id=model_id,
                messages=messages,
                toolkit=toolkit,
                format=format,
                **params,
            )

        input_messages, resolved_format, kwargs = _utils.encode_request(
            model_id=model_id,
            messages=messages,
            tools=toolkit,
            format=format,
            params=params,
        )
        anthropic_response = await self.async_client.messages.create(**kwargs)
        include_thoughts = _utils.get_include_thoughts(params)
        assistant_message, finish_reason, usage = _utils.decode_response(
            anthropic_response, model_id, include_thoughts=include_thoughts
        )
        return AsyncContextResponse(
            raw=anthropic_response,
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
        model_id: AnthropicModelId,
        messages: Sequence[Message],
        toolkit: Toolkit,
        format: FormatSpec[FormattableT] | None = None,
        **params: Unpack[Params],
    ) -> StreamResponse | StreamResponse[FormattableT]:
        """Generate an `llm.StreamResponse` by synchronously streaming from the Anthropic Messages API."""
        if _should_use_beta(model_id, format, toolkit):
            return self._beta_provider.stream(
                model_id=model_id,
                messages=messages,
                toolkit=toolkit,
                format=format,
                **params,
            )

        input_messages, resolved_format, kwargs = _utils.encode_request(
            model_id=model_id,
            messages=messages,
            tools=toolkit,
            format=format,
            params=params,
        )
        anthropic_stream = self.client.messages.stream(**kwargs)
        include_thoughts = _utils.get_include_thoughts(params)
        chunk_iterator = _utils.decode_stream(
            anthropic_stream, include_thoughts=include_thoughts
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
        model_id: AnthropicModelId,
        messages: Sequence[Message],
        toolkit: ContextToolkit[DepsT],
        format: FormatSpec[FormattableT] | None = None,
        **params: Unpack[Params],
    ) -> ContextStreamResponse[DepsT] | ContextStreamResponse[DepsT, FormattableT]:
        """Generate an `llm.ContextStreamResponse` by synchronously streaming from the Anthropic Messages API."""
        if _should_use_beta(model_id, format, toolkit):
            return self._beta_provider.context_stream(
                ctx=ctx,
                model_id=model_id,
                messages=messages,
                toolkit=toolkit,
                format=format,
                **params,
            )

        input_messages, resolved_format, kwargs = _utils.encode_request(
            model_id=model_id,
            messages=messages,
            tools=toolkit,
            format=format,
            params=params,
        )
        anthropic_stream = self.client.messages.stream(**kwargs)
        include_thoughts = _utils.get_include_thoughts(params)
        chunk_iterator = _utils.decode_stream(
            anthropic_stream, include_thoughts=include_thoughts
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
        model_id: AnthropicModelId,
        messages: Sequence[Message],
        toolkit: AsyncToolkit,
        format: FormatSpec[FormattableT] | None = None,
        **params: Unpack[Params],
    ) -> AsyncStreamResponse | AsyncStreamResponse[FormattableT]:
        """Generate an `llm.AsyncStreamResponse` by asynchronously streaming from the Anthropic Messages API."""
        if _should_use_beta(model_id, format, toolkit):
            return await self._beta_provider.stream_async(
                model_id=model_id,
                messages=messages,
                toolkit=toolkit,
                format=format,
                **params,
            )
        input_messages, resolved_format, kwargs = _utils.encode_request(
            model_id=model_id,
            messages=messages,
            tools=toolkit,
            format=format,
            params=params,
        )
        anthropic_stream = self.async_client.messages.stream(**kwargs)
        include_thoughts = _utils.get_include_thoughts(params)
        chunk_iterator = _utils.decode_async_stream(
            anthropic_stream, include_thoughts=include_thoughts
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
        model_id: AnthropicModelId,
        messages: Sequence[Message],
        toolkit: AsyncContextToolkit[DepsT],
        format: FormatSpec[FormattableT] | None = None,
        **params: Unpack[Params],
    ) -> (
        AsyncContextStreamResponse[DepsT]
        | AsyncContextStreamResponse[DepsT, FormattableT]
    ):
        """Generate an `llm.AsyncContextStreamResponse` by asynchronously streaming from the Anthropic Messages API."""
        if _should_use_beta(model_id, format, toolkit):
            return await self._beta_provider.context_stream_async(
                ctx=ctx,
                model_id=model_id,
                messages=messages,
                toolkit=toolkit,
                format=format,
                **params,
            )

        input_messages, resolved_format, kwargs = _utils.encode_request(
            model_id=model_id,
            messages=messages,
            tools=toolkit,
            format=format,
            params=params,
        )
        anthropic_stream = self.async_client.messages.stream(**kwargs)
        include_thoughts = _utils.get_include_thoughts(params)
        chunk_iterator = _utils.decode_async_stream(
            anthropic_stream, include_thoughts=include_thoughts
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
