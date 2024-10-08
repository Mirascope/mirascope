from collections.abc import AsyncGenerator, Callable, Coroutine, Generator
from functools import wraps
from typing import Any, ParamSpec

from mypy_boto3_bedrock_runtime.type_defs import (
    ConverseStreamResponseTypeDef,
)
from types_aiobotocore_bedrock_runtime.type_defs import (
    ConverseStreamResponseTypeDef as AsyncConverseStreamResponseTypeDef,
)

from mirascope.core.bedrock._utils._types import (
    AsyncStreamOutputChunk,
    StreamOutputChunk,
)

_P = ParamSpec("_P")


def _extract_sync_stream_fn(
    fn: Callable[_P, ConverseStreamResponseTypeDef], model: str
) -> Callable[_P, Generator[StreamOutputChunk, None, None]]:
    @wraps(fn)
    def _inner(
        *args: _P.args, **kwargs: _P.kwargs
    ) -> Generator[StreamOutputChunk, None, None]:
        response = fn(*args, **kwargs)
        for chunk in response["stream"]:
            yield StreamOutputChunk(
                responseMetadata=response["ResponseMetadata"], model=model, **chunk
            )

    return _inner


def _extract_async_stream_fn(
    fn: Callable[_P, Coroutine[Any, Any, AsyncConverseStreamResponseTypeDef]],
    model: str,
) -> Callable[_P, AsyncGenerator[AsyncStreamOutputChunk, None]]:
    @wraps(fn)
    async def _inner(
        *args: _P.args, **kwargs: _P.kwargs
    ) -> AsyncGenerator[AsyncStreamOutputChunk, None]:
        response = await fn(*args, **kwargs)
        async for chunk in response["stream"]:
            yield AsyncStreamOutputChunk(
                responseMetadata=response["ResponseMetadata"], model=model, **chunk
            )

    return _inner
