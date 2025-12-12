import asyncio
import threading
from collections.abc import Iterable, Sequence
from dataclasses import dataclass, field
from typing_extensions import Unpack

import mlx.core as mx
import mlx.nn as nn
from mlx_lm import stream_generate  # type: ignore[reportPrivateImportUsage]
from mlx_lm.generate import GenerationResponse
from transformers import PreTrainedTokenizer

from ...formatting import Format, FormattableT
from ...messages import AssistantMessage, Message, assistant
from ...responses import AsyncChunkIterator, ChunkIterator, StreamResponseChunk
from ...tools import AnyToolSchema, BaseToolkit
from ..base import Params
from . import _utils
from .encoding import BaseEncoder, TokenIds
from .model_id import MLXModelId


def _consume_sync_stream_into_queue(
    generation_stream: ChunkIterator,
    loop: asyncio.AbstractEventLoop,
    queue: asyncio.Queue[StreamResponseChunk | Exception | None],
) -> None:
    """Consume a synchronous stream and put chunks into an async queue.

    Args:
        sync_stream: The synchronous chunk iterator to consume.
        loop: The event loop for scheduling queue operations.
        queue: The async queue to put chunks into.
    """
    try:
        for response in generation_stream:
            asyncio.run_coroutine_threadsafe(queue.put(response), loop)
    except Exception as e:
        asyncio.run_coroutine_threadsafe(queue.put(e), loop)

    asyncio.run_coroutine_threadsafe(queue.put(None), loop)


@dataclass(frozen=True)
class MLX:
    """MLX model wrapper for synchronous and asynchronous generation.

    Args:
        model_id: The MLX model identifier.
        model: The underlying MLX model.
        tokenizer: The tokenizer for the model.
        encoder: The encoder for prompts and responses.
    """

    model_id: MLXModelId
    """The MLX model identifier."""

    model: nn.Module
    """The underlying MLX model."""

    tokenizer: PreTrainedTokenizer
    """The tokenizer for the model."""

    encoder: BaseEncoder
    """The encoder for prompts and responses."""

    _lock: threading.Lock = field(default_factory=threading.Lock)
    """The lock for thread-safety."""

    def _stream_generate(
        self,
        prompt: TokenIds,
        seed: int | None,
        **kwargs: Unpack[_utils.StreamGenerateKwargs],
    ) -> Iterable[GenerationResponse]:
        """Generator that streams generation responses.

        Using this generator instead of calling stream_generate directly ensures
        thread-safety when using the model in a multi-threaded context.
        """
        with self._lock:
            if seed is not None:
                mx.random.seed(seed)

            return stream_generate(
                self.model,
                self.tokenizer,
                prompt,
                **kwargs,
            )

    async def _stream_generate_async(
        self,
        prompt: TokenIds,
        seed: int | None,
        **kwargs: Unpack[_utils.StreamGenerateKwargs],
    ) -> AsyncChunkIterator:
        """Async generator that streams generation responses.

        Note that, while stream_generate returns an iterable of GenerationResponse,
        here we return an `AsyncChunkIterator`, in order to avoid having to implement
        both synchronous and asynchronous versions of BaseEncoder.decode_stream.
        This makes sense as in this case, there is nothing to gain from consuming the
        generation asyncnronously.
        """
        loop = asyncio.get_running_loop()
        generation_queue: asyncio.Queue[StreamResponseChunk | Exception | None] = (
            asyncio.Queue()
        )

        sync_stream = self.encoder.decode_stream(
            self._stream_generate(
                prompt,
                seed,
                **kwargs,
            )
        )

        consume_task = asyncio.create_task(
            asyncio.to_thread(
                _consume_sync_stream_into_queue, sync_stream, loop, generation_queue
            ),
        )
        while item := await generation_queue.get():
            if isinstance(item, Exception):
                raise item

            yield item

        await consume_task

    def stream(
        self,
        messages: Sequence[Message],
        tools: Sequence[AnyToolSchema] | BaseToolkit[AnyToolSchema] | None,
        format: type[FormattableT] | Format[FormattableT] | None,
        params: Params,
    ) -> tuple[Sequence[Message], Format[FormattableT] | None, ChunkIterator]:
        """Stream response chunks synchronously.

        Args:
            messages: The input messages.
            tools: Optional tools for the model.
            format: Optional response format.

        Returns:
            Tuple of messages, format, and chunk iterator.
        """
        messages, format, prompt = self.encoder.encode_request(messages, tools, format)
        seed, kwargs = _utils.encode_params(params)

        stream = self._stream_generate(prompt, seed, **kwargs)
        return messages, format, self.encoder.decode_stream(stream)

    async def stream_async(
        self,
        messages: Sequence[Message],
        tools: Sequence[AnyToolSchema] | BaseToolkit[AnyToolSchema] | None,
        format: type[FormattableT] | Format[FormattableT] | None,
        params: Params,
    ) -> tuple[Sequence[Message], Format[FormattableT] | None, AsyncChunkIterator]:
        """Stream response chunks asynchronously.

        Args:
            messages: The input messages.
            tools: Optional tools for the model.
            format: Optional response format.
        Returns:
            Tuple of messages, format, and async chunk iterator.
        """
        messages, format, prompt = await asyncio.to_thread(
            self.encoder.encode_request, messages, tools, format
        )
        seed, kwargs = _utils.encode_params(params)

        chunk_iterator = self._stream_generate_async(prompt, seed, **kwargs)
        return messages, format, chunk_iterator

    def generate(
        self,
        messages: Sequence[Message],
        tools: Sequence[AnyToolSchema] | BaseToolkit[AnyToolSchema] | None,
        format: type[FormattableT] | Format[FormattableT] | None,
        params: Params,
    ) -> tuple[
        Sequence[Message],
        Format[FormattableT] | None,
        AssistantMessage,
        GenerationResponse | None,
    ]:
        """Generate a response synchronously.

        Args:
            messages: The input messages.
            tools: Optional tools for the model.
            format: Optional response format.
            params: Generation parameters.
        Returns:
            Tuple of messages, format, assistant message, and last generation response.
        """
        messages, format, prompt = self.encoder.encode_request(messages, tools, format)
        seed, kwargs = _utils.encode_params(params)

        stream = self._stream_generate(prompt, seed, **kwargs)
        assistant_content, last_response = self.encoder.decode_response(stream)
        assistant_message = assistant(
            content=assistant_content,
            model_id=self.model_id,
            provider_id="mlx",
            raw_message=None,
            name=None,
        )
        return messages, format, assistant_message, last_response

    async def generate_async(
        self,
        messages: Sequence[Message],
        tools: Sequence[AnyToolSchema] | BaseToolkit[AnyToolSchema] | None,
        format: type[FormattableT] | Format[FormattableT] | None,
        params: Params,
    ) -> tuple[
        Sequence[Message],
        Format[FormattableT] | None,
        AssistantMessage,
        GenerationResponse | None,
    ]:
        """Generate a response asynchronously.

        Args:
            messages: The input messages.
            tools: Optional tools for the model.
            format: Optional response format.
            params: Generation parameters.
        Returns:
            Tuple of messages, format, assistant message, and last generation response.
        """
        return await asyncio.to_thread(self.generate, messages, tools, format, params)
