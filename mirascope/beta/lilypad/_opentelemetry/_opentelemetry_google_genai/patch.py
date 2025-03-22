from collections.abc import AsyncGenerator, Awaitable, Callable
from typing import Any, ParamSpec

from opentelemetry.semconv._incubating.attributes import gen_ai_attributes
from opentelemetry.semconv.attributes import error_attributes
from opentelemetry.trace import SpanKind, Status, StatusCode, Tracer

from .utils import (
    get_llm_request_attributes,
    set_content_event,
    set_response_attributes,
    set_stream,
)

P = ParamSpec("P")


def generate_content(
    tracer: Tracer,
    stream: bool = False,
) -> Callable[[Callable[P, Any], Any, tuple[Any, ...], dict[str, Any]], Any]:
    """Synchronous wrapper for generate_content.

    Extracts request attributes, records content events,
    starts a span, calls the wrapped method, and records response or streaming attributes.
    """

    def traced_method(
        wrapped: Callable[P, Any],
        instance: Any,
        args: tuple[Any, ...],
        kwargs: dict[str, Any],
    ) -> Any:
        span_attributes = {**get_llm_request_attributes(kwargs, instance)}
        span_name = (
            f"{span_attributes.get(gen_ai_attributes.GEN_AI_OPERATION_NAME, 'generate_content')} "
            f"{span_attributes.get(gen_ai_attributes.GEN_AI_REQUEST_MODEL, 'unknown')}"
        )
        with tracer.start_as_current_span(
            name=span_name,
            kind=SpanKind.CLIENT,
            attributes=span_attributes,
            end_on_exit=False,
        ) as span:
            if span.is_recording():
                for content in kwargs.get("contents", []):
                    set_content_event(span, content)
            try:
                result = wrapped(*args, **kwargs)
                if stream:
                    # For synchronous streaming, process stream chunks
                    set_stream(span, result, instance)
                elif span.is_recording():
                    set_response_attributes(span, result)
                span.end()
                return result
            except Exception as error:
                span.set_status(Status(StatusCode.ERROR, str(error)))
                if span.is_recording():
                    span.set_attribute(
                        error_attributes.ERROR_TYPE, type(error).__qualname__
                    )
                span.end()
                raise

    return traced_method


def generate_content_async(
    tracer: Tracer, stream: bool = False
) -> Callable[[Callable[P, Any], Any, tuple[Any, ...], dict[str, Any]], Awaitable[Any]]:
    """Asynchronous wrapper for generate_content_async.

    Extracts request attributes, records content events,
    starts a span, awaits the wrapped method, and records response or streaming attributes.
    """

    async def traced_method(
        wrapped: Callable[P, Any],
        instance: Any,
        args: tuple[Any, ...],
        kwargs: dict[str, Any],
    ) -> Any:
        span_attributes = {**get_llm_request_attributes(kwargs, instance)}
        span_name = (
            f"{span_attributes.get(gen_ai_attributes.GEN_AI_OPERATION_NAME, 'generate_content')} "
            f"{span_attributes.get(gen_ai_attributes.GEN_AI_REQUEST_MODEL, 'unknown')}"
        )
        with tracer.start_as_current_span(
            name=span_name,
            kind=SpanKind.CLIENT,
            attributes=span_attributes,
            end_on_exit=False,
        ) as span:
            if span.is_recording():
                for content in kwargs.get("contents", []):
                    set_content_event(span, content)
            try:
                result = await wrapped(*args, **kwargs)
                if stream:
                    # Wrap the async stream so that candidate events are recorded on-the-fly
                    async def stream_wrapper() -> AsyncGenerator[Any, Any]:
                        finish_reasons = []
                        async for chunk in result:
                            candidates = getattr(chunk, "candidates", None)
                            if candidates:
                                for candidate in candidates:
                                    finish_reason = (
                                        candidate.finish_reason.value
                                        if candidate.finish_reason
                                        else "none",
                                    )
                                    event_attrs = {
                                        "candidate_index": candidate.index or 0,
                                        "finish_reason": finish_reason,
                                    }
                                    span.add_event(
                                        "gen_ai.candidate", attributes=event_attrs
                                    )
                                    finish_reasons.append(finish_reason)
                            yield chunk
                        if finish_reasons:
                            span.set_attributes(
                                {
                                    gen_ai_attributes.GEN_AI_RESPONSE_FINISH_REASONS: finish_reasons[
                                        0
                                    ]
                                }
                            )

                    # Return a new async generator that wraps the original stream.
                    async def final_wrapper() -> AsyncGenerator[Any, Any]:
                        try:
                            async for chunk in stream_wrapper():
                                yield chunk
                        finally:
                            span.end()

                    return final_wrapper()
                elif span.is_recording():
                    set_response_attributes(span, result)
                span.end()
                return result
            except Exception as error:
                span.set_status(Status(StatusCode.ERROR, str(error)))
                if span.is_recording():
                    span.set_attribute(
                        error_attributes.ERROR_TYPE, type(error).__qualname__
                    )
                span.end()
                raise

    return traced_method
