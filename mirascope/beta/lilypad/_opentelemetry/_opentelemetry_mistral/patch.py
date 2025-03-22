from collections.abc import Awaitable, Callable
from typing import Any

from opentelemetry.semconv.attributes import error_attributes
from opentelemetry.trace import SpanKind, Status, StatusCode, Tracer
from typing_extensions import ParamSpec

from lilypad._opentelemetry._utils import AsyncStreamWrapper, StreamWrapper

from .utils import (
    MistralChunkHandler,
    MistralMetadata,
    default_mistral_cleanup,
    get_mistral_llm_request_attributes,
)

P = ParamSpec("P")


def mistral_complete_patch(
    tracer: Tracer,
) -> Callable[[Callable[P, Any], Any, tuple[Any, ...], dict[str, Any]], Any]:
    def traced_method(
        wrapped: Callable[P, Any],
        instance: Any,
        args: tuple[Any, ...],
        kwargs: dict[str, Any],
    ) -> Any:
        span_attributes = get_mistral_llm_request_attributes(kwargs)
        span_name = f"chat {span_attributes.get('gen_ai.request.model', 'unknown')}"
        with tracer.start_as_current_span(span_name, end_on_exit=False) as span:
            try:
                result = wrapped(*args, **kwargs)
                default_mistral_cleanup(span, MistralMetadata(), [])
                span.end()
                return result
            except Exception as err:
                span.set_status(Status(StatusCode.ERROR, str(err)))
                if span.is_recording():
                    span.set_attribute(
                        error_attributes.ERROR_TYPE, type(err).__qualname__
                    )
                span.end()
                raise

    return traced_method


def mistral_complete_async_patch(
    tracer: Tracer,
) -> Callable[[Callable[P, Any], Any, tuple[Any, ...], dict[str, Any]], Awaitable[Any]]:
    async def traced_method(
        wrapped: Callable[P, Any],
        instance: Any,
        args: tuple[Any, ...],
        kwargs: dict[str, Any],
    ) -> Any:
        span_attributes = get_mistral_llm_request_attributes(kwargs)
        span_name = f"chat {span_attributes.get('gen_ai.request.model', 'unknown')}"
        with tracer.start_as_current_span(span_name, end_on_exit=False) as span:
            try:
                result = await wrapped(*args, **kwargs)
                # Non-stream async returns ChatCompletionResponse
                default_mistral_cleanup(span, MistralMetadata(), [])
                span.end()
                return result
            except Exception as err:
                span.set_status(Status(StatusCode.ERROR, str(err)))
                if span.is_recording():
                    span.set_attribute(
                        error_attributes.ERROR_TYPE, type(err).__qualname__
                    )
                span.end()
                raise

    return traced_method


def mistral_stream_patch(
    tracer: Tracer,
) -> Callable[[Callable[P, Any], Any, tuple[Any, ...], dict[str, Any]], Any]:
    def traced_method(
        wrapped: Callable[P, Any],
        instance: Any,
        args: tuple[Any, ...],
        kwargs: dict[str, Any],
    ) -> Any:
        span_attributes = get_mistral_llm_request_attributes(kwargs)
        span_name = (
            f"chat_stream {span_attributes.get('gen_ai.request.model', 'unknown')}"
        )
        with tracer.start_as_current_span(
            name=span_name,
            kind=SpanKind.CLIENT,
            attributes=span_attributes,
            end_on_exit=False,
        ) as span:
            metadata = MistralMetadata()
            chunk_handler = MistralChunkHandler()
            try:
                original_stream = wrapped(*args, **kwargs)
                return StreamWrapper(
                    span=span,
                    stream=original_stream,
                    metadata=metadata,
                    chunk_handler=chunk_handler,  # pyright: ignore [reportArgumentType]
                    cleanup_handler=default_mistral_cleanup,
                )
            except Exception as err:
                span.set_status(Status(StatusCode.ERROR, str(err)))
                if span.is_recording():
                    span.set_attribute(
                        error_attributes.ERROR_TYPE, type(err).__qualname__
                    )
                span.end()
                raise

    return traced_method


def mistral_stream_async_patch(
    tracer: Tracer,
) -> Callable[[Callable[P, Any], Any, tuple[Any, ...], dict[str, Any]], Awaitable[Any]]:
    async def traced_method(
        wrapped: Callable[P, Any],
        instance: Any,
        args: tuple[Any, ...],
        kwargs: dict[str, Any],
    ) -> Any:
        span_attributes = get_mistral_llm_request_attributes(kwargs)
        span_name = (
            f"chat_stream {span_attributes.get('gen_ai.request.model', 'unknown')}"
        )
        with tracer.start_as_current_span(
            name=span_name,
            kind=SpanKind.CLIENT,
            attributes=span_attributes,
            end_on_exit=False,
        ) as span:
            metadata = MistralMetadata()
            chunk_handler = MistralChunkHandler()
            try:
                original_stream = await wrapped(*args, **kwargs)
                return AsyncStreamWrapper(
                    span=span,
                    stream=original_stream,  # pyright: ignore [reportArgumentType]
                    metadata=metadata,
                    chunk_handler=chunk_handler,  # pyright: ignore [reportArgumentType]
                    cleanup_handler=default_mistral_cleanup,
                )
            except Exception as err:
                span.set_status(Status(StatusCode.ERROR, str(err)))
                if span.is_recording():
                    span.set_attribute(
                        error_attributes.ERROR_TYPE, type(err).__qualname__
                    )
                span.end()
                raise

    return traced_method
