"""Mirascope x Langfuse Integration."""

from typing import (
    Awaitable,
    Callable,
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
_BaseStructuredStreamT = TypeVar("_BaseStructuredStreamT", bound=BaseStructuredStream)
_P = ParamSpec("_P")
SyncFunc = Callable[
    _P, _BaseCallResponseT | _BaseStreamT | _BaseModelT | _BaseStructuredStreamT
]
AsyncFunc = Callable[
    _P,
    Awaitable[_BaseCallResponseT | _BaseStreamT | _BaseModelT | _BaseStructuredStreamT],
]
_T = TypeVar("_T")


class ModelUsage(BaseModel):
    input: int | float | None
    output: int | float | None
    unit: str


def with_langfuse(
    fn: SyncFunc | AsyncFunc,
) -> SyncFunc | AsyncFunc:
    """Wraps a Mirascope function with Langfuse."""

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
        if isinstance(result, BaseModel):
            response: BaseCallResponse = result._response  # type: ignore
            langfuse_context.update_current_observation(
                **get_call_response_observation(response, fn),
                usage=ModelUsage(
                    input=response.input_tokens,
                    output=response.output_tokens,
                    unit="TOKENS",
                ),
                output=result,
            )
        elif isinstance(result, BaseStructuredStream):
            stream: BaseStream = result.stream
            usage = ModelUsage(
                input=stream.input_tokens,
                output=stream.output_tokens,
                unit="TOKENS",
            )
            langfuse_context.update_current_observation(
                **get_stream_observation(stream, fn),
                usage=usage,
                output=result.constructed_response_model,
            )

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
