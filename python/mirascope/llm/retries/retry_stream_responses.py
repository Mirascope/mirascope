"""Retry stream response wrappers that add retry capabilities to streaming LLM responses."""

from collections.abc import AsyncIterator, Awaitable, Callable, Iterator
from typing import TYPE_CHECKING, Generic, overload

from ..content import (
    AssistantContentChunk,
)
from ..context import Context, DepsT
from ..exceptions import RetriesExhausted, StreamRestarted
from ..formatting import FormattableT
from ..messages import UserContent
from ..models import Model
from ..responses import (
    AsyncContextStreamResponse,
    AsyncStreamResponse,
    ContextStreamResponse,
    StreamResponse,
)
from .utils import RetryFailure

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

    Supports fallback models - when the active model exhausts its retries,
    the next fallback model is tried.

    Example:
        ```python
        response = retry_model.stream("Tell me a story")

        while True:
            try:
                for chunk in response.text_stream():
                    print(chunk, end="", flush=True)
                break  # Success
            except llm.StreamRestarted as e:
                print(e.message)
        ```
    """

    _current_variant: "RetryModel"
    """The current RetryModel variant being used."""

    _variants_iter: Iterator["RetryModel"]
    """Iterator over model variants with backoff delays."""

    retry_failures: list[RetryFailure]
    """Failed attempts before success (empty if first attempt succeeded)."""

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
        self._variants_iter = retry_model.variants()
        self._current_variant = next(self._variants_iter)
        self._stream_fn = stream_fn
        self.retry_failures = []

        # Create the initial stream and copy all attributes
        initial_stream = stream_fn(self._current_variant.get_active_model())
        for key, value in initial_stream.__dict__.items():
            object.__setattr__(self, key, value)

    @property
    def model(self) -> "RetryModel":
        """A RetryModel with parameters matching this response."""
        return self._current_variant

    def _reset_stream(self, variant: "RetryModel") -> None:
        """Reset to a fresh stream for a new retry attempt."""
        new_stream = self._stream_fn(variant.get_active_model())
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
        config = self._current_variant.retry_config
        try:
            yield from super().chunk_stream()
        except config.retry_on as e:
            failure = RetryFailure(
                model=self._current_variant.get_active_model(), exception=e
            )
            self.retry_failures.append(failure)

            # Try to get next variant (handles backoff and fallback)
            try:
                self._current_variant = next(self._variants_iter)
            except StopIteration:
                raise RetriesExhausted(self.retry_failures) from None

            self._reset_stream(self._current_variant)

            raise StreamRestarted(
                failure=failure,
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

    Supports fallback models - when the active model exhausts its retries,
    the next fallback model is tried.

    Example:
        ```python
        response = await retry_model.stream_async("Tell me a story")

        while True:
            try:
                async for chunk in response.text_stream():
                    print(chunk, end="", flush=True)
                break  # Success
            except llm.StreamRestarted as e:
                print(e.message)
        ```
    """

    _current_variant: "RetryModel"
    """The current RetryModel variant being used."""

    _variants_iter: AsyncIterator["RetryModel"]
    """Async iterator over model variants with backoff delays."""

    retry_failures: list[RetryFailure]
    """Failed attempts before success (empty if first attempt succeeded)."""

    _stream_fn: Callable[[Model], Awaitable[AsyncStreamResponse[FormattableT]]]

    def __init__(
        self,
        stream_fn: Callable[[Model], Awaitable[AsyncStreamResponse[FormattableT]]],
        initial_stream: AsyncStreamResponse[FormattableT],
        initial_variant: "RetryModel",
        variants_iter: AsyncIterator["RetryModel"],
    ) -> None:
        """Initialize an AsyncRetryStreamResponse.

        Args:
            stream_fn: Async function that creates a stream from a Model.
            initial_stream: The pre-awaited initial stream.
            initial_variant: The first variant from the iterator.
            variants_iter: The async iterator for remaining variants.
        """
        # Copy all attributes from the initial stream
        for key, value in initial_stream.__dict__.items():
            object.__setattr__(self, key, value)

        self._current_variant = initial_variant
        self._variants_iter = variants_iter
        self._stream_fn = stream_fn
        self.retry_failures = []

    @property
    def model(self) -> "RetryModel":
        """A RetryModel with parameters matching this response."""
        return self._current_variant

    async def _reset_stream(self, variant: "RetryModel") -> None:
        """Reset to a fresh stream for a new retry attempt."""
        new_stream = await self._stream_fn(variant.get_active_model())
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
        config = self._current_variant.retry_config
        try:
            async for chunk in super().chunk_stream():
                yield chunk
        except config.retry_on as e:
            failure = RetryFailure(
                model=self._current_variant.get_active_model(), exception=e
            )
            self.retry_failures.append(failure)

            # Try to get next variant (handles backoff and fallback)
            try:
                self._current_variant = await anext(self._variants_iter)
            except StopAsyncIteration:
                raise RetriesExhausted(self.retry_failures) from None

            await self._reset_stream(self._current_variant)

            raise StreamRestarted(
                failure=failure,
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


class ContextRetryStreamResponse(
    ContextStreamResponse[DepsT, FormattableT], Generic[DepsT, FormattableT]
):
    """A context-aware streaming response wrapper that includes retry capabilities.

    Extends `ContextStreamResponse` directly, copying all attributes from a wrapped response
    and adding retry configuration.

    This wraps a `ContextStreamResponse` and adds automatic retry behavior when
    retryable errors occur during iteration. When a retry happens, a
    `StreamRestarted` exception is raised so the user can handle the restart
    (e.g., clear terminal output) before re-iterating.

    Supports fallback models - when the active model exhausts its retries,
    the next fallback model is tried.

    Example:
        ```python
        response = retry_model.context_stream("Tell me a story", ctx=ctx)

        while True:
            try:
                for chunk in response.text_stream():
                    print(chunk, end="", flush=True)
                break  # Success
            except llm.StreamRestarted as e:
                print(e.message)
        ```
    """

    _current_variant: "RetryModel"
    """The current RetryModel variant being used."""

    _variants_iter: Iterator["RetryModel"]
    """Iterator over model variants with backoff delays."""

    retry_failures: list[RetryFailure]
    """Failed attempts before success (empty if first attempt succeeded)."""

    _stream_fn: Callable[[Model], ContextStreamResponse[DepsT, FormattableT]]

    def __init__(
        self,
        retry_model: "RetryModel",
        stream_fn: Callable[[Model], ContextStreamResponse[DepsT, FormattableT]],
    ) -> None:
        """Initialize a ContextRetryStreamResponse.

        Args:
            retry_model: The RetryModel providing retry configuration.
            stream_fn: Function that creates a stream from a Model.
        """
        self._variants_iter = retry_model.variants()
        self._current_variant = next(self._variants_iter)
        self._stream_fn = stream_fn
        self.retry_failures = []

        # Create the initial stream and copy all attributes
        initial_stream = stream_fn(self._current_variant.get_active_model())
        for key, value in initial_stream.__dict__.items():
            object.__setattr__(self, key, value)

    @property
    def model(self) -> "RetryModel":
        """A RetryModel with parameters matching this response."""
        return self._current_variant

    def _reset_stream(self, variant: "RetryModel") -> None:
        """Reset to a fresh stream for a new retry attempt."""
        new_stream = self._stream_fn(variant.get_active_model())
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
        config = self._current_variant.retry_config
        try:
            yield from super().chunk_stream()
        except config.retry_on as e:
            failure = RetryFailure(
                model=self._current_variant.get_active_model(), exception=e
            )
            self.retry_failures.append(failure)

            # Try to get next variant (handles backoff and fallback)
            try:
                self._current_variant = next(self._variants_iter)
            except StopIteration:
                raise RetriesExhausted(self.retry_failures) from None

            self._reset_stream(self._current_variant)

            raise StreamRestarted(
                failure=failure,
            ) from e

    @overload
    def resume(
        self: "ContextRetryStreamResponse[DepsT, None]",
        ctx: Context[DepsT],
        content: UserContent,
    ) -> "ContextRetryStreamResponse[DepsT, None]": ...

    @overload
    def resume(
        self: "ContextRetryStreamResponse[DepsT, FormattableT]",
        ctx: Context[DepsT],
        content: UserContent,
    ) -> "ContextRetryStreamResponse[DepsT, FormattableT]": ...

    def resume(
        self, ctx: Context[DepsT], content: UserContent
    ) -> "ContextRetryStreamResponse[DepsT, None] | ContextRetryStreamResponse[DepsT, FormattableT]":
        """Generate a new ContextRetryStreamResponse using this response's messages with additional user content."""
        return self.model.context_resume_stream(ctx=ctx, response=self, content=content)


class AsyncContextRetryStreamResponse(
    AsyncContextStreamResponse[DepsT, FormattableT], Generic[DepsT, FormattableT]
):
    """An async context-aware streaming response wrapper that includes retry capabilities.

    Extends `AsyncContextStreamResponse` directly, copying all attributes from a wrapped response
    and adding retry configuration.

    This wraps an `AsyncContextStreamResponse` and adds automatic retry behavior when
    retryable errors occur during iteration. When a retry happens, a
    `StreamRestarted` exception is raised so the user can handle the restart
    (e.g., clear terminal output) before re-iterating.

    Supports fallback models - when the active model exhausts its retries,
    the next fallback model is tried.

    Example:
        ```python
        ctx = llm.Context(deps=my_deps)
        response = await retry_model.context_stream_async("Tell me a story", ctx=ctx)

        while True:
            try:
                async for chunk in response.text_stream():
                    print(chunk, end="", flush=True)
                break  # Success
            except llm.StreamRestarted as e:
                print(e.message)
        ```
    """

    _current_variant: "RetryModel"
    """The current RetryModel variant being used."""

    _variants_iter: AsyncIterator["RetryModel"]
    """Async iterator over model variants with backoff delays."""

    retry_failures: list[RetryFailure]
    """Failed attempts before success (empty if first attempt succeeded)."""

    _stream_fn: Callable[
        [Model], Awaitable[AsyncContextStreamResponse[DepsT, FormattableT]]
    ]

    def __init__(
        self,
        stream_fn: Callable[
            [Model], Awaitable[AsyncContextStreamResponse[DepsT, FormattableT]]
        ],
        initial_stream: AsyncContextStreamResponse[DepsT, FormattableT],
        initial_variant: "RetryModel",
        variants_iter: AsyncIterator["RetryModel"],
    ) -> None:
        """Initialize an AsyncContextRetryStreamResponse.

        Args:
            stream_fn: Async function that creates a stream from a Model.
            initial_stream: The pre-awaited initial stream.
            initial_variant: The first variant from the iterator.
            variants_iter: The async iterator for remaining variants.
        """
        # Copy all attributes from the initial stream
        for key, value in initial_stream.__dict__.items():
            object.__setattr__(self, key, value)

        self._current_variant = initial_variant
        self._variants_iter = variants_iter
        self._stream_fn = stream_fn
        self.retry_failures = []

    @property
    def model(self) -> "RetryModel":
        """A RetryModel with parameters matching this response."""
        return self._current_variant

    async def _reset_stream(self, variant: "RetryModel") -> None:
        """Reset to a fresh stream for a new retry attempt."""
        new_stream = await self._stream_fn(variant.get_active_model())
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
        config = self._current_variant.retry_config
        try:
            async for chunk in super().chunk_stream():
                yield chunk
        except config.retry_on as e:
            failure = RetryFailure(
                model=self._current_variant.get_active_model(), exception=e
            )
            self.retry_failures.append(failure)

            # Try to get next variant (handles backoff and fallback)
            try:
                self._current_variant = await anext(self._variants_iter)
            except StopAsyncIteration:
                raise RetriesExhausted(self.retry_failures) from None

            await self._reset_stream(self._current_variant)

            raise StreamRestarted(
                failure=failure,
            ) from e

    @overload
    async def resume(
        self: "AsyncContextRetryStreamResponse[DepsT, None]",
        ctx: Context[DepsT],
        content: UserContent,
    ) -> "AsyncContextRetryStreamResponse[DepsT, None]": ...

    @overload
    async def resume(
        self: "AsyncContextRetryStreamResponse[DepsT, FormattableT]",
        ctx: Context[DepsT],
        content: UserContent,
    ) -> "AsyncContextRetryStreamResponse[DepsT, FormattableT]": ...

    async def resume(
        self, ctx: Context[DepsT], content: UserContent
    ) -> "AsyncContextRetryStreamResponse[DepsT, None] | AsyncContextRetryStreamResponse[DepsT, FormattableT]":
        """Generate a new AsyncContextRetryStreamResponse using this response's messages with additional user content."""
        return await self.model.context_resume_stream_async(
            ctx=ctx, response=self, content=content
        )
