"""Anthropic client implementation."""

from collections.abc import Sequence
from typing_extensions import Unpack

from anthropic import Anthropic, AsyncAnthropic

from ...context import Context, DepsT
from ...formatting import Format, FormattableT, resolve_format
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
from ..base import Params
from . import _utils
from .base_provider import BaseAnthropicProvider
from .beta_provider import AnthropicBetaProvider
from .model_id import AnthropicModelId, model_name
from .model_info import MODELS_WITHOUT_STRICT_STRUCTURED_OUTPUTS


def _should_use_beta(
    model_id: AnthropicModelId,
    format: type[FormattableT] | Format[FormattableT] | None,
) -> bool:
    """Determine whether to use the beta API based on format mode.

    If the format resolves to strict mode, and the model plausibly has
    strict structured output support, then we will use the beta provider.
    """
    resolved = resolve_format(format, default_mode=_utils.DEFAULT_FORMAT_MODE)
    if resolved is None or resolved.mode != "strict":
        return False
    return model_name(model_id) not in MODELS_WITHOUT_STRICT_STRUCTURED_OUTPUTS


class AnthropicProvider(BaseAnthropicProvider):
    """The client for the Anthropic LLM model.

    Note: Azure-hosted Claude models use AzureAnthropicProvider which also
    inherits from BaseAnthropicProvider. Common logic (encode/decode, etc.)
    is implemented in the base class. Do not add provider-specific logic here
    that would break Azure routing.
    """

    id = "anthropic"
    default_scope = "anthropic/"
    _beta_provider: AnthropicBetaProvider

    def __init__(
        self, *, api_key: str | None = None, base_url: str | None = None
    ) -> None:
        """Initialize the Anthropic client."""
        self.client = Anthropic(api_key=api_key, base_url=base_url)
        self.async_client = AsyncAnthropic(api_key=api_key, base_url=base_url)
        self._beta_provider = AnthropicBetaProvider(api_key=api_key, base_url=base_url)

    def _call(
        self,
        *,
        model_id: AnthropicModelId,
        messages: Sequence[Message],
        tools: Sequence[Tool] | Toolkit | None = None,
        format: type[FormattableT] | Format[FormattableT] | None = None,
        **params: Unpack[Params],
    ) -> Response | Response[FormattableT]:
        """Generate an `llm.Response` by synchronously calling the Anthropic Messages API."""
        if _should_use_beta(model_id, format):
            return self._beta_provider.call(
                model_id=model_id,
                messages=messages,
                tools=tools,
                format=format,
                **params,
            )
        return super()._call(
            model_id=model_id,
            messages=messages,
            tools=tools,
            format=format,
            **params,
        )

    def _context_call(
        self,
        *,
        ctx: Context[DepsT],
        model_id: AnthropicModelId,
        messages: Sequence[Message],
        tools: Sequence[Tool | ContextTool[DepsT]]
        | ContextToolkit[DepsT]
        | None = None,
        format: type[FormattableT] | Format[FormattableT] | None = None,
        **params: Unpack[Params],
    ) -> ContextResponse[DepsT, None] | ContextResponse[DepsT, FormattableT]:
        """Generate an `llm.ContextResponse` by synchronously calling the Anthropic Messages API."""
        if _should_use_beta(model_id, format):
            return self._beta_provider.context_call(
                ctx=ctx,
                model_id=model_id,
                messages=messages,
                tools=tools,
                format=format,
                **params,
            )
        return super()._context_call(
            ctx=ctx,
            model_id=model_id,
            messages=messages,
            tools=tools,
            format=format,
            **params,
        )

    async def _call_async(
        self,
        *,
        model_id: AnthropicModelId,
        messages: Sequence[Message],
        tools: Sequence[AsyncTool] | AsyncToolkit | None = None,
        format: type[FormattableT] | Format[FormattableT] | None = None,
        **params: Unpack[Params],
    ) -> AsyncResponse | AsyncResponse[FormattableT]:
        """Generate an `llm.AsyncResponse` by asynchronously calling the Anthropic Messages API."""
        if _should_use_beta(model_id, format):
            return await self._beta_provider.call_async(
                model_id=model_id,
                messages=messages,
                tools=tools,
                format=format,
                **params,
            )
        return await super()._call_async(
            model_id=model_id,
            messages=messages,
            tools=tools,
            format=format,
            **params,
        )

    async def _context_call_async(
        self,
        *,
        ctx: Context[DepsT],
        model_id: AnthropicModelId,
        messages: Sequence[Message],
        tools: Sequence[AsyncTool | AsyncContextTool[DepsT]]
        | AsyncContextToolkit[DepsT]
        | None = None,
        format: type[FormattableT] | Format[FormattableT] | None = None,
        **params: Unpack[Params],
    ) -> AsyncContextResponse[DepsT, None] | AsyncContextResponse[DepsT, FormattableT]:
        """Generate an `llm.AsyncContextResponse` by asynchronously calling the Anthropic Messages API."""
        if _should_use_beta(model_id, format):
            return await self._beta_provider.context_call_async(
                ctx=ctx,
                model_id=model_id,
                messages=messages,
                tools=tools,
                format=format,
                **params,
            )
        return await super()._context_call_async(
            ctx=ctx,
            model_id=model_id,
            messages=messages,
            tools=tools,
            format=format,
            **params,
        )

    def _stream(
        self,
        *,
        model_id: AnthropicModelId,
        messages: Sequence[Message],
        tools: Sequence[Tool] | Toolkit | None = None,
        format: type[FormattableT] | Format[FormattableT] | None = None,
        **params: Unpack[Params],
    ) -> StreamResponse | StreamResponse[FormattableT]:
        """Generate an `llm.StreamResponse` by synchronously streaming from the Anthropic Messages API."""
        if _should_use_beta(model_id, format):
            return self._beta_provider.stream(
                model_id=model_id,
                messages=messages,
                tools=tools,
                format=format,
                **params,
            )
        return super()._stream(
            model_id=model_id,
            messages=messages,
            tools=tools,
            format=format,
            **params,
        )

    def _context_stream(
        self,
        *,
        ctx: Context[DepsT],
        model_id: AnthropicModelId,
        messages: Sequence[Message],
        tools: Sequence[Tool | ContextTool[DepsT]]
        | ContextToolkit[DepsT]
        | None = None,
        format: type[FormattableT] | Format[FormattableT] | None = None,
        **params: Unpack[Params],
    ) -> ContextStreamResponse[DepsT] | ContextStreamResponse[DepsT, FormattableT]:
        """Generate an `llm.ContextStreamResponse` by synchronously streaming from the Anthropic Messages API."""
        if _should_use_beta(model_id, format):
            return self._beta_provider.context_stream(
                ctx=ctx,
                model_id=model_id,
                messages=messages,
                tools=tools,
                format=format,
                **params,
            )
        return super()._context_stream(
            ctx=ctx,
            model_id=model_id,
            messages=messages,
            tools=tools,
            format=format,
            **params,
        )

    async def _stream_async(
        self,
        *,
        model_id: AnthropicModelId,
        messages: Sequence[Message],
        tools: Sequence[AsyncTool] | AsyncToolkit | None = None,
        format: type[FormattableT] | Format[FormattableT] | None = None,
        **params: Unpack[Params],
    ) -> AsyncStreamResponse | AsyncStreamResponse[FormattableT]:
        """Generate an `llm.AsyncStreamResponse` by asynchronously streaming from the Anthropic Messages API."""
        if _should_use_beta(model_id, format):
            return await self._beta_provider.stream_async(
                model_id=model_id,
                messages=messages,
                tools=tools,
                format=format,
                **params,
            )
        return await super()._stream_async(
            model_id=model_id,
            messages=messages,
            tools=tools,
            format=format,
            **params,
        )

    async def _context_stream_async(
        self,
        *,
        ctx: Context[DepsT],
        model_id: AnthropicModelId,
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
        """Generate an `llm.AsyncContextStreamResponse` by asynchronously streaming from the Anthropic Messages API."""
        if _should_use_beta(model_id, format):
            return await self._beta_provider.context_stream_async(
                ctx=ctx,
                model_id=model_id,
                messages=messages,
                tools=tools,
                format=format,
                **params,
            )
        return await super()._context_stream_async(
            ctx=ctx,
            model_id=model_id,
            messages=messages,
            tools=tools,
            format=format,
            **params,
        )
