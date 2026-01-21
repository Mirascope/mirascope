"""Azure Anthropic provider implementation."""

from __future__ import annotations

import os
from collections.abc import Sequence
from typing import TYPE_CHECKING, ClassVar
from typing_extensions import Unpack

from anthropic.lib.foundry import (
    AnthropicFoundry,
    AsyncAnthropicFoundry,
    AsyncAzureADTokenProvider,
    AzureADTokenProvider,
)

from ....context import Context, DepsT
from ....formatting import Format, FormattableT, OutputParser, resolve_format
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
    AnyToolSchema,
    AsyncContextTool,
    AsyncContextToolkit,
    AsyncTool,
    AsyncToolkit,
    BaseToolkit,
    ContextTool,
    ContextToolkit,
    Tool,
    Toolkit,
)
from ...anthropic import _utils as anthropic_utils
from ...anthropic.model_info import MODELS_WITHOUT_STRICT_STRUCTURED_OUTPUTS
from ...base import BaseProvider, _utils as _base_utils
from .. import _utils as azure_utils
from ..model_id import AzureModelId
from . import _utils
from .beta_provider import AzureAnthropicBetaProvider

if TYPE_CHECKING:
    from ....models import Params


def _should_use_beta(
    model_id: AzureModelId,
    format: type[FormattableT]
    | Format[FormattableT]
    | OutputParser[FormattableT]
    | None,
    tools: Sequence[AnyToolSchema] | BaseToolkit[AnyToolSchema] | None,
) -> bool:
    """Determine whether to use the beta API based on format mode or strict tools."""
    if _utils.azure_model_name(model_id) in MODELS_WITHOUT_STRICT_STRUCTURED_OUTPUTS:
        return False

    resolved = resolve_format(format, default_mode=anthropic_utils.DEFAULT_FORMAT_MODE)
    if resolved is not None and resolved.mode == "strict":
        return True

    return _base_utils.has_strict_tools(tools)


