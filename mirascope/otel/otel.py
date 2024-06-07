"""Integration with OpenTelemetry"""
import inspect
import json
from contextlib import (
    AbstractAsyncContextManager,
    AbstractContextManager,
    contextmanager,
)
from typing import Any, Callable, Optional, Sequence, Union, overload

from opentelemetry.sdk.trace import SpanProcessor, TracerProvider
from opentelemetry.sdk.trace.export import (
    ConsoleSpanExporter,
    SimpleSpanProcessor,
)
from opentelemetry.trace import (
    SpanKind,
    Tracer,
    get_tracer,
    get_tracer_provider,
    set_tracer_provider,
)
from opentelemetry.trace.span import Span
from opentelemetry.util.types import Attributes, AttributeValue
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


def mirascope_otel(cls) -> Callable:
    tracer = get_tracer("otel")

    def _set_response_attributes(
        span: Span, response: BaseCallResponse, messages: list[dict[str, Any]]
    ) -> None:
        """Sets the response attributes"""
        response_attributes: dict[str, AttributeValue] = {}
        if model := response.model:
            response_attributes["gen_ai.response.model"] = model
        if id := response.id:
            response_attributes["gen_ai.response.id"] = id
        if finish_reasons := response.finish_reasons:
            response_attributes["gen_ai.response.finish_reasons"] = finish_reasons
        if output_tokens := response.output_tokens:
            response_attributes["gen_ai.usage.completion_tokens"] = output_tokens
        if input_tokens := response.input_tokens:
            response_attributes["gen_ai.usage.prompt_tokens"] = input_tokens
        span.set_attributes(response_attributes)
        event_attributes: Attributes = {"gen_ai.completion": json.dumps(messages)}
        span.add_event(
            "gen_ai.content.completion",
            attributes=event_attributes,
        )

    def _set_span_data(
        span: Span,
        suffix: str,
        is_async: bool,
        model_name: Optional[str],
        args: tuple[Any],
    ) -> None:
        prompt = args[0] if len(args) > 0 else None
        if prompt and suffix == "gemini":
            prompt = {
                "messages": [
                    {"role": message["role"], "content": message["parts"][0]}
                    for message in prompt
                ]
            }

        max_tokens = None
        temperature = None
        top_p = None
        if hasattr(cls, "call_params"):
            call_params = cls.call_params
            max_tokens = getattr(call_params, "max_tokens", None)
            temperature = getattr(call_params, "temperature", None)
            top_p = getattr(call_params, "top_p", None)
        attributes: dict[str, AttributeValue] = {
            "async": is_async,
            "gen_ai.system": suffix,
        }
        if model_name:
            attributes["gen_ai.request.model"] = model_name
        if max_tokens:
            attributes["gen_ai.request.max_tokens"] = max_tokens
        if temperature:
            attributes["gen_ai.request.temperature"] = temperature
        if top_p:
            attributes["gen_ai.request.top_p"] = top_p

        events: Attributes = {
            "gen_ai.prompt": json.dumps(prompt),
        }
        span.set_attributes(attributes)
        span.add_event("gen_ai.content.prompt", attributes=events)

    @contextmanager
    def _mirascope_llm_span(
        fn: Callable,
        suffix: str,
        is_async: bool,
        model_name: Optional[str],
        args: tuple[Any],
        kwargs: dict[str, Any],
    ):
        """Wraps a pydantic class method with a OTel span."""
        tracer = get_tracer("otel")
        model = kwargs.get("model", "") or model_name
        with tracer.start_as_current_span(
            f"{suffix}.{fn.__name__} with {model}", kind=SpanKind.CLIENT
        ) as span:
            _set_span_data(span, suffix, is_async, model, args)
            yield span

    @contextmanager
    def record_streaming(
        span: Span,
        content_from_stream: Callable[
            [ChunkT, type[BaseCallResponseChunk]], BaseCallResponseChunk
        ],
    ):
        """OTel record_streaming with Mirascope providers"""
        content: list[str] = []
        response_attributes: dict[str, AttributeValue] = {}

        def record_chunk(
            raw_chunk: ChunkT, response_chunk_type: type[BaseCallResponseChunk]
        ) -> Any:
            """Handles all provider chunk_types instead of only OpenAI"""
            chunk: BaseCallResponseChunk = content_from_stream(
                raw_chunk, response_chunk_type
            )
            if model := chunk.model:
                response_attributes["gen_ai.response.model"] = model
            if id := chunk.id:
                response_attributes["gen_ai.response.id"] = id
            if finish_reasons := chunk.finish_reasons:
                response_attributes["gen_ai.response.finish_reasons"] = finish_reasons
            if output_tokens := chunk.output_tokens:
                response_attributes["gen_ai.usage.completion_tokens"] = output_tokens
            if input_tokens := chunk.input_tokens:
                response_attributes["gen_ai.usage.prompt_tokens"] = input_tokens
            chunk_content = chunk.content
            if chunk_content is not None:
                content.append(chunk_content)

        try:
            yield record_chunk
        finally:
            span.set_attributes(response_attributes)
            event_attributes: Attributes = {
                "gen_ai.completion": json.dumps(
                    {"role": "assistant", "content": "".join(content)}
                )
            }
            span.add_event(
                "gen_ai.content.completion",
                attributes=event_attributes,
            )

    def _extract_chunk(
        chunk: ChunkT, response_chunk_type: type[BaseCallResponseChunk]
    ) -> BaseCallResponseChunk:
        """Extracts the content from a chunk."""
        return response_chunk_type(chunk=chunk)

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
                    _set_response_attributes(span, response, [message])
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
                    _set_response_attributes(span, response, [message])
                return result

        def wrapper_generator(*args, **kwargs):
            model = kwargs.get("model", "") or model_name
            with tracer.start_as_current_span(
                f"{suffix}.{fn.__name__} with {model}"
            ) as span:
                _set_span_data(span, suffix, is_async, model, args)
                with record_streaming(span, _extract_chunk) as record_chunk:
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
            model = kwargs.get("model", "") or model_name
            with tracer.start_as_current_span(
                f"{suffix}.{fn.__name__} with {model}"
            ) as span:
                _set_span_data(span, suffix, is_async, model, args)
                with record_streaming(span, _extract_chunk) as record_chunk:
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


def custom_encoder(obj) -> str:
    """Custom encoder for the OpenTelemetry span"""
    return obj.__name__


@contextmanager
def handle_before_call(self: BaseModel, fn: Callable, **kwargs):
    """Handles before call"""

    class_vars = get_class_vars(self)
    inputs = self.model_dump()
    tracer = get_tracer("otel")
    attributes: dict[str, AttributeValue] = {**kwargs, **class_vars, **inputs}
    if hasattr(self, "call_params"):
        attributes["call_params"] = json.dumps(
            self.call_params.model_dump(), default=custom_encoder
        )
    if hasattr(self, "configuration"):
        configuration = self.configuration.model_dump()
        attributes["configuration"] = json.dumps(configuration, default=custom_encoder)

    if hasattr(self, "base_url"):
        attributes["base_url"] = self.base_url if self.base_url else ""

    if hasattr(self, "extract_schema"):
        attributes["extract_schema"] = self.extract_schema.__name__
    with tracer.start_as_current_span(
        f"{self.__class__.__name__}.{fn.__name__}"
    ) as span:
        span.set_attributes(attributes)
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
    """Wraps a pydantic class with a OTel span."""

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
            update={"llm_ops": [*cls.configuration.llm_ops, mirascope_otel(cls)]}
        )
    return cls
