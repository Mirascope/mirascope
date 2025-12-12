"""Tests for MLX class and helper functions."""

import asyncio
from collections.abc import Iterable
from unittest.mock import MagicMock

import pytest

from mirascope.llm.content import TextChunk
from mirascope.llm.providers.mlx.mlx import (
    _consume_sync_stream_into_queue,  # pyright: ignore[reportPrivateUsage]
)


def test_consume_sync_stream_into_queue_exception() -> None:
    """Test that exceptions in the sync stream are properly queued."""

    def failing_stream() -> Iterable[TextChunk]:
        yield TextChunk(delta="test")
        raise ValueError("Test error")

    loop = asyncio.new_event_loop()
    queue: asyncio.Queue[TextChunk | Exception | None] = asyncio.Queue()

    # Run the consumer in a thread
    import threading

    thread = threading.Thread(
        target=_consume_sync_stream_into_queue,
        args=(failing_stream(), loop, queue),
    )
    thread.start()
    thread.join()

    # Give time for coroutines to be scheduled
    loop.run_until_complete(asyncio.sleep(0.1))

    # Check queue contents
    items = []
    while not queue.empty():
        items.append(queue.get_nowait())

    assert len(items) == 3  # One chunk, one exception, one None
    assert isinstance(items[0], TextChunk)
    assert isinstance(items[1], ValueError)
    assert str(items[1]) == "Test error"
    assert items[2] is None

    loop.close()


@pytest.mark.asyncio
async def test_stream_generate_async_exception() -> None:
    """Test that exceptions in async streaming are properly raised."""
    from mirascope.llm.providers.mlx.mlx import MLX

    # Create a mock MLX instance
    mock_model = MagicMock()
    mock_tokenizer = MagicMock()
    mock_encoder = MagicMock()

    mlx = MLX(
        model_id="test-model",
        model=mock_model,
        tokenizer=mock_tokenizer,
        encoder=mock_encoder,
    )

    # Mock _stream_generate to return a stream that will fail
    def failing_sync_stream() -> Iterable[TextChunk]:
        yield TextChunk(delta="test")
        raise RuntimeError("Stream failed")

    mock_encoder.decode_stream.return_value = failing_sync_stream()

    # Call the async method and expect the exception
    async_gen = mlx._stream_generate_async(prompt=[1, 2, 3], seed=None)  # pyright: ignore[reportPrivateUsage]

    # First chunk should work
    chunk = await async_gen.__anext__()
    assert isinstance(chunk, TextChunk)
    assert chunk.delta == "test"

    # Second should raise the exception
    with pytest.raises(RuntimeError, match="Stream failed"):
        await async_gen.__anext__()
