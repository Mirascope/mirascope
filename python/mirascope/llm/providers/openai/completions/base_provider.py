"""Base class for OpenAI Completions-compatible providers."""

import os
from collections.abc import Sequence
from typing import ClassVar
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
from ..model_id import model_name as openai_model_name
from . import _utils


class BaseOpenAICompletionsProvider(BaseProvider[OpenAI]):
    """Base class for providers that use OpenAI Completions-compatible APIs."""

    id: ClassVar[str]
    default_scope: ClassVar[str | list[str]]
    default_base_url: ClassVar[str | None] = None
    api_key_env_var: ClassVar[str]
    api_key_required: ClassVar[bool] = True
    provider_name: ClassVar[str | None] = None

    def __init__(
        self,
        *,
        api_key: str | None = None,
        base_url: str | None = None,
    ) -> None:
        """Initialize the OpenAI Completions-compatible provider client."""
        resolved_api_key = api_key or os.environ.get(self.api_key_env_var)

        if self.api_key_required and not resolved_api_key:
            name = self.provider_name or self.id.split(":")[0].capitalize()
            raise ValueError(
                f"{name} API key is required. "
                f"Set the {self.api_key_env_var} environment variable "
                f"or pass the api_key parameter to register_provider()."
            )

        resolved_base_url = base_url or self.default_base_url

        effective_api_key: str | None = resolved_api_key
        if resolved_base_url is not None and not effective_api_key:
            effective_api_key = "not-needed"

        self.client = OpenAI(
            api_key=effective_api_key,
            base_url=resolved_base_url,
        )
        self.async_client = AsyncOpenAI(
            api_key=effective_api_key,
            base_url=resolved_base_url,
        )

    def _model_name(self, model_id: str) -> str:
        """Extract the model name to send to the API."""
        return openai_model_name(model_id, None)

    def _provider_model_name(self, model_id: str) -> str:
        """Get the model name for tracking in Response."""
        return self._model_name(model_id)

    def _call(
        self,
        *,
        model_id: str,
        messages: Sequence[Message],
        tools: Sequence[Tool] | Toolkit | None = None,
        format: type[FormattableT] | Format[FormattableT] | None = None,
        **params: Unpack[Params],
    ) -> Response | Response[FormattableT]:
        """Generate an `llm.Response` by synchronously calling the API.

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
        kwargs["model"] = self._model_name(model_id)

        openai_response = self.client.chat.completions.create(**kwargs)

        assistant_message, finish_reason, usage = _utils.decode_response(
            openai_response,
            model_id,
            self.id,
            self._provider_model_name(model_id),
        )

        return Response(
            raw=openai_response,
            provider_id=self.id,
            model_id=model_id,
            provider_model_name=self._provider_model_name(model_id),
            params=params,
            tools=tools,
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
        model_id: str,
        messages: Sequence[Message],
        tools: Sequence[Tool | ContextTool[DepsT]]
        | ContextToolkit[DepsT]
        | None = None,
        format: type[FormattableT] | Format[FormattableT] | None = None,
        **params: Unpack[Params],
    ) -> ContextResponse[DepsT, None] | ContextResponse[DepsT, FormattableT]:
        """Generate an `llm.ContextResponse` by synchronously calling the API.

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
        kwargs["model"] = self._model_name(model_id)

        openai_response = self.client.chat.completions.create(**kwargs)

        assistant_message, finish_reason, usage = _utils.decode_response(
            openai_response,
            model_id,
            self.id,
            self._provider_model_name(model_id),
        )

        return ContextResponse(
            raw=openai_response,
            provider_id=self.id,
            model_id=model_id,
            provider_model_name=self._provider_model_name(model_id),
            params=params,
            tools=tools,
            input_messages=input_messages,
            assistant_message=assistant_message,
            finish_reason=finish_reason,
            usage=usage,
            format=format,
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
        """Generate an `llm.AsyncResponse` by asynchronously calling the API.

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
        kwargs["model"] = self._model_name(model_id)

        openai_response = await self.async_client.chat.completions.create(**kwargs)

        assistant_message, finish_reason, usage = _utils.decode_response(
            openai_response,
            model_id,
            self.id,
            self._provider_model_name(model_id),
        )

        return AsyncResponse(
            raw=openai_response,
            provider_id=self.id,
            model_id=model_id,
            provider_model_name=self._provider_model_name(model_id),
            params=params,
            tools=tools,
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
        model_id: str,
        messages: Sequence[Message],
        tools: Sequence[AsyncTool | AsyncContextTool[DepsT]]
        | AsyncContextToolkit[DepsT]
        | None = None,
        format: type[FormattableT] | Format[FormattableT] | None = None,
        **params: Unpack[Params],
    ) -> AsyncContextResponse[DepsT, None] | AsyncContextResponse[DepsT, FormattableT]:
        """Generate an `llm.AsyncContextResponse` by asynchronously calling the API.

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
        kwargs["model"] = self._model_name(model_id)

        openai_response = await self.async_client.chat.completions.create(**kwargs)

        assistant_message, finish_reason, usage = _utils.decode_response(
            openai_response,
            model_id,
            self.id,
            self._provider_model_name(model_id),
        )

        return AsyncContextResponse(
            raw=openai_response,
            provider_id=self.id,
            model_id=model_id,
            provider_model_name=self._provider_model_name(model_id),
            params=params,
            tools=tools,
            input_messages=input_messages,
            assistant_message=assistant_message,
            finish_reason=finish_reason,
            usage=usage,
            format=format,
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
        """Generate an `llm.StreamResponse` by synchronously streaming from the API.

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
        kwargs["model"] = self._model_name(model_id)

        openai_stream = self.client.chat.completions.create(
            **kwargs,
            stream=True,
            stream_options={"include_usage": True},
        )

        chunk_iterator = _utils.decode_stream(openai_stream)

        return StreamResponse(
            provider_id=self.id,
            model_id=model_id,
            provider_model_name=self._provider_model_name(model_id),
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
        model_id: str,
        messages: Sequence[Message],
        tools: Sequence[Tool | ContextTool[DepsT]]
        | ContextToolkit[DepsT]
        | None = None,
        format: type[FormattableT] | Format[FormattableT] | None = None,
        **params: Unpack[Params],
    ) -> ContextStreamResponse[DepsT] | ContextStreamResponse[DepsT, FormattableT]:
        """Generate an `llm.ContextStreamResponse` by synchronously streaming from the API.

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
        kwargs["model"] = self._model_name(model_id)

        openai_stream = self.client.chat.completions.create(
            **kwargs,
            stream=True,
            stream_options={"include_usage": True},
        )

        chunk_iterator = _utils.decode_stream(openai_stream)

        return ContextStreamResponse(
            provider_id=self.id,
            model_id=model_id,
            provider_model_name=self._provider_model_name(model_id),
            params=params,
            tools=tools,
            input_messages=input_messages,
            chunk_iterator=chunk_iterator,
            format=format,
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
        """Generate an `llm.AsyncStreamResponse` by asynchronously streaming from the API.

        Args:
            model_id: Model identifier to use.
            messages: Messages to send to the LLM.
            tools: Optional tools that the model may invoke.
            format: Optional response format specifier.
            **params: Additional parameters to configure output (e.g. temperature). See `llm.Params`.

        Returns:
            An `llm.AsyncStreamResponse` object for iterating over the LLM-generated content.
        """
        input_messages, format, kwargs = _utils.encode_request(
            model_id=model_id,
            messages=messages,
            tools=tools,
            format=format,
            params=params,
        )
        kwargs["model"] = self._model_name(model_id)

        openai_stream = await self.async_client.chat.completions.create(
            **kwargs,
            stream=True,
            stream_options={"include_usage": True},
        )

        chunk_iterator = _utils.decode_async_stream(openai_stream)

        return AsyncStreamResponse(
            provider_id=self.id,
            model_id=model_id,
            provider_model_name=self._provider_model_name(model_id),
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
        """Generate an `llm.AsyncContextStreamResponse` by asynchronously streaming from the API.

        Args:
            ctx: Context object with dependencies for tools.
            model_id: Model identifier to use.
            messages: Messages to send to the LLM.
            tools: Optional tools that the model may invoke.
            format: Optional response format specifier.
            **params: Additional parameters to configure output (e.g. temperature). See `llm.Params`.

        Returns:
            An `llm.AsyncContextStreamResponse` object for iterating over the LLM-generated content.
        """
        input_messages, format, kwargs = _utils.encode_request(
            model_id=model_id,
            messages=messages,
            tools=tools,
            format=format,
            params=params,
        )
        kwargs["model"] = self._model_name(model_id)

        openai_stream = await self.async_client.chat.completions.create(
            **kwargs,
            stream=True,
            stream_options={"include_usage": True},
        )

        chunk_iterator = _utils.decode_async_stream(openai_stream)

        return AsyncContextStreamResponse(
            provider_id=self.id,
            model_id=model_id,
            provider_model_name=self._provider_model_name(model_id),
            params=params,
            tools=tools,
            input_messages=input_messages,
            chunk_iterator=chunk_iterator,
            format=format,
        )
