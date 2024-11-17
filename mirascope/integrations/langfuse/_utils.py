from collections.abc import Callable
from typing import Any

from langfuse.decorators import langfuse_context
from pydantic import BaseModel

from mirascope.core.base._utils._base_type import BaseType

from ...core.base import BaseCallResponse
from ...core.base._utils import get_metadata
from ...core.base.stream import BaseStream
from ...core.base.structured_stream import BaseStructuredStream


class ModelUsage(BaseModel):
    input: int | float | None
    output: int | float | None
    unit: str


def _get_call_response_observation(
    result: BaseCallResponse, fn: Callable
) -> dict[str, Any]:
    metadata = get_metadata(fn, {})
    tags = metadata.get("tags", [])
    return {
        "name": f"{fn.__name__} with {result.model}",
        "input": result.messages,
        "metadata": result.response,
        "tags": tags,
        "model": result.model,
        "output": result.message_param.get("content", None),
    }


def handle_call_response(result: BaseCallResponse, fn: Callable, context: None) -> None:
    langfuse_context.update_current_observation(
        **_get_call_response_observation(result, fn),
        usage=ModelUsage(
            input=result.input_tokens, output=result.output_tokens, unit="TOKENS"
        ),
    )


def handle_stream(stream: BaseStream, fn: Callable, context: None) -> None:
    usage = ModelUsage(
        input=stream.input_tokens,
        output=stream.output_tokens,
        unit="TOKENS",
    )
    langfuse_context.update_current_observation(
        **_get_call_response_observation(stream.construct_call_response(), fn),
        usage=usage,
    )


def handle_response_model(
    result: BaseModel | BaseType, fn: Callable, context: None
) -> None:
    if isinstance(result, BaseModel):
        response: BaseCallResponse = result._response  # pyright: ignore [reportAttributeAccessIssue]
        call_response_observation = _get_call_response_observation(response, fn)
        call_response_observation.pop("output")
        langfuse_context.update_current_observation(
            **call_response_observation,
            usage=ModelUsage(
                input=response.input_tokens,
                output=response.output_tokens,
                unit="TOKENS",
            ),
            output=result,
        )
    else:
        langfuse_context.update_current_observation(
            output=result,
        )


def handle_structured_stream(
    result: BaseStructuredStream, fn: Callable, context: None
) -> None:
    stream: BaseStream = result.stream
    usage = ModelUsage(
        input=stream.input_tokens,
        output=stream.output_tokens,
        unit="TOKENS",
    )
    langfuse_context.update_current_observation(
        **_get_call_response_observation(stream.construct_call_response(), fn),
        usage=usage,
        output=result.constructed_response_model,
    )


async def handle_call_response_async(
    result: BaseCallResponse, fn: Callable, context: None
) -> None:
    handle_call_response(result, fn, None)


async def handle_stream_async(stream: BaseStream, fn: Callable, context: None) -> None:
    handle_stream(stream, fn, None)


async def handle_response_model_async(
    result: BaseModel | BaseType, fn: Callable, context: None
) -> None:
    handle_response_model(result, fn, None)


async def handle_structured_stream_async(
    result: BaseStructuredStream, fn: Callable, context: None
) -> None:
    handle_structured_stream(result, fn, None)
