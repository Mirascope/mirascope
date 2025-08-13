"""Responses that stream content from LLMs."""

from collections.abc import AsyncIterator, Awaitable, Iterator, Sequence
from typing import TYPE_CHECKING, Any, Generic, Literal, TypeAlias, overload

from ..content import (
    AssistantContentChunk,
    AssistantContentPart,
    Text,
    TextChunk,
    TextEndChunk,
    TextStartChunk,
    Thinking,
    ThinkingChunk,
    ThinkingEndChunk,
    ThinkingStartChunk,
    ToolCall,
    ToolCallChunk,
    ToolCallEndChunk,
    ToolCallStartChunk,
)
from ..formatting import FormatT, Partial
from ..messages import AssistantMessage, Message
from ..streams import AsyncStream, Stream, StreamT
from .base_response import BaseResponse

if TYPE_CHECKING:
    from ..clients import Model, Provider


ChunkWithRaw: TypeAlias = tuple[AssistantContentChunk, Any]
"""A chunk paired with its raw provider data."""

ChunkIterator: TypeAlias = Iterator[ChunkWithRaw]
"""Synchronous iterator yielding chunks with raw data."""

AsyncChunkIterator: TypeAlias = AsyncIterator[ChunkWithRaw]
"""Asynchronous iterator yielding chunks with raw data."""


