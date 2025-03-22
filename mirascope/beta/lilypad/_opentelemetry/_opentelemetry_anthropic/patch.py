from collections.abc import Awaitable, Callable
from typing import Any, ParamSpec

from opentelemetry.semconv._incubating.attributes import gen_ai_attributes
from opentelemetry.semconv.attributes import error_attributes
from opentelemetry.trace import SpanKind, Status, StatusCode, Tracer

from lilypad._opentelemetry._opentelemetry_anthropic.utils import (
    AnthropicChunkHandler,
    AnthropicMetadata,
    default_anthropic_cleanup,
    get_llm_request_attributes,
    set_message_event,
    set_response_attributes,
)
from lilypad._opentelemetry._utils import (
    AsyncStreamWrapper,
    StreamWrapper,
)

P = ParamSpec("P")


def chat_completions_create(
    tracer: Tracer,
) -> Callable[[Callable[P, Any], Any, tuple[Any, ...], dict[str, Any]], Any]:
    def traced_method(
        wrapped: Callable[P, Any],
        instance: Any,
        args: tuple[Any, ...],
        kwargs: dict[str, Any],
    ) -> Any:
        span_attributes = {**get_llm_request_attributes(kwargs, instance)}

        span_name = f"{span_attributes[gen_ai_attributes.GEN_AI_OPERATION_NAME]} {span_attributes[gen_ai_attributes.GEN_AI_REQUEST_MODEL]}"
        with tracer.start_as_current_span(
            name=span_name,
            kind=SpanKind.CLIENT,
            attributes=span_attributes,
            end_on_exit=False,
        ) as span:
            if span.is_recording():
                for message in kwargs.get("messages", []):
                    set_message_event(span, message)
            try:
                result = wrapped(*args, **kwargs)
                if kwargs.get("stream", False):
                    return StreamWrapper(
                        span=span,
                        stream=result,
                        metadata=AnthropicMetadata(),
                        chunk_handler=AnthropicChunkHandler(),
                        cleanup_handler=default_anthropic_cleanup,
                    )

                if span.is_recording():
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


def chat_completions_create_async(
    tracer: Tracer,
) -> Callable[[Callable[P, Any], Any, tuple[Any, ...], dict[str, Any]], Awaitable[Any]]:
    async def traced_method(
        wrapped: Callable[P, Any],
        instance: Any,
        args: tuple[Any, ...],
        kwargs: dict[str, Any],
    ) -> Any:
        span_attributes = {**get_llm_request_attributes(kwargs, instance)}

        span_name = f"{span_attributes[gen_ai_attributes.GEN_AI_OPERATION_NAME]} {span_attributes[gen_ai_attributes.GEN_AI_REQUEST_MODEL]}"
        with tracer.start_as_current_span(
            name=span_name,
            kind=SpanKind.CLIENT,
            attributes=span_attributes,
            end_on_exit=False,
        ) as span:
            if span.is_recording():
                for message in kwargs.get("messages", []):
                    set_message_event(span, message)
            try:
                result = await wrapped(*args, **kwargs)
                if kwargs.get("stream", False):
                    return AsyncStreamWrapper(
                        span=span,
                        stream=result,
                        metadata=AnthropicMetadata(),
                        chunk_handler=AnthropicChunkHandler(),
                        cleanup_handler=default_anthropic_cleanup,
                    )

                if span.is_recording():
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
