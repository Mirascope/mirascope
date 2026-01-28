"""Google provider implementation."""

from __future__ import annotations

from collections.abc import Sequence
from typing import TYPE_CHECKING
from typing_extensions import Unpack

from google.genai import Client
from google.genai.types import HttpOptions

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
from .model_id import GoogleModelId, model_name

if TYPE_CHECKING:
    from ...models import Params


class GoogleProvider(BaseProvider[Client]):
    """The client for the Google LLM model."""

    id = "google"
    default_scope = "google/"
    error_map = _utils.GOOGLE_ERROR_MAP

    def __init__(
        self, *, api_key: str | None = None, base_url: str | None = None
    ) -> None:
        """Initialize the Google client."""
        http_options = None
        if base_url:
            http_options = HttpOptions(
                base_url=base_url,
                headers={"Authorization": f"Bearer {api_key}"},
            )

        self.client = Client(api_key=api_key, http_options=http_options)

    def get_error_status(self, e: Exception) -> int | None:
        """Extract HTTP status code from Google exception."""
        return getattr(e, "code", None)

    def _call(
        self,
        *,
        model_id: GoogleModelId,
        messages: Sequence[Message],
        toolkit: Toolkit,
        format: FormatSpec[FormattableT] | None = None,
        **params: Unpack[Params],
    ) -> Response | Response[FormattableT]:
        """Generate an `llm.Response` by synchronously calling the Google GenAI API.

        Args:
            model_id: Model identifier to use.
            messages: Messages to send to the LLM.
            tools: Optional tools that the model may invoke.
            format: Optional response format specifier.
            **params: Additional parameters to configure output (e.g. temperature). See `llm.Params`.

        Returns:
            An `llm.Response` object containing the LLM-generated content.
        """
        input_messages, format, kwargs = _utils.encode_request(
            model_id=model_id,
            messages=messages,
            tools=toolkit,
            format=format,
            params=params,
        )
        google_response = self.client.models.generate_content(**kwargs)

        include_thoughts = _utils.get_include_thoughts(params)
        assistant_message, finish_reason, usage = _utils.decode_response(
            google_response, model_id, include_thoughts=include_thoughts
        )

        return Response(
            raw=google_response,
            provider_id="google",
            model_id=model_id,
            provider_model_name=model_name(model_id),
            params=params,
            tools=toolkit,
            input_messages=input_messages,
            assistant_message=assistant_message,
            finish_reason=finish_reason,
            usage=usage,
            format=format,
        )

    def _context_call(
        self,
        *,
        ctx: Context[DepsT],
        model_id: GoogleModelId,
        messages: Sequence[Message],
        toolkit: ContextToolkit[DepsT],
        format: FormatSpec[FormattableT] | None = None,
        **params: Unpack[Params],
    ) -> ContextResponse[DepsT, None] | ContextResponse[DepsT, FormattableT]:
        """Generate an `llm.ContextResponse` by synchronously calling the Google GenAI API.

        Args:
            ctx: Context object with dependencies for tools.
            model_id: Model identifier to use.
            messages: Messages to send to the LLM.
            tools: Optional tools that the model may invoke.
            format: Optional response format specifier.
            **params: Additional parameters to configure output (e.g. temperature). See `llm.Params`.

        Returns:
            An `llm.ContextResponse` object containing the LLM-generated content.
        """
        input_messages, format, kwargs = _utils.encode_request(
            model_id=model_id,
            messages=messages,
            tools=toolkit,
            format=format,
            params=params,
        )
        google_response = self.client.models.generate_content(**kwargs)

        include_thoughts = _utils.get_include_thoughts(params)
        assistant_message, finish_reason, usage = _utils.decode_response(
            google_response, model_id, include_thoughts=include_thoughts
        )

        return ContextResponse(
            raw=google_response,
            provider_id="google",
            model_id=model_id,
            provider_model_name=model_name(model_id),
            params=params,
            tools=toolkit,
            input_messages=input_messages,
            assistant_message=assistant_message,
            finish_reason=finish_reason,
            usage=usage,
            format=format,
        )

    async def _call_async(
        self,
        *,
        model_id: GoogleModelId,
        messages: Sequence[Message],
        toolkit: AsyncToolkit,
        format: FormatSpec[FormattableT] | None = None,
        **params: Unpack[Params],
    ) -> AsyncResponse | AsyncResponse[FormattableT]:
        """Generate an `llm.AsyncResponse` by asynchronously calling the Google GenAI API.

        Args:
            model_id: Model identifier to use.
            messages: Messages to send to the LLM.
            tools: Optional tools that the model may invoke.
            format: Optional response format specifier.
            **params: Additional parameters to configure output (e.g. temperature). See `llm.Params`.

        Returns:
            An `llm.AsyncResponse` object containing the LLM-generated content.
        """
        input_messages, format, kwargs = _utils.encode_request(
            model_id=model_id,
            messages=messages,
            tools=toolkit,
            format=format,
            params=params,
        )
        google_response = await self.client.aio.models.generate_content(**kwargs)

        include_thoughts = _utils.get_include_thoughts(params)
        assistant_message, finish_reason, usage = _utils.decode_response(
            google_response, model_id, include_thoughts=include_thoughts
        )

        return AsyncResponse(
            raw=google_response,
            provider_id="google",
            model_id=model_id,
            provider_model_name=model_name(model_id),
            params=params,
            tools=toolkit,
            input_messages=input_messages,
            assistant_message=assistant_message,
            finish_reason=finish_reason,
            usage=usage,
            format=format,
        )

    async def _context_call_async(
        self,
        *,
        ctx: Context[DepsT],
        model_id: GoogleModelId,
        messages: Sequence[Message],
        toolkit: AsyncContextToolkit[DepsT],
        format: FormatSpec[FormattableT] | None = None,
        **params: Unpack[Params],
    ) -> AsyncContextResponse[DepsT, None] | AsyncContextResponse[DepsT, FormattableT]:
        """Generate an `llm.AsyncContextResponse` by asynchronously calling the Google GenAI API.

        Args:
            ctx: Context object with dependencies for tools.
            model_id: Model identifier to use.
            messages: Messages to send to the LLM.
            tools: Optional tools that the model may invoke.
            format: Optional response format specifier.
            **params: Additional parameters to configure output (e.g. temperature). See `llm.Params`.

        Returns:
            An `llm.AsyncContextResponse` object containing the LLM-generated content.
        """
        input_messages, format, kwargs = _utils.encode_request(
            model_id=model_id,
            messages=messages,
            tools=toolkit,
            format=format,
            params=params,
        )
        google_response = await self.client.aio.models.generate_content(**kwargs)

        include_thoughts = _utils.get_include_thoughts(params)
        assistant_message, finish_reason, usage = _utils.decode_response(
            google_response, model_id, include_thoughts=include_thoughts
        )

        return AsyncContextResponse(
            raw=google_response,
            provider_id="google",
            model_id=model_id,
            provider_model_name=model_name(model_id),
            params=params,
            tools=toolkit,
            input_messages=input_messages,
            assistant_message=assistant_message,
            finish_reason=finish_reason,
            usage=usage,
            format=format,
        )

    def _stream(
        self,
        *,
        model_id: GoogleModelId,
        messages: Sequence[Message],
        toolkit: Toolkit,
        format: FormatSpec[FormattableT] | None = None,
        **params: Unpack[Params],
    ) -> StreamResponse | StreamResponse[FormattableT]:
        """Generate an `llm.StreamResponse` by synchronously streaming from the Google GenAI API.

        Args:
            model_id: Model identifier to use.
            messages: Messages to send to the LLM.
            tools: Optional tools that the model may invoke.
            format: Optional response format specifier.
            **params: Additional parameters to configure output (e.g. temperature). See `llm.Params`.

        Returns:
            An `llm.StreamResponse` object for iterating over the LLM-generated content.
        """
        input_messages, format, kwargs = _utils.encode_request(
            model_id=model_id,
            messages=messages,
            tools=toolkit,
            format=format,
            params=params,
        )

        google_stream = self.client.models.generate_content_stream(**kwargs)

        include_thoughts = _utils.get_include_thoughts(params)
        chunk_iterator = _utils.decode_stream(
            google_stream, include_thoughts=include_thoughts
        )

        return StreamResponse(
            provider_id="google",
            model_id=model_id,
            provider_model_name=model_name(model_id),
            params=params,
            tools=toolkit,
            input_messages=input_messages,
            chunk_iterator=chunk_iterator,
            format=format,
        )

    def _context_stream(
        self,
        *,
        ctx: Context[DepsT],
        model_id: GoogleModelId,
        messages: Sequence[Message],
        toolkit: ContextToolkit[DepsT],
        format: FormatSpec[FormattableT] | None = None,
        **params: Unpack[Params],
    ) -> ContextStreamResponse[DepsT] | ContextStreamResponse[DepsT, FormattableT]:
        """Generate an `llm.ContextStreamResponse` by synchronously streaming from the Google GenAI API.

        Args:
            ctx: Context object with dependencies for tools.
            model_id: Model identifier to use.
            messages: Messages to send to the LLM.
            tools: Optional tools that the model may invoke.
            format: Optional response format specifier.
            **params: Additional parameters to configure output (e.g. temperature). See `llm.Params`.

        Returns:
            An `llm.ContextStreamResponse` object for iterating over the LLM-generated content.
        """
        input_messages, format, kwargs = _utils.encode_request(
            model_id=model_id,
            messages=messages,
            tools=toolkit,
            format=format,
            params=params,
        )

        google_stream = self.client.models.generate_content_stream(**kwargs)

        include_thoughts = _utils.get_include_thoughts(params)
        chunk_iterator = _utils.decode_stream(
            google_stream, include_thoughts=include_thoughts
        )

        return ContextStreamResponse(
            provider_id="google",
            model_id=model_id,
            provider_model_name=model_name(model_id),
            params=params,
            tools=toolkit,
            input_messages=input_messages,
            chunk_iterator=chunk_iterator,
            format=format,
        )

    async def _stream_async(
        self,
        *,
        model_id: GoogleModelId,
        messages: Sequence[Message],
        toolkit: AsyncToolkit,
        format: FormatSpec[FormattableT] | None = None,
        **params: Unpack[Params],
    ) -> AsyncStreamResponse | AsyncStreamResponse[FormattableT]:
        """Generate an `llm.AsyncStreamResponse` by asynchronously streaming from the Google GenAI API.

        Args:
            model_id: Model identifier to use.
            messages: Messages to send to the LLM.
            tools: Optional tools that the model may invoke.
            format: Optional response format specifier.
            **params: Additional parameters to configure output (e.g. temperature). See `llm.Params`.

        Returns:
            An `llm.AsyncStreamResponse` object for asynchronously iterating over the LLM-generated content.
        """
        input_messages, format, kwargs = _utils.encode_request(
            model_id=model_id,
            messages=messages,
            tools=toolkit,
            format=format,
            params=params,
        )

        google_stream = await self.client.aio.models.generate_content_stream(**kwargs)

        include_thoughts = _utils.get_include_thoughts(params)
        chunk_iterator = _utils.decode_async_stream(
            google_stream, include_thoughts=include_thoughts
        )

        return AsyncStreamResponse(
            provider_id="google",
            model_id=model_id,
            provider_model_name=model_name(model_id),
            params=params,
            tools=toolkit,
            input_messages=input_messages,
            chunk_iterator=chunk_iterator,
            format=format,
        )

    async def _context_stream_async(
        self,
        *,
        ctx: Context[DepsT],
        model_id: GoogleModelId,
        messages: Sequence[Message],
        toolkit: AsyncContextToolkit[DepsT],
        format: FormatSpec[FormattableT] | None = None,
        **params: Unpack[Params],
    ) -> (
        AsyncContextStreamResponse[DepsT]
        | AsyncContextStreamResponse[DepsT, FormattableT]
    ):
        """Generate an `llm.AsyncContextStreamResponse` by asynchronously streaming from the Google GenAI API.

        Args:
            ctx: Context object with dependencies for tools.
            model_id: Model identifier to use.
            messages: Messages to send to the LLM.
            tools: Optional tools that the model may invoke.
            format: Optional response format specifier.
            **params: Additional parameters to configure output (e.g. temperature). See `llm.Params`.

        Returns:
            An `llm.AsyncContextStreamResponse` object for asynchronously iterating over the LLM-generated content.
        """
        input_messages, format, kwargs = _utils.encode_request(
            model_id=model_id,
            messages=messages,
            tools=toolkit,
            format=format,
            params=params,
        )

        google_stream = await self.client.aio.models.generate_content_stream(**kwargs)

        include_thoughts = _utils.get_include_thoughts(params)
        chunk_iterator = _utils.decode_async_stream(
            google_stream, include_thoughts=include_thoughts
        )

        return AsyncContextStreamResponse(
            provider_id="google",
            model_id=model_id,
            provider_model_name=model_name(model_id),
            params=params,
            tools=toolkit,
            input_messages=input_messages,
            chunk_iterator=chunk_iterator,
            format=format,
        )
