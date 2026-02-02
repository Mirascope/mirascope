"""RetryModel extends Model to add retry logic."""

from collections.abc import Awaitable, Sequence
from typing import cast, overload
from typing_extensions import Unpack

from ..formatting import FormatSpec, FormattableT
from ..messages import Message, UserContent
from ..models import Model, Params
from ..providers import ModelId
from ..responses import (
    AsyncResponse,
    AsyncStreamResponse,
    Response,
    StreamResponse,
)
from ..tools import (
    AsyncTools,
    Tools,
)
from .retry_config import RetryConfig
from .retry_responses import (
    AsyncRetryResponse,
    RetryResponse,
)
from .retry_stream_responses import (
    AsyncRetryStreamResponse,
    RetryStreamResponse,
)
from .utils import with_retry, with_retry_async


class RetryModel(Model):
    """Extends Model with retry logic.

    This class inherits from Model and overrides call methods to return RetryResponse
    instances instead of Response instances. It implements retry logic for handling
    failures, rate limits, and validation errors.
    """

    retry_config: RetryConfig
    """The RetryConfig specifying retry behavior."""

    @overload
    def __init__(
        self,
        model: Model,
        retry_config: RetryConfig,
    ) -> None:
        """Wrap an existing Model with retry logic."""
        ...

    @overload
    def __init__(
        self,
        model: ModelId,
        retry_config: RetryConfig,
        **params: Unpack[Params],
    ) -> None:
        """Create a RetryModel from a ModelId with optional params."""
        ...

    def __init__(
        self,
        model: Model | ModelId,
        retry_config: RetryConfig,
        **params: Unpack[Params],
    ) -> None:
        """Initialize a RetryModel.

        Args:
            model: Either a Model instance to wrap, or a ModelId string to create
                a new Model from.
            retry_config: Configuration for retry behavior.
            **params: Additional parameters for the model. Only used when `model`
                is a ModelId string; ignored when wrapping an existing Model.
        """
        if isinstance(model, Model):
            # Wrap existing Model - copy its model_id and params
            super().__init__(model.model_id, **model.params)
        else:
            # Create from ModelId
            super().__init__(model, **params)
        self.retry_config = retry_config

    @overload
    def call(
        self,
        content: UserContent | Sequence[Message],
        *,
        tools: Tools | None = None,
        format: None = None,
    ) -> RetryResponse[None]: ...

    @overload
    def call(
        self,
        content: UserContent | Sequence[Message],
        *,
        tools: Tools | None = None,
        format: FormatSpec[FormattableT],
    ) -> RetryResponse[FormattableT]: ...

    @overload
    def call(
        self,
        content: UserContent | Sequence[Message],
        *,
        tools: Tools | None = None,
        format: FormatSpec[FormattableT] | None,
    ) -> RetryResponse[None] | RetryResponse[FormattableT]: ...

    def call(
        self,
        content: UserContent | Sequence[Message],
        *,
        tools: Tools | None = None,
        format: FormatSpec[FormattableT] | None = None,
    ) -> RetryResponse[None] | RetryResponse[FormattableT]:
        """Generate a RetryResponse by calling this model's LLM provider.

        Args:
            content: User content or LLM messages to send to the LLM.
            tools: Optional tools that the model may invoke.
            format: Optional response format specifier.

        Returns:
            A RetryResponse object containing the LLM-generated content and retry metadata.

        Raises:
            Exception: The last exception encountered if all retry attempts fail.
        """
        response, retry_state = with_retry(
            lambda: super(RetryModel, self).call(content, tools=tools, format=format),
            self.retry_config,
        )
        return RetryResponse(
            response=cast("Response[FormattableT]", response),
            retry_config=self.retry_config,
            retry_state=retry_state,
        )

    @overload
    async def call_async(
        self,
        content: UserContent | Sequence[Message],
        *,
        tools: AsyncTools | None = None,
        format: None = None,
    ) -> AsyncRetryResponse[None]: ...

    @overload
    async def call_async(
        self,
        content: UserContent | Sequence[Message],
        *,
        tools: AsyncTools | None = None,
        format: FormatSpec[FormattableT],
    ) -> AsyncRetryResponse[FormattableT]: ...

    @overload
    async def call_async(
        self,
        content: UserContent | Sequence[Message],
        *,
        tools: AsyncTools | None = None,
        format: FormatSpec[FormattableT] | None,
    ) -> AsyncRetryResponse[None] | AsyncRetryResponse[FormattableT]: ...

    async def call_async(
        self,
        content: UserContent | Sequence[Message],
        *,
        tools: AsyncTools | None = None,
        format: FormatSpec[FormattableT] | None = None,
    ) -> AsyncRetryResponse[None] | AsyncRetryResponse[FormattableT]:
        """Generate an AsyncRetryResponse by asynchronously calling this model's LLM provider.

        Args:
            content: User content or LLM messages to send to the LLM.
            tools: Optional tools that the model may invoke.
            format: Optional response format specifier.

        Returns:
            An AsyncRetryResponse object containing the LLM-generated content and retry metadata.

        Raises:
            Exception: The last exception encountered if all retry attempts fail.
        """
        response, retry_state = await with_retry_async(
            lambda: super(RetryModel, self).call_async(
                content, tools=tools, format=format
            ),
            self.retry_config,
        )
        return AsyncRetryResponse(
            response=cast("AsyncResponse[FormattableT]", response),
            retry_config=self.retry_config,
            retry_state=retry_state,
        )

    # Resume methods

    @overload
    def resume(
        self,
        *,
        response: Response[None],
        content: UserContent,
    ) -> RetryResponse[None]: ...

    @overload
    def resume(
        self,
        *,
        response: Response[FormattableT],
        content: UserContent,
    ) -> RetryResponse[FormattableT]: ...

    @overload
    def resume(
        self,
        *,
        response: Response[None] | Response[FormattableT],
        content: UserContent,
    ) -> RetryResponse[None] | RetryResponse[FormattableT]: ...

    def resume(
        self,
        *,
        response: Response[None] | Response[FormattableT],
        content: UserContent,
    ) -> RetryResponse[None] | RetryResponse[FormattableT]:
        """Generate a new RetryResponse by extending another response's messages.

        Args:
            response: Previous response to extend.
            content: Additional user content to append.

        Returns:
            A new RetryResponse containing the extended conversation.

        Raises:
            Exception: The last exception encountered if all retry attempts fail.
        """
        new_response, retry_state = with_retry(
            lambda: super(RetryModel, self).resume(response=response, content=content),
            self.retry_config,
        )
        return RetryResponse(
            response=cast("Response[FormattableT]", new_response),
            retry_config=self.retry_config,
            retry_state=retry_state,
        )

    @overload
    async def resume_async(
        self,
        *,
        response: AsyncResponse[None],
        content: UserContent,
    ) -> AsyncRetryResponse[None]: ...

    @overload
    async def resume_async(
        self,
        *,
        response: AsyncResponse[FormattableT],
        content: UserContent,
    ) -> AsyncRetryResponse[FormattableT]: ...

    @overload
    async def resume_async(
        self,
        *,
        response: AsyncResponse[None] | AsyncResponse[FormattableT],
        content: UserContent,
    ) -> AsyncRetryResponse[None] | AsyncRetryResponse[FormattableT]: ...

    async def resume_async(
        self,
        *,
        response: AsyncResponse[None] | AsyncResponse[FormattableT],
        content: UserContent,
    ) -> AsyncRetryResponse[None] | AsyncRetryResponse[FormattableT]:
        """Generate a new AsyncRetryResponse by extending another response's messages.

        Args:
            response: Previous async response to extend.
            content: Additional user content to append.

        Returns:
            A new AsyncRetryResponse containing the extended conversation.

        Raises:
            Exception: The last exception encountered if all retry attempts fail.
        """
        new_response, retry_state = await with_retry_async(
            lambda: super(RetryModel, self).resume_async(
                response=response, content=content
            ),
            self.retry_config,
        )
        return AsyncRetryResponse(
            response=cast("AsyncResponse[FormattableT]", new_response),
            retry_config=self.retry_config,
            retry_state=retry_state,
        )

    # Stream methods

    @overload
    def stream(
        self,
        content: UserContent | Sequence[Message],
        *,
        tools: Tools | None = None,
        format: None = None,
    ) -> RetryStreamResponse[None]: ...

    @overload
    def stream(
        self,
        content: UserContent | Sequence[Message],
        *,
        tools: Tools | None = None,
        format: FormatSpec[FormattableT],
    ) -> RetryStreamResponse[FormattableT]: ...

    @overload
    def stream(
        self,
        content: UserContent | Sequence[Message],
        *,
        tools: Tools | None = None,
        format: FormatSpec[FormattableT] | None,
    ) -> RetryStreamResponse[None] | RetryStreamResponse[FormattableT]: ...

    def stream(
        self,
        content: UserContent | Sequence[Message],
        *,
        tools: Tools | None = None,
        format: FormatSpec[FormattableT] | None = None,
    ) -> RetryStreamResponse[None] | RetryStreamResponse[FormattableT]:
        """Generate a RetryStreamResponse by streaming from this model's LLM provider.

        The returned response supports automatic retry on failure. If a retryable
        error occurs during iteration, a `StreamRestarted` exception is raised
        and the user can re-iterate to continue from the new attempt.

        Args:
            content: User content or LLM messages to send to the LLM.
            tools: Optional tools that the model may invoke.
            format: Optional response format specifier.

        Returns:
            A RetryStreamResponse for iterating over the LLM-generated content.
        """
        return RetryStreamResponse(
            self,
            lambda m: cast(
                "StreamResponse[FormattableT]",
                Model.stream(m, content=content, tools=tools, format=format),
            ),
        )

    @overload
    async def stream_async(
        self,
        content: UserContent | Sequence[Message],
        *,
        tools: AsyncTools | None = None,
        format: None = None,
    ) -> AsyncRetryStreamResponse[None]: ...

    @overload
    async def stream_async(
        self,
        content: UserContent | Sequence[Message],
        *,
        tools: AsyncTools | None = None,
        format: FormatSpec[FormattableT],
    ) -> AsyncRetryStreamResponse[FormattableT]: ...

    @overload
    async def stream_async(
        self,
        content: UserContent | Sequence[Message],
        *,
        tools: AsyncTools | None = None,
        format: FormatSpec[FormattableT] | None,
    ) -> AsyncRetryStreamResponse[None] | AsyncRetryStreamResponse[FormattableT]: ...

    async def stream_async(
        self,
        content: UserContent | Sequence[Message],
        *,
        tools: AsyncTools | None = None,
        format: FormatSpec[FormattableT] | None = None,
    ) -> AsyncRetryStreamResponse[None] | AsyncRetryStreamResponse[FormattableT]:
        """Generate an AsyncRetryStreamResponse by streaming from this model's LLM provider.

        The returned response supports automatic retry on failure. If a retryable
        error occurs during iteration, a `StreamRestarted` exception is raised
        and the user can re-iterate to continue from the new attempt.

        Args:
            content: User content or LLM messages to send to the LLM.
            tools: Optional tools that the model may invoke.
            format: Optional response format specifier.

        Returns:
            An AsyncRetryStreamResponse for asynchronously iterating over the LLM-generated content.
        """

        def stream_fn(m: Model) -> Awaitable[AsyncStreamResponse[FormattableT]]:
            return cast(
                "Awaitable[AsyncStreamResponse[FormattableT]]",
                Model.stream_async(m, content=content, tools=tools, format=format),
            )

        initial_stream = await stream_fn(self)
        return AsyncRetryStreamResponse(self, stream_fn, initial_stream)

    # Resume stream methods

    @overload
    def resume_stream(
        self,
        *,
        response: StreamResponse,
        content: UserContent,
    ) -> RetryStreamResponse[None]: ...

    @overload
    def resume_stream(
        self,
        *,
        response: StreamResponse[FormattableT],
        content: UserContent,
    ) -> RetryStreamResponse[FormattableT]: ...

    @overload
    def resume_stream(
        self,
        *,
        response: StreamResponse | StreamResponse[FormattableT],
        content: UserContent,
    ) -> RetryStreamResponse[None] | RetryStreamResponse[FormattableT]: ...

    def resume_stream(
        self,
        *,
        response: StreamResponse | StreamResponse[FormattableT],
        content: UserContent,
    ) -> RetryStreamResponse[None] | RetryStreamResponse[FormattableT]:
        """Generate a new RetryStreamResponse by extending another response's messages.

        Args:
            response: Previous stream response to extend.
            content: Additional user content to append.

        Returns:
            A new RetryStreamResponse for streaming the extended conversation.
        """
        return RetryStreamResponse(
            self,
            lambda m: cast(
                "StreamResponse[FormattableT]",
                Model.resume_stream(m, response=response, content=content),
            ),
        )

    @overload
    async def resume_stream_async(
        self,
        *,
        response: AsyncStreamResponse,
        content: UserContent,
    ) -> AsyncRetryStreamResponse[None]: ...

    @overload
    async def resume_stream_async(
        self,
        *,
        response: AsyncStreamResponse[FormattableT],
        content: UserContent,
    ) -> AsyncRetryStreamResponse[FormattableT]: ...

    @overload
    async def resume_stream_async(
        self,
        *,
        response: AsyncStreamResponse | AsyncStreamResponse[FormattableT],
        content: UserContent,
    ) -> AsyncRetryStreamResponse[None] | AsyncRetryStreamResponse[FormattableT]: ...

    async def resume_stream_async(
        self,
        *,
        response: AsyncStreamResponse | AsyncStreamResponse[FormattableT],
        content: UserContent,
    ) -> AsyncRetryStreamResponse[None] | AsyncRetryStreamResponse[FormattableT]:
        """Generate a new AsyncRetryStreamResponse by extending another response's messages.

        Args:
            response: Previous async stream response to extend.
            content: Additional user content to append.

        Returns:
            A new AsyncRetryStreamResponse for asynchronously streaming the extended conversation.
        """

        def stream_fn(m: Model) -> Awaitable[AsyncStreamResponse[FormattableT]]:
            return cast(
                "Awaitable[AsyncStreamResponse[FormattableT]]",
                Model.resume_stream_async(m, response=response, content=content),
            )

        initial_stream = await stream_fn(self)
        return AsyncRetryStreamResponse(self, stream_fn, initial_stream)
