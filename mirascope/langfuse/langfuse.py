"""Integration with Langfuse"""

import inspect
from contextlib import contextmanager
from functools import wraps
from typing import Any, Callable, Optional, Type, overload

from langfuse import Langfuse
from langfuse.client import StatefulGenerationClient, StatefulTraceClient
from langfuse.types import ModelUsage
from pydantic import BaseModel

from mirascope.base.ops_utils import get_class_vars, wrap_mirascope_class_functions
from mirascope.base.tools import BaseTool
from mirascope.base.types import BaseCallResponse, BaseCallResponseChunk, ChunkT

from ..types import (
    BaseCallT,
    BaseChunkerT,
    BaseEmbedderT,
    BaseExtractorT,
    BaseVectorStoreT,
)


@contextmanager
def record_streaming(generation: StatefulGenerationClient):
    """Langfuse record_streaming with Mirascope providers"""
    content: list[str] = []

    def record_chunk(
        chunk: ChunkT, response_chunk_type: type[BaseCallResponseChunk]
    ) -> Any:
        """Handles all provider chunk_types instead of only OpenAI"""
        chunk_content = response_chunk_type(chunk=chunk).content
        if chunk_content is not None:
            content.append(chunk_content)

    try:
        yield record_chunk
    finally:
        # TODO: Add usage for providers that support usage in streaming
        generation.end(output="".join(content), usage=None)


def langfuse_generation(
    trace: StatefulTraceClient, fn: Callable, suffix: str, **kwargs
):
    """Instantiates a Langfuse generation object with some data."""
    model = kwargs.get("model", "unknown")
    if suffix == "gemini":
        model = kwargs.pop("model")
    return trace.generation(
        name=f"{fn.__name__} with {model}",
        input=kwargs.get("messages", []),
        metadata=kwargs,
        tags=kwargs.pop("tags", []),
    )


def langfuse_generation_end(
    generation: StatefulGenerationClient,
    response_type: Optional[type[BaseCallResponse]] = None,
    result: Any = None,
    tool_types: Optional[list[type[BaseTool]]] = None,
):
    if response_type is not None:
        response = response_type(
            response=result, start_time=0, end_time=0, tool_types=tool_types
        )
        usage = ModelUsage(
            input=response.input_tokens,
            output=response.output_tokens,
            unit="TOKENS",
        )
        generation.end(output=response.content, usage=usage)


def mirascope_langfuse_generation(trace: StatefulTraceClient) -> Callable:
    """Wraps a function with a Langfuse generation."""

    def decorator(
        fn,
        suffix,
        *,
        is_async: bool = False,
        response_type: Optional[type[BaseCallResponse]] = None,
        response_chunk_type: Optional[type[BaseCallResponseChunk]] = None,
        tool_types: Optional[list[type[BaseTool]]] = None,
    ):
        """Wraps a LLM call with Langfuse."""

        def wrapper(*args, **kwargs):
            """Wraps a function that makes a call to an LLM with Langfuse."""
            generation = langfuse_generation(trace, fn, suffix, **kwargs)
            result = fn(*args, **kwargs)
            langfuse_generation_end(generation, response_type, result, tool_types)
            return result

        def wrapper_generator(*args, **kwargs):
            """Wraps a function that yields a call to an LLM with Langfuse."""
            generation = langfuse_generation(trace, fn, suffix, **kwargs)
            with record_streaming(generation) as record_chunk:
                generator = fn(*args, **kwargs)
                if suffix != "anthropic":
                    for chunk in generator:
                        record_chunk(chunk, response_chunk_type)
                        yield chunk
                else:
                    with generator as s:
                        for chunk in s:
                            record_chunk(chunk, response_chunk_type)
                            yield chunk

        async def wrapper_async(*args, **kwargs):
            """Wraps a function that makes an async call to an LLM with Langfuse."""
            generation = langfuse_generation(trace, fn, suffix, **kwargs)
            result = await fn(*args, **kwargs)
            langfuse_generation_end(generation, response_type, result, tool_types)
            return result

        async def wrapper_generator_async(*args, **kwargs):
            """Wraps a function that yields an async call to an LLM with Langfuse."""
            generation = langfuse_generation(trace, fn, suffix, **kwargs)
            with record_streaming(generation) as record_chunk:
                if suffix == "groq":
                    generator = await fn(*args, **kwargs)
                else:
                    generator = fn(*args, **kwargs)
                if suffix != "anthropic":
                    async for chunk in generator:
                        record_chunk(chunk, response_chunk_type)
                        yield chunk
                else:
                    async with generator as s:
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


def handle_before_call(self: BaseModel, fn, *args, trace=StatefulTraceClient, **kwargs):
    class_vars = get_class_vars(self)
    trace.update(
        input=class_vars.pop("prompt_template", None),
        metadata=class_vars,
        tags=class_vars.pop("tags", []),
    )
    return trace


def handle_after_call(
    cls, fn, result, before_call, trace=StatefulTraceClient, **kwargs
):
    trace.update(output=result)


@overload
def with_langfuse(cls: Type[BaseCallT]) -> Type[BaseCallT]:
    ...  # pragma: no cover


@overload
def with_langfuse(
    cls: Type[BaseExtractorT],
) -> Type[BaseExtractorT]:
    ...  # pragma: no cover


@overload
def with_langfuse(cls: Type[BaseVectorStoreT]) -> Type[BaseVectorStoreT]:
    ...  # pragma: no cover


@overload
def with_langfuse(cls: Type[BaseChunkerT]) -> Type[BaseChunkerT]:
    ...  # pragma: no cover


@overload
def with_langfuse(cls: Type[BaseEmbedderT]) -> Type[BaseEmbedderT]:
    ...  # pragma: no cover


def with_langfuse(cls):
    """Wraps base classes to automatically use weave.

    Supported base classes: `BaseCall`, `BaseExtractor`, `BaseVectorStore`,
    `BaseChunker`, `BaseEmbedder`

    Example:

    ```python

    from mirascope.openai import OpenAICall
    from mirascope.langfuse import with_langfuse


    @with_langfuse
    class BookRecommender(OpenAICall):
        prompt_template = "Please recommend some {genre} books"

        genre: str


    recommender = BookRecommender(genre="fantasy")
    response = recommender.call()  # this will automatically get logged with Langfuse
    print(response.content)
    ```
    """
    langfuse = Langfuse()
    trace = langfuse.trace(name=cls.__name__)
    wrap_mirascope_class_functions(
        cls, handle_before_call, handle_after_call, trace=trace
    )
    if hasattr(cls, "configuration"):
        cls.configuration.llm_ops.append(mirascope_langfuse_generation(trace))
    return cls
