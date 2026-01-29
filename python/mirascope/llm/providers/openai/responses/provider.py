"""OpenAI Responses API client implementation."""

from __future__ import annotations

from collections.abc import Sequence
from typing import TYPE_CHECKING
from typing_extensions import Unpack

from openai import AsyncOpenAI, BadRequestError as OpenAIBadRequestError, OpenAI

from ....context import Context, DepsT
from ....exceptions import BadRequestError, NotFoundError
from ....formatting import FormatSpec, FormattableT
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
from ....tools import AsyncContextToolkit, AsyncToolkit, ContextToolkit, Toolkit
from ...base import BaseProvider
from .. import _utils as _shared_utils
from ..model_id import OpenAIModelId, model_name
from . import _utils

if TYPE_CHECKING:
    from ....models import Params


class OpenAIResponsesProvider(BaseProvider[OpenAI]):
    """The client for the OpenAI Responses API."""

    id = "openai:responses"
    default_scope = "openai/"
    error_map = {
        **_shared_utils.OPENAI_ERROR_MAP,
        OpenAIBadRequestError: lambda e: NotFoundError
        if hasattr(e, "code") and e.code == "model_not_found"  # pyright: ignore[reportAttributeAccessIssue,reportUnknownMemberType]
        else BadRequestError,
    }

    def __init__(
        self,
        *,
        api_key: str | None = None,
        base_url: str | None = None,
    ) -> None:
        """Initialize the OpenAI Responses client."""
        self.client = OpenAI(api_key=api_key, base_url=base_url)
        self.async_client = AsyncOpenAI(api_key=api_key, base_url=base_url)

    def get_error_status(self, e: Exception) -> int | None:
        """Extract HTTP status code from OpenAI exception."""
        return getattr(e, "status_code", None)

    def _call(
        self,
        *,
        model_id: OpenAIModelId,
        messages: Sequence[Message],
        toolkit: Toolkit,
        format: FormatSpec[FormattableT] | None = None,
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
            tools=toolkit,
            format=format,
            params=params,
        )
        openai_response = self.client.responses.create(**kwargs)

        include_thoughts = _utils.get_include_thoughts(params)
        assistant_message, finish_reason, usage = _utils.decode_response(
            openai_response, model_id, self.id, include_thoughts=include_thoughts
        )
        provider_model_name = model_name(model_id, "responses")

        return Response(
            raw=openai_response,
            provider_id=self.id,
            model_id=model_id,
            provider_model_name=provider_model_name,
            params=params,
            tools=toolkit,
            input_messages=messages,
            assistant_message=assistant_message,
            finish_reason=finish_reason,
            usage=usage,
            format=format,
        )

    async def _call_async(
        self,
        *,
        model_id: OpenAIModelId,
        messages: Sequence[Message],
        toolkit: AsyncToolkit,
        format: FormatSpec[FormattableT] | None = None,
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
            tools=toolkit,
            format=format,
            params=params,
        )
        openai_response = await self.async_client.responses.create(**kwargs)

        include_thoughts = _utils.get_include_thoughts(params)
        assistant_message, finish_reason, usage = _utils.decode_response(
            openai_response, model_id, self.id, include_thoughts=include_thoughts
        )
        provider_model_name = model_name(model_id, "responses")

        return AsyncResponse(
            raw=openai_response,
            provider_id=self.id,
            model_id=model_id,
            provider_model_name=provider_model_name,
            params=params,
            tools=toolkit,
            input_messages=messages,
            assistant_message=assistant_message,
            finish_reason=finish_reason,
            usage=usage,
            format=format,
        )

    def _stream(
        self,
        *,
        model_id: OpenAIModelId,
        messages: Sequence[Message],
        toolkit: Toolkit,
        format: FormatSpec[FormattableT] | None = None,
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
            tools=toolkit,
            format=format,
            params=params,
        )
        openai_stream = self.client.responses.create(
            **kwargs,
            stream=True,
        )

        include_thoughts = _utils.get_include_thoughts(params)
        chunk_iterator = _utils.decode_stream(
            openai_stream, include_thoughts=include_thoughts
        )
        provider_model_name = model_name(model_id, "responses")

        return StreamResponse(
            provider_id=self.id,
            model_id=model_id,
            provider_model_name=provider_model_name,
            params=params,
            tools=toolkit,
            input_messages=messages,
            chunk_iterator=chunk_iterator,
            format=format,
        )

    async def _stream_async(
        self,
        *,
        model_id: OpenAIModelId,
        messages: Sequence[Message],
        toolkit: AsyncToolkit,
        format: FormatSpec[FormattableT] | None = None,
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
            tools=toolkit,
            format=format,
            params=params,
        )
        openai_stream = await self.async_client.responses.create(
            **kwargs,
            stream=True,
        )

        include_thoughts = _utils.get_include_thoughts(params)
        chunk_iterator = _utils.decode_async_stream(
            openai_stream, include_thoughts=include_thoughts
        )
        provider_model_name = model_name(model_id, "responses")

        return AsyncStreamResponse(
            provider_id=self.id,
            model_id=model_id,
            provider_model_name=provider_model_name,
            params=params,
            tools=toolkit,
            input_messages=messages,
            chunk_iterator=chunk_iterator,
            format=format,
        )

    def _context_call(
        self,
        *,
        ctx: Context[DepsT],
        model_id: OpenAIModelId,
        messages: Sequence[Message],
        toolkit: ContextToolkit[DepsT],
        format: FormatSpec[FormattableT] | None = None,
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
            tools=toolkit,
            format=format,
            params=params,
        )
        openai_response = self.client.responses.create(**kwargs)

        include_thoughts = _utils.get_include_thoughts(params)
        assistant_message, finish_reason, usage = _utils.decode_response(
            openai_response, model_id, self.id, include_thoughts=include_thoughts
        )
        provider_model_name = model_name(model_id, "responses")

        return ContextResponse(
            raw=openai_response,
            provider_id=self.id,
            model_id=model_id,
            provider_model_name=provider_model_name,
            params=params,
            tools=toolkit,
            input_messages=messages,
            assistant_message=assistant_message,
            finish_reason=finish_reason,
            usage=usage,
            format=format,
        )

    async def _context_call_async(
        self,
        *,
        ctx: Context[DepsT],
        model_id: OpenAIModelId,
        messages: Sequence[Message],
        toolkit: AsyncContextToolkit[DepsT],
        format: FormatSpec[FormattableT] | None = None,
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
            tools=toolkit,
            format=format,
            params=params,
        )
        openai_response = await self.async_client.responses.create(**kwargs)

        include_thoughts = _utils.get_include_thoughts(params)
        assistant_message, finish_reason, usage = _utils.decode_response(
            openai_response, model_id, self.id, include_thoughts=include_thoughts
        )
        provider_model_name = model_name(model_id, "responses")

        return AsyncContextResponse(
            raw=openai_response,
            provider_id=self.id,
            model_id=model_id,
            provider_model_name=provider_model_name,
            params=params,
            tools=toolkit,
            input_messages=messages,
            assistant_message=assistant_message,
            finish_reason=finish_reason,
            usage=usage,
            format=format,
        )

    def _context_stream(
        self,
        *,
        ctx: Context[DepsT],
        model_id: OpenAIModelId,
        messages: Sequence[Message],
        toolkit: ContextToolkit[DepsT],
        format: FormatSpec[FormattableT] | None = None,
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
            tools=toolkit,
            format=format,
            params=params,
        )

        openai_stream = self.client.responses.create(
            **kwargs,
            stream=True,
        )

        include_thoughts = _utils.get_include_thoughts(params)
        chunk_iterator = _utils.decode_stream(
            openai_stream, include_thoughts=include_thoughts
        )
        provider_model_name = model_name(model_id, "responses")

        return ContextStreamResponse(
            provider_id=self.id,
            model_id=model_id,
            provider_model_name=provider_model_name,
            params=params,
            tools=toolkit,
            input_messages=messages,
            chunk_iterator=chunk_iterator,
            format=format,
        )

    async def _context_stream_async(
        self,
        *,
        ctx: Context[DepsT],
        model_id: OpenAIModelId,
        messages: Sequence[Message],
        toolkit: AsyncContextToolkit[DepsT],
        format: FormatSpec[FormattableT] | None = None,
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
            tools=toolkit,
            format=format,
            params=params,
        )

        openai_stream = await self.async_client.responses.create(
            **kwargs,
            stream=True,
        )

        include_thoughts = _utils.get_include_thoughts(params)
        chunk_iterator = _utils.decode_async_stream(
            openai_stream, include_thoughts=include_thoughts
        )
        provider_model_name = model_name(model_id, "responses")

        return AsyncContextStreamResponse(
            provider_id=self.id,
            model_id=model_id,
            provider_model_name=provider_model_name,
            params=params,
            tools=toolkit,
            input_messages=messages,
            chunk_iterator=chunk_iterator,
            format=format,
        )
