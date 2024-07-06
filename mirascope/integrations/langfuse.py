"""Mirascope x Langfuse Integration."""

from typing import (
    Awaitable,
    Callable,
    ParamSpec,
    TypeVar,
    overload,
)

from langfuse.decorators import langfuse_context, observe
from langfuse.types import ModelUsage
from pydantic import BaseModel

from ..core.base import BaseCallResponse
from ..core.base._stream import BaseStream
from .utils import middleware

_P = ParamSpec("_P")
_R = TypeVar("_R", bound=BaseCallResponse | BaseStream | BaseModel)


@overload
def with_langfuse(fn: Callable[_P, _R]) -> Callable[_P, _R]: ...


@overload
def with_langfuse(fn: Callable[_P, Awaitable[_R]]) -> Callable[_P, Awaitable[_R]]: ...


def with_langfuse(
    fn: Callable[_P, _R] | Callable[_P, Awaitable[_R]],
) -> Callable[_P, _R] | Callable[_P, Awaitable[_R]]:
    """Wraps a Mirascope function with Langfuse tracing."""

    def get_call_response_observation(result: BaseCallResponse):
        return {
            "name": f"{fn.__name__} with {result.model}",
            "input": result.prompt_template,
            "metadata": result.response,
            "tags": result.tags,
            "model": result.model,
            "output": result.message_param.get("content", None),
        }

    def get_stream_observation(stream: BaseStream):
        return {
            "name": f"{fn.__name__} with {stream.model}",
            "input": stream.prompt_template,
            "tags": fn.__annotations__.get("tags", []),
            "model": stream.model,
            "output": stream.message_param.get("content", None),
        }

    def handle_call_response(result: BaseCallResponse):
        usage = ModelUsage(
            input=result.input_tokens,
            output=result.output_tokens,
            unit="TOKENS",
        )
        langfuse_context.update_current_observation(
            **get_call_response_observation(result),
            usage=usage,
        )

    def handle_stream(stream: BaseStream):
        # TODO: Re-add once Mirascope supports streaming usage
        # usage = ModelUsage(
        #     input=stream.input_tokens,
        #     output=stream.output_tokens,
        #     unit="TOKENS",
        # )
        langfuse_context.update_current_observation(
            **get_stream_observation(stream),
            # usage=usage,
        )

    def handle_base_model(result: BaseModel):
        if result._response is not None:
            response: BaseCallResponse = result._response
            handle_call_response(response)
        langfuse_context.update_current_observation(output=result)

    async def handle_call_response_async(result: BaseCallResponse):
        handle_call_response(result)

    async def handle_stream_async(stream: BaseStream):
        handle_stream(stream)

    async def handle_base_model_async(result: BaseModel):
        handle_base_model(result)

    return middleware(
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
