"""Integration with Langfuse"""

import inspect
from contextlib import (
    AbstractAsyncContextManager,
    AbstractContextManager,
    contextmanager,
)
from typing import Any, Callable, Generator, Optional, Type, overload

from langfuse.decorators import LangfuseDecorator, langfuse_context, observe
from langfuse.types import ModelUsage
from pydantic import BaseModel

from mirascope.base.ops_utils import (
    get_class_vars,
    wrap_mirascope_class_functions,
)
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
def record_streaming() -> Generator:
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
        langfuse_context.update_current_observation(output="".join(content), usage=None)


def langfuse_generation(fn: Callable, model_name: str, **kwargs) -> None:
    """Adds metadata to the Langfuse observation."""
    model = kwargs.get("model", None) or model_name
    langfuse_context.update_current_observation(
        name=f"{fn.__name__} with {model}",
        input=kwargs.get("messages", []),
        metadata=kwargs,
        tags=kwargs.pop("tags", []),
        model=model,
    )


def langfuse_generation_end(
    response_type: Optional[type[BaseCallResponse]] = None,
    result: Any = None,
    tool_types: Optional[list[type[BaseTool]]] = None,
) -> None:
    """Adds the response to the Langfuse observation."""
    if response_type is not None:
        response = response_type(
            response=result, start_time=0, end_time=0, tool_types=tool_types
        )
        usage = ModelUsage(
            input=response.input_tokens,
            output=response.output_tokens,
            unit="TOKENS",
        )
        langfuse_context.update_current_observation(
            output=response.content, usage=usage
        )


def mirascope_langfuse_generation() -> Callable:
    """Wraps a function with a Langfuse generation."""

    def mirascope_langfuse_decorator(
        fn,
        suffix,
        *,
        is_async: bool = False,
        response_type: Optional[type[BaseCallResponse]] = None,
        response_chunk_type: Optional[type[BaseCallResponseChunk]] = None,
        tool_types: Optional[list[type[BaseTool]]] = None,
        model_name: Optional[str] = None,
    ):
        """Wraps a LLM call with Langfuse."""

        def wrapper(*args, **kwargs):
            """Wraps a function that makes a call to an LLM with Langfuse."""
            langfuse_generation(fn, model_name, **kwargs)
            result = fn(*args, **kwargs)
            langfuse_generation_end(response_type, result, tool_types)
            return result

        def wrapper_generator(*args, **kwargs):
            """Wraps a function that yields a call to an LLM with Langfuse."""
            langfuse_generation(fn, model_name, **kwargs)
            with record_streaming() as record_chunk:
                generator = fn(*args, **kwargs)
                if isinstance(generator, AbstractContextManager):
                    with generator as s:
                        for chunk in s:
                            record_chunk(chunk, response_chunk_type)
                            yield chunk
                else:
                    for chunk in generator:
                        record_chunk(chunk, response_chunk_type)
                        yield chunk

        async def wrapper_async(*args, **kwargs):
            """Wraps a function that makes an async call to an LLM with Langfuse."""
            langfuse_generation(fn, model_name, **kwargs)
            result = await fn(*args, **kwargs)
            langfuse_generation_end(response_type, result, tool_types)
            return result

        async def wrapper_generator_async(*args, **kwargs):
            """Wraps a function that yields an async call to an LLM with Langfuse."""
            langfuse_generation(fn, model_name, **kwargs)
            with record_streaming() as record_chunk:
                stream = fn(*args, **kwargs)
                if inspect.iscoroutine(stream):
                    stream = await stream
                if isinstance(stream, AbstractAsyncContextManager):
                    async with stream as s:
                        async for chunk in s:
                            record_chunk(chunk, response_chunk_type)
                            yield chunk
                else:
                    async for chunk in stream:
                        record_chunk(chunk, response_chunk_type)
                        yield chunk

        wrapper_function = wrapper
        if response_chunk_type and is_async:
            wrapper_function = wrapper_generator_async
        elif response_type and is_async:
            wrapper_function = wrapper_async
        elif response_chunk_type:
            wrapper_function = wrapper_generator
        elif response_type:
            wrapper_function = wrapper
        else:
            raise ValueError("No response type or chunk type provided")

        return observe(name=fn.__name__)(wrapper_function)

    return mirascope_langfuse_decorator


def handle_before_call(self: BaseModel, fn, *args, **kwargs):
    """Adds metadata to the Mirascope Langfuse observation."""
    class_vars = get_class_vars(self)
    langfuse_context.update_current_observation(
        name=self.__class__.__name__,
        input=class_vars.pop("prompt_template", None),
        metadata=class_vars,
        tags=class_vars.pop("tags", []),
    )
    return langfuse_context


def handle_after_call(cls, fn, result, before_call: LangfuseDecorator, **kwargs):
    """Adds the response to the Mirascope Langfuse observation."""
    before_call.update_current_observation(output=result)


@overload
def with_langfuse(cls: Type[BaseCallT]) -> Type[BaseCallT]:
    ...  # pragma: no cover


@overload
def with_langfuse(
    cls: Type[BaseExtractorT],
) -> Type[BaseExtractorT]:
    ...  # pragma: no cover


@overload
def with_langfuse(
    cls: Type[BaseVectorStoreT],
) -> Type[BaseVectorStoreT]:
    ...  # pragma: no cover


@overload
def with_langfuse(
    cls: Type[BaseChunkerT],
) -> Type[BaseChunkerT]:
    ...  # pragma: no cover


@overload
def with_langfuse(
    cls: Type[BaseEmbedderT],
) -> Type[BaseEmbedderT]:
    ...  # pragma: no cover


def with_langfuse(cls):
    """Wraps base classes to automatically use langfuse.

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
    wrap_mirascope_class_functions(
        cls,
        handle_before_call=handle_before_call,
        handle_after_call=handle_after_call,
        decorator=observe(),
    )
    if cls._provider and cls._provider == "openai":
        cls.configuration = cls.configuration.model_copy(
            update={
                "client_wrappers": [
                    *cls.configuration.client_wrappers,
                    "langfuse",
                ]
            }
        )
    else:
        cls.configuration = cls.configuration.model_copy(
            update={
                "llm_ops": [
                    *cls.configuration.llm_ops,
                    mirascope_langfuse_generation(),
                ]
            }
        )
    return cls
