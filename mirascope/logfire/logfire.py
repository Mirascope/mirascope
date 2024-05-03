"""Integration with Logfire from Pydantic"""
import inspect
from contextlib import contextmanager
from functools import wraps
from typing import Any, Callable, Optional, overload

import logfire
from pydantic import BaseModel

from mirascope.base.types import BaseCallResponse, BaseCallResponseChunk, ChunkT

from ..types import (
    BaseCallT,
    BaseChunkerT,
    BaseEmbedderT,
    BaseExtractorT,
    BaseVectorStoreT,
)


def mirascope_logfire_span(fn: Callable):
    """Wraps a pydantic class method with a Logfire span."""

    @contextmanager
    def mirascope_span(self: BaseModel, **kwargs):
        """Wraps a pydantic class method with a Logfire span."""
        class_vars = {}
        for classvars in self.__class_vars__:
            if not classvars == "api_key":
                class_vars[classvars] = getattr(self.__class__, classvars)
        with logfire.span(
            f"{self.__class__.__name__}.{fn.__name__}",
            class_vars=class_vars,
            **kwargs,
        ) as logfire_span:
            yield logfire_span

    @wraps(fn)
    def wrapper(self: BaseModel, *args, **kwargs):
        """Wraps a pydantic class method that returns a value."""
        with mirascope_span(self, **kwargs) as logfire_span:
            result = fn(self, *args, **kwargs)
            logfire_span.set_attribute("response", result)
            return result

    @wraps(fn)
    async def wrapper_async(self: BaseModel, *args, **kwargs):
        """Wraps a pydantic async class method that returns a value."""
        with mirascope_span(self, **kwargs) as logfire_span:
            result = await fn(self, *args, **kwargs)
            logfire_span.set_attribute("response", result)
            return result

    @wraps(fn)
    def wrapper_generator(self: BaseModel, *args, **kwargs):
        """Wraps a pydantic class method that returns a generator."""
        with mirascope_span(self, **kwargs) as logfire_span:
            result = fn(self, *args, **kwargs)
            logfire_span.set_attribute("response", result)
            for value in result:
                yield value

    @wraps(fn)
    async def wrapper_generator_async(self: BaseModel, *args, **kwargs):
        """Wraps a pydantic async class method that returns a generator."""
        with mirascope_span(self, **kwargs) as logfire_span:
            result = fn(self, *args, **kwargs)
            logfire_span.set_attribute("response", result)
            async for value in result:
                yield value

    if inspect.isasyncgenfunction(fn):
        return wrapper_generator_async
    if inspect.iscoroutinefunction(fn):
        return wrapper_async
    if inspect.isgeneratorfunction(fn):
        return wrapper_generator
    return wrapper


def mirascope_logfire(
    fn: Callable,
    suffix: str,
    *,
    response_type: Optional[type[BaseCallResponse]] = None,
    response_chunk_type: Optional[type[BaseCallResponseChunk]] = None,
) -> Callable:
    """Wraps a function with a Logfire span."""
    if response_chunk_type is not None:
        return mirascope_logfire_stream(fn, suffix, response_chunk_type)
    return mirascope_logfire_create(fn, suffix, response_type)


def mirascope_logfire_async(
    fn: Callable,
    suffix: str,
    *,
    response_type: Optional[type[BaseCallResponse]] = None,
    response_chunk_type: Optional[type[BaseCallResponseChunk]] = None,
):
    """Wraps an asynchronous function with a Logfire span."""
    if response_chunk_type is not None:
        return mirascope_logfire_stream_async(fn, suffix, response_chunk_type)
    return mirascope_logfire_create_async(fn, suffix, response_type)


def _extract_chunk_content(
    chunk: ChunkT, response_chunk_type: type[BaseCallResponseChunk]
) -> str:
    """Extracts the content from a chunk."""
    return response_chunk_type(chunk=chunk).content


@contextmanager
def _mirascope_llm_span(
    fn: Callable, suffix: str, is_async: bool, args: tuple[Any], kwargs: dict[str, Any]
):
    """Wraps a pydantic class method with a Logfire span."""
    additional_request_data = {}
    model = kwargs.get("model", "unknown")
    if suffix == "gemini":
        gemini_messages = args[0]
        additional_request_data["messages"] = [
            {"role": message["role"], "content": message["parts"][0]}
            for message in gemini_messages
        ]
        model = kwargs.pop("model")
        additional_request_data["model"] = model
    span_data: dict[str, Any] = {
        "async": is_async,
        "request_data": kwargs | additional_request_data,
    }
    with logfire.with_settings(custom_scope_suffix=suffix, tags=["llm"]).span(
        f"{suffix}.{fn.__name__} with {model}", **span_data
    ) as logfire_span:
        yield logfire_span


def mirascope_logfire_create(
    fn: Callable, suffix: str, response_type: Optional[type[BaseCallResponse]]
) -> Callable:
    """Wraps a function with a Logfire span."""

    @wraps(fn)
    def wrapper(*args, **kwargs):
        with _mirascope_llm_span(fn, suffix, False, args, kwargs) as logfire_span:
            result = fn(*args, **kwargs)
            logfire_span.set_attribute("original_response", result)
            if response_type is not None:
                response = response_type(response=result, start_time=0, end_time=0)
                logfire_span.set_attribute(
                    "response_data",
                    {"message": {"role": "assistant", "content": response.content}},
                )
            return result

    return wrapper


