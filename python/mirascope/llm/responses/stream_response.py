"""StreamResponse and AsyncStreamResponse to stream content from LLMs."""

import asyncio
from collections.abc import Sequence
from typing import TYPE_CHECKING, Generic, overload

from ..content import ToolOutput
from ..context import Context, DepsT
from ..exceptions import ParseError
from ..formatting import Format, FormattableT
from ..messages import Message, UserContent
from ..tools import (
    AsyncContextToolkit,
    AsyncContextTools,
    AsyncToolkit,
    AsyncTools,
    ContextToolkit,
    ContextTools,
    Toolkit,
    Tools,
)
from ..types import Jsonable
from .base_stream_response import (
    AsyncChunkIterator,
    BaseAsyncStreamResponse,
    BaseSyncStreamResponse,
    ChunkIterator,
)

if TYPE_CHECKING:
    from ..models import Params
    from ..providers import ModelId, ProviderId


class StreamResponse(BaseSyncStreamResponse[Toolkit, FormattableT]):
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
            provider_id="openai",
            model_id="openai/gpt-5-mini",
        )
        def answer_question(question: str) -> str:
            return f"Answer this question: {question}"

        stream_response = answer_question.stream("What is the capital of France?")

        for chunk in stream_response.text_stream():
            print(chunk, end="", flush=True)
        ```
    """

    def __init__(
        self,
        *,
        provider_id: "ProviderId",
        model_id: "ModelId",
        provider_model_name: str,
        params: "Params",
        tools: Tools | None = None,
        format: Format[FormattableT] | None = None,
        input_messages: Sequence[Message],
        chunk_iterator: ChunkIterator,
    ) -> None:
        """Initialize a `StreamResponse`."""
        toolkit = tools if isinstance(tools, Toolkit) else Toolkit(tools=tools)
        super().__init__(
            provider_id=provider_id,
            model_id=model_id,
            provider_model_name=provider_model_name,
            params=params,
            toolkit=toolkit,
            format=format,
            input_messages=input_messages,
            chunk_iterator=chunk_iterator,
        )

    def execute_tools(self) -> Sequence[ToolOutput[Jsonable]]:
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
        self: "StreamResponse[FormattableT]", content: UserContent
    ) -> "StreamResponse[FormattableT]": ...

    def resume(
        self, content: UserContent
    ) -> "StreamResponse | StreamResponse[FormattableT]":
        """Generate a new `StreamResponse` using this response's messages with additional user content.

        Uses this response's tools and format type. Also uses this response's provider,
        model, client, and params, unless the model context manager is being used to
        provide a new LLM as an override.

        Args:
            content: The new user message content to append to the message history.

        Returns:
            A new `StreamResponse` instance generated from the extended message history.
        """
        return self.model.resume_stream(
            response=self,
            content=content,
        )

    @overload
    def validate(
        self: "StreamResponse[None]", max_retries: int = 1
    ) -> tuple[None, "StreamResponse[None]"]: ...

    @overload
    def validate(
        self: "StreamResponse[FormattableT]", max_retries: int = 1
    ) -> tuple[FormattableT, "StreamResponse[FormattableT]"]: ...

    def validate(
        self, max_retries: int = 1
    ) -> tuple[
        FormattableT | None, "StreamResponse[FormattableT] | StreamResponse[None]"
    ]:
        """Parse and validate the response, retrying on parse errors.

        Consumes the stream (calls `finish()`) and then attempts to parse. On
        `ParseError`, asks the LLM to fix its output by resuming with the error
        message. Returns both the parsed value and the (potentially updated) response.

        Args:
            max_retries: Maximum number of retry attempts on parse failure.
                Defaults to 1 (2 total attempts). Must be non-negative.

        Returns:
            A tuple of (parsed_value, response). If parsing succeeded on the first
            attempt, returns (value, self). If retries were needed, returns
            (value, new_response) where new_response is the final successful response.

        Raises:
            ValueError: If max_retries is negative.
            ParseError: If parsing fails after exhausting all retry attempts.
            Error: If the LLM call fails while generating a retry response.
        """
        if max_retries < 0:
            raise ValueError("max_retries must be non-negative")

        self.finish()

        if self.format is None:
            return None, self

        current_response: StreamResponse[FormattableT] = self
        for attempt in range(max_retries + 1):
            try:
                return current_response.parse(), current_response
            except ParseError as e:
                if attempt == max_retries:
                    raise
                current_response = current_response.resume(e.retry_message())
                current_response.finish()

        raise AssertionError("Unreachable")  # pragma: no cover


class AsyncStreamResponse(BaseAsyncStreamResponse[AsyncToolkit, FormattableT]):
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
            provider_id="openai",
            model_id="openai/gpt-5-mini",
        )
        async def answer_question(question: str) -> str:
            return f"Answer this question: {question}"

        stream_response = await answer_question.stream("What is the capital of France?")

        async for chunk in stream_response.text_stream():
            print(chunk, end="", flush=True)
        ```
    """

    def __init__(
        self,
        *,
        provider_id: "ProviderId",
        model_id: "ModelId",
        provider_model_name: str,
        params: "Params",
        tools: AsyncTools | None = None,
        format: Format[FormattableT] | None = None,
        input_messages: Sequence[Message],
        chunk_iterator: AsyncChunkIterator,
    ) -> None:
        """Initialize an `AsyncStreamResponse`."""
        toolkit = (
            tools if isinstance(tools, AsyncToolkit) else AsyncToolkit(tools=tools)
        )
        super().__init__(
            provider_id=provider_id,
            model_id=model_id,
            provider_model_name=provider_model_name,
            params=params,
            toolkit=toolkit,
            format=format,
            input_messages=input_messages,
            chunk_iterator=chunk_iterator,
        )

    async def execute_tools(self) -> Sequence[ToolOutput[Jsonable]]:
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
        self: "AsyncStreamResponse[FormattableT]", content: UserContent
    ) -> "AsyncStreamResponse[FormattableT]": ...

    async def resume(
        self, content: UserContent
    ) -> "AsyncStreamResponse | AsyncStreamResponse[FormattableT]":
        """Generate a new `AsyncStreamResponse` using this response's messages with additional user content.

        Uses this response's tools and format type. Also uses this response's provider,
        model, client, and params, unless the model context manager is being used to
        provide a new LLM as an override.

        Args:
            content: The new user message content to append to the message history.

        Returns:
            A new `AsyncStreamResponse` instance generated from the extended message history.
        """
        return await self.model.resume_stream_async(
            response=self,
            content=content,
        )

    @overload
    async def validate(
        self: "AsyncStreamResponse[None]", max_retries: int = 1
    ) -> tuple[None, "AsyncStreamResponse[None]"]: ...

    @overload
    async def validate(
        self: "AsyncStreamResponse[FormattableT]", max_retries: int = 1
    ) -> tuple[FormattableT, "AsyncStreamResponse[FormattableT]"]: ...

    async def validate(
        self, max_retries: int = 1
    ) -> tuple[
        FormattableT | None,
        "AsyncStreamResponse[FormattableT] | AsyncStreamResponse[None]",
    ]:
        """Parse and validate the response, retrying on parse errors.

        Consumes the stream (calls `finish()`) and then attempts to parse. On
        `ParseError`, asks the LLM to fix its output by resuming with the error
        message. Returns both the parsed value and the (potentially updated) response.

        Args:
            max_retries: Maximum number of retry attempts on parse failure.
                Defaults to 1 (2 total attempts). Must be non-negative.

        Returns:
            A tuple of (parsed_value, response). If parsing succeeded on the first
            attempt, returns (value, self). If retries were needed, returns
            (value, new_response) where new_response is the final successful response.

        Raises:
            ValueError: If max_retries is negative.
            ParseError: If parsing fails after exhausting all retry attempts.
            Error: If the LLM call fails while generating a retry response.
        """
        if max_retries < 0:
            raise ValueError("max_retries must be non-negative")

        await self.finish()

        if self.format is None:
            return None, self

        current_response: AsyncStreamResponse[FormattableT] = self
        for attempt in range(max_retries + 1):
            try:
                return current_response.parse(), current_response
            except ParseError as e:
                if attempt == max_retries:
                    raise
                current_response = await current_response.resume(e.retry_message())
                await current_response.finish()

        raise AssertionError("Unreachable")  # pragma: no cover


class ContextStreamResponse(
    BaseSyncStreamResponse[ContextToolkit[DepsT], FormattableT],
    Generic[DepsT, FormattableT],
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
            provider_id="openai",
            model_id="openai/gpt-5-mini",
        )
        def answer_question(ctx: llm.Context, question: str) -> str:
            return f"Answer this question: {question}"

        ctx = llm.Context()
        stream_response = answer_question.stream(ctx, "What is the capital of France?")

        for chunk in stream_response.text_stream():
            print(chunk, end="", flush=True)
        ```
    """

    def __init__(
        self,
        *,
        provider_id: "ProviderId",
        model_id: "ModelId",
        provider_model_name: str,
        params: "Params",
        tools: ContextTools[DepsT] | None = None,
        format: Format[FormattableT] | None = None,
        input_messages: Sequence[Message],
        chunk_iterator: ChunkIterator,
    ) -> None:
        """Initialize a `ContextStreamResponse`."""
        toolkit = (
            tools if isinstance(tools, ContextToolkit) else ContextToolkit(tools=tools)
        )
        super().__init__(
            provider_id=provider_id,
            model_id=model_id,
            provider_model_name=provider_model_name,
            params=params,
            toolkit=toolkit,
            format=format,
            input_messages=input_messages,
            chunk_iterator=chunk_iterator,
        )

    def execute_tools(self, ctx: Context[DepsT]) -> Sequence[ToolOutput[Jsonable]]:
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
        self: "ContextStreamResponse[DepsT, FormattableT]",
        ctx: Context[DepsT],
        content: UserContent,
    ) -> "ContextStreamResponse[DepsT, FormattableT]": ...

    def resume(
        self, ctx: Context[DepsT], content: UserContent
    ) -> "ContextStreamResponse[DepsT] | ContextStreamResponse[DepsT, FormattableT]":
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
        return self.model.context_resume_stream(
            ctx=ctx,
            response=self,
            content=content,
        )

    @overload
    def validate(
        self: "ContextStreamResponse[DepsT, None]",
        ctx: Context[DepsT],
        max_retries: int = 1,
    ) -> tuple[None, "ContextStreamResponse[DepsT, None]"]: ...

    @overload
    def validate(
        self: "ContextStreamResponse[DepsT, FormattableT]",
        ctx: Context[DepsT],
        max_retries: int = 1,
    ) -> tuple[FormattableT, "ContextStreamResponse[DepsT, FormattableT]"]: ...

    def validate(
        self, ctx: Context[DepsT], max_retries: int = 1
    ) -> tuple[
        FormattableT | None,
        "ContextStreamResponse[DepsT, FormattableT] | ContextStreamResponse[DepsT, None]",
    ]:
        """Parse and validate the response, retrying on parse errors.

        Consumes the stream (calls `finish()`) and then attempts to parse. On
        `ParseError`, asks the LLM to fix its output by resuming with the error
        message. Returns both the parsed value and the (potentially updated) response.

        Args:
            ctx: A `Context` with the required deps type.
            max_retries: Maximum number of retry attempts on parse failure.
                Defaults to 1 (2 total attempts). Must be non-negative.

        Returns:
            A tuple of (parsed_value, response). If parsing succeeded on the first
            attempt, returns (value, self). If retries were needed, returns
            (value, new_response) where new_response is the final successful response.

        Raises:
            ValueError: If max_retries is negative.
            ParseError: If parsing fails after exhausting all retry attempts.
            Error: If the LLM call fails while generating a retry response.
        """
        if max_retries < 0:
            raise ValueError("max_retries must be non-negative")

        self.finish()

        if self.format is None:
            return None, self

        current_response: ContextStreamResponse[DepsT, FormattableT] = self
        for attempt in range(max_retries + 1):
            try:
                return current_response.parse(), current_response
            except ParseError as e:
                if attempt == max_retries:
                    raise
                current_response = current_response.resume(ctx, e.retry_message())
                current_response.finish()

        raise AssertionError("Unreachable")  # pragma: no cover


