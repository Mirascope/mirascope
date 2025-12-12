"""OpenAI client implementation."""

from collections.abc import Sequence
from typing import Literal
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
from ...base import BaseProvider, Params
from ..model_id import OpenAIModelId, model_name
from . import _utils


class OpenAICompletionsProvider(BaseProvider[OpenAI]):
    """The client for the OpenAI LLM model."""

    id = "openai:completions"
    default_scope = "openai/"

    def __init__(
        self,
        *,
        api_key: str | None = None,
        base_url: str | None = None,
        wrapped_by_openai_provider: bool = False,
    ) -> None:
        """Initialize the OpenAI client."""
        self.client = OpenAI(api_key=api_key, base_url=base_url)
        self.async_client = AsyncOpenAI(api_key=api_key, base_url=base_url)
        self.active_provider_id: Literal["openai", "openai:completions"] = (
            "openai" if wrapped_by_openai_provider else "openai:completions"
        )

    def _call(
        self,
        *,
        model_id: OpenAIModelId,
        messages: Sequence[Message],
        tools: Sequence[Tool] | Toolkit | None = None,
        format: type[FormattableT] | Format[FormattableT] | None = None,
        **params: Unpack[Params],
    ) -> Response | Response[FormattableT]:
        """Generate an `llm.Response` by synchronously calling the OpenAI ChatCompletions API.

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
            tools=tools,
            format=format,
            params=params,
        )

        openai_response = self.client.chat.completions.create(**kwargs)

        assistant_message, finish_reason = _utils.decode_response(
            openai_response, model_id, self.active_provider_id
        )

        return Response(
            raw=openai_response,
            provider_id=self.active_provider_id,
            model_id=model_id,
            provider_model_name=model_name(model_id, "completions"),
            params=params,
            tools=tools,
            input_messages=input_messages,
            assistant_message=assistant_message,
            finish_reason=finish_reason,
            format=format,
        )

    def _context_call(
        self,
        *,
        ctx: Context[DepsT],
        model_id: OpenAIModelId,
        messages: Sequence[Message],
        tools: Sequence[Tool | ContextTool[DepsT]]
        | ContextToolkit[DepsT]
        | None = None,
        format: type[FormattableT] | Format[FormattableT] | None = None,
        **params: Unpack[Params],
    ) -> ContextResponse[DepsT, None] | ContextResponse[DepsT, FormattableT]:
        """Generate an `llm.ContextResponse` by synchronously calling the OpenAI ChatCompletions API.

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
            tools=tools,
            format=format,
            params=params,
        )

        openai_response = self.client.chat.completions.create(**kwargs)

        assistant_message, finish_reason = _utils.decode_response(
            openai_response, model_id, self.active_provider_id
        )

        return ContextResponse(
            raw=openai_response,
            provider_id=self.active_provider_id,
            model_id=model_id,
            provider_model_name=model_name(model_id, "completions"),
            params=params,
            tools=tools,
            input_messages=input_messages,
            assistant_message=assistant_message,
            finish_reason=finish_reason,
            format=format,
        )

    async def _call_async(
        self,
        *,
        model_id: OpenAIModelId,
        messages: Sequence[Message],
        tools: Sequence[AsyncTool] | AsyncToolkit | None = None,
        format: type[FormattableT] | Format[FormattableT] | None = None,
        **params: Unpack[Params],
    ) -> AsyncResponse | AsyncResponse[FormattableT]:
        """Generate an `llm.AsyncResponse` by asynchronously calling the OpenAI ChatCompletions API.

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
            params=params,
            messages=messages,
            tools=tools,
            format=format,
        )

        openai_response = await self.async_client.chat.completions.create(**kwargs)

        assistant_message, finish_reason = _utils.decode_response(
            openai_response, model_id, self.active_provider_id
        )

        return AsyncResponse(
            raw=openai_response,
            provider_id=self.active_provider_id,
            model_id=model_id,
            provider_model_name=model_name(model_id, "completions"),
            params=params,
            tools=tools,
            input_messages=input_messages,
            assistant_message=assistant_message,
            finish_reason=finish_reason,
            format=format,
        )

    async def _context_call_async(
        self,
        *,
        ctx: Context[DepsT],
        model_id: OpenAIModelId,
        messages: Sequence[Message],
        tools: Sequence[AsyncTool | AsyncContextTool[DepsT]]
        | AsyncContextToolkit[DepsT]
        | None = None,
        format: type[FormattableT] | Format[FormattableT] | None = None,
        **params: Unpack[Params],
    ) -> AsyncContextResponse[DepsT, None] | AsyncContextResponse[DepsT, FormattableT]:
        """Generate an `llm.AsyncContextResponse` by asynchronously calling the OpenAI ChatCompletions API.

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
            params=params,
            messages=messages,
            tools=tools,
            format=format,
        )

        openai_response = await self.async_client.chat.completions.create(**kwargs)

        assistant_message, finish_reason = _utils.decode_response(
            openai_response, model_id, self.active_provider_id
        )

        return AsyncContextResponse(
            raw=openai_response,
            provider_id=self.active_provider_id,
            model_id=model_id,
            provider_model_name=model_name(model_id, "completions"),
            params=params,
            tools=tools,
            input_messages=input_messages,
            assistant_message=assistant_message,
            finish_reason=finish_reason,
            format=format,
        )

    def _stream(
        self,
        *,
        model_id: OpenAIModelId,
        messages: Sequence[Message],
        tools: Sequence[Tool] | Toolkit | None = None,
        format: type[FormattableT] | Format[FormattableT] | None = None,
        **params: Unpack[Params],
    ) -> StreamResponse | StreamResponse[FormattableT]:
        """Generate an `llm.StreamResponse` by synchronously streaming from the OpenAI ChatCompletions API.

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
            tools=tools,
            format=format,
            params=params,
        )

        openai_stream = self.client.chat.completions.create(
            **kwargs,
            stream=True,
        )

        chunk_iterator = _utils.decode_stream(openai_stream)

        return StreamResponse(
            provider_id=self.active_provider_id,
            model_id=model_id,
            provider_model_name=model_name(model_id, "completions"),
            params=params,
            tools=tools,
            input_messages=input_messages,
            chunk_iterator=chunk_iterator,
            format=format,
        )

    def _context_stream(
        self,
        *,
        ctx: Context[DepsT],
        model_id: OpenAIModelId,
        messages: Sequence[Message],
        tools: Sequence[Tool | ContextTool[DepsT]]
        | ContextToolkit[DepsT]
        | None = None,
        format: type[FormattableT] | Format[FormattableT] | None = None,
        **params: Unpack[Params],
    ) -> ContextStreamResponse[DepsT] | ContextStreamResponse[DepsT, FormattableT]:
        """Generate an `llm.ContextStreamResponse` by synchronously streaming from the OpenAI ChatCompletions API.

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
            tools=tools,
            format=format,
            params=params,
        )

        openai_stream = self.client.chat.completions.create(
            **kwargs,
            stream=True,
        )

        chunk_iterator = _utils.decode_stream(openai_stream)

        return ContextStreamResponse(
            provider_id=self.active_provider_id,
            model_id=model_id,
            provider_model_name=model_name(model_id, "completions"),
            params=params,
            tools=tools,
            input_messages=input_messages,
            chunk_iterator=chunk_iterator,
            format=format,
        )

    async def _stream_async(
        self,
        *,
        model_id: OpenAIModelId,
        messages: Sequence[Message],
        tools: Sequence[AsyncTool] | AsyncToolkit | None = None,
        format: type[FormattableT] | Format[FormattableT] | None = None,
        **params: Unpack[Params],
    ) -> AsyncStreamResponse | AsyncStreamResponse[FormattableT]:
        """Generate an `llm.AsyncStreamResponse` by asynchronously streaming from the OpenAI ChatCompletions API.

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
            tools=tools,
            format=format,
            params=params,
        )

        openai_stream = await self.async_client.chat.completions.create(
            **kwargs,
            stream=True,
        )

        chunk_iterator = _utils.decode_async_stream(openai_stream)

        return AsyncStreamResponse(
            provider_id=self.active_provider_id,
            model_id=model_id,
            provider_model_name=model_name(model_id, "completions"),
            params=params,
            tools=tools,
            input_messages=input_messages,
            chunk_iterator=chunk_iterator,
            format=format,
        )

    async def _context_stream_async(
        self,
        *,
        ctx: Context[DepsT],
        model_id: OpenAIModelId,
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
        """Generate an `llm.AsyncContextStreamResponse` by asynchronously streaming from the OpenAI ChatCompletions API.

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
            tools=tools,
            format=format,
            params=params,
        )

        openai_stream = await self.async_client.chat.completions.create(
            **kwargs,
            stream=True,
        )

        chunk_iterator = _utils.decode_async_stream(openai_stream)

        return AsyncContextStreamResponse(
            provider_id=self.active_provider_id,
            model_id=model_id,
            provider_model_name=model_name(model_id, "completions"),
            params=params,
            tools=tools,
            input_messages=input_messages,
            chunk_iterator=chunk_iterator,
            format=format,
        )
