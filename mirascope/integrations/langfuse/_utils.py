from typing import Callable

from langfuse.decorators import langfuse_context
from pydantic import BaseModel

from ...core.base import BaseCallResponse
from ...core.base._stream import BaseStream
from ...core.base._structured_stream import BaseStructuredStream
from ...core.base._utils import get_metadata


class ModelUsage(BaseModel):
    input: int | float | None
    output: int | float | None
    unit: str


def get_call_response_observation(result: BaseCallResponse, fn: Callable):
    metadata = get_metadata(fn, {})
    tags = metadata.get("tags", [])
    return {
        "name": f"{fn.__name__} with {result.model}",
        "input": result.prompt_template,
        "metadata": result.response,
        "tags": tags,
        "model": result.model,
        "output": result.message_param.get("content", None),
    }


def get_stream_observation(stream: BaseStream, fn: Callable):
    metadata = get_metadata(fn, {})
    tags = metadata.get("tags", [])

    return {
        "name": f"{fn.__name__} with {stream.model}",
        "input": stream.prompt_template,
        "tags": tags,
        "model": stream.model,
        "output": stream.message_param.get("content", None),  # type: ignore
    }


def handle_call_response(result: BaseCallResponse, fn: Callable, context: None):
    langfuse_context.update_current_observation(
        **get_call_response_observation(result, fn),
        usage=ModelUsage(
            input=result.input_tokens, output=result.output_tokens, unit="TOKENS"
        ),
    )


def handle_stream(stream: BaseStream, fn: Callable, context: None):
    usage = ModelUsage(
        input=stream.input_tokens,
        output=stream.output_tokens,
        unit="TOKENS",
    )
    langfuse_context.update_current_observation(
        **get_stream_observation(stream, fn),
        usage=usage,
    )


def handle_base_model(
    result: BaseModel | BaseStructuredStream, fn: Callable, context: None
):
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


def handle_structured_stream(result: BaseStructuredStream, fn: Callable, context: None):
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


async def handle_call_response_async(
    result: BaseCallResponse, fn: Callable, context: None
):
    handle_call_response(result, fn, None)


async def handle_stream_async(stream: BaseStream, fn: Callable, context: None):
    handle_stream(stream, fn, None)


async def handle_base_model_async(result: BaseModel, fn: Callable, context: None):
    handle_base_model(result, fn, None)


async def handle_structured_stream_async(
    result: BaseStructuredStream, fn: Callable, context: None
):
    handle_structured_stream(result, fn, None)
