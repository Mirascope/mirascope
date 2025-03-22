"""This module contains the `generation` decorator and related utilities for tracing."""

import json
from collections.abc import Generator
from contextlib import contextmanager
from functools import wraps
from typing import (
    Any,
    ParamSpec,
    TypeAlias,
    TypeVar,
    overload,
)

from opentelemetry.trace import Span, get_tracer
from opentelemetry.util.types import AttributeValue
from pydantic import BaseModel

from . import _utils
from .spans import span_order_context

_P = ParamSpec("_P")
_R = TypeVar("_R")


class _ResultHolder:
    """A class to hold the result of a function call."""

    def __init__(self) -> None:
        self.result = None

    def set_result(self, result: Any) -> None:  # noqa: ANN401
        """Set the result attribute."""
        self.result: Any = result


_TraceAttribute: TypeAlias = dict[str, AttributeValue]


@contextmanager
def _set_span_attributes(
    trace_type: str, span: Span, span_attribute: _TraceAttribute, is_async: bool
) -> Generator[_ResultHolder, None, None]:
    """Set the attributes on the span."""
    settings = _utils.load_settings()
    span_attribute["lilypad.project_uuid"] = (
        settings.project_id if settings.project_id else ""
    )
    span_attribute["lilypad.type"] = trace_type
    span_attribute["lilypad.is_async"] = is_async
    span.set_attributes(span_attribute)
    result_holder = _ResultHolder()
    yield result_holder
    original_output = result_holder.result
    output_for_span = (
        original_output.model_dump()
        if isinstance(original_output, BaseModel)
        else original_output
    )
    span.set_attribute(f"lilypad.{trace_type}.output", str(output_for_span))


TraceDecorator: TypeAlias = _utils.protocols.PassthroughDecorator


def _trace(
    trace_type: str,
    trace_attribute: _TraceAttribute,
) -> TraceDecorator:
    @overload
    def decorator(
        fn: _utils.protocols.AsyncFunction[_P, _R],
    ) -> _utils.protocols.AsyncFunction[_P, _R]: ...

    @overload
    def decorator(
        fn: _utils.protocols.SyncFunction[_P, _R],
    ) -> _utils.protocols.SyncFunction[_P, _R]: ...

    def decorator(
        fn: _utils.protocols.AsyncFunction[_P, _R]
        | _utils.protocols.SyncFunction[_P, _R],
    ) -> _utils.protocols.AsyncFunction[_P, _R] | _utils.protocols.SyncFunction[_P, _R]:
        if _utils.fn_is_async(fn):

            @wraps(fn)
            async def inner_async(*args: _P.args, **kwargs: _P.kwargs) -> _R:
                with (
                    get_tracer("lilypad").start_as_current_span(
                        _utils.get_qualified_name(fn)
                    ) as span,
                    span_order_context(span),
                    _set_span_attributes(
                        trace_type, span, trace_attribute, is_async=True
                    ) as result_holder,
                ):
                    output = await fn(*args, **kwargs)
                    result_holder.set_result(output)

                return output

            return inner_async

        else:

            @wraps(fn)
            def inner(*args: _P.args, **kwargs: _P.kwargs) -> _R:
                with (
                    get_tracer("lilypad").start_as_current_span(
                        _utils.get_qualified_name(fn)
                    ) as span,
                    span_order_context(span),
                    _set_span_attributes(
                        trace_type, span, trace_attribute, is_async=True
                    ) as result_holder,
                ):
                    output = fn(*args, **kwargs)
                    result_holder.set_result(output)
                return output

            return inner

    return decorator


def _construct_trace_attributes(
    arg_types: dict[str, str],
    arg_values: dict[str, Any],
) -> dict[str, AttributeValue]:
    jsonable_arg_values = {}
    for arg_name, arg_value in arg_values.items():
        try:
            serialized_arg_value = _utils.jsonable_encoder(arg_value)
        except ValueError:
            serialized_arg_value = "could not serialize"
        jsonable_arg_values[arg_name] = serialized_arg_value
    return {
        "lilypad.trace.arg_types": json.dumps(arg_types),
        "lilypad.trace.arg_values": json.dumps(jsonable_arg_values),
    }


def trace() -> TraceDecorator:
    """The tracing LLM generations.

    The decorated function will trace and log automatically.

    Returns:
        TraceDecorator: The `trace` decorator return protocol.
    """

    @overload
    def decorator(
        fn: _utils.protocols.AsyncFunction[_P, _R],
    ) -> _utils.protocols.AsyncFunction[_P, _R]: ...

    @overload
    def decorator(
        fn: _utils.protocols.SyncFunction[_P, _R],
    ) -> _utils.protocols.SyncFunction[_P, _R]: ...

    def decorator(
        fn: _utils.protocols.AsyncFunction[_P, _R]
        | _utils.protocols.SyncFunction[_P, _R],
    ) -> _utils.protocols.AsyncFunction[_P, _R] | _utils.protocols.SyncFunction[_P, _R]:
        if _utils.fn_is_async(fn):

            @_utils.call_safely(fn)
            async def inner_async(*args: _P.args, **kwargs: _P.kwargs) -> _R:
                arg_types, arg_values = _utils.inspect_arguments(fn, *args, **kwargs)
                decorator_inner = _trace(
                    "trace",
                    _construct_trace_attributes(
                        arg_types=arg_types,
                        arg_values=arg_values,
                    ),
                )
                return await decorator_inner(fn)(*args, **kwargs)

            return inner_async

        else:

            @_utils.call_safely(fn)
            def inner(*args: _P.args, **kwargs: _P.kwargs) -> _R:
                arg_types, arg_values = _utils.inspect_arguments(fn, *args, **kwargs)
                decorator_inner = _trace(
                    "trace",
                    _construct_trace_attributes(
                        arg_types=arg_types,
                        arg_values=arg_values,
                    ),
                )
                return decorator_inner(fn)(*args, **kwargs)

            return inner

    return decorator
