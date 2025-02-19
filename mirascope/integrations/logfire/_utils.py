"""Mirascope x Logfire Integration utils"""

from collections.abc import Callable, Generator
from contextlib import contextmanager
from typing import (
    Any,
)

import logfire
from pydantic import BaseModel

from mirascope.core.base._utils._base_type import BaseType

from ...core.base import BaseCallResponse, _utils
from ...core.base.metadata import Metadata
from ...core.base.stream import BaseStream
from ...core.base.structured_stream import BaseStructuredStream


@contextmanager
def custom_context_manager(
    fn: Callable,
) -> Generator[logfire.LogfireSpan, Any, None]:
    metadata: Metadata = _utils.get_metadata(fn, None)
    tags = metadata.get("tags", [])
    with logfire.with_settings(custom_scope_suffix="mirascope", tags=list(tags)).span(  # pyright: ignore[reportGeneralTypeIssues]
        fn.__name__
    ) as logfire_span:
        yield logfire_span


def _get_call_response_span_data(result: BaseCallResponse) -> dict[str, Any]:
    output: dict[str, Any] = {}
    if cost := result.cost:
        output["cost"] = cost
    if input_tokens := result.input_tokens:
        output["input_tokens"] = input_tokens
    if output_tokens := result.output_tokens:
        output["output_tokens"] = output_tokens
    if content := result.content:
        output["content"] = content
    return {
        "async": False,
        "call_params": result.call_params,
        "call_kwargs": result.call_kwargs,
        "model": result.model,
        "provider": result._provider,
        "prompt_template": result.prompt_template or "",
        "template_variables": result.fn_args,
        "messages": result.messages,
        "response_data": result.response,
        "output": output,
    }


def _get_tool_calls(result: BaseCallResponse) -> list[dict[str, Any]] | None:
    if tools := result.tools:
        tool_calls = [
            {
                "function": {
                    "arguments": tool.args,
                    "name": tool._name(),
                }
            }
            for tool in tools
        ]
        return tool_calls
    return None


def handle_call_response(
    result: BaseCallResponse, fn: Callable, logfire_span: logfire.LogfireSpan | None
) -> None:
    if logfire_span is None:
        return
    span_data = _get_call_response_span_data(result)
    span_data["async"] = False
    tool_calls = _get_tool_calls(result)
    if tool_calls:
        span_data["output"]["tool_calls"] = tool_calls
    logfire_span.set_attributes(span_data)


def handle_stream(
    stream: BaseStream,
    fn: Callable,
    logfire_span: logfire.LogfireSpan | None,
) -> None:
    handle_call_response(stream.construct_call_response(), fn, logfire_span)


def _set_response_model_output(
    result: BaseModel | BaseType, output: dict[str, Any]
) -> None:
    if isinstance(result, BaseModel):
        output["response_model"] = {
            "name": result.__class__.__name__,
            "arguments": result.model_dump(),
        }
    else:
        output["content"] = result


def handle_response_model(
    result: BaseModel | BaseType, fn: Callable, logfire_span: logfire.LogfireSpan | None
) -> None:
    if logfire_span is None:
        return
    span_data: dict[str, Any] = {"output": {}, "async": False}
    if isinstance(result, BaseModel):
        response: BaseCallResponse = result._response  # pyright: ignore [reportAttributeAccessIssue]
        span_data |= _get_call_response_span_data(response)
    _set_response_model_output(result, span_data["output"])
    logfire_span.set_attributes(span_data)


def _get_structured_stream_span_data(result: BaseStructuredStream) -> dict[str, Any]:
    span_data = _get_call_response_span_data(result.stream.construct_call_response())
    output = span_data.get("output", {})
    response_model = result.constructed_response_model
    if isinstance(response_model, BaseModel):
        output["response_model"] = {
            "name": response_model.__class__.__name__,
            "arguments": response_model.model_dump(),
        }
    else:
        output["content"] = response_model
    span_data["output"] = output

    return span_data


def handle_structured_stream(
    result: BaseStructuredStream, fn: Callable, logfire_span: logfire.LogfireSpan | None
) -> None:
    if logfire_span is None:
        return
    span_data = _get_structured_stream_span_data(result)
    span_data["async"] = False
    logfire_span.set_attributes(span_data)


def _get_error_span_data(e: Exception, fn: Callable) -> dict[str, Any]:
    span_data: dict[str, Any] = {}
    if hasattr(e, "_response"):
        response: BaseCallResponse = e._response  # pyright: ignore [reportAttributeAccessIssue]
        span_data = _get_call_response_span_data(response)
        tool_calls = _get_tool_calls(response)
        if tool_calls:
            span_data["output"]["tool_calls"] = tool_calls
    span_data["error"] = type(e).__name__
    span_data["error_message"] = str(e)
    return span_data


def handle_error(
    e: Exception, fn: Callable, logfire_span: logfire.LogfireSpan | None
) -> None:
    if logfire_span is None:
        return
    span_data = _get_error_span_data(e, fn)
    span_data["async"] = False
    logfire_span.set_attributes(span_data)
    # propagate error
    raise e


async def handle_call_response_async(
    result: BaseCallResponse, fn: Callable, logfire_span: logfire.LogfireSpan | None
) -> None:
    if logfire_span is None:
        return
    span_data = _get_call_response_span_data(result)
    span_data["async"] = True
    tool_calls = _get_tool_calls(result)
    if tool_calls:
        span_data["output"]["tool_calls"] = tool_calls
    logfire_span.set_attributes(span_data)


async def handle_stream_async(
    stream: BaseStream,
    fn: Callable,
    logfire_span: logfire.LogfireSpan | None,
) -> None:
    await handle_call_response_async(stream.construct_call_response(), fn, logfire_span)


async def handle_response_model_async(
    result: BaseModel | BaseType,
    fn: Callable,
    logfire_span: logfire.LogfireSpan | None,
) -> None:
    if logfire_span is None:
        return
    span_data: dict[str, Any] = {"output": {}, "async": True}
    if isinstance(result, BaseModel):
        response: BaseCallResponse = result._response  # pyright: ignore [reportAttributeAccessIssue]
        span_data |= _get_call_response_span_data(response)
    _set_response_model_output(result, span_data["output"])
    logfire_span.set_attributes(span_data)


async def handle_structured_stream_async(
    result: BaseStructuredStream,
    fn: Callable,
    logfire_span: logfire.LogfireSpan | None,
) -> None:
    if logfire_span is None:
        return
    span_data = _get_structured_stream_span_data(result)
    span_data["async"] = True
    logfire_span.set_attributes(span_data)


async def handle_error_async(
    e: Exception, fn: Callable, logfire_span: logfire.LogfireSpan | None
) -> None:
    if logfire_span is None:
        return
    span_data = _get_error_span_data(e, fn)
    span_data["async"] = True
    logfire_span.set_attributes(span_data)
    # propagate error
    raise e
