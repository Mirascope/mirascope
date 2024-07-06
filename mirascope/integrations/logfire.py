"""Mirascope x Logfire Integration."""

from contextlib import contextmanager
from typing import (
    Any,
    Awaitable,
    Callable,
    Generator,
    ParamSpec,
    TypeVar,
    overload,
)

import logfire
from pydantic import BaseModel

from ..core.base import BaseCallResponse
from ..core.base._stream import BaseStream
from .utils import middleware

_P = ParamSpec("_P")
_R = TypeVar("_R", bound=BaseCallResponse | BaseStream | BaseModel)


@overload
def with_logfire(fn: Callable[_P, _R]) -> Callable[_P, _R]: ...


@overload
def with_logfire(fn: Callable[_P, Awaitable[_R]]) -> Callable[_P, Awaitable[_R]]: ...


def with_logfire(
    fn: Callable[_P, _R] | Callable[_P, Awaitable[_R]],
) -> Callable[_P, _R] | Callable[_P, Awaitable[_R]]:
    """Wraps a Mirascope function with Logfire tracing."""

    @contextmanager
    def custom_context_manager() -> Generator[logfire.LogfireSpan, Any, None]:
        metadata = fn.__annotations__.get("metadata", {})
        tags = getattr(metadata, "tags", {})
        with logfire.with_settings(
            custom_scope_suffix="mirascope", tags=list(tags)
        ).span(fn.__name__) as logfire_span:
            yield logfire_span

    def get_call_response_span_data(result: BaseCallResponse) -> dict:
        return {
            "async": False,
            "call_params": result.call_params,
            "model": result.model,
            "provider": result._provider,
            "prompt_template": result.prompt_template,
            "template_variables": result.fn_args,
            "messages": result.messages,
            "response_data": result.response,
        }

    def get_stream_span_data(stream: BaseStream) -> dict:
        return {
            "messages": [stream.user_message_param],
            "call_params": stream.call_params,
            "model": stream.model,
            "provider": stream.provider,
            "prompt_template": stream.prompt_template,
            "template_variables": stream.fn_args,
            "output": {
                "cost": stream.cost,
                "content": stream.message_param.get("content", None),
            },
        }

    def get_tool_calls(result: BaseCallResponse) -> list[dict] | None:
        if tools := result.tools:
            tool_calls = [
                {
                    "function": {
                        "arguments": tool.model_dump_json(exclude={"tool_call"}),
                        "name": tool.name(),
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
        result: BaseCallResponse, logfire_span: logfire.LogfireSpan | None
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
        logfire_span: logfire.LogfireSpan | None,
    ):
        span_data = get_stream_span_data(stream) | {"async": False}
        if logfire_span is not None:
            logfire_span.set_attributes(span_data)

    def handle_base_model(result: BaseModel, logfire_span: logfire.LogfireSpan | None):
        span_data: dict[str, Any] = {}
        output: dict[str, Any] = {}
        if result._response is not None:
            response: BaseCallResponse = result._response
            span_data |= get_call_response_span_data(response)
            output |= get_output(response)
        output["response_model"] = result
        span_data["async"] = False
        span_data["output"] = output
        logfire_span.set_attributes(span_data)

    async def handle_call_response_async(
        result: BaseCallResponse, logfire_span: logfire.LogfireSpan | None
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
        logfire_span: logfire.LogfireSpan | None,
    ):
        span_data = get_stream_span_data(stream) | {"async": True}
        if logfire_span is not None:
            logfire_span.set_attributes(span_data)

    async def handle_base_model_async(
        result: BaseModel, logfire_span: logfire.LogfireSpan | None
    ):
        span_data: dict[str, Any] = {}
        output: dict[str, Any] = {}
        if result._response is not None:
            response: BaseCallResponse = result._response
            span_data |= get_call_response_span_data(response)
            output |= get_output(response)
        output["response_model"] = result
        span_data["async"] = True
        span_data["output"] = output
        logfire_span.set_attributes(span_data)

    return middleware(
        fn,
        custom_context_manager=custom_context_manager,
        handle_call_response=handle_call_response,
        handle_call_response_async=handle_call_response_async,
        handle_stream=handle_stream,
        handle_stream_async=handle_stream_async,
        handle_base_model=handle_base_model,
        handle_base_model_async=handle_base_model_async,
    )
