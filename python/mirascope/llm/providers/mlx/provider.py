from collections.abc import Sequence
from functools import cache, lru_cache
from typing import cast
from typing_extensions import Unpack

import mlx.nn as nn
from mlx_lm import load as mlx_load
from transformers import PreTrainedTokenizer

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
from . import _utils
from .encoding import TransformersEncoder
from .mlx import MLX
from .model_id import MLXModelId


@cache
def _mlx_client_singleton() -> "MLXProvider":
    """Get or create the singleton MLX client instance."""
    return MLXProvider()


def client() -> "MLXProvider":
    """Get the MLX client singleton instance."""
    return _mlx_client_singleton()


@lru_cache(maxsize=16)
def _get_mlx(model_id: MLXModelId) -> MLX:
    model, tokenizer = cast(tuple[nn.Module, PreTrainedTokenizer], mlx_load(model_id))
    encoder = TransformersEncoder(tokenizer)
    return MLX(
        model_id,
        model,
        tokenizer,
        encoder,
    )


class MLXProvider(BaseProvider[None]):
    """Client for interacting with MLX language models.

    This client provides methods for generating responses from MLX models,
    supporting both synchronous and asynchronous operations, as well as
    streaming responses.
    """

    id = "mlx"
    default_scope = "mlx-community/"

    def _call(
        self,
        *,
        model_id: MLXModelId,
        messages: Sequence[Message],
        tools: Sequence[Tool] | Toolkit | None = None,
        format: type[FormattableT] | Format[FormattableT] | None = None,
        **params: Unpack[Params],
    ) -> Response | Response[FormattableT]:
        """Generate an `llm.Response` using MLX model.

        Args:
            model_id: Model identifier to use.
            messages: Messages to send to the LLM.
            tools: Optional tools that the model may invoke.
            format: Optional response format specifier.
            **params: Additional parameters to configure output (e.g. temperature). See `llm.Params`.

        Returns:
            An `llm.Response` object containing the LLM-generated content.
        """
        mlx = _get_mlx(model_id)

        input_messages, format, assistant_message, response = mlx.generate(
            messages, tools, format, params
        )

        return Response(
            raw=response,
            provider_id="mlx",
            model_id=model_id,
            provider_model_name=model_id,
            params=params,
            tools=tools,
            input_messages=input_messages,
            assistant_message=assistant_message,
            finish_reason=_utils.extract_finish_reason(response),
            usage=_utils.extract_usage(response),
            format=format,
        )

    def _context_call(
        self,
        *,
        ctx: Context[DepsT],
        model_id: MLXModelId,
        messages: Sequence[Message],
        tools: Sequence[Tool | ContextTool[DepsT]]
        | ContextToolkit[DepsT]
        | None = None,
        format: type[FormattableT] | Format[FormattableT] | None = None,
        **params: Unpack[Params],
    ) -> ContextResponse[DepsT, None] | ContextResponse[DepsT, FormattableT]:
        """Generate an `llm.ContextResponse` using MLX model.

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
        mlx = _get_mlx(model_id)

        input_messages, format, assistant_message, response = mlx.generate(
            messages, tools, format, params
        )

        return ContextResponse(
            raw=response,
            provider_id="mlx",
            model_id=model_id,
            provider_model_name=model_id,
            params=params,
            tools=tools,
            input_messages=input_messages,
            assistant_message=assistant_message,
            finish_reason=_utils.extract_finish_reason(response),
            usage=_utils.extract_usage(response),
            format=format,
        )

    async def _call_async(
        self,
        *,
        model_id: MLXModelId,
        messages: Sequence[Message],
        tools: Sequence[AsyncTool] | AsyncToolkit | None = None,
        format: type[FormattableT] | Format[FormattableT] | None = None,
        **params: Unpack[Params],
    ) -> AsyncResponse | AsyncResponse[FormattableT]:
        """Generate an `llm.AsyncResponse` using MLX model by asynchronously calloing
        `asycio.to_thread`.

        Args:
            model_id: Model identifier to use.
            messages: Messages to send to the LLM.
            tools: Optional tools that the model may invoke.
            format: Optional response format specifier.
            **params: Additional parameters to configure output (e.g. temperature). See `llm.Params`.

        Returns:
            An `llm.AsyncResponse` object containing the LLM-generated content.
        """
        mlx = _get_mlx(model_id)

        (
            input_messages,
            format,
            assistant_message,
            response,
        ) = await mlx.generate_async(messages, tools, format, params)

        return AsyncResponse(
            raw=response,
            provider_id="mlx",
            model_id=model_id,
            provider_model_name=model_id,
            params=params,
            tools=tools,
            input_messages=input_messages,
            assistant_message=assistant_message,
            finish_reason=_utils.extract_finish_reason(response),
            usage=_utils.extract_usage(response),
            format=format,
        )

    async def _context_call_async(
        self,
        *,
        ctx: Context[DepsT],
        model_id: MLXModelId,
        messages: Sequence[Message],
        tools: Sequence[AsyncTool | AsyncContextTool[DepsT]]
        | AsyncContextToolkit[DepsT]
        | None = None,
        format: type[FormattableT] | Format[FormattableT] | None = None,
        **params: Unpack[Params],
    ) -> AsyncContextResponse[DepsT, None] | AsyncContextResponse[DepsT, FormattableT]:
        """Generate an `llm.AsyncResponse` using MLX model by asynchronously calloing
        `asycio.to_thread`.

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
        mlx = _get_mlx(model_id)

        (
            input_messages,
            format,
            assistant_message,
            response,
        ) = await mlx.generate_async(messages, tools, format, params)

        return AsyncContextResponse(
            raw=response,
            provider_id="mlx",
            model_id=model_id,
            provider_model_name=model_id,
            params=params,
            tools=tools,
            input_messages=input_messages,
            assistant_message=assistant_message,
            finish_reason=_utils.extract_finish_reason(response),
            usage=_utils.extract_usage(response),
            format=format,
        )

    def _stream(
        self,
        *,
        model_id: MLXModelId,
        messages: Sequence[Message],
        tools: Sequence[Tool] | Toolkit | None = None,
        format: type[FormattableT] | Format[FormattableT] | None = None,
        **params: Unpack[Params],
    ) -> StreamResponse | StreamResponse[FormattableT]:
        """Generate an `llm.StreamResponse` by synchronously streaming from MLX model output.

        Args:
            model_id: Model identifier to use.
            messages: Messages to send to the LLM.
            tools: Optional tools that the model may invoke.
            format: Optional response format specifier.
            **params: Additional parameters to configure output (e.g. temperature). See `llm.Params`.

        Returns:
            An `llm.StreamResponse` object for iterating over the LLM-generated content.
        """
        mlx = _get_mlx(model_id)

        input_messages, format, chunk_iterator = mlx.stream(
            messages, tools, format, params
        )

        return StreamResponse(
            provider_id="mlx",
            model_id=model_id,
            provider_model_name=model_id,
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
        model_id: MLXModelId,
        messages: Sequence[Message],
        tools: Sequence[Tool | ContextTool[DepsT]]
        | ContextToolkit[DepsT]
        | None = None,
        format: type[FormattableT] | Format[FormattableT] | None = None,
        **params: Unpack[Params],
    ) -> ContextStreamResponse[DepsT] | ContextStreamResponse[DepsT, FormattableT]:
        """Generate an `llm.ContextStreamResponse` by synchronously streaming from MLX model output.

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
        mlx = _get_mlx(model_id)

        input_messages, format, chunk_iterator = mlx.stream(
            messages, tools, format, params
        )

        return ContextStreamResponse(
            provider_id="mlx",
            model_id=model_id,
            provider_model_name=model_id,
            params=params,
            tools=tools,
            input_messages=input_messages,
            chunk_iterator=chunk_iterator,
            format=format,
        )

    async def _stream_async(
        self,
        *,
        model_id: MLXModelId,
        messages: Sequence[Message],
        tools: Sequence[AsyncTool] | AsyncToolkit | None = None,
        format: type[FormattableT] | Format[FormattableT] | None = None,
        **params: Unpack[Params],
    ) -> AsyncStreamResponse | AsyncStreamResponse[FormattableT]:
        """Generate an `llm.AsyncStreamResponse` by asynchronously streaming from MLX model output.

        Args:
            model_id: Model identifier to use.
            messages: Messages to send to the LLM.
            tools: Optional tools that the model may invoke.
            format: Optional response format specifier.
            **params: Additional parameters to configure output (e.g. temperature). See `llm.Params`.

        Returns:
            An `llm.AsyncStreamResponse` object for asynchronously iterating over the LLM-generated content.
        """
        mlx = _get_mlx(model_id)

        input_messages, format, chunk_iterator = await mlx.stream_async(
            messages, tools, format, params
        )

        return AsyncStreamResponse(
            provider_id="mlx",
            model_id=model_id,
            provider_model_name=model_id,
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
        model_id: MLXModelId,
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
        """Generate an `llm.AsyncContextStreamResponse` by asynchronously streaming from MLX model output.

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
        mlx = _get_mlx(model_id)

        input_messages, format, chunk_iterator = await mlx.stream_async(
            messages, tools, format, params
        )

        return AsyncContextStreamResponse(
            provider_id="mlx",
            model_id=model_id,
            provider_model_name=model_id,
            params=params,
            tools=tools,
            input_messages=input_messages,
            chunk_iterator=chunk_iterator,
            format=format,
        )
