"""Bedrock Anthropic provider implementation."""

from __future__ import annotations

import os
from collections.abc import Sequence
from typing import TYPE_CHECKING, ClassVar
from typing_extensions import Unpack

import httpx
from anthropic import AnthropicBedrock, AsyncAnthropicBedrock

from ....context import Context, DepsT
from ....formatting import Format, FormattableT, OutputParser
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
from ...anthropic import _utils as anthropic_utils
from ...base import BaseProvider
from .. import _utils as bedrock_utils
from ..model_id import BedrockModelId
from . import _utils

if TYPE_CHECKING:
    from ....models import Params


class BedrockAnthropicApiKeyClient(AnthropicBedrock):
    """AnthropicBedrock client that uses API key authentication instead of SigV4.

    This client overrides _prepare_request to inject a Bearer token for
    Bedrock's API key authentication, bypassing the default SigV4 signing.

    Note:
        The parent's _prepare_request only adds SigV4 authentication headers via
        get_auth_headers(). Since API key auth uses Bearer tokens instead, we
        intentionally skip the parent's implementation to avoid conflicting auth
        headers. This was verified against anthropic SDK v0.52.0+. SDK updates
        may require re-verification.
    """

    def __init__(
        self, api_key: str, aws_region: str, base_url: str | None = None
    ) -> None:
        self._bearer_token = api_key
        super().__init__(
            aws_region=aws_region,
            base_url=base_url,
        )

    def _prepare_request(self, request: httpx.Request) -> None:
        request.headers["Authorization"] = f"Bearer {self._bearer_token}"


class AsyncBedrockAnthropicApiKeyClient(AsyncAnthropicBedrock):
    """Async AnthropicBedrock client that uses API key authentication instead of SigV4.

    This client overrides _prepare_request to inject a Bearer token for
    Bedrock's API key authentication, bypassing the default SigV4 signing.

    Note:
        The parent's _prepare_request only adds SigV4 authentication headers via
        get_auth_headers(). Since API key auth uses Bearer tokens instead, we
        intentionally skip the parent's implementation to avoid conflicting auth
        headers. This was verified against anthropic SDK v0.52.0+. SDK updates
        may require re-verification.
    """

    def __init__(
        self, api_key: str, aws_region: str, base_url: str | None = None
    ) -> None:
        self._bearer_token = api_key
        super().__init__(
            aws_region=aws_region,
            base_url=base_url,
        )

    async def _prepare_request(self, request: httpx.Request) -> None:
        request.headers["Authorization"] = f"Bearer {self._bearer_token}"


