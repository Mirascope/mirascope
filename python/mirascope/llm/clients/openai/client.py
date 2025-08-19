"""OpenAI client implementation."""

import os
from collections.abc import Sequence

import httpx
from openai import OpenAI

from ...context import Context, DepsT
from ...formatting import FormatT, _utils as _formatting_utils
from ...messages import Message
from ...responses import AsyncStreamResponse, Response, StreamResponse
from ...tools import (
    FORMAT_TOOL_NAME,
    AsyncContextTool,
    AsyncTool,
    ContextTool,
    Tool,
)
from ..base import BaseClient, _utils as _base_utils
from . import _utils
from .models import OpenAIModel
from .params import OpenAIParams

_global_client: "OpenAIClient | None" = None


def get_openai_client() -> "OpenAIClient":
    """Get a global OpenAI client instance.

    Returns:
        An OpenAI client instance. Multiple calls return the same instance.
    """
    global _global_client
    if _global_client is None:
        api_key = os.getenv("OPENAI_API_KEY")
        _global_client = OpenAIClient(api_key=api_key)
    return _global_client


class OpenAIClient(BaseClient[OpenAIParams, OpenAIModel, OpenAI]):
    """The client for the OpenAI LLM model."""

    def __init__(
        self, *, api_key: str | None = None, base_url: str | httpx.URL | None = None
    ) -> None:
        """Initialize the OpenAIClient with optional API key.

        If api_key is not set, OpenAI will look for it in env as "OPENAI_API_KEY".
        """
        self.client = OpenAI(api_key=api_key, base_url=base_url)

    def call(
        self,
        *,
        model: OpenAIModel,
        messages: Sequence[Message],
        tools: Sequence[Tool] | None = None,
        params: OpenAIParams | None = None,
    ) -> Response[None]:
        """Make a call to the OpenAI ChatCompletions API."""
        if params:
            raise NotImplementedError("param use not yet supported")

        message_params, tool_params = _utils.prepare_openai_request(messages, tools)

        openai_response = self.client.chat.completions.create(
            model=model,
            messages=message_params,
            tools=tool_params,
        )

        assistant_message, finish_reason = _utils.decode_response(openai_response)

        return Response(
            provider="openai",
            model=model,
            raw=openai_response,
            input_messages=messages,
            assistant_message=assistant_message,
            finish_reason=finish_reason,
        )

    def context_call(
        self,
        *,
        ctx: Context[DepsT],
        model: OpenAIModel,
        messages: Sequence[Message],
        tools: Sequence[Tool | ContextTool[DepsT]],
        params: OpenAIParams | None = None,
    ) -> Response[None]:
        raise NotImplementedError

    def structured_call(
        self,
        *,
        model: OpenAIModel,
        messages: Sequence[Message],
        tools: Sequence[Tool] | None = None,
        format: type[FormatT],
        params: OpenAIParams | None = None,
    ) -> Response[FormatT]:
        """Make a structured call to OpenAI with formatted output."""
        if params:
            raise NotImplementedError("param use not yet supported")

        format_info = _formatting_utils.ensure_formattable(format)
        format_mode = format_info.mode

        additional_system_instructions: list[str] = []
        if format_mode == "tool":
            additional_system_instructions.append(
                f"When you are ready to respond to the user, use the {FORMAT_TOOL_NAME} tool to construct a properly formatted response."
            )
        if format_info.formatting_instructions:
            additional_system_instructions.append(format_info.formatting_instructions)
        if additional_system_instructions:
            messages = _base_utils.add_system_instructions(
                messages, additional_system_instructions
            )
        message_params, tool_params = _utils.prepare_openai_request(messages, tools)

        if format_mode in ("strict", "strict-or-tool", "strict-or-json"):
            openai_response = self.client.chat.completions.create(
                model=model,
                messages=message_params,
                tools=tool_params,
                response_format=_utils.create_strict_response_format(format_info),
            )
        elif format_mode == "tool":
            format_tool_param = _utils.create_format_tool_param(format_info)
            tool_params = list(tool_params) if isinstance(tool_params, list) else []
            tool_params.append(format_tool_param)

            openai_response = self.client.chat.completions.create(
                model=model,
                messages=message_params,
                tools=tool_params,
            )
        elif format_mode == "json":
            raise NotImplementedError
        else:
            raise ValueError(
                f"Unsupported formatting mode: {format_mode}"
            )  # pragma: no cover

        assistant_message, finish_reason = _utils.decode_response(openai_response)

        if format_mode == "tool":
            assistant_message, finish_reason = _base_utils.handle_format_tool_response(
                assistant_message, finish_reason
            )

        return Response[FormatT](
            provider="openai",
            model=model,
            raw=openai_response,
            input_messages=messages,
            assistant_message=assistant_message,
            finish_reason=finish_reason,
            format=format,
        )

    def structured_context_call(
        self,
        *,
        ctx: Context[DepsT],
        model: OpenAIModel,
        messages: Sequence[Message],
        tools: Sequence[Tool | ContextTool[DepsT]],
        format: type[FormatT],
        params: OpenAIParams | None = None,
    ) -> Response[FormatT]:
        raise NotImplementedError

    async def call_async(
        self,
        *,
        model: OpenAIModel,
        messages: Sequence[Message],
        tools: Sequence[AsyncTool] | None = None,
        params: OpenAIParams | None = None,
    ) -> Response[None]:
        raise NotImplementedError

    async def context_call_async(
        self,
        *,
        ctx: Context[DepsT],
        model: OpenAIModel,
        messages: Sequence[Message],
        tools: Sequence[AsyncTool | AsyncContextTool[DepsT]],
        params: OpenAIParams | None = None,
    ) -> Response[None]:
        raise NotImplementedError

    async def structured_call_async(
        self,
        *,
        model: OpenAIModel,
        messages: Sequence[Message],
        tools: Sequence[AsyncTool] | None = None,
        format: type[FormatT],
        params: OpenAIParams | None = None,
    ) -> Response[FormatT]:
        raise NotImplementedError

    async def structured_context_call_async(
        self,
        *,
        ctx: Context[DepsT],
        model: OpenAIModel,
        messages: Sequence[Message],
        tools: Sequence[AsyncTool | AsyncContextTool[DepsT]],
        format: type[FormatT],
        params: OpenAIParams | None = None,
    ) -> Response[FormatT]:
        raise NotImplementedError

    def stream(
        self,
        *,
        model: OpenAIModel,
        messages: Sequence[Message],
        tools: Sequence[Tool] | None = None,
        params: OpenAIParams | None = None,
    ) -> StreamResponse:
        """Make a streaming call to the OpenAI API."""
        if params:
            raise NotImplementedError("param use not yet supported")

        message_params, tool_params = _utils.prepare_openai_request(messages, tools)

        openai_stream = self.client.chat.completions.create(
            model=model,
            messages=message_params,
            tools=tool_params,
            stream=True,
        )

        chunk_iterator = _utils.convert_openai_stream_to_chunk_iterator(openai_stream)

        return StreamResponse(
            provider="openai",
            model=model,
            input_messages=messages,
            chunk_iterator=chunk_iterator,
        )

    def context_stream(
        self,
        *,
        ctx: Context[DepsT],
        model: OpenAIModel,
        messages: Sequence[Message],
        tools: Sequence[Tool | ContextTool[DepsT]],
        params: OpenAIParams | None = None,
    ) -> StreamResponse:
        raise NotImplementedError

    def structured_stream(
        self,
        *,
        model: OpenAIModel,
        messages: Sequence[Message],
        tools: Sequence[Tool] | None = None,
        format: type[FormatT],
        params: OpenAIParams | None = None,
    ) -> StreamResponse[FormatT]:
        raise NotImplementedError

    def structured_context_stream(
        self,
        *,
        ctx: Context[DepsT],
        model: OpenAIModel,
        messages: Sequence[Message],
        tools: Sequence[Tool | ContextTool[DepsT]],
        format: type[FormatT],
        params: OpenAIParams | None = None,
    ) -> StreamResponse[FormatT]:
        raise NotImplementedError

    async def stream_async(
        self,
        *,
        model: OpenAIModel,
        messages: Sequence[Message],
        tools: Sequence[AsyncTool] | None = None,
        params: OpenAIParams | None = None,
    ) -> AsyncStreamResponse:
        raise NotImplementedError

    async def context_stream_async(
        self,
        *,
        ctx: Context[DepsT],
        model: OpenAIModel,
        messages: Sequence[Message],
        tools: Sequence[AsyncTool | AsyncContextTool[DepsT]],
        params: OpenAIParams | None = None,
    ) -> AsyncStreamResponse:
        raise NotImplementedError

    async def structured_stream_async(
        self,
        *,
        model: OpenAIModel,
        messages: Sequence[Message],
        tools: Sequence[AsyncTool] | None = None,
        format: type[FormatT],
        params: OpenAIParams | None = None,
    ) -> AsyncStreamResponse[FormatT]:
        raise NotImplementedError

    async def structured_context_stream_async(
        self,
        *,
        ctx: Context[DepsT],
        model: OpenAIModel,
        messages: Sequence[Message],
        tools: Sequence[AsyncTool | AsyncContextTool[DepsT]],
        format: type[FormatT],
        params: OpenAIParams | None = None,
    ) -> AsyncStreamResponse[FormatT]:
        raise NotImplementedError
