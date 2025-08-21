"""StreamResponse and AsyncStreamResponse to stream content from LLMs."""

from typing import Generic

from ..context import DepsT
from ..formatting import FormatT
from ..tools import AsyncContextToolkit, AsyncToolkit, ContextToolkit, Toolkit
from .base_stream_response import BaseAsyncStreamResponse, BaseSyncStreamResponse


class StreamResponse(BaseSyncStreamResponse[Toolkit, FormatT]):
    """A `StreamResponse` wraps response content from the LLM with a streaming interface.

    This class supports iteration to process chunks as they arrive from the model.

    Content can be streamed in one of three ways:
    - Via `.streams()`, which provides an iterator of streams, where each
      stream contains chunks of streamed data. The chunks contain `delta`s (new content
      in that particular chunk), and the stream itself accumulates the collected state
      of all the chunks processed thus far.
    - Via `.chunk_stream()` which allows iterating over Mirascope's provider-
      agnostic chunk representation.
    - Via `.pretty_stream()` a helper method which provides all response content
      as `str` deltas. Iterating through `pretty_stream` will yield text content and
      optionally placeholder representations for other content types, but it will still
      consume the full stream.
    - Via `.structured_stream()`, a helper method which provides partial
      structured outputs from a response (useful when FormatT is set). Iterating through
      `structured_stream` will only yield structured partials, but it will still consume
      the full stream.

    As chunks are consumed, they are collected in-memory on the `StreamResponse`, and they
    become available in `.content`, `.messages`, `.tool_calls`, etc. All of the stream
    iterators can be restarted after the stream has been consumed, in which case they
    will yield chunks from memory in the original sequence that came from the LLM. If
    the stream is only partially consumed, a fresh iterator will first iterate through
    in-memory content, and then will continue consuming fresh chunks from the LLM.

    In the specific case of text chunks, they are included in the response content as soon
    as they become available, via an `llm.Text` part that updates as more deltas come in.
    This enables the behavior where resuming a partially-streamed response will include
    as much text as the model generated.

    For other chunks, like `Thinking` or `ToolCall`, they are only added to response
    content once the corresponding part has fully streamed. This avoids issues like
    adding incomplete tool calls, or thinking blocks missing signatures, to the response.

    For each iterator, fully iterating through the iterator will consume the whole
    LLM stream. You can pause stream execution midway by breaking out of the iterator,
    and you can safely resume execution from the same iterator if desired.


    Example:
        ```python
        from mirascope import llm

        @llm.call(
            provider="openai",
            model="gpt-4o-mini",
        )
        def answer_question(question: str) -> str:
            return f"Answer this question: {question}"

        stream_response = answer_question.stream("What is the capital of France?")

        for chunk in stream_response.pretty_stream():
            print(chunk, end="", flush=True)
        print()
        ```
    """


class AsyncStreamResponse(BaseAsyncStreamResponse[AsyncToolkit, FormatT]):
    """An `AsyncStreamResponse` wraps response content from the LLM with a streaming interface.

    This class supports iteration to process chunks as they arrive from the model.

    Content can be streamed in one of three ways:
    - Via `.streams()`, which provides an iterator of streams, where each
      stream contains chunks of streamed data. The chunks contain `delta`s (new content
      in that particular chunk), and the stream itself accumulates the collected state
      of all the chunks processed thus far.
    - Via `.chunk_stream()` which allows iterating over Mirascope's provider-
      agnostic chunk representation.
    - Via `.pretty_stream()` a helper method which provides all response content
      as `str` deltas. Iterating through `pretty_stream` will yield text content and
      optionally placeholder representations for other content types, but it will still
      consume the full stream.
    - Via `.structured_stream()`, a helper method which provides partial
      structured outputs from a response (useful when FormatT is set). Iterating through
      `structured_stream` will only yield structured partials, but it will still consume
      the full stream.

    As chunks are consumed, they are collected in-memory on the `AsyncContextStreamResponse`, and they
    become available in `.content`, `.messages`, `.tool_calls`, etc. All of the stream
    iterators can be restarted after the stream has been consumed, in which case they
    will yield chunks from memory in the original sequence that came from the LLM. If
    the stream is only partially consumed, a fresh iterator will first iterate through
    in-memory content, and then will continue consuming fresh chunks from the LLM.

    In the specific case of text chunks, they are included in the response content as soon
    as they become available, via an `llm.Text` part that updates as more deltas come in.
    This enables the behavior where resuming a partially-streamed response will include
    as much text as the model generated.

    For other chunks, like `Thinking` or `ToolCall`, they are only added to response
    content once the corresponding part has fully streamed. This avoids issues like
    adding incomplete tool calls, or thinking blocks missing signatures, to the response.

    For each iterator, fully iterating through the iterator will consume the whole
    LLM stream. You can pause stream execution midway by breaking out of the iterator,
    and you can safely resume execution from the same iterator if desired.


    Example:
        ```python
        from mirascope import llm

        @llm.call(
            provider="openai",
            model="gpt-4o-mini",
        )
        async def answer_question(question: str) -> str:
            return f"Answer this question: {question}"

        stream_response = await answer_question.stream("What is the capital of France?")

        async for chunk in stream_response.pretty_stream():
            print(chunk, end="", flush=True)
        print()
        ```
    """


