"""Unified OpenAI client implementation."""

from collections.abc import Sequence
from typing_extensions import Unpack

from openai import OpenAI

from ...context import Context, DepsT
from ...formatting import Format, FormattableT
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
from ..base import BaseProvider, Params
from .completions import OpenAICompletionsProvider
from .model_id import OPENAI_KNOWN_MODELS, OpenAIModelId
from .responses import OpenAIResponsesProvider


def _has_audio_content(messages: Sequence[Message]) -> bool:
    """Returns whether a sequence of messages contains any audio content."""
    for message in messages:
        if message.role == "system":
            continue
        for content in message.content:
            if content.type == "audio":
                return True
    return False


def choose_api_mode(model_id: OpenAIModelId, messages: Sequence[Message]) -> str:
    """Choose between 'responses' or 'completions' API based on model_id and messages.

    Args:
        model_id: The model identifier.
        messages: The messages to send to the LLM.

    Returns:
        Either "responses" or "completions" depending on the model and message content.

    If the user manually specified an api mode (by appending it as a suffix to the model
    id), then we use it.

    Otherwise, we prefer the responses API where supported (because it has better
    reasoning support and better prompt caching). However we will use the :completions api
    if the messages contain any audio content, as audio content is not yet supported in
    the responses API.
    """
    if model_id.endswith(":completions"):
        return "completions"
    elif model_id.endswith(":responses"):
        return "responses"

    if _has_audio_content(messages):
        return "completions"

    if f"{model_id}:responses" in OPENAI_KNOWN_MODELS:
        # Prefer responses api when we know it is available
        return "responses"
    elif f"{model_id}:completions" in OPENAI_KNOWN_MODELS:
        # If we know from testing that the completions api is available, and
        # (implied by above) that responses wasn't, then we should use completions
        return "completions"

    # If we don't have either :responses or :completions in the known_models, it's
    # likely that this is a new model we haven't tested. We default to responses api for
    # openai/ models (on the assumption that they are new models and OpenAI prefers
    # the responses API) but completions for other models (on the assumption that they
    # are other models routing through the OpenAI completions API)
    if model_id.startswith("openai/"):
        return "responses"
    else:
        return "completions"


class OpenAIRoutedCompletionsProvider(OpenAICompletionsProvider):
    """OpenAI completions client that reports provider_id as 'openai'."""

    id = "openai"


class OpenAIRoutedResponsesProvider(OpenAIResponsesProvider):
    """OpenAI responses client that reports provider_id as 'openai'."""

    id = "openai"


