"""Integration with OpenTelemetry"""
import inspect
import json
from contextlib import (
    AbstractAsyncContextManager,
    AbstractContextManager,
    contextmanager,
)
from typing import Any, Callable, Optional, Sequence, Union, overload

from opentelemetry.sdk.trace import Span, SpanProcessor, TracerProvider
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
from pydantic import BaseModel
from typing_extensions import LiteralString

from mirascope.base.ops_utils import get_class_vars, wrap_mirascope_class_functions
from mirascope.base.types import (
    BaseCallResponse,
    BaseCallResponseChunk,
    BaseTool,
    ChunkT,
)

from ..types import (
    BaseCallT,
    BaseChunkerT,
    BaseEmbedderT,
    BaseExtractorT,
    BaseVectorStoreT,
)

ONE_SECOND_IN_NANOSECONDS = 1_000_000_000
STEAMING_MSG_TEMPLATE: LiteralString = (
    "streaming response from {request_data[model]!r} took {duration:.2f}s"
)


def mirascope_otel() -> Callable:
    tracer = get_tracer("otel")

    def mirascope_otel_decorator(
        fn: Callable,
        suffix: str,
        *,
        is_async: bool = False,
        response_type: Optional[type[BaseCallResponse]] = None,
        response_chunk_type: Optional[type[BaseCallResponseChunk]] = None,
        tool_types: Optional[list[type[BaseTool]]] = None,
        model_name: Optional[str] = None,
    ) -> Callable:
        """Wraps a LLM call with OTEL"""

        def wrapper(*args, **kwargs):
            with _mirascope_llm_span(
                fn, suffix, is_async, model_name, args, kwargs
            ) as span:
                result = fn(*args, **kwargs)
                if response_type is not None:
                    response = response_type(
                        response=result, start_time=0, end_time=0, tool_types=tool_types
                    )
                    message = {"role": "assistant", "content": response.content}
                    if tools := response.tools:
                        tool_calls = [
                            {
                                "function": {
                                    "arguments": tool.model_dump_json(
                                        exclude={"tool_call"}
                                    ),
                                    "name": tool.__class__.__name__,
                                }
                            }
                            for tool in tools
                        ]
                        message["tool_calls"] = tool_calls
                        message.pop("content")
                    span.set_attribute(
                        "response_data", json.dumps({"message": message})
                    )
                return result

        async def wrapper_async(*args, **kwargs):
            with _mirascope_llm_span(
                fn, suffix, is_async, model_name, args, kwargs
            ) as span:
                result = await fn(*args, **kwargs)
                if response_type is not None:
                    response = response_type(
                        response=result, start_time=0, end_time=0, tool_types=tool_types
                    )
                    message = {"role": "assistant", "content": response.content}
                    if tools := response.tools:
                        tool_calls = [
                            {
                                "function": {
                                    "arguments": tool.model_dump_json(
                                        exclude={"tool_call"}
                                    ),
                                    "name": tool.__class__.__name__,
                                }
                            }
                            for tool in tools
                        ]
                        message["tool_calls"] = tool_calls
                        message.pop("content")
                    span.set_attribute(
                        "response_data", json.dumps({"message": message})
                    )
                return result

        def wrapper_generator(*args, **kwargs):
            span_data = _get_span_data(suffix, is_async, model_name, args, kwargs)
            model = kwargs.get("model", "") or model_name
            with tracer.start_as_current_span(
                f"{suffix}.{fn.__name__} with {model}"
            ) as span:
                with record_streaming(
                    span, span_data, _extract_chunk_content
                ) as record_chunk:
                    stream = fn(*args, **kwargs)
                    if isinstance(stream, AbstractContextManager):
                        with stream as s:
                            for chunk in s:
                                record_chunk(chunk, response_chunk_type)
                                yield chunk
                    else:
                        for chunk in stream:
                            record_chunk(chunk, response_chunk_type)
                            yield chunk

        async def wrapper_generator_async(*args, **kwargs):
            span_data = _get_span_data(suffix, is_async, model_name, args, kwargs)
            model = kwargs.get("model", "") or model_name
            with tracer.start_as_current_span(
                f"{suffix}.{fn.__name__} with {model}"
            ) as span:
                with record_streaming(
                    span, span_data, _extract_chunk_content
                ) as record_chunk:
                    stream = fn(*args, **kwargs)
                    if inspect.iscoroutine(stream):
                        stream = await stream
                    if isinstance(stream, AbstractAsyncContextManager):
                        async with stream as s:
                            async for chunk in s:
                                record_chunk(chunk, response_chunk_type)
                                yield chunk
                    else:
                        async for chunk in stream:
                            record_chunk(chunk, response_chunk_type)
                            yield chunk

        if response_chunk_type and is_async:
            return wrapper_generator_async
        elif response_type and is_async:
            return wrapper_async
        elif response_chunk_type:
            return wrapper_generator
        elif response_type:
            return wrapper
        raise ValueError("No response type or chunk type provided")

    return mirascope_otel_decorator


