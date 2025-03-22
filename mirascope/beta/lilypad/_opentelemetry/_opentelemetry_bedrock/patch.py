"""Bedrock OpenTelemetry patching."""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from typing import Any

from botocore.eventstream import EventStream
from opentelemetry.semconv.attributes import error_attributes
from opentelemetry.trace import SpanKind, Status, StatusCode, Tracer
from typing_extensions import ParamSpec

from lilypad._opentelemetry._utils import AsyncStreamWrapper, StreamWrapper

from .utils import (
    BedrockChunkHandler,
    BedrockMetadata,
    default_bedrock_cleanup,
    get_bedrock_llm_request_attributes,
    set_bedrock_message_event,
)

P = ParamSpec("P")


class SyncEventStreamAdapter:
    """Sync EventStream adapter."""

    def __init__(self, event_stream: EventStream) -> None:
        self._iter = iter(event_stream)

    def __iter__(self) -> SyncEventStreamAdapter:
        return self

    def __next__(self) -> Any:
        return next(self._iter)


class AsyncEventStreamAdapter:
    """Async EventStream adapter."""

    def __init__(self, event_stream: EventStream) -> None:
        self._stream = event_stream

    def __aiter__(self) -> AsyncEventStreamAdapter:
        return self

    async def __anext__(self) -> Any:
        try:
            return await self._stream.__anext__()  # pyright: ignore [reportAttributeAccessIssue]
        except StopAsyncIteration:
            raise
        except Exception as ex:
            raise ex


def make_api_call_patch(
    tracer: Tracer,
) -> Callable[[Callable[P, Any], Any, tuple[Any, ...], dict[str, Any]], Any]:
    """Patch for bedrock-runtime synchronous _make_api_call."""

    def wrapper(
        wrapped: Callable[P, Any],
        instance: Any,
        args: tuple[Any, ...],
        kwargs: dict[str, Any],
    ) -> Any:
        operation_name, params = args
        service_name = instance.meta.service_model.service_name
        if service_name != "bedrock-runtime":
            return wrapped(*args, **kwargs)
        span_attrs = get_bedrock_llm_request_attributes(params, instance)
        if operation_name == "Converse":
            span_name = f"chat {span_attrs.get('gen_ai.request.model', 'unknown')}"
            with tracer.start_as_current_span(
                name=span_name,
                kind=SpanKind.CLIENT,
                attributes=span_attrs,
                end_on_exit=False,
            ) as span:
                try:
                    if span.is_recording():
                        msgs = params.get("messages", [])
                        for m in msgs:
                            set_bedrock_message_event(span, m)
                    result = wrapped(*args, **kwargs)
                    default_bedrock_cleanup(span, BedrockMetadata(), [])
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
        elif operation_name == "ConverseStream":
            span_name = (
                f"chat_stream {span_attrs.get('gen_ai.request.model', 'unknown')}"
            )
            with tracer.start_as_current_span(
                name=span_name,
                kind=SpanKind.CLIENT,
                attributes=span_attrs,
                end_on_exit=False,
            ) as span:
                try:
                    if span.is_recording():
                        msgs = params.get("messages", [])
                        for m in msgs:
                            set_bedrock_message_event(span, m)
                    response = wrapped(*args, **kwargs)
                    if "stream" in response:
                        raw_stream = response["stream"]
                        adapt = SyncEventStreamAdapter(raw_stream)
                        metadata = BedrockMetadata()
                        chunk_handler = BedrockChunkHandler()
                        wrapped_stream = StreamWrapper(
                            span=span,
                            stream=adapt,  # pyright: ignore [reportArgumentType]
                            metadata=metadata,
                            chunk_handler=chunk_handler,
                            cleanup_handler=default_bedrock_cleanup,
                        )
                        response["stream"] = wrapped_stream
                    else:
                        default_bedrock_cleanup(span, BedrockMetadata(), [])
                        span.end()
                    return response
                except Exception as err:
                    span.set_status(Status(StatusCode.ERROR, str(err)))
                    if span.is_recording():
                        span.set_attribute(
                            error_attributes.ERROR_TYPE, type(err).__qualname__
                        )
                    span.end()
                    raise
        return wrapped(*args, **kwargs)

    return wrapper


def make_api_call_async_patch(
    tracer: Tracer,
) -> Callable[[Callable[P, Any], Any, tuple[Any, ...], dict[str, Any]], Awaitable[Any]]:
    """Patch for bedrock-runtime asynchronous _make_api_call."""

    async def wrapper(
        wrapped: Callable[P, Any],
        instance: Any,
        args: tuple[Any, ...],
        kwargs: dict[str, Any],
    ) -> Any:
        operation_name, params = args
        service_name = instance.meta.service_model.service_name
        if service_name != "bedrock-runtime":
            return await wrapped(*args, **kwargs)
        span_attrs = get_bedrock_llm_request_attributes(params, instance)
        if operation_name == "Converse":
            span_name = f"chat {span_attrs.get('gen_ai.request.model', 'unknown')}"
            with tracer.start_as_current_span(
                name=span_name,
                kind=SpanKind.CLIENT,
                attributes=span_attrs,
                end_on_exit=False,
            ) as span:
                try:
                    if span.is_recording():
                        msgs = params.get("messages", [])
                        for m in msgs:
                            set_bedrock_message_event(span, m)
                    resp = await wrapped(*args, **kwargs)
                    default_bedrock_cleanup(span, BedrockMetadata(), [])
                    span.end()
                    return resp
                except Exception as err:
                    span.set_status(Status(StatusCode.ERROR, str(err)))
                    if span.is_recording():
                        span.set_attribute(
                            error_attributes.ERROR_TYPE, type(err).__qualname__
                        )
                    span.end()
                    raise
        elif operation_name == "ConverseStream":
            span_name = (
                f"chat_stream {span_attrs.get('gen_ai.request.model', 'unknown')}"
            )
            with tracer.start_as_current_span(
                name=span_name,
                kind=SpanKind.CLIENT,
                attributes=span_attrs,
                end_on_exit=False,
            ) as span:
                try:
                    if span.is_recording():
                        msgs = params.get("messages", [])
                        for m in msgs:
                            set_bedrock_message_event(span, m)
                    resp = await wrapped(*args, **kwargs)
                    if "stream" in resp:
                        raw_stream = resp["stream"]
                        adapt = AsyncEventStreamAdapter(raw_stream)
                        metadata = BedrockMetadata()
                        chunk_handler = BedrockChunkHandler()
                        wrapped_stream = AsyncStreamWrapper(
                            span=span,
                            stream=adapt,  # pyright: ignore [reportArgumentType]
                            metadata=metadata,
                            chunk_handler=chunk_handler,
                            cleanup_handler=default_bedrock_cleanup,
                        )
                        resp["stream"] = wrapped_stream
                    else:
                        default_bedrock_cleanup(span, BedrockMetadata(), [])
                        span.end()
                    return resp
                except Exception as err:
                    span.set_status(Status(StatusCode.ERROR, str(err)))
                    if span.is_recording():
                        span.set_attribute(
                            error_attributes.ERROR_TYPE, type(err).__qualname__
                        )
                    span.end()
                    raise
        return await wrapped(*args, **kwargs)

    return wrapper
