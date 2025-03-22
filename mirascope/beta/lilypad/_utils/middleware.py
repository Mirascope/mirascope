"""Utilities for middleware for Lilypad prompts and Mirascope calls."""

import base64
import json
from collections.abc import Callable, Generator
from contextlib import _GeneratorContextManager, contextmanager
from io import BytesIO
from typing import Any, ParamSpec, TypeVar, cast
from uuid import UUID

import PIL
import PIL.WebPImagePlugin
from opentelemetry.trace import get_tracer
from opentelemetry.trace.span import Span, SpanContext
from opentelemetry.util.types import AttributeValue
from pydantic import BaseModel

from mirascope.core import base as mb
from mirascope.integrations import middleware_factory

from ..server.client import GenerationPublic, LilypadClient
from .functions import ArgValues, jsonable_encoder

_P = ParamSpec("_P")
_R = TypeVar("_R")


class SpanContextHolder:
    def __init__(self) -> None:
        self._span_context: SpanContext | None = None

    def set_span_context(self, span: Span) -> None:
        self._span_context = span.get_span_context()

    @property
    def span_context(self) -> SpanContext | None:
        return self._span_context


def _get_custom_context_manager(
    generation: GenerationPublic,
    arg_values: ArgValues,
    is_async: bool,
    prompt_template: str | None = None,
    project_uuid: UUID | None = None,
    span_context_holder: SpanContextHolder | None = None,
) -> Callable[..., _GeneratorContextManager[Span]]:
    @contextmanager
    def custom_context_manager(
        fn: Callable,
    ) -> Generator[Span, Any, None]:
        tracer = get_tracer("lilypad")
        lilypad_client = LilypadClient()
        new_project_uuid = project_uuid or lilypad_client.project_uuid
        jsonable_arg_values = {}
        for arg_name, arg_value in arg_values.items():
            try:
                serialized_arg_value = jsonable_encoder(arg_value)
            except ValueError:
                serialized_arg_value = "could not serialize"
            jsonable_arg_values[arg_name] = serialized_arg_value
        with tracer.start_as_current_span(f"{fn.__name__}") as span:
            attributes: dict[str, AttributeValue] = {
                "lilypad.project_uuid": str(new_project_uuid)
                if new_project_uuid
                else "",
                "lilypad.type": "generation",
                "lilypad.generation.uuid": str(generation.uuid),
                "lilypad.generation.name": fn.__name__,
                "lilypad.generation.signature": generation.signature,
                "lilypad.generation.code": generation.code,
                "lilypad.generation.arg_types": json.dumps(generation.arg_types),
                "lilypad.generation.arg_values": json.dumps(jsonable_arg_values),
                "lilypad.generation.prompt_template": prompt_template or "",
                "lilypad.generation.version": generation.version_num
                if generation.version_num
                else -1,
                "lilypad.is_async": is_async,
            }
            span.set_attributes(attributes)
            if span_context_holder:
                span_context_holder.set_span_context(span)
            yield span

    return custom_context_manager


def encode_gemini_part(
    part: str | dict | PIL.WebPImagePlugin.WebPImageFile,
) -> str | dict:
    if isinstance(part, dict):
        if "mime_type" in part and "data" in part:
            # Handle binary data by base64 encoding it
            return {
                "mime_type": part["mime_type"],
                "data": base64.b64encode(part["data"]).decode("utf-8"),
            }
        return part
    elif isinstance(part, PIL.WebPImagePlugin.WebPImageFile):
        buffered = BytesIO()
        part.save(buffered, format="WEBP")  # Use "WEBP" to maintain the original format
        img_bytes = buffered.getvalue()
        return {
            "mime_type": "image/webp",
            "data": base64.b64encode(img_bytes).decode("utf-8"),
        }
    return part


def _serialize_proto_data(data: list[dict]) -> str:
    serializable_data = []
    for item in data:
        serialized_item = item.copy()
        if "parts" in item:
            serialized_item["parts"] = [
                encode_gemini_part(part) for part in item["parts"]
            ]
        serializable_data.append(serialized_item)

    return json.dumps(serializable_data)


