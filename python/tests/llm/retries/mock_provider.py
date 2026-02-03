"""Mock Provider for testing retry logic."""

from collections.abc import AsyncIterator, Iterator, Sequence
from typing import Any, ClassVar
from typing_extensions import Unpack

from mirascope import llm
from mirascope.llm import (
    AsyncContextResponse,
    AsyncContextStreamResponse,
    AsyncContextToolkit,
    AsyncResponse,
    AsyncStreamResponse,
    AsyncToolkit,
    Context,
    ContextResponse,
    ContextStreamResponse,
    ContextToolkit,
    DepsT,
    Format,
    FormattableT,
    OutputParser,
    Params,
    Response,
    StreamResponse,
    Toolkit,
)
from mirascope.llm.content import TextChunk, TextEndChunk, TextStartChunk
from mirascope.llm.providers import BaseProvider
from mirascope.llm.providers.base import ProviderErrorMap
from mirascope.llm.responses.base_stream_response import StreamResponseChunk


class MockProvider(BaseProvider[None]):
    """A mock Provider for testing that returns configurable responses.

    The provider can be configured with a sequence of exceptions to raise before
    eventually returning a successful response. This allows testing retry logic
    with predictable failure patterns.
    """

    # TODO Consider unifying with test provider.
    # cf #2101 (https://github.com/Mirascope/mirascope/issues/2120)

    id: ClassVar[llm.ProviderId] = "mock"
    default_scope: ClassVar[str | list[str]] = "mock/"
    error_map: ClassVar[ProviderErrorMap] = {}

    def __init__(self) -> None:
        """Initialize the MockProvider."""
        self.client = None
        self._exceptions: list[BaseException] = []
        self._stream_exceptions: list[BaseException] = []
        self._call_count = 0
        self._stream_count = 0
        self._stream_text: str | None = None  # Custom text for streaming (single)
        self._response_texts: list[
            str
        ] = []  # Queue of response texts for non-streaming
        self._stream_texts: list[str] = []  # Queue of stream texts

    @property
    def call_count(self) -> int:
        """The number of times _call() has been invoked."""
        return self._call_count

    @property
    def stream_count(self) -> int:
        """The number of times _stream() has been invoked."""
        return self._stream_count

    def set_exceptions(self, exceptions: Sequence[BaseException]) -> None:
        """Set exceptions to raise before returning a successful response.

        Args:
            exceptions: A list of exceptions to raise in order. Once exhausted,
                subsequent calls will return the mock response.
        """
        self._exceptions = list(exceptions)

    def set_stream_exceptions(self, exceptions: Sequence[BaseException]) -> None:
        """Set exceptions to raise during stream iteration.

        Args:
            exceptions: A list of exceptions to raise mid-stream. Each exception
                is raised once during iteration. Once exhausted, subsequent streams
                will complete successfully.
        """
        self._stream_exceptions = list(exceptions)

    def set_stream_text(self, text: str) -> None:
        """Set custom text to stream instead of default 'mock response'.

        Args:
            text: The text to stream in chunks.
        """
        self._stream_text = text

    def set_response_texts(self, texts: Sequence[str]) -> None:
        """Set a queue of response texts for non-streaming calls.

        Each call will use the next text in the queue. Once exhausted,
        subsequent calls will use the default 'mock response'.

        Args:
            texts: A list of response texts in order.
        """
        self._response_texts = list(texts)

    def set_stream_texts(self, texts: Sequence[str]) -> None:
        """Set a queue of stream texts for streaming calls.

        Each stream will use the next text in the queue. Once exhausted,
        subsequent streams will use the default 'mock response'.

        Args:
            texts: A list of stream texts in order.
        """
        self._stream_texts = list(texts)

    def _make_response(
        self,
        model_id: str,
        messages: Sequence[llm.messages.Message],
        format: Format[Any] | None = None,
    ) -> Response[Any]:
        """Create a minimal valid Response for testing."""
        # Use queued response text if available
        text = self._response_texts.pop(0) if self._response_texts else "mock response"
        return Response(
            raw={"mock": True},
            usage=None,
            provider_id="mock",
            model_id=model_id,
            provider_model_name="test-model",
            params={},
            tools=None,
            format=format,
            input_messages=list(messages),
            assistant_message=llm.messages.assistant(
                [llm.Text(text=text)],
                model_id=model_id,
                provider_id="mock",
            ),
            finish_reason=None,
        )

    def _make_async_response(
        self,
        model_id: str,
        messages: Sequence[llm.messages.Message],
        format: Format[Any] | None = None,
    ) -> AsyncResponse[Any]:
        """Create a minimal valid AsyncResponse for testing."""
        # Use queued response text if available
        text = self._response_texts.pop(0) if self._response_texts else "mock response"
        return AsyncResponse(
            raw={"mock": True},
            usage=None,
            provider_id="mock",
            model_id=model_id,
            provider_model_name="test-model",
            params={},
            tools=None,
            format=format,
            input_messages=list(messages),
            assistant_message=llm.messages.assistant(
                [llm.Text(text=text)],
                model_id=model_id,
                provider_id="mock",
            ),
            finish_reason=None,
        )

    def _make_context_response(
        self,
        model_id: str,
        messages: Sequence[llm.messages.Message],
        format: Format[Any] | None = None,
    ) -> ContextResponse[Any, Any]:
        """Create a minimal valid ContextResponse for testing."""
        # Use queued response text if available
        text = self._response_texts.pop(0) if self._response_texts else "mock response"
        return ContextResponse(
            raw={"mock": True},
            usage=None,
            provider_id="mock",
            model_id=model_id,
            provider_model_name="test-model",
            params={},
            tools=None,
            format=format,
            input_messages=list(messages),
            assistant_message=llm.messages.assistant(
                [llm.Text(text=text)],
                model_id=model_id,
                provider_id="mock",
            ),
            finish_reason=None,
        )

    def _make_async_context_response(
        self,
        model_id: str,
        messages: Sequence[llm.messages.Message],
        format: Format[Any] | None = None,
    ) -> AsyncContextResponse[Any, Any]:
        """Create a minimal valid AsyncContextResponse for testing."""
        # Use queued response text if available
        text = self._response_texts.pop(0) if self._response_texts else "mock response"
        return AsyncContextResponse(
            raw={"mock": True},
            usage=None,
            provider_id="mock",
            model_id=model_id,
            provider_model_name="test-model",
            params={},
            tools=None,
            format=format,
            input_messages=list(messages),
            assistant_message=llm.messages.assistant(
                [llm.Text(text=text)],
                model_id=model_id,
                provider_id="mock",
            ),
            finish_reason=None,
        )

    def _call(
        self,
        *,
        model_id: str,
        messages: Sequence[llm.messages.Message],
        toolkit: Toolkit,
        format: type[FormattableT]
        | Format[FormattableT]
        | OutputParser[FormattableT]
        | None = None,
        **params: Unpack[Params],
    ) -> Response[Any]:
        """Return the configured response or raise the next configured exception."""
        self._call_count += 1
        if self._exceptions:
            raise self._exceptions.pop(0)
        # Resolve format to Format object
        resolved_format: Format[Any] | None = None
        if format is not None:
            if isinstance(format, Format):
                resolved_format = format
            elif isinstance(format, OutputParser):
                resolved_format = llm.format(format, mode="parser")
            else:
                resolved_format = llm.format(format, mode="json")
        return self._make_response(model_id, messages, resolved_format)

    async def _call_async(
        self,
        *,
        model_id: str,
        messages: Sequence[llm.messages.Message],
        toolkit: AsyncToolkit,
        format: type[FormattableT]
        | Format[FormattableT]
        | OutputParser[FormattableT]
        | None = None,
        **params: Unpack[Params],
    ) -> AsyncResponse[Any]:
        """Return the configured response or raise the next configured exception."""
        self._call_count += 1
        if self._exceptions:
            raise self._exceptions.pop(0)
        # Resolve format to Format object
        resolved_format: Format[Any] | None = None
        if format is not None:
            if isinstance(format, Format):
                resolved_format = format
            elif isinstance(format, OutputParser):
                resolved_format = llm.format(format, mode="parser")
            else:
                resolved_format = llm.format(format, mode="json")
        return self._make_async_response(model_id, messages, resolved_format)

    def _context_call(
        self,
        *,
        ctx: Context[DepsT],
        model_id: str,
        messages: Sequence[llm.messages.Message],
        toolkit: ContextToolkit[DepsT],
        format: type[FormattableT]
        | Format[FormattableT]
        | OutputParser[FormattableT]
        | None = None,
        **params: Unpack[Params],
    ) -> ContextResponse[DepsT, None] | ContextResponse[DepsT, FormattableT]:
        """Return the configured response or raise the next configured exception."""
        self._call_count += 1
        if self._exceptions:
            raise self._exceptions.pop(0)
        # Resolve format to Format object
        resolved_format: Format[Any] | None = None
        if format is not None:
            if isinstance(format, Format):
                resolved_format = format
            elif isinstance(format, OutputParser):
                resolved_format = llm.format(format, mode="parser")
            else:
                resolved_format = llm.format(format, mode="json")
        return self._make_context_response(model_id, messages, resolved_format)

    async def _context_call_async(
        self,
        *,
        ctx: Context[DepsT],
        model_id: str,
        messages: Sequence[llm.messages.Message],
        toolkit: AsyncContextToolkit[DepsT],
        format: type[FormattableT]
        | Format[FormattableT]
        | OutputParser[FormattableT]
        | None = None,
        **params: Unpack[Params],
    ) -> AsyncContextResponse[DepsT, None] | AsyncContextResponse[DepsT, FormattableT]:
        """Return the configured response or raise the next configured exception."""
        self._call_count += 1
        if self._exceptions:
            raise self._exceptions.pop(0)
        # Resolve format to Format object
        resolved_format: Format[Any] | None = None
        if format is not None:
            if isinstance(format, Format):
                resolved_format = format
            elif isinstance(format, OutputParser):
                resolved_format = llm.format(format, mode="parser")
            else:
                resolved_format = llm.format(format, mode="json")
        return self._make_async_context_response(model_id, messages, resolved_format)

    def _make_chunk_iterator(self) -> Iterator[StreamResponseChunk]:
        """Create a chunk iterator that yields mock text chunks.

        If stream exceptions are configured, raises the next one mid-stream.
        """
        yield TextStartChunk()
        # Determine text to stream: queued texts > single text > default
        if self._stream_texts:
            text = self._stream_texts.pop(0)
        elif self._stream_text is not None:
            text = self._stream_text
        else:
            text = "mock response"

        mid = len(text) // 2
        yield TextChunk(delta=text[:mid])
        # Raise exception mid-stream if configured
        if self._stream_exceptions:
            raise self._stream_exceptions.pop(0)
        yield TextChunk(delta=text[mid:])
        yield TextEndChunk()

    async def _make_async_chunk_iterator(self) -> AsyncIterator[StreamResponseChunk]:
        """Create an async chunk iterator that yields mock text chunks.

        If stream exceptions are configured, raises the next one mid-stream.
        """
        yield TextStartChunk()
        # Determine text to stream: queued texts > single text > default
        if self._stream_texts:
            text = self._stream_texts.pop(0)
        elif self._stream_text is not None:
            text = self._stream_text
        else:
            text = "mock response"

        mid = len(text) // 2
        yield TextChunk(delta=text[:mid])
        # Raise exception mid-stream if configured
        if self._stream_exceptions:
            raise self._stream_exceptions.pop(0)
        yield TextChunk(delta=text[mid:])
        yield TextEndChunk()

    def _stream(
        self,
        *,
        model_id: str,
        messages: Sequence[llm.messages.Message],
        toolkit: Toolkit,
        format: type[FormattableT]
        | Format[FormattableT]
        | OutputParser[FormattableT]
        | None = None,
        **params: Unpack[Params],
    ) -> StreamResponse[Any]:
        """Return a StreamResponse with configurable mid-stream exceptions."""
        self._stream_count += 1
        # Convert format to Format if it's a type
        resolved_format: Format[Any] | None = None
        if format is not None:
            if isinstance(format, Format):
                resolved_format = format
            elif isinstance(format, OutputParser):
                resolved_format = llm.format(format, mode="parser")
            else:
                resolved_format = llm.format(format, mode="json")
        return StreamResponse(
            provider_id="mock",
            model_id=model_id,
            provider_model_name="test-model",
            params={},
            tools=None,
            format=resolved_format,
            input_messages=list(messages),
            chunk_iterator=self._make_chunk_iterator(),
        )

    async def _stream_async(
        self,
        *,
        model_id: str,
        messages: Sequence[llm.messages.Message],
        toolkit: AsyncToolkit,
        format: type[FormattableT]
        | Format[FormattableT]
        | OutputParser[FormattableT]
        | None = None,
        **params: Unpack[Params],
    ) -> AsyncStreamResponse[Any]:
        """Return an AsyncStreamResponse with configurable mid-stream exceptions."""
        self._stream_count += 1
        # Convert format to Format if it's a type
        resolved_format: Format[Any] | None = None
        if format is not None:
            if isinstance(format, Format):
                resolved_format = format
            elif isinstance(format, OutputParser):
                resolved_format = llm.format(format, mode="parser")
            else:
                resolved_format = llm.format(format, mode="json")
        return AsyncStreamResponse(
            provider_id="mock",
            model_id=model_id,
            provider_model_name="test-model",
            params={},
            tools=None,
            format=resolved_format,
            input_messages=list(messages),
            chunk_iterator=self._make_async_chunk_iterator(),
        )

    def _context_stream(
        self,
        *,
        ctx: Context[DepsT],
        model_id: str,
        messages: Sequence[llm.messages.Message],
        toolkit: ContextToolkit[DepsT],
        format: type[FormattableT]
        | Format[FormattableT]
        | OutputParser[FormattableT]
        | None = None,
        **params: Unpack[Params],
    ) -> (
        ContextStreamResponse[DepsT, None] | ContextStreamResponse[DepsT, FormattableT]
    ):
        """Return a ContextStreamResponse with configurable mid-stream exceptions."""
        self._stream_count += 1
        # Convert format to Format if it's a type
        resolved_format: Format[Any] | None = None
        if format is not None:
            if isinstance(format, Format):
                resolved_format = format
            elif isinstance(format, OutputParser):
                resolved_format = llm.format(format, mode="parser")
            else:
                resolved_format = llm.format(format, mode="json")
        return ContextStreamResponse(
            provider_id="mock",
            model_id=model_id,
            provider_model_name="test-model",
            params={},
            tools=None,
            format=resolved_format,
            input_messages=list(messages),
            chunk_iterator=self._make_chunk_iterator(),
        )

    async def _context_stream_async(
        self,
        *,
        ctx: Context[DepsT],
        model_id: str,
        messages: Sequence[llm.messages.Message],
        toolkit: AsyncContextToolkit[DepsT],
        format: type[FormattableT]
        | Format[FormattableT]
        | OutputParser[FormattableT]
        | None = None,
        **params: Unpack[Params],
    ) -> (
        AsyncContextStreamResponse[DepsT, None]
        | AsyncContextStreamResponse[DepsT, FormattableT]
    ):
        """Return an AsyncContextStreamResponse with configurable mid-stream exceptions."""
        self._stream_count += 1
        # Convert format to Format if it's a type
        resolved_format: Format[Any] | None = None
        if format is not None:
            if isinstance(format, Format):
                resolved_format = format
            elif isinstance(format, OutputParser):
                resolved_format = llm.format(format, mode="parser")
            else:
                resolved_format = llm.format(format, mode="json")
        return AsyncContextStreamResponse(
            provider_id="mock",
            model_id=model_id,
            provider_model_name="test-model",
            params={},
            tools=None,
            format=resolved_format,
            input_messages=list(messages),
            chunk_iterator=self._make_async_chunk_iterator(),
        )

    def get_error_status(self, e: Exception) -> int | None:
        """Return None for mock provider."""
        return None
