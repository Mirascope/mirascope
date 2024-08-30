from collections.abc import AsyncGenerator, Generator, Iterable, Iterator
from typing import Any

import pytest

from mirascope.core.base._utils._get_create_fn_or_async_create_fn import (
    get_async_create_fn,
    get_create_fn,
)


@pytest.mark.asyncio
async def test_get_async_create_fn_non_streaming():
    async def async_func(**kwargs: Any) -> str:
        return "non-streaming result"

    create_or_stream = get_async_create_fn(async_func)
    result = await create_or_stream(stream=False)
    assert result == "non-streaming result"


@pytest.mark.asyncio
async def test_get_async_create_fn_streaming_with_generator():
    async def async_func(**kwargs: Any) -> str:
        return "non-streaming result"  # pragma: no cover

    async def async_generator_func(**kwargs: Any) -> AsyncGenerator[str, None]:
        yield "streaming result 1"
        yield "streaming result 2"

    create_or_stream = get_async_create_fn(async_func, async_generator_func)
    stream_result = await create_or_stream(stream=True)
    assert isinstance(stream_result, AsyncGenerator)

    results = [item async for item in stream_result]
    assert results == ["streaming result 1", "streaming result 2"]


@pytest.mark.asyncio
async def test_get_async_create_fn_streaming_without_generator():
    async def async_func(**kwargs: Any) -> AsyncGenerator[str, None]:
        async def generator() -> AsyncGenerator[str, None]:
            yield "streaming result 1"
            yield "streaming result 2"

        return generator()

    create_or_stream = get_async_create_fn(async_func)
    stream_result = await create_or_stream(stream=True)
    assert isinstance(stream_result, AsyncGenerator)

    results = [item async for item in stream_result]
    assert results == ["streaming result 1", "streaming result 2"]


@pytest.mark.asyncio
async def test_get_async_create_fn_with_additional_kwargs():
    async def async_func(**kwargs: Any) -> str:
        return f"result: {kwargs.get('param', '')}"

    create_or_stream = get_async_create_fn(async_func)
    result = await create_or_stream(stream=False, param="test")
    assert result == "result: test"


@pytest.mark.asyncio
async def test_get_async_create_fn_streaming_with_additional_kwargs():
    async def async_func(**kwargs: Any) -> str:
        return "unused"  # pragma: no cover

    async def async_generator_func(**kwargs: Any) -> AsyncGenerator[str, None]:
        yield f"streaming result: {kwargs.get('param', '')}"

    create_or_stream = get_async_create_fn(async_func, async_generator_func)
    stream_result = await create_or_stream(stream=True, param="test")
    assert isinstance(stream_result, AsyncGenerator)

    results = [item async for item in stream_result]
    assert results == ["streaming result: test"]


@pytest.mark.asyncio
async def test_get_async_create_fn_default_stream_value():
    async def async_func(**kwargs: Any) -> str:
        return "non-streaming result"

    create_or_stream = get_async_create_fn(async_func)
    result = await create_or_stream()  # Default stream=False
    assert result == "non-streaming result"


@pytest.mark.asyncio
async def test_get_async_create_fn_type_casting():
    async def async_func(**kwargs: Any) -> str:
        return "non-streaming result"

    async def async_generator_func(**kwargs: Any) -> AsyncGenerator[str, None]:
        yield "streaming result"

    create_or_stream = get_async_create_fn(async_func, async_generator_func)

    # Test non-streaming mode
    non_stream_result = await create_or_stream(stream=False)
    assert isinstance(non_stream_result, str)
    assert non_stream_result == "non-streaming result"

    # Test streaming mode
    stream_result = await create_or_stream(stream=True)
    assert isinstance(stream_result, AsyncGenerator)

    # Consume the AsyncGenerator to verify its content
    results = [item async for item in stream_result]
    assert results == ["streaming result"]


def test_get_create_fn_non_streaming():
    def sync_func(**kwargs: Any) -> str:
        return "non-streaming result"

    create_or_stream = get_create_fn(sync_func)
    result = create_or_stream(stream=False)
    assert result == "non-streaming result"


def test_get_create_fn_streaming_with_generator():
    def sync_func(**kwargs: Any) -> str:
        return "non-streaming result"  # pragma: no cover

    def sync_generator_func(**kwargs: Any) -> Iterator[str]:
        yield "streaming result 1"
        yield "streaming result 2"

    create_or_stream = get_create_fn(sync_func, sync_generator_func)
    stream_result = create_or_stream(stream=True)
    assert isinstance(stream_result, Generator)

    results = list(stream_result)
    assert results == ["streaming result 1", "streaming result 2"]


def test_get_create_fn_streaming_without_generator():
    def sync_func(**kwargs: Any) -> Iterator[str]:
        yield "streaming result 1"
        yield "streaming result 2"

    create_or_stream = get_create_fn(sync_func)
    stream_result = create_or_stream(stream=True)
    assert isinstance(stream_result, Generator)

    results = list(stream_result)
    assert results == ["streaming result 1", "streaming result 2"]


def test_get_create_fn_streaming_with_iterable():
    def sync_func(**kwargs: Any) -> Iterable[str]:
        return ["streaming result 1", "streaming result 2"]

    create_or_stream = get_create_fn(sync_func)
    stream_result = create_or_stream(stream=True)
    assert isinstance(stream_result, Generator)

    results = list(stream_result)
    assert results == ["streaming result 1", "streaming result 2"]


def test_get_create_fn_with_additional_kwargs():
    def sync_func(**kwargs: Any) -> str:
        return f"result: {kwargs.get('param', '')}"

    create_or_stream = get_create_fn(sync_func)
    result = create_or_stream(stream=False, param="test")
    assert result == "result: test"


def test_get_create_fn_streaming_with_additional_kwargs():
    def sync_generator_func(**kwargs: Any) -> Iterator[str]:
        yield f"streaming result: {kwargs.get('param', '')}"

    create_or_stream = get_create_fn(lambda **kwargs: "unused", sync_generator_func)
    stream_result = create_or_stream(stream=True, param="test")
    assert isinstance(stream_result, Generator)

    results = list(stream_result)
    assert results == ["streaming result: test"]


def test_get_create_fn_default_stream_value():
    def sync_func(**kwargs: Any) -> str:
        return "non-streaming result"

    create_or_stream = get_create_fn(sync_func)
    result = create_or_stream()  # Default stream=False
    assert result == "non-streaming result"


def test_get_create_fn_type_casting():
    def sync_func(**kwargs: Any) -> str:
        return "non-streaming result"

    def sync_generator_func(**kwargs: Any) -> Iterator[str]:
        yield "streaming result"

    create_or_stream = get_create_fn(sync_func, sync_generator_func)

    # Test non-streaming mode
    non_stream_result = create_or_stream(stream=False)
    assert isinstance(non_stream_result, str)
    assert non_stream_result == "non-streaming result"

    # Test streaming mode
    stream_result = create_or_stream(stream=True)
    assert isinstance(stream_result, Generator)

    # Consume the Generator to verify its content
    results = list(stream_result)
    assert results == ["streaming result"]