def _set_call_response_attributes(response: mb.BaseCallResponse, span: Span) -> None:
    try:
        output = json.dumps(jsonable_encoder(response.message_param))
    except TypeError:
        output = str(response.message_param)
    try:
        messages = json.dumps(jsonable_encoder(response.messages))
    except TypeError:
        messages = _serialize_proto_data(response.messages)  # Gemini
    attributes: dict[str, AttributeValue] = {
        "lilypad.generation.output": output,
        "lilypad.generation.messages": messages,
    }
    span.set_attributes(attributes)


def _set_response_model_attributes(result: BaseModel | mb.BaseType, span: Span) -> None:
    if isinstance(result, BaseModel):
        completion = result.model_dump_json()
        # Safely handle the case where result._response might be None
        if (_response := getattr(result, "_response", None)) and (
            _response_messages := getattr(_response, "messages", None)
        ):
            messages = json.dumps(jsonable_encoder(_response_messages))
        else:
            messages = None
    else:
        if not isinstance(result, str | int | float | bool):
            result = str(result)
        completion = result
        messages = None

    attributes: dict[str, AttributeValue] = {
        "lilypad.generation.output": completion,
    }
    if messages:
        attributes["lilypad.generation.messages"] = messages
    span.set_attributes(attributes)


def _handle_call_response(
    result: mb.BaseCallResponse, fn: Callable, span: Span | None
) -> None:
    if span is None:
        return
    _set_call_response_attributes(result, span)


def _handle_stream(stream: mb.BaseStream, fn: Callable, span: Span | None) -> None:
    if span is None:
        return
    call_response = cast(mb.BaseCallResponse, stream.construct_call_response())
    _set_call_response_attributes(call_response, span)


def _handle_response_model(
    result: BaseModel | mb.BaseType, fn: Callable, span: Span | None
) -> None:
    if span is None:
        return

    _set_response_model_attributes(result, span)


def _handle_structured_stream(
    result: mb.BaseStructuredStream, fn: Callable, span: Span | None
) -> None:
    if span is None:
        return

    _set_response_model_attributes(result.constructed_response_model, span)


async def _handle_call_response_async(
    result: mb.BaseCallResponse, fn: Callable, span: Span | None
) -> None:
    if span is None:
        return

    _set_call_response_attributes(result, span)


async def _handle_stream_async(
    stream: mb.BaseStream, fn: Callable, span: Span | None
) -> None:
    if span is None:
        return
    call_response = cast(mb.BaseCallResponse, stream.construct_call_response())
    _set_call_response_attributes(call_response, span)


async def _handle_response_model_async(
    result: BaseModel | mb.BaseType, fn: Callable, span: Span | None
) -> None:
    if span is None:
        return
    _set_response_model_attributes(result, span)


async def _handle_structured_stream_async(
    result: mb.BaseStructuredStream, fn: Callable, span: Span | None
) -> None:
    if span is None:
        return
    _set_response_model_attributes(result.constructed_response_model, span)


def create_mirascope_middleware(
    generation: GenerationPublic,
    arg_values: ArgValues,
    is_async: bool,
    prompt_template: str | None = None,
    project_uuid: UUID | None = None,
    span_context_holder: SpanContextHolder | None = None,
) -> Callable[[Callable[_P, _R]], Callable[_P, _R]]:
    """Creates the middleware decorator for a Lilypad/Mirascope function."""
    return middleware_factory(
        custom_context_manager=_get_custom_context_manager(
            generation,
            arg_values,
            is_async,
            prompt_template,
            project_uuid,
            span_context_holder,
        ),
        handle_call_response=_handle_call_response,
        handle_call_response_async=_handle_call_response_async,
        handle_stream=_handle_stream,
        handle_stream_async=_handle_stream_async,
        handle_response_model=_handle_response_model,
        handle_response_model_async=_handle_response_model_async,
        handle_structured_stream=_handle_structured_stream,
        handle_structured_stream_async=_handle_structured_stream_async,
    )


__all__ = ["create_mirascope_middleware"]
