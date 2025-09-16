"""StreamResponse and AsyncStreamResponse to stream content from LLMs."""

import asyncio
from collections.abc import Sequence
from typing import TYPE_CHECKING, Generic, overload

from ..content import ToolOutput
from ..context import Context, DepsT
from ..formatting import FormatT
from ..messages import Message, UserContent, user
from ..tools import (
    AsyncContextTool,
    AsyncContextToolkit,
    AsyncTool,
    AsyncToolkit,
    ContextTool,
    ContextToolkit,
    Tool,
    Toolkit,
)
from .base_stream_response import (
    AsyncChunkIterator,
    BaseAsyncStreamResponse,
    BaseSyncStreamResponse,
    ChunkIterator,
)

if TYPE_CHECKING:
    from ..clients import BaseParams, ModelId, Provider


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
            model_id="gpt-4o-mini",
        )
        def answer_question(question: str) -> str:
            return f"Answer this question: {question}"

        stream_response = answer_question.stream("What is the capital of France?")

        for chunk in stream_response.pretty_stream():
            print(chunk, end="", flush=True)
        print()
        ```
    """

    def __init__(
        self,
        *,
        provider: "Provider",
        model_id: "ModelId",
        params: "BaseParams | None",
        tools: Sequence[Tool] | None = None,
        format_type: type[FormatT] | None = None,
        input_messages: Sequence[Message],
        chunk_iterator: ChunkIterator,
    ) -> None:
        """Initialize a `StreamResponse`."""
        super().__init__(
            provider=provider,
            model_id=model_id,
            params=params,
            toolkit=Toolkit(tools=tools),
            format_type=format_type,
            input_messages=input_messages,
            chunk_iterator=chunk_iterator,
        )

    def execute_tools(self) -> Sequence[ToolOutput]:
        """Execute and return all of the tool calls in the response.

        Returns:
            A sequence containing a `ToolOutput` for every tool call in the order they appeared.

        Raises:
            ToolNotFoundError: If one of the response's tool calls has no matching tool.
            Exception: If one of the tools throws an exception.
        """
        return [self.toolkit.execute(tool_call) for tool_call in self.tool_calls]

    @overload
    def resume(self: "StreamResponse", content: UserContent) -> "StreamResponse": ...

    @overload
    def resume(
        self: "StreamResponse[FormatT]", content: UserContent
    ) -> "StreamResponse[FormatT]": ...

    def resume(
        self, content: UserContent
    ) -> "StreamResponse | StreamResponse[FormatT]":
        """Generate a new `StreamResponse` using this response's messages with additional user content.

        Uses this response's tools and format type. Also uses this response's provider,
        model, client, and params, unless the model context manager is being used to
        provide a new LLM as an override.

        Args:
            content: The new user message content to append to the message history.

        Returns:
            A new `StreamResponse` instance generated from the extended message history.
        """
        messages = self.messages + [user(content)]
        return self.model.stream(
            messages=messages, tools=self.toolkit.tools, format=self.format_type
        )


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
            model_id="gpt-4o-mini",
        )
        async def answer_question(question: str) -> str:
            return f"Answer this question: {question}"

        stream_response = await answer_question.stream("What is the capital of France?")

        async for chunk in stream_response.pretty_stream():
            print(chunk, end="", flush=True)
        print()
        ```
    """

    def __init__(
        self,
        *,
        provider: "Provider",
        model_id: "ModelId",
        params: "BaseParams | None",
        tools: Sequence[AsyncTool] | None = None,
        format_type: type[FormatT] | None = None,
        input_messages: Sequence[Message],
        chunk_iterator: AsyncChunkIterator,
    ) -> None:
        """Initialize an `AsyncStreamResponse`."""
        super().__init__(
            provider=provider,
            model_id=model_id,
            params=params,
            toolkit=AsyncToolkit(tools=tools),
            format_type=format_type,
            input_messages=input_messages,
            chunk_iterator=chunk_iterator,
        )

    async def execute_tools(self) -> Sequence[ToolOutput]:
        """Execute and return all of the tool calls in the response.

        Returns:
            A sequence containing a `ToolOutput` for every tool call in the order they appeared.

        Raises:
            ToolNotFoundError: If one of the response's tool calls has no matching tool.
            Exception: If one of the tools throws an exception.
        """
        tasks = [self.toolkit.execute(tool_call) for tool_call in self.tool_calls]
        return await asyncio.gather(*tasks)

    @overload
    async def resume(
        self: "AsyncStreamResponse", content: UserContent
    ) -> "AsyncStreamResponse": ...

    @overload
    async def resume(
        self: "AsyncStreamResponse[FormatT]", content: UserContent
    ) -> "AsyncStreamResponse[FormatT]": ...

    async def resume(
        self, content: UserContent
    ) -> "AsyncStreamResponse | AsyncStreamResponse[FormatT]":
        """Generate a new `AsyncStreamResponse` using this response's messages with additional user content.

        Uses this response's tools and format type. Also uses this response's provider,
        model, client, and params, unless the model context manager is being used to
        provide a new LLM as an override.

        Args:
            content: The new user message content to append to the message history.

        Returns:
            A new `AsyncStreamResponse` instance generated from the extended message history.
        """
        messages = self.messages + [user(content)]
        return await self.model.stream_async(
            messages=messages, tools=self.toolkit.tools, format=self.format_type
        )


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
            model_id="gpt-4o-mini",
        )
        def answer_question(ctx: llm.Context, question: str) -> str:
            return f"Answer this question: {question}"

        ctx = llm.Context()
        stream_response = answer_question.stream(ctx, "What is the capital of France?")

        for chunk in stream_response.pretty_stream():
            print(chunk, end="", flush=True)
        print()
        ```
    """

    def __init__(
        self,
        *,
        provider: "Provider",
        model_id: "ModelId",
        params: "BaseParams | None",
        tools: Sequence[Tool | ContextTool[DepsT]] | None = None,
        format_type: type[FormatT] | None = None,
        input_messages: Sequence[Message],
        chunk_iterator: ChunkIterator,
    ) -> None:
        """Initialize a `ContextStreamResponse`."""
        super().__init__(
            provider=provider,
            model_id=model_id,
            params=params,
            toolkit=ContextToolkit(tools=tools),
            format_type=format_type,
            input_messages=input_messages,
            chunk_iterator=chunk_iterator,
        )

    def execute_tools(self, ctx: Context[DepsT]) -> Sequence[ToolOutput]:
        """Execute and return all of the tool calls in the response.

        Args:
            ctx: A `Context` with the required deps type.

        Returns:
            A sequence containing a `ToolOutput` for every tool call.

        Raises:
            ToolNotFoundError: If one of the response's tool calls has no matching tool.
            Exception: If one of the tools throws an exception.
        """
        return [self.toolkit.execute(ctx, tool_call) for tool_call in self.tool_calls]

    @overload
    def resume(
        self: "ContextStreamResponse[DepsT]", ctx: Context[DepsT], content: UserContent
    ) -> "ContextStreamResponse[DepsT]": ...

    @overload
    def resume(
        self: "ContextStreamResponse[DepsT, FormatT]",
        ctx: Context[DepsT],
        content: UserContent,
    ) -> "ContextStreamResponse[DepsT, FormatT]": ...

    def resume(
        self, ctx: Context[DepsT], content: UserContent
    ) -> "ContextStreamResponse[DepsT] | ContextStreamResponse[DepsT, FormatT]":
        """Generate a new `ContextStreamResponse` using this response's messages with additional user content.

        Uses this response's tools and format type. Also uses this response's provider,
        model, client, and params, unless the model context manager is being used to
        provide a new LLM as an override.

        Args:
            ctx: A Context with the required deps type.
            content: The new user message content to append to the message history.

        Returns:
            A new `ContextStreamResponse` instance generated from the extended message history.
        """
        messages = self.messages + [user(content)]
        return self.model.context_stream(
            ctx=ctx,
            messages=messages,
            tools=self.toolkit.tools,
            format=self.format_type,
        )


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
            model_id="gpt-4o-mini",
        )
        async def answer_question(ctx: llm.Context, question: str) -> str:
            return f"Answer this question: {question}"

        ctx = llm.Context()
        stream_response = await answer_question.stream(ctx, "What is the capital of France?")

        async for chunk in stream_response.pretty_stream():
            print(chunk, end="", flush=True)
        print()
        ```
    """

    def __init__(
        self,
        *,
        provider: "Provider",
        model_id: "ModelId",
        params: "BaseParams | None",
        tools: Sequence[AsyncTool | AsyncContextTool[DepsT]] | None = None,
        format_type: type[FormatT] | None = None,
        input_messages: Sequence[Message],
        chunk_iterator: AsyncChunkIterator,
    ) -> None:
        """Initialize an `AsyncContextStreamResponse`."""
        super().__init__(
            provider=provider,
            model_id=model_id,
            params=params,
            toolkit=AsyncContextToolkit(tools=tools),
            format_type=format_type,
            input_messages=input_messages,
            chunk_iterator=chunk_iterator,
        )

    async def execute_tools(self, ctx: Context[DepsT]) -> Sequence[ToolOutput]:
        """Execute and return all of the tool calls in the response.

        Args:
            ctx: A `Context` with the required deps type.

        Returns:
            A sequence containing a `ToolOutput` for every tool call in the order they appeared.

        Raises:
            ToolNotFoundError: If one of the response's tool calls has no matching tool.
            Exception: If one of the tools throws an exception.
        """
        tasks = [self.toolkit.execute(ctx, tool_call) for tool_call in self.tool_calls]
        return await asyncio.gather(*tasks)

    @overload
    async def resume(
        self: "AsyncContextStreamResponse[DepsT]",
        ctx: Context[DepsT],
        content: UserContent,
    ) -> "AsyncContextStreamResponse[DepsT]": ...

    @overload
    async def resume(
        self: "AsyncContextStreamResponse[DepsT, FormatT]",
        ctx: Context[DepsT],
        content: UserContent,
    ) -> "AsyncContextStreamResponse[DepsT, FormatT]": ...

    async def resume(
        self, ctx: Context[DepsT], content: UserContent
    ) -> (
        "AsyncContextStreamResponse[DepsT] | AsyncContextStreamResponse[DepsT, FormatT]"
    ):
        """Generate a new `AsyncContextStreamResponse` using this response's messages with additional user content.

        Uses this response's tools and format type. Also uses this response's provider,
        model, client, and params, unless the model context manager is being used to
        provide a new LLM as an override.

        Args:
            ctx: A Context with the required deps type.
            content: The new user message content to append to the message history.

        Returns:
            A new `AsyncContextStreamResponse` instance generated from the extended message history.
        """
        messages = self.messages + [user(content)]
        return await self.model.context_stream_async(
            ctx=ctx,
            messages=messages,
            tools=self.toolkit.tools,
            format=self.format_type,
        )