class StreamResponse(BaseResponse[FormatT], Generic[StreamT, FormatT]):
    """A StreamResponse wraps response content from the LLM with a streaming interface.

    This class is generic over both the stream type (StreamT) and format type (FormatT).
    The StreamT parameter determines whether streaming is synchronous or asynchronous:
    - StreamResponse[Stream, FormatT] for synchronous streaming
    - StreamResponse[AsyncStream, FormatT] for asynchronous streaming

    This class supports iteration to process chunks as they arrive from the model.

    Content can be streamed in one of three ways:
    - Via `response.streams()`, which provides an iterator of streams, where each
      stream contains chunks of streamed data. The chunks contain `delta`s (new content
      in that particular chunk), and the stream itself accumulates the collected state
      of all the chunks processed thus far.
    - Via `response.pretty_stream()` a helper method which provides all response content
      as `str` deltas. Iterating through `pretty_stream` will yield text content and
      optionally placeholder representations for other content types, but it will still consume the full stream.
    - Via `response.structured_stream()`, a helper method which provides partial
      structured outputs from a response (useful when FormatT is set). Iterating through
      `structured_stream` will only yield structured partials, but it will still consume
      the full stream.
    - Via `response.chunk_stream()` which allows iterating over the underlying chunk
      representation, without being organized into streams for content part streams for
      convenience.

    As chunks are consumed, they are collected in-memory on the StreamResponse, and they
    become available in `response.content`, `response.messages`, `response.tool_calls`,
    etc. All of the stream iterators can be replayed after the stream has been consumed,
    in which case they will yield chunks from memory in the original sequence that
    came from the LLM. If the stream is only partially consumed, a fresh iterator will
    first iterate through in-memory content, and then will continue consuming fresh
    chunks from the LLM.

    In the specific case of text chunks, they are included in the response content as soon
    as they become available, via an `llm.Text` part that updates as more deltas come in.
    This enables the behavior where resuming a partially-streamed response will include
    as much text as the model generated.

    For other chunks, like `Thinking` or `ToolCall`, they are only added to response
    content once the corresponding part has fully streamed. This avoids issues like
    adding incomplete tool calls, or thinking blocks missing signatures, to the response.

    For each iterator, fully iterating through the iterator will consume the whole
    LLM stream, such that `finish_reason` will be set (not None). You can pause stream
    execution midway by breaking out of the iterator.

    Here is an example showing semantics for breaking midway through a stream:
    ```python
    # First iteration - stream until we hit a tool call, then break
    stream_count = 0
    for stream in response.streams():
        stream_count += 1
        print(f"First pass: Stream {stream_count} - {stream.type}")
        if stream.content_type == "tool_call":
            break  # Break after seeing tool call stream

    # Second iteration - replays from memory, then continues if more data available
    stream_count = 0
    for stream in response.streams():
        stream_count += 1
        print(f"Second pass: Stream {stream_count} - {stream.type}")

    # Output might be:
    # > First pass: Stream 1 - thinking_stream
    # > First pass: Stream 2 - tool_call_stream
    # > Second pass: Stream 1 - thinking_stream
    # > Second pass: Stream 2 - tool_call_stream
    # > Second pass: Stream 3 - text_stream
    ```

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

    raw: Sequence[Any]
    """The raw chunks from the LLM."""

    chunks: Sequence[AssistantContentChunk]
    """All of the raw chunks consumed from the stream."""

    content: Sequence[AssistantContentPart]
    """The content generated by the LLM.
    
    Content is updated in this array as it is consumed by the stream. Text content will 
    update with each text chunk (this will mutate the Text object that is returned 
    rather than creating a new one). Other content will be added once each part
    is fully streamed.
    """

    messages: list[Message]
    """The message history, including the most recent assistant message.

    The most recent assistant message will have all of the completed content that has 
    already been consumed from the stream. Text content will be included as each chunk 
    is processed; other content will be included only when its corresponding part is 
    completed (to avoid partial tool calls and the like). If no content has been 
    streamed, then the final assistant message will be present (to maintain turn order 
    expectations), but will be empty.
    """

    texts: Sequence[Text]
    """The text content in the generated response, if any.
    
    Text content updates with each text chunk as it streams. The Text objects are 
    mutated in place rather than creating new ones for each chunk.
    """

    tool_calls: Sequence[ToolCall]
    """The tools the LLM wants called on its behalf, if any.
    
    Tool calls are only added to this sequence once they have been fully streamed 
    to avoid partial tool calls in the response.
    """

    thinkings: Sequence[Thinking]
    """The thinking content in the generated response, if any.
    
    Thinking content is only added to this sequence once it has been fully streamed 
    to avoid partial thinking blocks in the response.
    """

    consumed: bool = False
    """Whether the stream has been fully consumed.
    
    This is True after all chunks have been processed from the underlying iterator.
    When False, more content may be available by calling the stream methods.
    """

    def __init__(
        self,
        *,
        provider: "Provider",
        model: "Model",
        input_messages: Sequence[Message],
        chunk_iterator: ChunkIterator | AsyncChunkIterator,
    ) -> None:
        """Initialize the StreamResponse.

        Args:
            provider: The provider name (e.g., "anthropic", "openai")
            model: The model identifier
            input_messages: The input messages that were sent to the LLM
            chunk_iterator: Iterator that yields (AssistantContentChunk, raw_data) tuples

        The StreamResponse will process the tuples to build the chunks and raw lists
        as the stream is consumed.
        """

        self.provider = provider
        self.model = model

        # Internal-only lists which we mutate (append) during chunk processing
        self._chunks: list[AssistantContentChunk] = []
        self._content: list[AssistantContentPart] = []
        self._texts: list[Text] = []
        self._thinkings: list[Thinking] = []
        self._tool_calls: list[ToolCall] = []
        self._raw: list[Any] = []
        self._last_raw_chunk: Any | None = None

        # Externally-facing references typed as immutable Sequences
        self.chunks = self._chunks
        self.content = self._content
        self.texts = self._texts
        self.thinkings = self._thinkings
        self.tool_calls = self._tool_calls
        self.raw = self._raw

        self.finish_reason = None  # TODO: Add support for finish reason to chunks

        self.messages = list(input_messages) + [AssistantMessage(content=self._content)]

        self._current_content: Text | Thinking | ToolCall | None = None
        self._chunk_iterator = chunk_iterator

    @overload
    def pretty_stream(self: "StreamResponse[Stream, FormatT]") -> Iterator[str]:
        """Returns a sync string iterator over response content."""

    @overload
    def pretty_stream(
        self: "StreamResponse[AsyncStream, FormatT]",
    ) -> Awaitable[AsyncIterator[str]]:
        """Returns an async string iterator over response content."""

    def pretty_stream(
        self, include_content_placeholders: bool = True
    ) -> Iterator[str] | Awaitable[AsyncIterator[str]]:
        """Returns an iterator over string chunks containing all response content.

        The return type depends on the StreamT generic parameter:
        - For StreamResponse[Stream, FormatT]: returns Iterator[str] (synchronous iterator)
        - For StreamResponse[AsyncStream, FormatT]: returns Awaitable[AsyncIterator[str]]

        Fully iterating through this iterator will fully consume the underlying stream,
        updating the Response with all collected content (Text and other).

        When called, pretty_stream always returns a fresh iterator that replays
        chunks starting at the beginning of the stream.
        """
        raise NotImplementedError()

    @overload
    def streams(self: "StreamResponse[Stream, FormatT]") -> Iterator[Stream]:
        """Overload for synchronous streaming."""
        ...

    @overload
    def streams(
        self: "StreamResponse[AsyncStream, FormatT]",
    ) -> Awaitable[AsyncIterator[AsyncStream]]:
        """Overload for asynchronous streaming."""
        ...

    def streams(self) -> Iterator[Stream] | Awaitable[AsyncIterator[AsyncStream]]:
        """Returns an iterator that yields streams for each content part in the response.

        The return type depends on the StreamT generic parameter:
        - For StreamResponse[Stream, FormatT]: returns Iterator[Stream] (synchronous)
        - For StreamResponse[AsyncStream, FormatT]: returns Awaitable[AsyncIterator[AsyncStream]]

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

    @overload
    def chunk_stream(
        self: "StreamResponse[Stream, FormatT]",
    ) -> Iterator[AssistantContentChunk]:
        """Returns a sync iterator over content chunks."""
        ...

    @overload
    def chunk_stream(
        self: "StreamResponse[AsyncStream, FormatT]",
    ) -> Awaitable[AsyncIterator[AssistantContentChunk]]:
        """Returns an async iterator over content chunks."""
        ...

    def chunk_stream(
        self,
    ) -> (
        Iterator[AssistantContentChunk]
        | Awaitable[AsyncIterator[AssistantContentChunk]]
    ):
        """Returns an iterator that yields content chunks as they are received.

        The return type depends on the StreamT generic parameter:
        - For StreamResponse[Stream, FormatT]: returns Iterator[AssistantContentChunk] (synchronous)
        - For StreamResponse[AsyncStream, FormatT]: returns Awaitable[AsyncIterator[AssistantContentChunk]]

        This provides access to the Mirascope chunk data including start, delta, and end chunks
        for each content type (text, thinking, tool_call). Unlike the streams() method
        that groups chunks by content part, this yields individual chunks as they arrive.

        Fully iterating through this iterator will fully consume the underlying stream,
        updating the Response with all collected content.

        As chunks are consumed, they are cached on the StreamResponse. If a new iterator
        is constructed via calling `chunks()`, it will start by replaying the cached
        chunks from the response, and (if there is still more content to consume from
        the LLM), it will proceed to consume it once it has iterated through all the
        cached chunks.
        """
        if isinstance(self._chunk_iterator, Iterator):
            return self._sync_chunk_stream()
        else:
            return self._async_chunk_stream()

    def _handle_chunk(self, chunk: AssistantContentChunk, raw_chunk: Any) -> None:  # noqa: ANN401
        if self.finish_reason is not None:
            raise RuntimeError(
                f"Stream already finished with reason: {self.finish_reason}"
            )
        if chunk.type == "finish_reason_chunk":
            self.finish_reason = chunk.finish_reason
        elif chunk.content_type == "text":
            self._handle_text_chunk(chunk)
        elif chunk.content_type == "thinking":
            self._handle_thinking_chunk(chunk)
        elif chunk.content_type == "tool_call":
            self._handle_tool_call_chunk(chunk)
        else:
            raise NotImplementedError

        self._chunks.append(chunk)
        if self._last_raw_chunk is not raw_chunk:
            self._raw.append(raw_chunk)
            self._last_raw_chunk = raw_chunk

    def _handle_text_chunk(
        self, chunk: TextStartChunk | TextChunk | TextEndChunk
    ) -> None:
        if chunk.type == "text_start_chunk":
            if self._current_content:
                raise RuntimeError(
                    "Received text_start_chunk while processing another chunk"
                )
            self._current_content = Text(text="")
            # Text gets included in content even when unfinished.
            self._content.append(self._current_content)
            self._texts.append(self._current_content)

        elif chunk.type == "text_chunk":
            if self._current_content is None or self._current_content.type != "text":
                raise RuntimeError("Received text_chunk while not processing text.")
            self._current_content.text += chunk.delta

        elif chunk.type == "text_end_chunk":
            if self._current_content is None or self._current_content.type != "text":
                raise RuntimeError("Received text_end_chunk while not processing text.")
            self._current_content = None

    def _handle_thinking_chunk(
        self, chunk: ThinkingStartChunk | ThinkingChunk | ThinkingEndChunk
    ) -> None:
        if chunk.type == "thinking_start_chunk":
            if self._current_content:
                raise RuntimeError(
                    "Received thinking_start_chunk while processing another chunk"
                )
            new_thinking = Thinking(thinking="", signature=None)
            self._current_content = new_thinking

        elif chunk.type == "thinking_chunk":
            if (
                self._current_content is None
                or self._current_content.type != "thinking"
            ):
                raise RuntimeError(
                    "Received thinking_chunk while not processing thinking."
                )
            self._current_content.thinking += chunk.delta

        elif chunk.type == "thinking_end_chunk":
            if (
                self._current_content is None
                or self._current_content.type != "thinking"
            ):
                raise RuntimeError(
                    "Received thinking_end_chunk while not processing thinking."
                )
            # Only add to content and thinkings when complete
            self._current_content.signature = chunk.signature
            self._content.append(self._current_content)
            self._thinkings.append(self._current_content)
            self._current_content = None

    def _handle_tool_call_chunk(
        self, chunk: ToolCallStartChunk | ToolCallChunk | ToolCallEndChunk
    ) -> None:
        if chunk.type == "tool_call_start_chunk":
            if self._current_content:
                raise RuntimeError(
                    "Received tool_call_start_chunk while processing another chunk"
                )
            self._current_content = ToolCall(
                id=chunk.id,
                name=chunk.name,
                args="",
            )

        elif chunk.type == "tool_call_chunk":
            if (
                self._current_content is None
                or self._current_content.type != "tool_call"
            ):
                raise RuntimeError(
                    "Received tool_call_chunk while not processing tool call."
                )
            self._current_content.args += chunk.delta

        elif chunk.type == "tool_call_end_chunk":
            if (
                self._current_content is None
                or self._current_content.type != "tool_call"
            ):
                raise RuntimeError(
                    "Received tool_call_end_chunk while not processing tool call."
                )
            if not self._current_content.args:
                self._current_content.args = "{}"
            self._content.append(self._current_content)
            self._tool_calls.append(self._current_content)
            self._current_content = None

    def _sync_chunk_stream(self) -> Iterator[AssistantContentChunk]:
        """Synchronous implementation of chunk_stream."""
        if not isinstance(self._chunk_iterator, Iterator):
            raise TypeError(
                "Expected Iterator for synchronous streaming"
            )  # pragma: no cover

        for chunk in self.chunks:
            yield chunk

        if self.consumed:
            return

        for chunk, raw_chunk in self._chunk_iterator:
            self._handle_chunk(chunk, raw_chunk)

            yield chunk

        self.consumed = True

    async def _async_chunk_stream(
        self,
    ) -> AsyncIterator[AssistantContentChunk]:
        """Asynchronous implementation of chunk_stream."""

        async def generator() -> AsyncIterator[AssistantContentChunk]:
            if isinstance(self._chunk_iterator, Iterator):
                raise TypeError(
                    "Expected AsyncIterator for asynchronous streaming"
                )  # pragma: no cover

            for chunk in self.chunks:
                yield chunk

            if self.consumed:
                return

            async for chunk, raw_chunk in self._chunk_iterator:
                self._handle_chunk(chunk, raw_chunk)
                yield chunk

            self.consumed = True

        return generator()

    @overload
    def structured_stream(
        self: "StreamResponse[Stream, FormatT]",
    ) -> Iterator[Partial[FormatT]]:
        """Overload for synchronous structured streaming."""
        ...

    @overload
    def structured_stream(
        self: "StreamResponse[AsyncStream, FormatT]",
    ) -> Awaitable[AsyncIterator[Partial[FormatT]]]:
        """Overload for asynchronous structured streaming."""
        ...

    def structured_stream(
        self,
    ) -> Iterator[Partial[FormatT]] | Awaitable[AsyncIterator[Partial[FormatT]]]:
        """Returns an iterator that yields partial structured objects as content streams.

        The return type depends on the StreamT generic parameter:
        - For StreamResponse[Stream, FormatT]: returns Iterator[Partial[FormatT]] (synchronous)
        - For StreamResponse[AsyncStream, FormatT]: returns Awaitable[AsyncIterator[Partial[FormatT]]]

        This method yields Partial[FormatT] objects as the response content is streamed,
        allowing you to access partial structured data before the response is fully complete.
        Each yielded object represents the current state of the parsed structure with all
        fields optional.

        Fully iterating through this iterator will fully consume the underlying stream,
        updating the Response with all collected content.
        """
        raise NotImplementedError()

    @overload
    def format(self, partial: Literal[True]) -> Partial[FormatT]:
        """Format the response into a Partial[BaseModel] (with optional fields).

        This is useful for when the stream is only partially consumed, in which case the
        structured output may only be partially available.
        """
        ...

    @overload
    def format(self, partial: Literal[False] = False) -> FormatT:
        """Format the response into a Pydantic BaseModel."""
        ...

    def format(self, partial: bool = False) -> FormatT | Partial[FormatT]:
        """Format the response according to the response format parser.

        It will parse the response content according to the specified format (if present)
        and return a structured object. Returns None if there was no format.

        When called with `partial=True`, it will return a partial of the model, with all
        fields optional.

        Returns:
            The formatted response object of type T.

        Raises:
            ValueError: If the response cannot be formatted according to the
                specified format.
        """
        raise NotImplementedError()