class ContextStreamResponse(
    BaseSyncStreamResponse[ContextToolkit, FormatT], Generic[DepsT, FormatT]
):
    """A `ContextStreamResponse` wraps response content from the LLM with a streaming interface.

    This class supports iteration to process chunks as they arrive from the model.

    Content can be streamed in one of three ways:
    - Via `.streams()`, which provides an iterator of streams, where each
      stream contains chunks of streamed data. The chunks contain `delta`s (new content
      in that particular chunk), and the stream itself accumulates the collected state
      of all the chunks processed thus far.
    - Via `.chunk_stream()` which allows iterating over Mirascope's provider-
      agnostic chunk representation.
    - Via `.pretty_stream()` a helper method which provides all response content
      as `str` deltas. Iterating through `pretty_stream` will yield text content and
      optionally placeholder representations for other content types, but it will still
      consume the full stream.
    - Via `.structured_stream()`, a helper method which provides partial
      structured outputs from a response (useful when FormatT is set). Iterating through
      `structured_stream` will only yield structured partials, but it will still consume
      the full stream.

    As chunks are consumed, they are collected in-memory on the `ContextStreamResponse`, and they
    become available in `.content`, `.messages`, `.tool_calls`, etc. All of the stream
    iterators can be restarted after the stream has been consumed, in which case they
    will yield chunks from memory in the original sequence that came from the LLM. If
    the stream is only partially consumed, a fresh iterator will first iterate through
    in-memory content, and then will continue consuming fresh chunks from the LLM.

    In the specific case of text chunks, they are included in the response content as soon
    as they become available, via an `llm.Text` part that updates as more deltas come in.
    This enables the behavior where resuming a partially-streamed response will include
    as much text as the model generated.

    For other chunks, like `Thinking` or `ToolCall`, they are only added to response
    content once the corresponding part has fully streamed. This avoids issues like
    adding incomplete tool calls, or thinking blocks missing signatures, to the response.

    For each iterator, fully iterating through the iterator will consume the whole
    LLM stream. You can pause stream execution midway by breaking out of the iterator,
    and you can safely resume execution from the same iterator if desired.


    Example:
        ```python
        from mirascope import llm

        @llm.call(
            provider="openai",
            model="gpt-4o-mini",
        )
        def answer_question(question: str) -> str:
            return f"Answer this question: {question}"

        stream_response = answer_question.stream("What is the capital of France?")

        for chunk in stream_response.pretty_stream():
            print(chunk, end="", flush=True)
        print()
        ```
    """


class AsyncContextStreamResponse(
    BaseAsyncStreamResponse[AsyncContextToolkit, FormatT], Generic[DepsT, FormatT]
):
    """An `AsyncContextStreamResponse` wraps response content from the LLM with a streaming interface.

    This class supports iteration to process chunks as they arrive from the model.

    Content can be streamed in one of three ways:
    - Via `.streams()`, which provides an iterator of streams, where each
      stream contains chunks of streamed data. The chunks contain `delta`s (new content
      in that particular chunk), and the stream itself accumulates the collected state
      of all the chunks processed thus far.
    - Via `.chunk_stream()` which allows iterating over Mirascope's provider-
      agnostic chunk representation.
    - Via `.pretty_stream()` a helper method which provides all response content
      as `str` deltas. Iterating through `pretty_stream` will yield text content and
      optionally placeholder representations for other content types, but it will still
      consume the full stream.
    - Via `.structured_stream()`, a helper method which provides partial
      structured outputs from a response (useful when FormatT is set). Iterating through
      `structured_stream` will only yield structured partials, but it will still consume
      the full stream.

    As chunks are consumed, they are collected in-memory on the `AsyncContextStreamResponse`, and they
    become available in `.content`, `.messages`, `.tool_calls`, etc. All of the stream
    iterators can be restarted after the stream has been consumed, in which case they
    will yield chunks from memory in the original sequence that came from the LLM. If
    the stream is only partially consumed, a fresh iterator will first iterate through
    in-memory content, and then will continue consuming fresh chunks from the LLM.

    In the specific case of text chunks, they are included in the response content as soon
    as they become available, via an `llm.Text` part that updates as more deltas come in.
    This enables the behavior where resuming a partially-streamed response will include
    as much text as the model generated.

    For other chunks, like `Thinking` or `ToolCall`, they are only added to response
    content once the corresponding part has fully streamed. This avoids issues like
    adding incomplete tool calls, or thinking blocks missing signatures, to the response.

    For each iterator, fully iterating through the iterator will consume the whole
    LLM stream. You can pause stream execution midway by breaking out of the iterator,
    and you can safely resume execution from the same iterator if desired.


    Example:
        ```python
        from mirascope import llm

        @llm.call(
            provider="openai",
            model="gpt-4o-mini",
        )
        async def answer_question(question: str) -> str:
            return f"Answer this question: {question}"

        stream_response = await answer_question.stream("What is the capital of France?")

        async for chunk in stream_response.pretty_stream():
            print(chunk, end="", flush=True)
        print()
        ```
    """
