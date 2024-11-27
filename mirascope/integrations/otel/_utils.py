"""Mirascope x OpenTelemetry Integration utils"""

import json
from collections.abc import Callable, Generator, Sequence
from contextlib import contextmanager
from typing import Any

from opentelemetry.sdk.trace import SpanProcessor, TracerProvider
from opentelemetry.sdk.trace.export import (
    ConsoleSpanExporter,
    SimpleSpanProcessor,
)
from opentelemetry.trace import (
    Tracer,
    get_tracer,
    set_tracer_provider,
)
from opentelemetry.trace.span import Span
from opentelemetry.util.types import Attributes, AttributeValue
from pydantic import BaseModel

from mirascope.core.base._utils._base_type import BaseType

from ...core.base import BaseCallResponse
from ...core.base.stream import BaseStream
from ...core.base.structured_stream import BaseStructuredStream


def configure(
    processors: Sequence[SpanProcessor] | None = None,
) -> Tracer:
    """Configures the OpenTelemetry tracer, this function should only be called once.

    Args:
        processors: Optional[Sequence[SpanProcessor]]
            The span processors to use, if None, a console exporter will be used.

    Returns:
        The configured tracer.
    """
    provider = TracerProvider()
    if processors is None:
        provider.add_span_processor(SimpleSpanProcessor(ConsoleSpanExporter()))
    else:
        for processor in processors:
            provider.add_span_processor(processor)
    # NOTE: Sets the global trace provider, should only be called once
    set_tracer_provider(provider)
    return get_tracer("otel")


@contextmanager
def custom_context_manager(
    fn: Callable,
) -> Generator[Span, Any, None]:
    tracer = get_tracer("otel")
    with tracer.start_as_current_span(f"{fn.__name__}") as span:
        yield span


def _get_call_response_attributes(
    result: BaseCallResponse,
) -> dict[str, AttributeValue]:
    max_tokens = getattr(result.call_params, "max_tokens", 0)
    temperature = getattr(result.call_params, "temperature", 0)
    top_p = getattr(result.call_params, "top_p", 0)

    return {
        "gen_ai.system": result.prompt_template if result.prompt_template else "",
        "gen_ai.request.model": result.call_kwargs.get("model", ""),
        "gen_ai.request.max_tokens": max_tokens,
        "gen_ai.request.temperature": temperature,
        "gen_ai.request.top_p": top_p,
        "gen_ai.response.model": result.model if result.model else "",
        "gen_ai.response.id": result.id if result.id else "",
        "gen_ai.response.finish_reasons": result.finish_reasons
        if result.finish_reasons
        else "",
        "gen_ai.usage.completion_tokens": result.output_tokens
        if result.output_tokens
        else "",
        "gen_ai.usage.prompt_tokens": result.input_tokens
        if result.input_tokens
        else "",
    }


def _set_call_response_event_attributes(result: BaseCallResponse, span: Span) -> None:
    prompt_attributes = {
        "gen_ai.prompt": json.dumps(result.user_message_param),
    }
    completion_attributes: Attributes = {
        "gen_ai.completion": json.dumps(result.message_param),
    }
    span.add_event(
        "gen_ai.content.prompt",
        attributes=prompt_attributes,
    )
    span.add_event(
        "gen_ai.content.completion",
        attributes=completion_attributes,
    )


def handle_call_response(
    result: BaseCallResponse, fn: Callable, span: Span | None
) -> None:
    if span is None:
        return

    attributes = _get_call_response_attributes(result)
    attributes["async"] = False
    span.set_attributes(attributes)
    _set_call_response_event_attributes(result, span)


def handle_stream(stream: BaseStream, fn: Callable, span: Span | None) -> None:
    if span is None:
        return
    constructed_call_response = stream.construct_call_response()
    attributes = _get_call_response_attributes(constructed_call_response)
    attributes["async"] = False
    span.set_attributes(attributes)
    _set_call_response_event_attributes(constructed_call_response, span)


