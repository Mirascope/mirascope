"""Retry stream response wrappers that add retry capabilities to streaming LLM responses."""

from collections.abc import AsyncIterator, Awaitable, Callable, Iterator
from typing import TYPE_CHECKING, overload

from ..content import (
    AssistantContentChunk,
)
from ..exceptions import StreamRestarted
from ..formatting import FormattableT
from ..messages import UserContent
from ..models import Model
from ..responses import (
    AsyncStreamResponse,
    StreamResponse,
)
from .retry_config import RetryConfig
from .utils import RetryState

if TYPE_CHECKING:
    from .retry_models import RetryModel


class RetryStreamResponse(StreamResponse[FormattableT]):
    """A streaming response wrapper that includes retry capabilities.

    Extends `StreamResponse` directly, copying all attributes from a wrapped response
    and adding retry configuration.

    This wraps a `StreamResponse` and adds automatic retry behavior when
    retryable errors occur during iteration. When a retry happens, a
    `StreamRestarted` exception is raised so the user can handle the restart
    (e.g., clear terminal output) before re-iterating.

    Example:
        ```python
        response = retry_model.stream("Tell me a story")

        while True:
            try:
                for chunk in response.text_stream():
                    print(chunk, end="", flush=True)
                break  # Success
            except llm.StreamRestarted as e:
                print(f"\\n[Retry {e.attempt} after: {e.error}]")
        ```
    """

    retry_config: RetryConfig
    """Configuration for retry behavior."""

    retry_state: RetryState
    """State tracking retry attempts and any exceptions caught."""

    _stream_fn: Callable[[Model], StreamResponse[FormattableT]]

    def __init__(
        self,
        retry_model: "RetryModel",
        stream_fn: Callable[[Model], StreamResponse[FormattableT]],
    ) -> None:
        """Initialize a RetryStreamResponse.

        Args:
            retry_model: The RetryModel providing retry configuration.
            stream_fn: Function that creates a stream from a Model.
        """
        retry_config = retry_model.retry_config

        # Create the initial stream and copy all attributes from it
        initial_stream = stream_fn(retry_model)
        for key, value in initial_stream.__dict__.items():
            object.__setattr__(self, key, value)

        self.retry_config = retry_config
        self._stream_fn = stream_fn

        self.retry_state = RetryState(
            max_retries=retry_config.max_retries,
            retry_on=retry_config.retry_on,
            retries=0,
            exceptions=[],
        )

    @property
    def model(self) -> "RetryModel":
        """A RetryModel with parameters matching this response."""
        from .retry_models import RetryModel

        base_model = super().model
        return RetryModel(base_model, retry_config=self.retry_config)

    def _reset_stream(self) -> None:
        """Reset to a fresh stream for a new retry attempt."""
        new_stream = self._stream_fn(self.model)
        # Copy all attributes from the new stream
        for key, value in new_stream.__dict__.items():
            object.__setattr__(self, key, value)

    def chunk_stream(self) -> Iterator[AssistantContentChunk]:
        """Returns an iterator that yields content chunks with retry support.

        If a retryable error occurs during iteration, the stream is reset
        and a `StreamRestarted` exception is raised. The user should catch
        this exception and re-iterate to continue from the new attempt.

        Raises:
            StreamRestarted: When the stream is reset for a retry attempt.
            Exception: The underlying error if max retries are exhausted.
        """
        try:
            yield from super().chunk_stream()
        except self.retry_config.retry_on as e:
            self.retry_state.exceptions.append(e)
            self.retry_state.retries += 1

            if self.retry_state.retries > self.retry_config.max_retries:
                raise

            self._reset_stream()

            raise StreamRestarted(
                attempt=self.retry_state.retries,
                error=e,
            ) from e

    @overload
    def resume(
        self: "RetryStreamResponse[None]", content: UserContent
    ) -> "RetryStreamResponse[None]": ...

    @overload
    def resume(
        self: "RetryStreamResponse[FormattableT]", content: UserContent
    ) -> "RetryStreamResponse[FormattableT]": ...

    def resume(
        self, content: UserContent
    ) -> "RetryStreamResponse[None] | RetryStreamResponse[FormattableT]":
        """Generate a new RetryStreamResponse using this response's messages with additional user content."""
        return self.model.resume_stream(response=self, content=content)