def mirascope_logfire_stream(
    fn: Callable, suffix: str, response_chunk_type: type[BaseCallResponseChunk]
) -> Callable:
    """Wraps a function that yields a generator with a Logfire span."""

    @wraps(fn)
    def wrapper(*args, **kwargs):
        with _mirascope_llm_span(fn, suffix, False, args, kwargs) as logfire_span:
            content = []
            stream = fn(*args, **kwargs)
            if suffix != "anthropic":
                for chunk in stream:
                    chunk_content = _extract_chunk_content(chunk, response_chunk_type)
                    content.append(chunk_content)
                    yield chunk
            else:
                with stream as s:
                    for chunk in s:
                        chunk_content = _extract_chunk_content(
                            chunk, response_chunk_type
                        )
                        content.append(chunk_content)
                        yield chunk
            logfire_span.set_attribute(
                "response_data",
                {
                    "combined_chunk_content": "".join(content),
                    "chunk_count": len(content),
                },
            )

    return wrapper


def mirascope_logfire_create_async(
    fn: Callable, suffix: str, response_type: Optional[type[BaseCallResponse]]
) -> Callable:
    """Wraps a asynchronous function that yields a generator with a Logfire span."""

    @wraps(fn)
    async def wrapper(*args, **kwargs):
        with _mirascope_llm_span(fn, suffix, True, args, kwargs) as logfire_span:
            result = await fn(*args, **kwargs)
            logfire_span.set_attribute("original_response", result)
            if response_type is not None:
                response = response_type(response=result, start_time=0, end_time=0)
                logfire_span.set_attribute(
                    "response_data",
                    {"message": {"role": "assistant", "content": response.content}},
                )
            return result

    return wrapper


def mirascope_logfire_stream_async(
    fn: Callable, suffix: str, response_chunk_type: type[BaseCallResponseChunk]
) -> Callable:
    """Wraps an asynchronous function with a Logfire span."""

    @wraps(fn)
    async def wrapper(*args, **kwargs):
        with _mirascope_llm_span(fn, suffix, True, args, kwargs) as logfire_span:
            content = []
            if suffix == "groq":
                stream = await fn(*args, **kwargs)
            else:
                stream = fn(*args, **kwargs)
            if suffix != "anthropic":
                async for chunk in stream:
                    chunk_content = _extract_chunk_content(chunk, response_chunk_type)
                    content.append(chunk_content)
                    yield chunk
            else:
                async with stream as s:
                    async for chunk in s:
                        chunk_content = _extract_chunk_content(
                            chunk, response_chunk_type
                        )
                        content.append(chunk_content)
                        yield chunk
            logfire_span.set_attribute(
                "response_data",
                {
                    "combined_chunk_content": "".join(content),
                    "chunk_count": len(content),
                },
            )

    return wrapper


def get_parent_class_name(cls: type[BaseModel], target_name: str) -> Optional[str]:
    """Recursively searches for a parent class with a given name."""
    for base in cls.__bases__:
        if base.__name__.startswith(target_name):
            return base.__name__
        else:
            parent_name = get_parent_class_name(base, target_name)
            if parent_name:
                return parent_name
    return None


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
    if hasattr(cls, "call"):
        setattr(cls, "call", mirascope_logfire_span(cls.call))
    if hasattr(cls, "stream"):
        setattr(cls, "stream", mirascope_logfire_span(cls.stream))
    if hasattr(cls, "call_async"):
        setattr(cls, "call_async", mirascope_logfire_span(cls.call_async))
    if hasattr(cls, "stream_async"):
        setattr(cls, "stream_async", mirascope_logfire_span(cls.stream_async))
    if hasattr(cls, "extract"):
        setattr(cls, "extract", mirascope_logfire_span(cls.extract))
    if hasattr(cls, "extract_async"):
        setattr(cls, "extract_async", mirascope_logfire_span(cls.extract_async))
    if hasattr(cls, "retrieve"):
        setattr(cls, "retrieve", mirascope_logfire_span(cls.retrieve))
    if hasattr(cls, "add"):
        setattr(cls, "add", mirascope_logfire_span(cls.add))
    if get_parent_class_name(cls, "OpenAI"):
        if hasattr(cls, "call_params"):
            cls.call_params.logfire = logfire.instrument_openai
        if hasattr(cls, "embedding_params"):
            cls.embedding_params.logfire = logfire.instrument_openai
    else:
        # TODO: Use instrument instead when they are integrated into logfire
        if hasattr(cls, "call_params"):
            cls.call_params.logfire = mirascope_logfire
            cls.call_params.logfire_async = mirascope_logfire_async
        if hasattr(cls, "vectorstore_params"):
            # Wraps class methods rather than calls directly
            cls.vectorstore_params.logfire = mirascope_logfire_span
            cls.vectorstore_params.logfire_async = mirascope_logfire_span
        if hasattr(cls, "embedding_params"):
            cls.embedding_params.logfire = mirascope_logfire
            cls.embedding_params.logfire_async = mirascope_logfire_async
    return cls