class OpenAIProvider(BaseProvider[OpenAI]):
    """Unified provider for OpenAI that routes to Completions or Responses API based on model_id."""

    id = "openai"
    default_scope = "openai/"

    def __init__(
        self, *, api_key: str | None = None, base_url: str | None = None
    ) -> None:
        """Initialize the OpenAI provider with both subclients."""
        self._completions_provider = OpenAIRoutedCompletionsProvider(
            api_key=api_key, base_url=base_url
        )
        self._responses_provider = OpenAIRoutedResponsesProvider(
            api_key=api_key, base_url=base_url
        )
        # Use completions client's underlying OpenAI client as the main one
        self.client = self._completions_provider.client

    def _choose_subprovider(
        self, model_id: OpenAIModelId, messages: Sequence[Message]
    ) -> OpenAICompletionsProvider | OpenAIResponsesProvider:
        """Choose the appropriate provider based on model_id and messages.

        Args:
            model_id: The model identifier.
            messages: The messages to send to the LLM.

        Returns:
            The responses or completions subclient.
        """
        api_mode = choose_api_mode(model_id, messages)
        if api_mode == "responses":
            return self._responses_provider
        return self._completions_provider

    def _call(
        self,
        *,
        model_id: OpenAIModelId,
        messages: Sequence[Message],
        tools: Sequence[Tool] | Toolkit | None = None,
        format: type[FormattableT] | Format[FormattableT] | None = None,
        **params: Unpack[Params],
    ) -> Response | Response[FormattableT]:
        """Generate an `llm.Response` by synchronously calling the OpenAI API.

        Args:
            model_id: Model identifier to use.
            messages: Messages to send to the LLM.
            tools: Optional tools that the model may invoke.
            format: Optional response format specifier.
            **params: Additional parameters to configure output (e.g. temperature). See `llm.Params`.

        Returns:
            An `llm.Response` object containing the LLM-generated content.
        """
        client = self._choose_subprovider(model_id, messages)
        return client.call(
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
        model_id: OpenAIModelId,
        messages: Sequence[Message],
        tools: Sequence[Tool | ContextTool[DepsT]]
        | ContextToolkit[DepsT]
        | None = None,
        format: type[FormattableT] | Format[FormattableT] | None = None,
        **params: Unpack[Params],
    ) -> ContextResponse[DepsT, None] | ContextResponse[DepsT, FormattableT]:
        """Generate an `llm.ContextResponse` by synchronously calling the OpenAI API.

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
        client = self._choose_subprovider(model_id, messages)
        return client.context_call(
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
        model_id: OpenAIModelId,
        messages: Sequence[Message],
        tools: Sequence[AsyncTool] | AsyncToolkit | None = None,
        format: type[FormattableT] | Format[FormattableT] | None = None,
        **params: Unpack[Params],
    ) -> AsyncResponse | AsyncResponse[FormattableT]:
        """Generate an `llm.AsyncResponse` by asynchronously calling the OpenAI API.

        Args:
            model_id: Model identifier to use.
            messages: Messages to send to the LLM.
            tools: Optional tools that the model may invoke.
            format: Optional response format specifier.
            **params: Additional parameters to configure output (e.g. temperature). See `llm.Params`.

        Returns:
            An `llm.AsyncResponse` object containing the LLM-generated content.
        """
        return await self._choose_subprovider(model_id, messages).call_async(
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
        model_id: OpenAIModelId,
        messages: Sequence[Message],
        tools: Sequence[AsyncTool | AsyncContextTool[DepsT]]
        | AsyncContextToolkit[DepsT]
        | None = None,
        format: type[FormattableT] | Format[FormattableT] | None = None,
        **params: Unpack[Params],
    ) -> AsyncContextResponse[DepsT, None] | AsyncContextResponse[DepsT, FormattableT]:
        """Generate an `llm.AsyncContextResponse` by asynchronously calling the OpenAI API.

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
        return await self._choose_subprovider(model_id, messages).context_call_async(
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
        model_id: OpenAIModelId,
        messages: Sequence[Message],
        tools: Sequence[Tool] | Toolkit | None = None,
        format: type[FormattableT] | Format[FormattableT] | None = None,
        **params: Unpack[Params],
    ) -> StreamResponse | StreamResponse[FormattableT]:
        """Generate an `llm.StreamResponse` by synchronously streaming from the OpenAI API.

        Args:
            model_id: Model identifier to use.
            messages: Messages to send to the LLM.
            tools: Optional tools that the model may invoke.
            format: Optional response format specifier.
            **params: Additional parameters to configure output (e.g. temperature). See `llm.Params`.

        Returns:
            An `llm.StreamResponse` object for iterating over the LLM-generated content.
        """
        client = self._choose_subprovider(model_id, messages)
        return client.stream(
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
        model_id: OpenAIModelId,
        messages: Sequence[Message],
        tools: Sequence[Tool | ContextTool[DepsT]]
        | ContextToolkit[DepsT]
        | None = None,
        format: type[FormattableT] | Format[FormattableT] | None = None,
        **params: Unpack[Params],
    ) -> ContextStreamResponse[DepsT] | ContextStreamResponse[DepsT, FormattableT]:
        """Generate an `llm.ContextStreamResponse` by synchronously streaming from the OpenAI API.

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
        client = self._choose_subprovider(model_id, messages)
        return client.context_stream(
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
        model_id: OpenAIModelId,
        messages: Sequence[Message],
        tools: Sequence[AsyncTool] | AsyncToolkit | None = None,
        format: type[FormattableT] | Format[FormattableT] | None = None,
        **params: Unpack[Params],
    ) -> AsyncStreamResponse | AsyncStreamResponse[FormattableT]:
        """Generate an `llm.AsyncStreamResponse` by asynchronously streaming from the OpenAI API.

        Args:
            model_id: Model identifier to use.
            messages: Messages to send to the LLM.
            tools: Optional tools that the model may invoke.
            format: Optional response format specifier.
            **params: Additional parameters to configure output (e.g. temperature). See `llm.Params`.

        Returns:
            An `llm.AsyncStreamResponse` object for asynchronously iterating over the LLM-generated content.
        """
        return await self._choose_subprovider(model_id, messages).stream_async(
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
        """Generate an `llm.AsyncContextStreamResponse` by asynchronously streaming from the OpenAI API.

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
        return await self._choose_subprovider(model_id, messages).context_stream_async(
            ctx=ctx,
            model_id=model_id,
            messages=messages,
            tools=tools,
            format=format,
            **params,
        )