class BedrockAnthropicProvider(BaseProvider[AnthropicBedrock]):
    """Provider for Anthropic models on Amazon Bedrock."""

    id: ClassVar[str] = "bedrock:anthropic"
    default_scope: ClassVar[str | list[str]] = bedrock_utils.default_anthropic_scopes()
    api_key_env_var: ClassVar[str] = "AWS_BEDROCK_ANTHROPIC_API_KEY"
    error_map = anthropic_utils.ANTHROPIC_ERROR_MAP

    def __init__(
        self,
        *,
        api_key: str | None = None,
        aws_region: str | None = None,
        aws_access_key: str | None = None,
        aws_secret_key: str | None = None,
        aws_session_token: str | None = None,
        aws_profile: str | None = None,
        base_url: str | None = None,
    ) -> None:
        """Initialize the Bedrock Anthropic provider.

        Args:
            api_key: Optional API key for authentication. If provided, this takes
                priority over AWS credentials. Falls back to AWS_BEDROCK_ANTHROPIC_API_KEY
                environment variable.
            aws_region: AWS region for Bedrock. Defaults to environment configuration.
            aws_access_key: AWS access key ID. Defaults to environment configuration.
            aws_secret_key: AWS secret access key. Defaults to environment configuration.
            aws_session_token: AWS session token for temporary credentials.
            aws_profile: AWS profile name for credentials. Defaults to environment.
            base_url: Custom base URL for Bedrock endpoint (e.g., for GovCloud).
        """
        resolved_api_key = api_key or os.environ.get(self.api_key_env_var)
        resolved_region = (
            aws_region
            or os.environ.get("AWS_REGION")
            or os.environ.get("AWS_DEFAULT_REGION")
            or "us-east-1"
        )

        if resolved_api_key:
            self.client = BedrockAnthropicApiKeyClient(
                api_key=resolved_api_key,
                aws_region=resolved_region,
                base_url=base_url,
            )
            self.async_client = AsyncBedrockAnthropicApiKeyClient(
                api_key=resolved_api_key,
                aws_region=resolved_region,
                base_url=base_url,
            )
        else:
            self.client = AnthropicBedrock(
                aws_region=aws_region,
                aws_access_key=aws_access_key,
                aws_secret_key=aws_secret_key,
                aws_session_token=aws_session_token,
                aws_profile=aws_profile,
                base_url=base_url,
            )
            self.async_client = AsyncAnthropicBedrock(
                aws_region=aws_region,
                aws_access_key=aws_access_key,
                aws_secret_key=aws_secret_key,
                aws_session_token=aws_session_token,
                aws_profile=aws_profile,
                base_url=base_url,
            )

    def get_error_status(self, e: Exception) -> int | None:
        """Extract HTTP status code from Anthropic exception."""
        return getattr(e, "status_code", None)

    def _model_name(self, model_id: str) -> str:
        return _utils.bedrock_anthropic_model_name(model_id)

    def _call(
        self,
        *,
        model_id: BedrockModelId,
        messages: Sequence[Message],
        tools: Sequence[Tool] | Toolkit | None = None,
        format: type[FormattableT]
        | Format[FormattableT]
        | OutputParser[FormattableT]
        | None = None,
        **params: Unpack[Params],
    ) -> Response | Response[FormattableT]:
        """Generate an `llm.Response` by synchronously calling the Bedrock API."""
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
        model_id: BedrockModelId,
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
        """Generate an `llm.ContextResponse` by calling the Bedrock API."""
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
        model_id: BedrockModelId,
        messages: Sequence[Message],
        tools: Sequence[AsyncTool] | AsyncToolkit | None = None,
        format: type[FormattableT]
        | Format[FormattableT]
        | OutputParser[FormattableT]
        | None = None,
        **params: Unpack[Params],
    ) -> AsyncResponse | AsyncResponse[FormattableT]:
        """Generate an `llm.AsyncResponse` by calling the Bedrock API."""
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
        model_id: BedrockModelId,
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
        """Generate an `llm.AsyncContextResponse` by calling the Bedrock API."""
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
        model_id: BedrockModelId,
        messages: Sequence[Message],
        tools: Sequence[Tool] | Toolkit | None = None,
        format: type[FormattableT]
        | Format[FormattableT]
        | OutputParser[FormattableT]
        | None = None,
        **params: Unpack[Params],
    ) -> StreamResponse | StreamResponse[FormattableT]:
        """Generate an `llm.StreamResponse` by streaming the Bedrock API response."""
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
        model_id: BedrockModelId,
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
        """Generate an `llm.ContextStreamResponse` by streaming the Bedrock API."""
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
        model_id: BedrockModelId,
        messages: Sequence[Message],
        tools: Sequence[AsyncTool] | AsyncToolkit | None = None,
        format: type[FormattableT]
        | Format[FormattableT]
        | OutputParser[FormattableT]
        | None = None,
        **params: Unpack[Params],
    ) -> AsyncStreamResponse | AsyncStreamResponse[FormattableT]:
        """Generate an `llm.AsyncStreamResponse` by streaming the Bedrock API."""
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
        model_id: BedrockModelId,
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
        """Generate an `llm.AsyncContextStreamResponse` by streaming the Bedrock API."""
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


class BedrockAnthropicRoutedProvider(BedrockAnthropicProvider):
    """Bedrock Anthropic provider that reports provider_id as 'bedrock'."""

    id: ClassVar[str] = "bedrock"