class AzureAnthropicProvider(BaseProvider[AnthropicFoundry]):
    """Provider for Azure-hosted Anthropic Claude models."""

    id: ClassVar[str] = "azure:anthropic"
    default_scope: ClassVar[str | list[str]] = azure_utils.default_anthropic_scopes()
    error_map = anthropic_utils.ANTHROPIC_ERROR_MAP
    _beta_provider: AzureAnthropicBetaProvider

    def __init__(
        self,
        *,
        api_key: str | None = None,
        base_url: str | None = None,
        azure_ad_token_provider: AzureADTokenProvider
        | AsyncAzureADTokenProvider
        | None = None,
    ) -> None:
        """Initialize the Azure Anthropic provider."""
        resolved_api_key = api_key or os.environ.get("AZURE_ANTHROPIC_API_KEY")
        resolved_base_url = base_url or os.environ.get("AZURE_AI_ANTHROPIC_ENDPOINT")

        if not resolved_api_key and azure_ad_token_provider is None:
            raise ValueError(
                "Azure Anthropic API key or Azure AD token provider is required. "
                "Set the AZURE_ANTHROPIC_API_KEY environment variable "
                "or pass the api_key or azure_ad_token_provider parameter to "
                "register_provider()."
            )

        if not resolved_base_url:
            raise ValueError(
                "Azure Anthropic endpoint is required. "
                "Set the AZURE_AI_ANTHROPIC_ENDPOINT environment variable "
                "or pass the base_url parameter to register_provider()."
            )

        normalized_base_url = _utils.normalize_base_url(resolved_base_url)
        sync_token_provider = _utils.coerce_sync_token_provider(azure_ad_token_provider)
        async_token_provider = _utils.coerce_async_token_provider(
            azure_ad_token_provider
        )

        self.client = AnthropicFoundry(
            api_key=resolved_api_key,
            azure_ad_token_provider=sync_token_provider,
            base_url=normalized_base_url,
        )
        self.async_client = AsyncAnthropicFoundry(
            api_key=resolved_api_key,
            azure_ad_token_provider=async_token_provider,
            base_url=normalized_base_url,
        )
        self._beta_provider = AzureAnthropicBetaProvider(
            api_key=resolved_api_key,
            base_url=normalized_base_url,
            azure_ad_token_provider=azure_ad_token_provider,
        )

    def get_error_status(self, e: Exception) -> int | None:
        """Extract HTTP status code from Anthropic exception."""
        return getattr(e, "status_code", None)

    def _model_name(self, model_id: str) -> str:
        """Strip 'azure/' prefix from model ID for Azure Anthropic API."""
        return _utils.azure_model_name(model_id)

    def _call(
        self,
        *,
        model_id: AzureModelId,
        messages: Sequence[Message],
        tools: Sequence[Tool] | Toolkit | None = None,
        format: type[FormattableT]
        | Format[FormattableT]
        | OutputParser[FormattableT]
        | None = None,
        **params: Unpack[Params],
    ) -> Response | Response[FormattableT]:
        """Generate an `llm.Response` by synchronously calling the Azure API."""
        if _should_use_beta(model_id, format, tools):
            return self._beta_provider.call(
                model_id=model_id,
                messages=messages,
                tools=tools,
                format=format,
                **params,
            )

        input_messages, resolved_format, kwargs = _utils.encode_request(
            model_id=model_id,
            messages=messages,
            tools=tools,
            format=format,
            params=params,
        )
        anthropic_response = self.client.messages.create(**kwargs)
        include_thoughts = anthropic_utils.get_include_thoughts(params)
        assistant_message, finish_reason, usage = _utils.decode_response(
            anthropic_response,
            model_id,
            include_thoughts=include_thoughts,
            provider_id=self.id,
        )
        return Response(
            raw=anthropic_response,
            provider_id=self.id,
            model_id=model_id,
            provider_model_name=self._model_name(model_id),
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
        model_id: AzureModelId,
        messages: Sequence[Message],
        tools: Sequence[Tool | ContextTool[DepsT]]
        | ContextToolkit[DepsT]
        | None = None,
        format: type[FormattableT]
        | Format[FormattableT]
        | OutputParser[FormattableT]
        | None = None,
        **params: Unpack[Params],
    ) -> ContextResponse[DepsT, None] | ContextResponse[DepsT, FormattableT]:
        """Generate an `llm.ContextResponse` by calling the Azure API."""
        if _should_use_beta(model_id, format, tools):
            return self._beta_provider.context_call(
                ctx=ctx,
                model_id=model_id,
                messages=messages,
                tools=tools,
                format=format,
                **params,
            )

        input_messages, resolved_format, kwargs = _utils.encode_request(
            model_id=model_id,
            messages=messages,
            tools=tools,
            format=format,
            params=params,
        )
        anthropic_response = self.client.messages.create(**kwargs)
        include_thoughts = anthropic_utils.get_include_thoughts(params)
        assistant_message, finish_reason, usage = _utils.decode_response(
            anthropic_response,
            model_id,
            include_thoughts=include_thoughts,
            provider_id=self.id,
        )
        return ContextResponse(
            raw=anthropic_response,
            provider_id=self.id,
            model_id=model_id,
            provider_model_name=self._model_name(model_id),
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
        model_id: AzureModelId,
        messages: Sequence[Message],
        tools: Sequence[AsyncTool] | AsyncToolkit | None = None,
        format: type[FormattableT]
        | Format[FormattableT]
        | OutputParser[FormattableT]
        | None = None,
        **params: Unpack[Params],
    ) -> AsyncResponse | AsyncResponse[FormattableT]:
        """Generate an `llm.AsyncResponse` by calling the Azure API."""
        if _should_use_beta(model_id, format, tools):
            return await self._beta_provider.call_async(
                model_id=model_id,
                messages=messages,
                tools=tools,
                format=format,
                **params,
            )

        input_messages, resolved_format, kwargs = _utils.encode_request(
            model_id=model_id,
            messages=messages,
            tools=tools,
            format=format,
            params=params,
        )
        anthropic_response = await self.async_client.messages.create(**kwargs)
        include_thoughts = anthropic_utils.get_include_thoughts(params)
        assistant_message, finish_reason, usage = _utils.decode_response(
            anthropic_response,
            model_id,
            include_thoughts=include_thoughts,
            provider_id=self.id,
        )
        return AsyncResponse(
            raw=anthropic_response,
            provider_id=self.id,
            model_id=model_id,
            provider_model_name=self._model_name(model_id),
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
        model_id: AzureModelId,
        messages: Sequence[Message],
        tools: Sequence[AsyncTool | AsyncContextTool[DepsT]]
        | AsyncContextToolkit[DepsT]
        | None = None,
        format: type[FormattableT]
        | Format[FormattableT]
        | OutputParser[FormattableT]
        | None = None,
        **params: Unpack[Params],
    ) -> AsyncContextResponse[DepsT, None] | AsyncContextResponse[DepsT, FormattableT]:
        """Generate an `llm.AsyncContextResponse` by calling the Azure API."""
        if _should_use_beta(model_id, format, tools):
            return await self._beta_provider.context_call_async(
                ctx=ctx,
                model_id=model_id,
                messages=messages,
                tools=tools,
                format=format,
                **params,
            )

        input_messages, resolved_format, kwargs = _utils.encode_request(
            model_id=model_id,
            messages=messages,
            tools=tools,
            format=format,
            params=params,
        )
        anthropic_response = await self.async_client.messages.create(**kwargs)
        include_thoughts = anthropic_utils.get_include_thoughts(params)
        assistant_message, finish_reason, usage = _utils.decode_response(
            anthropic_response,
            model_id,
            include_thoughts=include_thoughts,
            provider_id=self.id,
        )
        return AsyncContextResponse(
            raw=anthropic_response,
            provider_id=self.id,
            model_id=model_id,
            provider_model_name=self._model_name(model_id),
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
        model_id: AzureModelId,
        messages: Sequence[Message],
        tools: Sequence[Tool] | Toolkit | None = None,
        format: type[FormattableT]
        | Format[FormattableT]
        | OutputParser[FormattableT]
        | None = None,
        **params: Unpack[Params],
    ) -> StreamResponse | StreamResponse[FormattableT]:
        """Generate an `llm.StreamResponse` by streaming the Azure API response."""
        if _should_use_beta(model_id, format, tools):
            return self._beta_provider.stream(
                model_id=model_id,
                messages=messages,
                tools=tools,
                format=format,
                **params,
            )

        input_messages, resolved_format, kwargs = _utils.encode_request(
            model_id=model_id,
            messages=messages,
            tools=tools,
            format=format,
            params=params,
        )
        anthropic_stream = self.client.messages.stream(**kwargs)
        include_thoughts = anthropic_utils.get_include_thoughts(params)
        chunk_iterator = anthropic_utils.decode_stream(
            anthropic_stream, include_thoughts=include_thoughts
        )
        return StreamResponse(
            provider_id=self.id,
            model_id=model_id,
            provider_model_name=self._model_name(model_id),
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
        model_id: AzureModelId,
        messages: Sequence[Message],
        tools: Sequence[Tool | ContextTool[DepsT]]
        | ContextToolkit[DepsT]
        | None = None,
        format: type[FormattableT]
        | Format[FormattableT]
        | OutputParser[FormattableT]
        | None = None,
        **params: Unpack[Params],
    ) -> ContextStreamResponse[DepsT] | ContextStreamResponse[DepsT, FormattableT]:
        """Generate an `llm.ContextStreamResponse` by streaming the Azure API."""
        if _should_use_beta(model_id, format, tools):
            return self._beta_provider.context_stream(
                ctx=ctx,
                model_id=model_id,
                messages=messages,
                tools=tools,
                format=format,
                **params,
            )

        input_messages, resolved_format, kwargs = _utils.encode_request(
            model_id=model_id,
            messages=messages,
            tools=tools,
            format=format,
            params=params,
        )
        anthropic_stream = self.client.messages.stream(**kwargs)
        include_thoughts = anthropic_utils.get_include_thoughts(params)
        chunk_iterator = anthropic_utils.decode_stream(
            anthropic_stream, include_thoughts=include_thoughts
        )
        return ContextStreamResponse(
            provider_id=self.id,
            model_id=model_id,
            provider_model_name=self._model_name(model_id),
            params=params,
            tools=tools,
            input_messages=input_messages,
            chunk_iterator=chunk_iterator,
            format=resolved_format,
        )

    async def _stream_async(
        self,
        *,
        model_id: AzureModelId,
        messages: Sequence[Message],
        tools: Sequence[AsyncTool] | AsyncToolkit | None = None,
        format: type[FormattableT]
        | Format[FormattableT]
        | OutputParser[FormattableT]
        | None = None,
        **params: Unpack[Params],
    ) -> AsyncStreamResponse | AsyncStreamResponse[FormattableT]:
        """Generate an `llm.AsyncStreamResponse` by streaming the Azure API."""
        if _should_use_beta(model_id, format, tools):
            return await self._beta_provider.stream_async(
                model_id=model_id,
                messages=messages,
                tools=tools,
                format=format,
                **params,
            )

        input_messages, resolved_format, kwargs = _utils.encode_request(
            model_id=model_id,
            messages=messages,
            tools=tools,
            format=format,
            params=params,
        )
        anthropic_stream = self.async_client.messages.stream(**kwargs)
        include_thoughts = anthropic_utils.get_include_thoughts(params)
        chunk_iterator = anthropic_utils.decode_async_stream(
            anthropic_stream, include_thoughts=include_thoughts
        )
        return AsyncStreamResponse(
            provider_id=self.id,
            model_id=model_id,
            provider_model_name=self._model_name(model_id),
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
        model_id: AzureModelId,
        messages: Sequence[Message],
        tools: Sequence[AsyncTool | AsyncContextTool[DepsT]]
        | AsyncContextToolkit[DepsT]
        | None = None,
        format: type[FormattableT]
        | Format[FormattableT]
        | OutputParser[FormattableT]
        | None = None,
        **params: Unpack[Params],
    ) -> (
        AsyncContextStreamResponse[DepsT]
        | AsyncContextStreamResponse[DepsT, FormattableT]
    ):
        """Generate an `llm.AsyncContextStreamResponse` by streaming the Azure API."""
        if _should_use_beta(model_id, format, tools):
            return await self._beta_provider.context_stream_async(
                ctx=ctx,
                model_id=model_id,
                messages=messages,
                tools=tools,
                format=format,
                **params,
            )

        input_messages, resolved_format, kwargs = _utils.encode_request(
            model_id=model_id,
            messages=messages,
            tools=tools,
            format=format,
            params=params,
        )
        anthropic_stream = self.async_client.messages.stream(**kwargs)
        include_thoughts = anthropic_utils.get_include_thoughts(params)
        chunk_iterator = anthropic_utils.decode_async_stream(
            anthropic_stream, include_thoughts=include_thoughts
        )
        return AsyncContextStreamResponse(
            provider_id=self.id,
            model_id=model_id,
            provider_model_name=self._model_name(model_id),
            params=params,
            tools=tools,
            input_messages=input_messages,
            chunk_iterator=chunk_iterator,
            format=resolved_format,
        )


class AzureAnthropicRoutedProvider(AzureAnthropicProvider):
    """Azure Anthropic provider that reports provider_id as 'azure'."""

    id: ClassVar[str] = "azure"
