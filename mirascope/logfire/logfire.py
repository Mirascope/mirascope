"""Integration with Logfire from Pydantic"""
from contextlib import contextmanager
from typing import Any, Callable, Optional, Union, overload

import logfire
from logfire import LogfireSpan
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


def mirascope_logfire() -> Callable:
    def decorator(
        fn: Callable,
        suffix: str,
        *,
        is_async: bool = False,
        response_type: Optional[type[BaseCallResponse]] = None,
        response_chunk_type: Optional[type[BaseCallResponseChunk]] = None,
        tool_types: Optional[list[type[BaseTool]]] = None,
    ) -> Callable:
        """Wraps a LLM call with Pydantic Logfire"""

        def wrapper(*args, **kwargs):
            with _mirascope_llm_span(fn, suffix, False, args, kwargs) as logfire_span:
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
                                    "name": tool.__class__.__name__,
                                }
                            }
                            for tool in tools
                        ]
                        message["tool_calls"] = tool_calls
                        message.pop("content")
                    logfire_span.set_attribute("response_data", {"message": message})
                return result

        async def wrapper_async(*args, **kwargs):
            with _mirascope_llm_span(fn, suffix, True, args, kwargs) as logfire_span:
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
                                    "name": tool.__class__.__name__,
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
            span_data = _get_span_data(suffix, False, args, kwargs)
            with record_streaming(
                logfire_span, span_data, _extract_chunk_content
            ) as record_chunk:
                stream = fn(*args, **kwargs)
                if suffix != "anthropic":
                    for chunk in stream:
                        record_chunk(chunk, response_chunk_type)
                        yield chunk
                else:
                    with stream as s:
                        for chunk in s:
                            record_chunk(chunk, response_chunk_type)
                            yield chunk

        async def wrapper_generator_async(*args, **kwargs):
            logfire_span = logfire.with_settings(
                custom_scope_suffix=suffix, tags=["llm"]
            )
            span_data = _get_span_data(suffix, True, args, kwargs)
            with record_streaming(
                logfire_span, span_data, _extract_chunk_content
            ) as record_chunk:
                if suffix == "groq":
                    stream = await fn(*args, **kwargs)
                else:
                    stream = fn(*args, **kwargs)
                if suffix != "anthropic":
                    async for chunk in stream:
                        record_chunk(chunk, response_chunk_type)
                        yield chunk
                else:
                    async with stream as s:
                        async for chunk in s:
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

    return decorator


def _extract_chunk_content(
    chunk: ChunkT, response_chunk_type: type[BaseCallResponseChunk]
) -> str:
    """Extracts the content from a chunk."""
    return response_chunk_type(chunk=chunk).content


def _get_span_data(
    suffix: str, is_async: bool, args: tuple[Any], kwargs: dict[str, Any]
) -> dict[str, Any]:
    additional_request_data = {}
    if suffix == "gemini":
        gemini_messages = args[0]
        additional_request_data["messages"] = [
            {"role": message["role"], "content": message["parts"][0]}
            for message in gemini_messages
        ]
        model = kwargs.pop("model")
        additional_request_data["model"] = model
    return {
        "async": is_async,
        "request_data": kwargs | additional_request_data,
    }


@contextmanager
def _mirascope_llm_span(
    fn: Callable, suffix: str, is_async: bool, args: tuple[Any], kwargs: dict[str, Any]
):
    """Wraps a pydantic class method with a Logfire span."""
    model = kwargs.get("model", "unknown")
    span_data = _get_span_data(suffix, is_async, args, kwargs)
    with logfire.with_settings(custom_scope_suffix=suffix, tags=["llm"]).span(
        f"{suffix}.{fn.__name__} with {model}", **span_data
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
    with logfire.span(
        f"{self.__class__.__name__}.{fn.__name__}",
        class_vars=class_vars,
        **kwargs,
    ) as logfire_span:
        yield logfire_span


def handle_after_call(self: BaseModel, fn, result, logfire_span: LogfireSpan, **kwargs):
    """Handles after call"""
    logfire_span.set_attribute("response", result)


@overload
def with_logfire(cls: type[BaseCallT]) -> type[BaseCallT]:
    ...  # pragma: no cover


@overload
def with_logfire(cls: type[BaseExtractorT]) -> type[BaseExtractorT]:
    ...  # pragma: no cover


@overload
def with_logfire(cls: type[BaseVectorStoreT]) -> type[BaseVectorStoreT]:
    ...  # pragma: no cover


@overload
def with_logfire(cls: type[BaseChunkerT]) -> type[BaseChunkerT]:
    ...  # pragma: no cover


@overload
def with_logfire(cls: type[BaseEmbedderT]) -> type[BaseEmbedderT]:
    ...  # pragma: no cover


def with_logfire(cls):
    """Wraps a pydantic class with a Logfire span."""
    wrap_mirascope_class_functions(cls, handle_before_call, handle_after_call)
    if cls._provider and cls._provider == "openai":
        if hasattr(cls, "configuration"):
            cls.configuration.llm_ops.append(logfire.instrument_openai)
    else:
        # TODO: Use instrument instead when they are integrated into logfire
        if hasattr(cls, "configuration"):
            llm_ops = cls.configuration.llm_ops
            llm_ops.append(mirascope_logfire())
    return cls
