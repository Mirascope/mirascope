"""Mirascope x Logfire Integration utils"""

from contextlib import contextmanager
from typing import (
    Any,
    Callable,
    Generator,
)

import logfire
from pydantic import BaseModel

from ...core.base import BaseCallResponse, _utils
from ...core.base._stream import BaseStream
from ...core.base._structured_stream import BaseStructuredStream
from ...core.base.metadata import Metadata


@contextmanager
def custom_context_manager(
    fn: Callable,
) -> Generator[logfire.LogfireSpan, Any, None]:
    metadata: Metadata = _utils.get_metadata(fn, None)
    tags = metadata.get("tags", [])
    with logfire.with_settings(custom_scope_suffix="mirascope", tags=list(tags)).span(
        fn.__name__
    ) as logfire_span:
        yield logfire_span


def get_call_response_span_data(result: BaseCallResponse) -> dict:
    return {
        "async": False,
        "call_params": result.call_params,
        "call_kwargs": result.call_kwargs,
        "model": result.model,
        "provider": result._provider,
        "prompt_template": result.prompt_template,
        "template_variables": result.fn_args,
        "messages": result.messages,
        "response_data": result.response,
    }


def get_stream_span_data(stream: BaseStream) -> dict:
    content = ""
    if stream.message_param:
        content = stream.message_param.get("content", "") or stream.message_param.get(
            "message", ""
        )

    return {
        "messages": [stream.user_message_param],
        "call_params": stream.call_params,
        "call_kwargs": stream.call_kwargs,
        "model": stream.model,
        "provider": stream._provider,
        "prompt_template": stream.prompt_template,
        "template_variables": stream.fn_args,
        "output": {"cost": stream.cost, "content": content},
    }


def get_tool_calls(result: BaseCallResponse) -> list[dict] | None:
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


def get_output(result: BaseCallResponse) -> dict[str, Any]:
    output: dict[str, Any] = {}
    if cost := result.cost:
        output["cost"] = cost
    if input_tokens := result.input_tokens:
        output["input_tokens"] = input_tokens
    if output_tokens := result.output_tokens:
        output["output_tokens"] = output_tokens
    if content := result.content:
        output["content"] = content
    return output


def handle_call_response(
    result: BaseCallResponse, fn: Callable, logfire_span: logfire.LogfireSpan | None
):
    if logfire_span is None:
        return
    output = get_output(result)
    span_data = get_call_response_span_data(result)
    span_data["async"] = False
    tool_calls = get_tool_calls(result)
    if tool_calls:
        output["tool_calls"] = tool_calls
    span_data["output"] = output
    logfire_span.set_attributes(span_data)


def handle_stream(
    stream: BaseStream,
    fn: Callable,
    logfire_span: logfire.LogfireSpan | None,
):
    if logfire_span is None:
        return
    span_data = get_stream_span_data(stream)
    span_data["async"] = False
    logfire_span.set_attributes(span_data)


def handle_base_model(
    result: BaseModel, fn: Callable, logfire_span: logfire.LogfireSpan | None
):
    if logfire_span is None:
        return
    response: BaseCallResponse = result._response  # type: ignore
    span_data = get_call_response_span_data(response)
    output = get_output(response)
    output["response_model"] = result
    span_data["output"] = output
    span_data["async"] = False
    logfire_span.set_attributes(span_data)


def handle_structured_stream(
    result: BaseStructuredStream, fn: Callable, logfire_span: logfire.LogfireSpan | None
):
    if logfire_span is None:
        return
    span_data = get_stream_span_data(result.stream)
    output = span_data.get("output", {})
    output["response_model"] = result.constructed_response_model
    span_data["output"] = output
    span_data["async"] = False
    logfire_span.set_attributes(span_data)


async def handle_call_response_async(
    result: BaseCallResponse, fn: Callable, logfire_span: logfire.LogfireSpan | None
):
    if logfire_span is None:
        return
    output = get_output(result)
    span_data = get_call_response_span_data(result)
    span_data["async"] = True
    tool_calls = get_tool_calls(result)
    if tool_calls:
        output["tool_calls"] = tool_calls
    span_data["output"] = output
    logfire_span.set_attributes(span_data)


async def handle_stream_async(
    stream: BaseStream,
    fn: Callable,
    logfire_span: logfire.LogfireSpan | None,
):
    if logfire_span is None:
        return
    span_data = get_stream_span_data(stream)
    span_data["async"] = True
    logfire_span.set_attributes(span_data)


async def handle_base_model_async(
    result: BaseModel,
    fn: Callable,
    logfire_span: logfire.LogfireSpan | None,
):
    if logfire_span is None:
        return
    response: BaseCallResponse = result._response  # type: ignore
    span_data = get_call_response_span_data(response)
    output = get_output(response)
    output["response_model"] = result
    span_data["output"] = output
    span_data["output"] = output
    span_data["async"] = True
    logfire_span.set_attributes(span_data)


async def handle_structured_stream_async(
    result: BaseStructuredStream,
    fn: Callable,
    logfire_span: logfire.LogfireSpan | None,
):
    if logfire_span is None:
        return
    span_data = get_stream_span_data(result.stream)
    output = span_data.get("output", {})
    output["response_model"] = result.constructed_response_model
    span_data["output"] = output
    span_data["async"] = True
    logfire_span.set_attributes(span_data)
