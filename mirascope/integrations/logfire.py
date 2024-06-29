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

from ..core.base import BaseAsyncStream, BaseCallResponse, BaseStream
from .utils import middleware

_P = ParamSpec("_P")
_R = TypeVar("_R", bound=BaseCallResponse | BaseStream | BaseModel | BaseAsyncStream)


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
        with logfire.with_settings(
            custom_scope_suffix="mirascope", tags=fn.__annotations__.get("tags", [])
        ).span(fn.__name__) as logfire_span:
            yield logfire_span

    def handle_call_response(
        result: BaseCallResponse, logfire_span: logfire.LogfireSpan | None
    ):
        if logfire_span is None:
            return
        output: dict[str, Any] = {}
        span_data = {
            "async": False,
            "call_params": result.call_params,
            "model": result.model,
            "provider": result.provider,
            "prompt_template": result.prompt_template,
            "template_variables": result.fn_args,
            "output": output,
            "messages": result.messages,
            "response_data": result.response,
        }

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
            output["tool_calls"] = tool_calls
        if cost := result.cost:
            output["cost"] = cost
        if input_tokens := result.input_tokens:
            output["input_tokens"] = input_tokens
        if output_tokens := result.output_tokens:
            output["output_tokens"] = output_tokens
        if content := result.content:
            output["content"] = content
        logfire_span.set_attributes(span_data)

    def handle_stream(
        stream: BaseStream,
        logfire_span: logfire.LogfireSpan | None,
    ):
        output: dict[str, Any] = {
            "cost": stream.cost,
            "input_tokens": stream.input_tokens,
            "output_tokens": stream.output_tokens,
            "content": stream.message_param.get("content", None),
        }
        span_data = {
            "async": False,
            "output": output,
            "messages": [stream.user_message_param],
            "call_params": stream.call_params,
            "model": stream.model,
            "provider": stream.provider,
            "prompt_template": stream.prompt_template,
            "template_variables": stream.fn_args,
        }
        if logfire_span is not None:
            logfire_span.set_attributes(span_data)

    def handle_base_model(result: BaseModel, logfire_span: logfire.LogfireSpan | None):
        response: BaseCallResponse = result._response
        # handle_call_response(response, logfire_span)
        output: dict[str, Any] = {"response_model": result}
        # if cost := response.cost:
        #     output["cost"] = cost
        # if input_tokens := response.input_tokens:
        #     output["input_tokens"] = input_tokens
        # if output_tokens := response.output_tokens:
        #     output["output_tokens"] = output_tokens
        # if content := response.content:
        #     output["content"] = content
        logfire_span.set_attribute("output", output)

    async def handle_call_response_async(
        result: BaseCallResponse, logfire_span: logfire.LogfireSpan | None
    ):
        if logfire_span is None:
            return
        output: dict[str, Any] = {}
        span_data = {
            "async": True,
            "call_params": result.call_params,
            "model": result.model,
            "provider": result.provider,
            "prompt_template": result.prompt_template,
            "template_variables": result.fn_args,
            "output": output,
            "messages": result.messages,
            "response_data": result.response,
        }

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
            output["tool_calls"] = tool_calls
        if cost := result.cost:
            output["cost"] = cost
        if input_tokens := result.input_tokens:
            output["input_tokens"] = input_tokens
        if output_tokens := result.output_tokens:
            output["output_tokens"] = output_tokens
        if content := result.content:
            output["content"] = content
        logfire_span.set_attributes(span_data)

    async def handle_stream_async(
        stream: BaseStream,
        logfire_span: logfire.LogfireSpan | None,
    ):
        output: dict[str, Any] = {
            "cost": stream.cost,
            "input_tokens": stream.input_tokens,
            "output_tokens": stream.output_tokens,
            "content": stream.message_param.get("content", None),
        }
        span_data = {
            "async": True,
            "output": output,
            "messages": [stream.user_message_param],
            "call_params": stream.call_params,
            "model": stream.model,
            "provider": stream.provider,
            "prompt_template": stream.prompt_template,
            "template_variables": stream.fn_args,
        }
        if logfire_span is not None:
            logfire_span.set_attributes(span_data)

    return middleware(
        fn,
        custom_context_manager=custom_context_manager,
        handle_call_response=handle_call_response,
        handle_call_response_async=handle_call_response_async,
        handle_stream=handle_stream,
        handle_stream_async=handle_stream_async,
        handle_base_model=handle_base_model,
        # handle_base_model_async=handle_base_model_async,
    )