def handle_response_model(
    result: BaseModel | BaseType, fn: Callable, span: Span | None
) -> None:
    if span is None:
        return
    if isinstance(result, BaseModel):
        response: BaseCallResponse = result._response  # pyright: ignore [reportAttributeAccessIssue]
        attributes = _get_call_response_attributes(response)
        attributes["async"] = False
        span.set_attributes(attributes)
        prompt_attributes = {
            "gen_ai.prompt": json.dumps(response.user_message_param),
        }
        completion_attributes: Attributes = {
            "gen_ai.completion": result.model_dump_json(),
        }
        span.add_event(
            "gen_ai.content.prompt",
            attributes=prompt_attributes,
        )
    else:
        span.set_attributes({"async": False})
        if not isinstance(result, str | int | float | bool):
            result = str(result)
        completion_attributes: Attributes = {
            "gen_ai.completion": result,
        }
    span.add_event(
        "gen_ai.content.completion",
        attributes=completion_attributes,
    )


def handle_structured_stream(
    result: BaseStructuredStream, fn: Callable, span: Span | None
) -> None:
    if span is None:
        return
    attributes = _get_call_response_attributes(result.stream.construct_call_response())
    attributes["async"] = False
    span.set_attributes(attributes)
    prompt_attributes = {
        "gen_ai.prompt": json.dumps(result.stream.user_message_param),
    }
    if isinstance(result.constructed_response_model, BaseModel):
        completion = result.constructed_response_model.model_dump_json()
    else:
        completion = result.constructed_response_model
    completion_attributes: Attributes = {
        "gen_ai.completion": completion,
    }
    span.add_event(
        "gen_ai.content.prompt",
        attributes=prompt_attributes,
    )
    span.add_event(
        "gen_ai.content.completion",
        attributes=completion_attributes,
    )


async def handle_call_response_async(
    result: BaseCallResponse, fn: Callable, span: Span | None
) -> None:
    if span is None:
        return

    attributes = _get_call_response_attributes(result)
    attributes["async"] = True
    span.set_attributes(attributes)
    _set_call_response_event_attributes(result, span)


async def handle_stream_async(
    stream: BaseStream, fn: Callable, span: Span | None
) -> None:
    if span is None:
        return
    constructed_call_response = stream.construct_call_response()
    attributes = _get_call_response_attributes(constructed_call_response)
    attributes["async"] = True
    span.set_attributes(attributes)
    _set_call_response_event_attributes(constructed_call_response, span)


async def handle_response_model_async(
    result: BaseModel | BaseType, fn: Callable, span: Span | None
) -> None:
    if span is None:
        return
    if isinstance(result, BaseModel):
        response: BaseCallResponse = result._response  # pyright: ignore [reportAttributeAccessIssue]
        attributes = _get_call_response_attributes(response)
        attributes["async"] = True
        span.set_attributes(attributes)
        prompt_attributes = {
            "gen_ai.prompt": json.dumps(response.user_message_param),
        }
        completion_attributes: Attributes = {
            "gen_ai.completion": result.model_dump_json(),
        }
        span.add_event(
            "gen_ai.content.prompt",
            attributes=prompt_attributes,
        )
    else:
        span.set_attributes({"async": True})
        if not isinstance(result, str | int | float | bool):
            result = str(result)
        completion_attributes: Attributes = {
            "gen_ai.completion": result,
        }
    span.add_event(
        "gen_ai.content.completion",
        attributes=completion_attributes,
    )


async def handle_structured_stream_async(
    result: BaseStructuredStream, fn: Callable, span: Span | None
) -> None:
    if span is None:
        return
    attributes = _get_call_response_attributes(result.stream.construct_call_response())
    attributes["async"] = True
    span.set_attributes(attributes)
    prompt_attributes = {
        "gen_ai.prompt": json.dumps(result.stream.user_message_param),
    }
    if isinstance(result.constructed_response_model, BaseModel):
        completion = result.constructed_response_model.model_dump_json()
    else:
        completion = result.constructed_response_model
    completion_attributes: Attributes = {
        "gen_ai.completion": completion,
    }
    span.add_event(
        "gen_ai.content.prompt",
        attributes=prompt_attributes,
    )
    span.add_event(
        "gen_ai.content.completion",
        attributes=completion_attributes,
    )