def _extract_chunk_content(
    chunk: ChunkT, response_chunk_type: type[BaseCallResponseChunk]
) -> str:
    """Extracts the content from a chunk."""
    return response_chunk_type(chunk=chunk).content


def _get_span_data(
    suffix: str,
    is_async: bool,
    model_name: Optional[str],
    args: tuple[Any],
    kwargs: dict[str, Any],
) -> dict[str, Any]:
    additional_request_data = {}
    if suffix == "gemini":
        gemini_messages = args[0]
        additional_request_data = {
            "messages": [
                {"role": message["role"], "content": message["parts"][0]}
                for message in gemini_messages
            ],
            "model": model_name,
        }
    return {
        "async": is_async,
        "request_data": json.dumps(kwargs | additional_request_data),
    }


@contextmanager
def _mirascope_llm_span(
    fn: Callable,
    suffix: str,
    is_async: bool,
    model_name: Optional[str],
    args: tuple[Any],
    kwargs: dict[str, Any],
):
    """Wraps a pydantic class method with a Logfire span."""
    tracer = get_tracer("otel")
    model = kwargs.get("model", "") or model_name
    span_data = _get_span_data(suffix, is_async, model, args, kwargs)
    with tracer.start_as_current_span(f"{suffix}.{fn.__name__} with {model}") as span:
        span.set_attributes(span_data)
        yield span


@contextmanager
def record_streaming(
    span: Span,
    span_data: dict[str, Any],
    content_from_stream: Callable[
        [ChunkT, type[BaseCallResponseChunk]], Union[str, None]
    ],
):
    """Logfire record_streaming with Mirascope providers"""
    content: list[str] = []

    def record_chunk(
        chunk: ChunkT, response_chunk_type: type[BaseCallResponseChunk]
    ) -> Any:
        """Handles all provider chunk_types instead of only OpenAI"""
        chunk_content = content_from_stream(chunk, response_chunk_type)
        if chunk_content is not None:
            content.append(chunk_content)

    try:
        yield record_chunk
    finally:
        attributes = {
            **span_data,
            "response_data": {
                "combined_chunk_content": "".join(content),
                "chunk_count": len(content),
            },
        }
        span.set_attributes(attributes)


@contextmanager
def handle_before_call(self: BaseModel, fn: Callable, **kwargs):
    """Handles before call"""

    class_vars = get_class_vars(self)
    inputs = self.model_dump()
    tracer = get_tracer("otel")
    with tracer.start_as_current_span(
        f"{self.__class__.__name__}.{fn.__name__}"
    ) as span:
        span.set_attributes({**kwargs, **class_vars, **inputs})
        yield span


def handle_after_call(
    self: BaseModel,
    fn,
    result: Union[BaseCallResponse, list[BaseCallResponseChunk]],
    span: Span,
    **kwargs,
) -> None:
    """Handles after call"""
    if isinstance(result, list):
        response = [chunk.model_dump() for chunk in result]
        span.set_attribute("response", str(response))
    else:
        span.set_attribute("response", str(result.model_dump()))


def configure(
    processors: Optional[Sequence[SpanProcessor]] = None,
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
def with_otel(cls: type[BaseCallT]) -> type[BaseCallT]:
    ...  # pragma: no cover


@overload
def with_otel(cls: type[BaseExtractorT]) -> type[BaseExtractorT]:
    ...  # pragma: no cover


@overload
def with_otel(cls: type[BaseVectorStoreT]) -> type[BaseVectorStoreT]:
    ...  # pragma: no cover


@overload
def with_otel(cls: type[BaseChunkerT]) -> type[BaseChunkerT]:
    ...  # pragma: no cover


@overload
def with_otel(cls: type[BaseEmbedderT]) -> type[BaseEmbedderT]:
    ...  # pragma: no cover


def with_otel(cls):
    """Wraps a pydantic class with a Logfire span."""

    provider = get_tracer_provider()
    if not isinstance(provider, TracerProvider):
        configure()
    wrap_mirascope_class_functions(
        cls,
        handle_before_call=handle_before_call,
        handle_after_call=handle_after_call,
    )
    if hasattr(cls, "configuration"):
        cls.configuration = cls.configuration.model_copy(
            update={"llm_ops": [*cls.configuration.llm_ops, mirascope_otel()]}
        )
    return cls
