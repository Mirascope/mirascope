"""Integration with Langfuse"""

import inspect
from contextlib import contextmanager
from functools import wraps
from typing import Any, Callable, Optional, Type, overload

from langfuse import Langfuse
from langfuse.client import StatefulGenerationClient, StatefulTraceClient
from langfuse.types import ModelUsage
from pydantic import BaseModel

from mirascope.base.types import BaseCallResponse, BaseCallResponseChunk, ChunkT

from ..types import (
    BaseCallT,
    BaseChunkerT,
    BaseEmbedderT,
    BaseExtractorT,
    BaseVectorStoreT,
)


def mirascope_langfuse_observe(fn: Callable, trace: StatefulTraceClient):
    """Wraps a pydantic class method with a Langfuse trace."""

    def collect_trace_data(self: BaseModel, **kwargs):
        """Wraps a pydantic class method with a Langfuse trace."""
        class_vars = {}
        for classvars in self.__class_vars__:
            if not classvars == "api_key":
                class_vars[classvars] = getattr(self.__class__, classvars)
        trace.update(
            input=class_vars.pop("prompt_template", None),
            metadata=class_vars,
            tags=class_vars.pop("tags", []),
        )

    @wraps(fn)
    def wrapper(self: BaseModel, *args, **kwargs):
        """Wraps a pydantic class method that returns a value."""
        collect_trace_data(self, **kwargs)
        result = fn(self, *args, **kwargs)
        trace.update(output=result)
        return result

    @wraps(fn)
    async def wrapper_async(self: BaseModel, *args, **kwargs):
        """Wraps a pydantic async class method that returns a value."""
        collect_trace_data(self, **kwargs)
        result = await fn(self, *args, **kwargs)
        trace.update(output=result)
        return result

    @wraps(fn)
    def wrapper_generator(self: BaseModel, *args, **kwargs):
        """Wraps a pydantic class method that returns a generator."""
        collect_trace_data(self, **kwargs)
        result = fn(self, *args, **kwargs)

        output = []
        for value in result:
            output.append(value)
            yield value
        trace.update(output=output)

    @wraps(fn)
    async def wrapper_generator_async(self: BaseModel, *args, **kwargs):
        """Wraps a pydantic async class method that returns a generator."""
        collect_trace_data(self, **kwargs)
        result = fn(self, *args, **kwargs)
        output = []
        async for value in result:
            output.append(value)
            yield value
        trace.update(output=output)

    if inspect.isasyncgenfunction(fn):
        return wrapper_generator_async
    elif inspect.iscoroutinefunction(fn):
        return wrapper_async
    elif inspect.isgeneratorfunction(fn):
        return wrapper_generator
    return wrapper


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
):
    if response_type is not None:
        response = response_type(response=result, start_time=0, end_time=0)
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
    ):
        """Wraps a LLM call with Langfuse."""

        def wrapper(*args, **kwargs):
            """Wraps a function that makes a call to an LLM with Langfuse."""
            generation = langfuse_generation(trace, fn, suffix, **kwargs)
            result = fn(*args, **kwargs)
            langfuse_generation_end(generation, response_type, result)
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
            langfuse_generation_end(generation, response_type, result)
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
    if hasattr(cls, "call"):
        setattr(cls, "call", mirascope_langfuse_observe(cls.call, trace))
    if hasattr(cls, "call_async"):
        setattr(cls, "call_async", mirascope_langfuse_observe(cls.call_async, trace))

    # VectorStore
    if hasattr(cls, "retrieve"):
        setattr(cls, "retrieve", mirascope_langfuse_observe(cls.retrieve, trace))
    if hasattr(cls, "add"):
        setattr(cls, "add", mirascope_langfuse_observe(cls.add, trace))

    # Embedder
    if hasattr(cls, "embed"):
        setattr(cls, "embed", mirascope_langfuse_observe(cls.embed, trace))
    if hasattr(cls, "embed_async"):
        setattr(cls, "embed_async", mirascope_langfuse_observe(cls.embed_async, trace))

    if hasattr(cls, "stream"):
        setattr(cls, "stream", mirascope_langfuse_observe(cls.stream, trace))
    if hasattr(cls, "stream_async"):
        setattr(
            cls, "stream_async", mirascope_langfuse_observe(cls.stream_async, trace)
        )

    if hasattr(cls, "extract"):
        setattr(cls, "extract", mirascope_langfuse_observe(cls.extract, trace))
    if hasattr(cls, "extract_async"):
        setattr(
            cls, "extract_async", mirascope_langfuse_observe(cls.extract_async, trace)
        )

    if hasattr(cls, "call_params"):
        setattr(
            cls,
            "call_params",
            cls.call_params.model_copy(
                update={
                    "langfuse": mirascope_langfuse_generation(trace),
                }
            ),
        )
    if hasattr(cls, "vectorstore_params"):
        setattr(
            cls,
            "vectorstore_params",
            cls.vectorstore_params.model_copy(
                update={
                    "langfuse": mirascope_langfuse_generation(trace),
                }
            ),
        )
    if hasattr(cls, "embedding_params"):
        setattr(
            cls,
            "embedding_params",
            cls.embedding_params.model_copy(
                update={
                    "langfuse": mirascope_langfuse_generation(trace),
                }
            ),
        )
    return cls