class AsyncContextStreamResponse(
    BaseAsyncStreamResponse[AsyncContextToolkit[DepsT], FormattableT],
    Generic[DepsT, FormattableT],
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
            provider_id="openai",
            model_id="openai/gpt-5-mini",
        )
        async def answer_question(ctx: llm.Context, question: str) -> str:
            return f"Answer this question: {question}"

        ctx = llm.Context()
        stream_response = await answer_question.stream(ctx, "What is the capital of France?")

        async for chunk in stream_response.text_stream():
            print(chunk, end="", flush=True)
        ```
    """

    def __init__(
        self,
        *,
        provider_id: "ProviderId",
        model_id: "ModelId",
        provider_model_name: str,
        params: "Params",
        tools: AsyncContextTools[DepsT] | None = None,
        format: Format[FormattableT] | None = None,
        input_messages: Sequence[Message],
        chunk_iterator: AsyncChunkIterator,
    ) -> None:
        """Initialize an `AsyncContextStreamResponse`."""
        toolkit = (
            tools
            if isinstance(tools, AsyncContextToolkit)
            else AsyncContextToolkit(tools=tools)
        )
        super().__init__(
            provider_id=provider_id,
            model_id=model_id,
            provider_model_name=provider_model_name,
            params=params,
            toolkit=toolkit,
            format=format,
            input_messages=input_messages,
            chunk_iterator=chunk_iterator,
        )

    async def execute_tools(
        self, ctx: Context[DepsT]
    ) -> Sequence[ToolOutput[Jsonable]]:
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
        self: "AsyncContextStreamResponse[DepsT, FormattableT]",
        ctx: Context[DepsT],
        content: UserContent,
    ) -> "AsyncContextStreamResponse[DepsT, FormattableT]": ...

    async def resume(
        self, ctx: Context[DepsT], content: UserContent
    ) -> "AsyncContextStreamResponse[DepsT] | AsyncContextStreamResponse[DepsT, FormattableT]":
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
        return await self.model.context_resume_stream_async(
            ctx=ctx,
            response=self,
            content=content,
        )

    @overload
    async def validate(
        self: "AsyncContextStreamResponse[DepsT, None]",
        ctx: Context[DepsT],
        max_retries: int = 1,
    ) -> tuple[None, "AsyncContextStreamResponse[DepsT, None]"]: ...

    @overload
    async def validate(
        self: "AsyncContextStreamResponse[DepsT, FormattableT]",
        ctx: Context[DepsT],
        max_retries: int = 1,
    ) -> tuple[FormattableT, "AsyncContextStreamResponse[DepsT, FormattableT]"]: ...

    async def validate(
        self, ctx: Context[DepsT], max_retries: int = 1
    ) -> tuple[
        FormattableT | None,
        "AsyncContextStreamResponse[DepsT, FormattableT] | AsyncContextStreamResponse[DepsT, None]",
    ]:
        """Parse and validate the response, retrying on parse errors.

        Consumes the stream (calls `finish()`) and then attempts to parse. On
        `ParseError`, asks the LLM to fix its output by resuming with the error
        message. Returns both the parsed value and the (potentially updated) response.

        Args:
            ctx: A `Context` with the required deps type.
            max_retries: Maximum number of retry attempts on parse failure.
                Defaults to 1 (2 total attempts). Must be non-negative.

        Returns:
            A tuple of (parsed_value, response). If parsing succeeded on the first
            attempt, returns (value, self). If retries were needed, returns
            (value, new_response) where new_response is the final successful response.

        Raises:
            ValueError: If max_retries is negative.
            ParseError: If parsing fails after exhausting all retry attempts.
            Error: If the LLM call fails while generating a retry response.
        """
        if max_retries < 0:
            raise ValueError("max_retries must be non-negative")

        await self.finish()

        if self.format is None:
            return None, self

        current_response: AsyncContextStreamResponse[DepsT, FormattableT] = self
        for attempt in range(max_retries + 1):
            try:
                return current_response.parse(), current_response
            except ParseError as e:
                if attempt == max_retries:
                    raise
                current_response = await current_response.resume(ctx, e.retry_message())
                await current_response.finish()

        raise AssertionError("Unreachable")  # pragma: no cover
