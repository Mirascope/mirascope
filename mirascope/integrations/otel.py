"""Mirascope x OpenTelemetry Integration."""

import json
from contextlib import contextmanager
from typing import (
    Any,
    Awaitable,
    Callable,
    Generator,
    ParamSpec,
    Sequence,
    TypeVar,
    overload,
)

from opentelemetry.sdk.trace import SpanProcessor, TracerProvider
from opentelemetry.sdk.trace.export import (
    ConsoleSpanExporter,
    SimpleSpanProcessor,
)
from opentelemetry.trace import (
    Tracer,
    get_tracer,
    get_tracer_provider,
    set_tracer_provider,
)
from opentelemetry.trace.span import Span
from opentelemetry.util.types import Attributes, AttributeValue
from pydantic import BaseModel

from ..core.base import BaseAsyncStream, BaseCallResponse, BaseStream
from .utils import middleware

_P = ParamSpec("_P")
_R = TypeVar("_R", bound=BaseCallResponse | BaseStream | BaseModel | BaseAsyncStream)


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


@overload
def with_otel(fn: Callable[_P, _R]) -> Callable[_P, _R]: ...


@overload
def with_otel(fn: Callable[_P, Awaitable[_R]]) -> Callable[_P, Awaitable[_R]]: ...


def with_otel(
    fn: Callable[_P, _R] | Callable[_P, Awaitable[_R]],
) -> Callable[_P, _R] | Callable[_P, Awaitable[_R]]:
    """Wraps a Mirascope function with OpenTelemetry tracing."""

    @contextmanager
    def custom_context_manager() -> Generator[Span, Any, None]:
        tracer = get_tracer("otel")
        with tracer.start_as_current_span(f"{fn.__name__}") as span:
            yield span

    def handle_call_response(result: BaseCallResponse, span: Span | None):
        if span is None:
            return
        max_tokens = getattr(result.call_params, "max_tokens", 0)
        temperature = getattr(result.call_params, "temperature", 0)
        top_p = getattr(result.call_params, "top_p", 0)
        attributes: dict[str, AttributeValue] = {
            "async": False,
            "gen_ai.system": result.prompt_template,
            "gen_ai.request.model": result.model,
            "gen_ai.request.max_tokens": max_tokens,
            "gen_ai.request.temperature": temperature,
            "gen_ai.request.top_p": top_p,
            "gen_ai.response.model": result.model,
            "gen_ai.response.id": result.id,
            "gen_ai.response.finish_reasons": result.finish_reasons,
            "gen_ai.usage.completion_tokens": result.output_tokens,
            "gen_ai.usage.prompt_tokens": result.input_tokens,
        }

        prompt_event: Attributes = {
            "gen_ai.prompt": json.dumps(result.user_message_param),
        }
        completion_event: Attributes = {
            "gen_ai.completion": json.dumps(result.message_param),
        }
        span.set_attributes(attributes)
        span.add_event("gen_ai.content.prompt", attributes=prompt_event)
        span.add_event(
            "gen_ai.content.completion",
            attributes=completion_event,
        )

    def handle_stream(stream: BaseStream, span: Span | None):
        if span is None:
            return
        max_tokens = getattr(stream.call_params, "max_tokens", 0)
        temperature = getattr(stream.call_params, "temperature", 0)
        top_p = getattr(stream.call_params, "top_p", 0)
        attributes: dict[str, AttributeValue] = {
            "async": False,
            "gen_ai.system": stream.prompt_template,
            "gen_ai.request.model": stream.model,
            "gen_ai.request.max_tokens": max_tokens,
            "gen_ai.request.temperature": temperature,
            "gen_ai.request.top_p": top_p,
            "gen_ai.response.model": stream.model,
            "gen_ai.usage.completion_tokens": stream.output_tokens,
            "gen_ai.usage.prompt_tokens": stream.input_tokens,
        }

        prompt_event: Attributes = {
            "gen_ai.prompt": json.dumps(stream.user_message_param),
        }
        completion_event: Attributes = {
            "gen_ai.completion": json.dumps(stream.message_param),
        }
        span.set_attributes(attributes)
        span.add_event("gen_ai.content.prompt", attributes=prompt_event)
        span.add_event(
            "gen_ai.content.completion",
            attributes=completion_event,
        )

    def handle_base_model(result: BaseModel, span: Span | None): ...

    async def handle_call_response_async(
        result: BaseCallResponse, span: Span | None
    ): ...

    async def handle_stream_async(stream: BaseStream, span: Span | None): ...

    provider = get_tracer_provider()
    if not isinstance(provider, TracerProvider):
        configure()
    return middleware(
        fn,
        custom_context_manager=custom_context_manager,
        handle_call_response=handle_call_response,
        handle_call_response_async=handle_call_response_async,
        handle_stream=handle_stream,
        handle_stream_async=handle_stream_async,
        handle_base_model=handle_base_model,
        # handle_base_model_async=handle_base_model_async,
    )