class AsyncRetryStreamResponse(AsyncStreamResponse[FormattableT]):
    """An async streaming response wrapper that includes retry capabilities.

    Extends `AsyncStreamResponse` directly, copying all attributes from a wrapped response
    and adding retry configuration.

    This wraps an `AsyncStreamResponse` and adds automatic retry behavior when
    retryable errors occur during iteration. When a retry happens, a
    `StreamRestarted` exception is raised so the user can handle the restart
    (e.g., clear terminal output) before re-iterating.

    Example:
        ```python
        response = await retry_model.stream_async("Tell me a story")

        while True:
            try:
                async for chunk in response.text_stream():
                    print(chunk, end="", flush=True)
                break  # Success
            except llm.StreamRestarted as e:
                print(f"\\n[Retry {e.attempt} after: {e.error}]")
        ```
    """

    retry_config: RetryConfig
    """Configuration for retry behavior."""

    retry_state: RetryState
    """State tracking retry attempts and any exceptions caught."""

    _stream_fn: Callable[[Model], Awaitable[AsyncStreamResponse[FormattableT]]]

    def __init__(
        self,
        retry_model: "RetryModel",
        stream_fn: Callable[[Model], Awaitable[AsyncStreamResponse[FormattableT]]],
        initial_stream: AsyncStreamResponse[FormattableT],
    ) -> None:
        """Initialize an AsyncRetryStreamResponse.

        Args:
            retry_model: The RetryModel providing retry configuration.
            stream_fn: Async function that creates a stream from a Model.
            initial_stream: The pre-awaited initial stream.
        """
        retry_config = retry_model.retry_config

        # Copy all attributes from the initial stream
        for key, value in initial_stream.__dict__.items():
            object.__setattr__(self, key, value)

        self.retry_config = retry_config
        self._stream_fn = stream_fn

        self.retry_state = RetryState(
            max_retries=retry_config.max_retries,
            retry_on=retry_config.retry_on,
            retries=0,
            exceptions=[],
        )

    @property
    def model(self) -> "RetryModel":
        """A RetryModel with parameters matching this response."""
        from .retry_models import RetryModel

        base_model = super().model
        return RetryModel(base_model, retry_config=self.retry_config)

    async def _reset_stream(self) -> None:
        """Reset to a fresh stream for a new retry attempt."""
        new_stream = await self._stream_fn(self.model)
        # Copy all attributes from the new stream
        for key, value in new_stream.__dict__.items():
            object.__setattr__(self, key, value)

    async def chunk_stream(self) -> AsyncIterator[AssistantContentChunk]:
        """Returns an async iterator that yields content chunks with retry support.

        If a retryable error occurs during iteration, the stream is reset
        and a `StreamRestarted` exception is raised. The user should catch
        this exception and re-iterate to continue from the new attempt.

        Raises:
            StreamRestarted: When the stream is reset for a retry attempt.
            Exception: The underlying error if max retries are exhausted.
        """
        try:
            async for chunk in super().chunk_stream():
                yield chunk
        except self.retry_config.retry_on as e:
            self.retry_state.exceptions.append(e)
            self.retry_state.retries += 1

            if self.retry_state.retries > self.retry_config.max_retries:
                raise

            await self._reset_stream()

            raise StreamRestarted(
                attempt=self.retry_state.retries,
                error=e,
            ) from e

    @overload
    async def resume(
        self: "AsyncRetryStreamResponse[None]", content: UserContent
    ) -> "AsyncRetryStreamResponse[None]": ...

    @overload
    async def resume(
        self: "AsyncRetryStreamResponse[FormattableT]", content: UserContent
    ) -> "AsyncRetryStreamResponse[FormattableT]": ...

    async def resume(
        self, content: UserContent
    ) -> "AsyncRetryStreamResponse[None] | AsyncRetryStreamResponse[FormattableT]":
        """Generate a new AsyncRetryStreamResponse using this response's messages with additional user content."""
        return await self.model.resume_stream_async(response=self, content=content)
