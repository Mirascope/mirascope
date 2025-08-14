"""StreamResponse and AsyncStreamResponse to stream content from LLMs."""

from collections.abc import AsyncIterator, Iterator
from typing import TYPE_CHECKING

from ..content import (
    AssistantContentChunk,
)
from ..formatting import FormatT, Partial
from ..streams import AsyncStream, Stream
from .base_stream_response import AsyncChunkIterator, BaseStreamResponse, ChunkIterator

if TYPE_CHECKING:
    pass


class StreamResponse(BaseStreamResponse[ChunkIterator, FormatT]):
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

    def streams(self) -> Iterator[Stream]:
        """Returns an iterator that yields streams for each content part in the response.

        Returns:
            Iterator[Stream]: Synchronous iterator yielding Stream objects

        Each content part in the response will correspond to one stream, which will yield
        chunks of content as they come in from the underlying LLM.

        Fully iterating through this iterator will fully consume the underlying stream,
        updating the Response with all collected content.

        As content is consumed, it is cached on the StreamResponse. If a new iterator
        is constructed via calling `streams()`, it will start by replaying the cached
        content from the response, and (if there is still more content to consume from
        the LLM), it will proceed to consume it once it has iterated through all the
        cached chunks.
        """
        raise NotImplementedError()

    def chunk_stream(
        self,
    ) -> Iterator[AssistantContentChunk]:
        """Returns an iterator that yields content chunks as they are received.

        Returns:
            Iterator[AssistantContentChunk]: Synchronous iterator yielding chunks

        This provides access to the Mirascope chunk data including start, delta, and end chunks
        for each content type (text, thinking, tool_call). Unlike the streams() method
        that groups chunks by content part, this yields individual chunks as they arrive.

        Fully iterating through this iterator will fully consume the underlying stream,
        updating the Response with all collected content.

        As chunks are consumed, they are cached on the StreamResponse. If a new iterator
        is constructed via calling `chunk_stream()`, it will start by replaying the cached
        chunks from the response, and (if there is still more content to consume from
        the LLM), it will proceed to consume it once it has iterated through all the
        cached chunks.
        """
        for chunk in self.chunks:
            yield chunk

        if self.consumed:
            return

        for chunk in self._chunk_iterator:
            if chunk.type == "raw_chunk":
                self._raw.append(chunk.raw)
            else:
                self._handle_chunk(chunk)
                yield chunk

        self.consumed = True

    def pretty_stream(self, include_content_placeholders: bool = True) -> Iterator[str]:
        """Returns an iterator over string chunks containing all response content.

        Args:
            include_content_placeholders: Whether to include placeholders for non-text content

        Returns:
            Iterator[str]: Synchronous iterator yielding string chunks

        Fully iterating through this iterator will fully consume the underlying stream,
        updating the Response with all collected content (Text and other).

        When called, pretty_stream always returns a fresh iterator that replays
        chunks starting at the beginning of the stream.
        """
        raise NotImplementedError()

    def structured_stream(
        self,
    ) -> Iterator[Partial[FormatT]]:
        """Returns an iterator that yields partial structured objects as content streams.

        Returns:
            Iterator[Partial[FormatT]]: Synchronous iterator yielding partial structured objects

        This method yields Partial[FormatT] objects as the response content is streamed,
        allowing you to access partial structured data before the response is fully complete.
        Each yielded object represents the current state of the parsed structure with all
        fields optional.

        Fully iterating through this iterator will fully consume the underlying stream,
        updating the Response with all collected content.
        """
        raise NotImplementedError()


class AsyncStreamResponse(BaseStreamResponse[AsyncChunkIterator, FormatT]):
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

    As chunks are consumed, they are collected in-memory on the `AsyncStreamResponse`, and they
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

    async def streams(self) -> AsyncIterator[AsyncStream]:
        """Returns an async iterator that yields streams for each content part in the response.

        Returns:
            AsyncIterator[AsyncStream]: Async iterator yielding AsyncStream objects

        Each content part in the response will correspond to one stream, which will yield
        chunks of content as they come in from the underlying LLM.

        Fully iterating through this iterator will fully consume the underlying stream,
        updating the Response with all collected content.

        As content is consumed, it is cached on the AsyncStreamResponse. If a new iterator
        is constructed via calling `streams()`, it will start by replaying the cached
        content from the response, and (if there is still more content to consume from
        the LLM), it will proceed to consume it once it has iterated through all the
        cached chunks.
        """
        raise NotImplementedError()

    async def chunk_stream(
        self,
    ) -> AsyncIterator[AssistantContentChunk]:
        """Returns an async iterator that yields content chunks as they are received.

        Returns:
            AsyncIterator[AssistantContentChunk]: Async iterator yielding chunks

        This provides access to the Mirascope chunk data including start, delta, and end chunks
        for each content type (text, thinking, tool_call). Unlike the streams() method
        that groups chunks by content part, this yields individual chunks as they arrive.

        Fully iterating through this iterator will fully consume the underlying stream,
        updating the Response with all collected content.

        As chunks are consumed, they are cached on the AsyncStreamResponse. If a new iterator
        is constructed via calling `chunk_stream()`, it will start by replaying the cached
        chunks from the response, and (if there is still more content to consume from
        the LLM), it will proceed to consume it once it has iterated through all the
        cached chunks.
        """

        for chunk in self.chunks:
            yield chunk

        if self.consumed:
            return

        async for chunk in self._chunk_iterator:
            if chunk.type == "raw_chunk":
                self._raw.append(chunk.raw)
            else:
                self._handle_chunk(chunk)
                yield chunk

        self.consumed = True

    def pretty_stream(
        self, include_content_placeholders: bool = True
    ) -> AsyncIterator[str]:
        """Returns an async iterator over string chunks containing all response content.

        Args:
            include_content_placeholders: Whether to include placeholders for non-text content

        Returns:
            AsyncIterator[str]: Async iterator yielding string chunks

        Fully iterating through this iterator will fully consume the underlying stream,
        updating the Response with all collected content (Text and other).

        When called, pretty_stream always returns a fresh iterator that replays
        chunks starting at the beginning of the stream.
        """
        raise NotImplementedError()

    def structured_stream(
        self,
    ) -> AsyncIterator[Partial[FormatT]]:
        """Returns an async iterator that yields partial structured objects as content streams.

        Returns:
            AsyncIterator[Partial[FormatT]]: Async iterator yielding partial structured objects

        This method yields Partial[FormatT] objects as the response content is streamed,
        allowing you to access partial structured data before the response is fully complete.
        Each yielded object represents the current state of the parsed structure with all
        fields optional.

        Fully iterating through this iterator will fully consume the underlying stream,
        updating the Response with all collected content.
        """
        raise NotImplementedError()
