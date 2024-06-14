"""Integration with Logfire from Pydantic"""
import inspect
from contextlib import (
    contextmanager,
)
from string import Formatter
from textwrap import dedent
from typing import Any, Callable, Optional, Union, overload

import logfire
from logfire import LogfireSpan
from pydantic import BaseModel
from typing_extensions import LiteralString

from mirascope.base.calls import BaseCall
from mirascope.base.extractors import BaseExtractor
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


def mirascope_logfire() -> Callable:
    def mirascope_logfire_decorator(
        fn: Callable,
        suffix: str,
        *,
        is_async: bool = False,
        response_type: Optional[type[BaseCallResponse]] = None,
        response_chunk_type: Optional[type[BaseCallResponseChunk]] = None,
        tool_types: Optional[list[type[BaseTool]]] = None,
        model_name: Optional[str] = None,
    ) -> Callable:
        """Wraps a LLM call with Pydantic Logfire"""

        def wrapper(*args, **kwargs):
            with _mirascope_llm_span(
                fn, suffix, is_async, model_name, args, kwargs
            ) as logfire_span:
                result = fn(*args, **kwargs)
                logfire_span.set_attribute("original_response", result)
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
                                    "name": tool.name(),
                                }
                            }
                            for tool in tools
                        ]
                        message["tool_calls"] = tool_calls
                        message.pop("content")
                    logfire_span.set_attribute("response_data", {"message": message})
                return result

        async def wrapper_async(*args, **kwargs):
            with _mirascope_llm_span(
                fn, suffix, is_async, model_name, args, kwargs
            ) as logfire_span:
                result = await fn(*args, **kwargs)
                logfire_span.set_attribute("original_response", result)
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
                                    "name": tool.name(),
                                }
                            }
                            for tool in tools
                        ]
                        message["tool_calls"] = tool_calls
                        message.pop("content")
                    logfire_span.set_attribute("response_data", {"message": message})
                return result

        def wrapper_generator(*args, **kwargs):
            logfire_span = logfire.with_settings(
                custom_scope_suffix=suffix, tags=["llm"]
            )
            span_data = _get_span_data(suffix, is_async, model_name, args, kwargs)
            with record_streaming(
                logfire_span, span_data, _extract_chunk_content
            ) as record_chunk:
                stream = fn(*args, **kwargs)
                for chunk in stream:
                    record_chunk(chunk, response_chunk_type)
                    yield chunk

        async def wrapper_generator_async(*args, **kwargs):
            logfire_span = logfire.with_settings(
                custom_scope_suffix=suffix, tags=["llm"]
            )
            span_data = _get_span_data(suffix, is_async, model_name, args, kwargs)
            with record_streaming(
                logfire_span, span_data, _extract_chunk_content
            ) as record_chunk:
                stream = fn(*args, **kwargs)
                if inspect.iscoroutine(stream):
                    stream = await stream
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

    return mirascope_logfire_decorator


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
        "request_data": kwargs | additional_request_data,
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
    model = kwargs.get("model", "") or model_name
    span_data = _get_span_data(suffix, is_async, model, args, kwargs)
    name = f"{suffix}.{fn.__name__} with {model}"
    with logfire.with_settings(custom_scope_suffix=suffix, tags=["llm"]).span(
        name, **span_data
    ) as logfire_span:
        yield logfire_span


@contextmanager
def record_streaming(
    logfire_span: logfire.Logfire,
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

    timer = logfire_span._config.ns_timestamp_generator  # type: ignore
    start = timer()
    try:
        yield record_chunk
    finally:
        duration = (timer() - start) / ONE_SECOND_IN_NANOSECONDS
        logfire_span.info(
            STEAMING_MSG_TEMPLATE,
            **span_data,
            duration=duration,
            response_data={
                "combined_chunk_content": "".join(content),
                "chunk_count": len(content),
            },
        )


@contextmanager
def handle_before_call(self: BaseModel, fn: Callable, **kwargs):
    """Handles before call"""
    class_vars = get_class_vars(self)
    name = f"{self.__class__.__name__}.{fn.__name__}"
    tags = class_vars.pop("tags", [])
    template_variables = {**self.model_dump()}
    if hasattr(self, "prompt_template"):
        template_variables |= {
            var: getattr(self, var, None)
            for _, var, _, _ in Formatter().parse(self.prompt_template)
            if var is not None
        }
        class_vars["prompt_template"] = dedent(self.prompt_template)
    span_data = {
        "tags": tags,
        "class_vars": class_vars,
        "template_variables": template_variables,
        **kwargs,
    }
    if hasattr(self, "messages"):
        span_data["messages"] = self.messages()
    with logfire.with_settings(custom_scope_suffix="mirascope", tags=tags).span(
        name, **span_data
    ) as logfire_span:
        yield logfire_span


def handle_after_call(
    self: BaseModel, fn, result, logfire_span: LogfireSpan, **kwargs
) -> None:
    """Handles after call"""
    logfire_span.set_attribute("response_data", result)
    output: dict[str, Any] = {}
    response = None
    if isinstance(result, list):
        output["content"] = "\n".join([chunk.content for chunk in result])
    elif isinstance(self, BaseExtractor):
        response = result._response
    elif isinstance(self, BaseCall):
        response = result
    if response:
        if tools := response.tools:
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
        if cost := response.cost:
            output["cost"] = cost
        if input_tokens := response.input_tokens:
            output["input_tokens"] = input_tokens
        if output_tokens := response.output_tokens:
            output["output_tokens"] = output_tokens
        if content := response.content:
            output["content"] = content
    logfire_span.set_attribute("output", output)


@overload
def with_logfire(cls: type[BaseCallT]) -> type[BaseCallT]:
    ...  # pragma: no cover


@overload
def with_logfire(
    cls: type[BaseExtractorT],
) -> type[BaseExtractorT]:
    ...  # pragma: no cover


@overload
def with_logfire(
    cls: type[BaseVectorStoreT],
) -> type[BaseVectorStoreT]:
    ...  # pragma: no cover


@overload
def with_logfire(cls: type[BaseChunkerT]) -> type[BaseChunkerT]:
    ...  # pragma: no cover


@overload
def with_logfire(
    cls: type[BaseEmbedderT],
) -> type[BaseEmbedderT]:
    ...  # pragma: no cover


def with_logfire(cls):
    """Wraps a pydantic class with a Logfire span."""
    wrap_mirascope_class_functions(
        cls,
        handle_before_call=handle_before_call,
        handle_after_call=handle_after_call,
    )
    instrumented_providers = ["openai", "anthropic"]
    if cls._provider and cls._provider in instrumented_providers:
        if hasattr(cls, "configuration"):
            cls.configuration = cls.configuration.model_copy(
                update={
                    "client_wrappers": [*cls.configuration.client_wrappers, "logfire"]
                }
            )
    else:
        # TODO: Use instrument instead when they are integrated into logfire
        if hasattr(cls, "configuration"):
            cls.configuration = cls.configuration.model_copy(
                update={"llm_ops": [*cls.configuration.llm_ops, mirascope_logfire()]}
            )
    return cls
