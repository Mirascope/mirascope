# Copyright The OpenTelemetry Authors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# Modifications copyright (C) 2024 Mirascope
from collections.abc import Awaitable, Callable
from typing import Any, ParamSpec

from opentelemetry.semconv._incubating.attributes import (
    gen_ai_attributes,
    server_attributes,
)
from opentelemetry.semconv.attributes import error_attributes
from opentelemetry.trace import SpanKind, Status, StatusCode, Tracer
from opentelemetry.util.types import AttributeValue

from lilypad._opentelemetry._opentelemetry_openai.utils import (
    OpenAIChunkHandler,
    OpenAIMetadata,
    default_openai_cleanup,
    set_message_event,
    set_response_attributes,
)
from lilypad._opentelemetry._utils import (
    AsyncStreamWrapper,
    StreamWrapper,
    set_server_address_and_port,
)

P = ParamSpec("P")


def get_llm_request_attributes(
    kwargs: dict[str, Any],
    client_instance: Any,
    operation_name: str = gen_ai_attributes.GenAiOperationNameValues.CHAT.value,
) -> dict[str, AttributeValue]:
    response_format = kwargs.get("response_format", {})
    if isinstance(response_format, dict):
        response_format = response_format.get("type")
    else:
        response_format = response_format.__name__
    attributes = {
        gen_ai_attributes.GEN_AI_OPERATION_NAME: operation_name,
        gen_ai_attributes.GEN_AI_REQUEST_MODEL: kwargs.get("model"),
        gen_ai_attributes.GEN_AI_REQUEST_TEMPERATURE: kwargs.get("temperature"),
        gen_ai_attributes.GEN_AI_REQUEST_TOP_P: kwargs.get("p") or kwargs.get("top_p"),
        gen_ai_attributes.GEN_AI_REQUEST_MAX_TOKENS: kwargs.get("max_tokens"),
        gen_ai_attributes.GEN_AI_REQUEST_PRESENCE_PENALTY: kwargs.get(
            "presence_penalty"
        ),
        gen_ai_attributes.GEN_AI_REQUEST_FREQUENCY_PENALTY: kwargs.get(
            "frequency_penalty"
        ),
        gen_ai_attributes.GEN_AI_OPENAI_REQUEST_RESPONSE_FORMAT: response_format,
        gen_ai_attributes.GEN_AI_OPENAI_REQUEST_SEED: kwargs.get("seed"),
    }
    set_server_address_and_port(client_instance, attributes)
    system = gen_ai_attributes.GenAiSystemValues.OPENAI.value
    if "openrouter" in attributes.get(server_attributes.SERVER_ADDRESS, ""):
        system = "openrouter"
    attributes[gen_ai_attributes.GEN_AI_SYSTEM] = system

    service_tier = kwargs.get("service_tier")
    attributes[gen_ai_attributes.GEN_AI_OPENAI_RESPONSE_SERVICE_TIER] = (
        service_tier if service_tier != "auto" else None
    )

    # filter out None values
    return {k: v for k, v in attributes.items() if v is not None}


def _sync_wrapper(
    tracer: Tracer, handle_stream: bool
) -> Callable[[Callable[P, Any], Any, tuple[Any, ...], dict[str, Any]], Any]:
    """Internal sync wrapper for OpenAI API calls."""

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
                if handle_stream and kwargs.get("stream", False):
                    return StreamWrapper(
                        span=span,
                        stream=result,
                        metadata=OpenAIMetadata(),
                        chunk_handler=OpenAIChunkHandler(),
                        cleanup_handler=default_openai_cleanup,
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


def _async_wrapper(
    tracer: Tracer, handle_stream: bool
) -> Callable[[Callable[P, Any], Any, tuple[Any, ...], dict[str, Any]], Awaitable[Any]]:
    """Internal async wrapper for OpenAI API calls."""

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
                if handle_stream and kwargs.get("stream", False):
                    return AsyncStreamWrapper(
                        span=span,
                        stream=result,
                        metadata=OpenAIMetadata(),
                        chunk_handler=OpenAIChunkHandler(),
                        cleanup_handler=default_openai_cleanup,
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


def chat_completions_create(
    tracer: Tracer,
) -> Callable[[Callable[P, Any], Any, tuple[Any, ...], dict[str, Any]], Any]:
    """Wrapper for sync chat completions create method."""
    return _sync_wrapper(tracer, handle_stream=True)


def chat_completions_create_async(
    tracer: Tracer,
) -> Callable[[Callable[P, Any], Any, tuple[Any, ...], dict[str, Any]], Awaitable[Any]]:
    """Wrapper for async chat completions create method."""
    return _async_wrapper(tracer, handle_stream=True)


def chat_completions_parse(
    tracer: Tracer,
) -> Callable[[Callable[P, Any], Any, tuple[Any, ...], dict[str, Any]], Any]:
    """Wrapper for sync chat completions parse method."""
    # Stream is not handled in .parse method
    # https://platform.openai.com/docs/guides/structured-outputs/structured-outputs#streaming
    return _sync_wrapper(tracer, handle_stream=False)


def chat_completions_parse_async(
    tracer: Tracer,
) -> Callable[[Callable[P, Any], Any, tuple[Any, ...], dict[str, Any]], Awaitable[Any]]:
    """Wrapper for async chat completions parse method."""
    return _async_wrapper(tracer, handle_stream=False)
