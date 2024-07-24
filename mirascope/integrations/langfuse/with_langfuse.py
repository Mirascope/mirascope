"""Mirascope x Langfuse Integration."""

from typing import (
    AsyncIterable,
    Awaitable,
    Callable,
    Iterable,
    ParamSpec,
    TypeVar,
)

from langfuse.decorators import langfuse_context, observe
from pydantic import BaseModel

from mirascope.core.base._structured_stream import BaseStructuredStream

from ...core.base import BaseCallResponse
from ...core.base._stream import BaseStream
from ..middleware_factory import middleware_decorator
from ._utils import get_call_response_observation, get_stream_observation

_BaseCallResponseT = TypeVar("_BaseCallResponseT", bound=BaseCallResponse)
_BaseStreamT = TypeVar("_BaseStreamT", bound=BaseStream)
_BaseModelT = TypeVar("_BaseModelT", bound=BaseModel)
_IterableT = TypeVar("_IterableT", bound=Iterable)
_AsyncIterableT = TypeVar("_AsyncIterableT", bound=AsyncIterable)
_P = ParamSpec("_P")
SyncFunc = Callable[_P, _BaseCallResponseT | _BaseStreamT | _BaseModelT | _IterableT]
AsyncFunc = Callable[
    _P, Awaitable[_BaseCallResponseT | _BaseStreamT | _BaseModelT | _AsyncIterableT]
]
_T = TypeVar("_T")


def with_langfuse(
    fn: SyncFunc | AsyncFunc,
) -> SyncFunc | AsyncFunc:
    """Wraps a Mirascope function with Langfuse."""

    class ModelUsage(BaseModel):
        input: int | float | None
        output: int | float | None
        unit: str

    def handle_call_response(result: BaseCallResponse, context: None):
        langfuse_context.update_current_observation(
            **get_call_response_observation(result, fn),
            usage=ModelUsage(
                input=result.input_tokens, output=result.output_tokens, unit="TOKENS"
            ),
        )

    def handle_stream(stream: BaseStream, context: None):
        usage = ModelUsage(
            input=stream.input_tokens,
            output=stream.output_tokens,
            unit="TOKENS",
        )
        langfuse_context.update_current_observation(
            **get_stream_observation(stream, fn),
            usage=usage,
        )

    def handle_base_model(result: BaseModel | BaseStructuredStream, context: None):
        if result._response is not None:  # type: ignore
            response: BaseCallResponse = result._response  # type: ignore
            handle_call_response(response, None)
        langfuse_context.update_current_observation(output=result)

    async def handle_call_response_async(result: BaseCallResponse, context: None):
        handle_call_response(result, None)

    async def handle_stream_async(stream: BaseStream, context: None):
        handle_stream(stream, None)

    async def handle_base_model_async(
        result: BaseModel | BaseStructuredStream, context: None
    ):
        handle_base_model(result, None)

    return middleware_decorator(
        fn,
        custom_decorator=observe(
            name=fn.__name__,
            as_type="generation",
            capture_input=False,
            capture_output=False,
        ),
        handle_call_response=handle_call_response,
        handle_call_response_async=handle_call_response_async,
        handle_stream=handle_stream,
        handle_stream_async=handle_stream_async,
        handle_base_model=handle_base_model,
        handle_base_model_async=handle_base_model_async,
    )
