"""Patch methods for OpenTelemetry tracing in Outlines."""

from __future__ import annotations

from collections.abc import Callable, Coroutine, Generator
from typing import Any

from opentelemetry.trace import SpanKind, Status, StatusCode
from typing_extensions import ParamSpec

from .utils import (
    extract_arguments,
    extract_generation_attributes,
    record_prompts,
    record_stop_sequences,
    set_choice_event,
)

P = ParamSpec("P")


def model_generate(
    tracer: Any,
) -> Callable[[Callable[P, Any], Any, tuple[Any, ...], dict[str, Any]], Any]:
    """Wrapper for synchronous generate methods."""

    def traced_method(
        wrapped: Callable[P, Any],
        instance: Any,
        args: tuple[Any, ...],
        kwargs: dict[str, Any],
    ) -> Any:
        prompts, generation_parameters, sampling_parameters, model_name = (
            extract_arguments(wrapped, instance, args, kwargs)
        )
        attributes = extract_generation_attributes(
            generation_parameters, sampling_parameters, model_name
        )
        span_name = f"outlines.generate {model_name}"

        with tracer.start_as_current_span(
            name=span_name,
            kind=SpanKind.CLIENT,
            attributes=attributes,
            end_on_exit=False,
        ) as span:
            stop_at = generation_parameters.stop_at if generation_parameters else None
            record_prompts(span, prompts)
            record_stop_sequences(span, stop_at)

            try:
                result = wrapped(*args, **kwargs)
                set_choice_event(span, result)
                span.end()
                return result
            except Exception as e:
                span.set_status(Status(StatusCode.ERROR, str(e)))
                span.record_exception(e)
                span.end()
                raise

    return traced_method


def model_generate_stream(
    tracer: Any,
) -> Callable[[Callable[P, Any], Any, tuple[Any, ...], dict[str, Any]], Any]:
    """Wrapper for synchronous stream methods."""

    def traced_method(
        wrapped: Callable[P, Any],
        instance: Any,
        args: tuple[Any, ...],
        kwargs: dict[str, Any],
    ) -> Any:
        prompts, generation_parameters, sampling_parameters, model_name = (
            extract_arguments(wrapped, instance, args, kwargs)
        )
        attributes = extract_generation_attributes(
            generation_parameters, sampling_parameters, model_name
        )
        span_name = f"outlines.stream {model_name}"

        with tracer.start_as_current_span(
            name=span_name,
            kind=SpanKind.CLIENT,
            attributes=attributes,
            end_on_exit=False,
        ) as span:
            stop_at = generation_parameters.stop_at if generation_parameters else None
            record_prompts(span, prompts)
            record_stop_sequences(span, stop_at)

            try:
                generator = wrapped(*args, **kwargs)

                def gen() -> Generator[Any, None, None]:
                    try:
                        for chunk in generator:
                            if span.is_recording():
                                span.add_event(
                                    "gen_ai.partial_response",
                                    attributes={"chunk": str(chunk)},
                                )
                            yield chunk
                    except Exception as e:
                        span.set_status(Status(StatusCode.ERROR, str(e)))
                        span.record_exception(e)
                        raise
                    finally:
                        span.end()

                return gen()
            except Exception as e:
                span.set_status(Status(StatusCode.ERROR, str(e)))
                span.record_exception(e)
                span.end()
                raise

    return traced_method


def model_generate_async(
    tracer: Any,
) -> Callable[
    [Callable[P, Any], Any, tuple[Any, ...], dict[str, Any]], Coroutine[Any, Any, Any]
]:
    """Wrapper for async methods like async def generate_chat(...)"""

    async def traced_method(
        wrapped: Callable[P, Any],
        instance: Any,
        args: tuple[Any, ...],
        kwargs: dict[str, Any],
    ) -> Any:
        prompts, generation_parameters, sampling_parameters, model_name = (
            extract_arguments(wrapped, instance, args, kwargs)
        )
        attributes = extract_generation_attributes(
            generation_parameters, sampling_parameters, model_name
        )
        span_name = f"outlines.generate_async {model_name}"

        with tracer.start_as_current_span(
            name=span_name,
            kind=SpanKind.CLIENT,
            attributes=attributes,
            end_on_exit=False,
        ) as span:
            stop_at = generation_parameters.stop_at if generation_parameters else None
            record_prompts(span, prompts)
            record_stop_sequences(span, stop_at)

            try:
                result = await wrapped(*args, **kwargs)
                set_choice_event(span, result)
                span.end()
                return result
            except Exception as e:
                span.set_status(Status(StatusCode.ERROR, str(e)))
                span.record_exception(e)
                span.end()
                raise

    return traced_method
