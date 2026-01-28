"""RetryModel wraps Model to add retry logic."""

from collections.abc import Sequence
from typing import cast, overload

from ..formatting import Format, FormattableT, OutputParser
from ..messages import Message, UserContent
from ..models import Model, Params
from ..providers import ModelId
from ..responses import (
    AsyncResponse,
    Response,
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
from .retry_utils import with_retry, with_retry_async


class RetryModel:
    """Wraps a Model with retry logic.

    This class delegates all calls to the underlying Model, but returns RetryResponse
    instances instead of Response instances. In the future, it will implement actual
    retry logic for handling failures, rate limits, and validation errors.
    """

    wrapped_model: Model
    """The underlying Model wrapped with retry behavior."""

    retry_config: RetryConfig
    """The RetryConfig specifying retry behavior."""

    def __init__(
        self,
        model: Model,
        retry_config: RetryConfig,
    ) -> None:
        """Initialize a RetryModel.

        Args:
            model: The underlying Model to wrap with retry logic.
            config: Configuration for retry behavior.
        """
        self.wrapped_model = model
        self.retry_config = retry_config

    @property
    def model_id(self) -> ModelId:
        """The model being used (e.g. "openai/gpt-4o-mini")."""
        return self.wrapped_model.model_id

    @property
    def params(self) -> Params:
        """The default parameters for the model."""
        return self.wrapped_model.params

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
        format: type[FormattableT] | Format[FormattableT],
    ) -> RetryResponse[FormattableT]: ...

    @overload
    def call(
        self,
        content: UserContent | Sequence[Message],
        *,
        tools: Tools | None = None,
        format: type[FormattableT]
        | Format[FormattableT]
        | OutputParser[FormattableT]
        | None,
    ) -> RetryResponse[None] | RetryResponse[FormattableT]: ...

    def call(
        self,
        content: UserContent | Sequence[Message],
        *,
        tools: Tools | None = None,
        format: type[FormattableT]
        | Format[FormattableT]
        | OutputParser[FormattableT]
        | None = None,
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
            lambda: self.wrapped_model.call(
                content=content, tools=tools, format=format
            ),
            self.retry_config,
        )
        # The overloads ensure type safety; cast needed due to union in implementation
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
        format: type[FormattableT] | Format[FormattableT],
    ) -> AsyncRetryResponse[FormattableT]: ...

    @overload
    async def call_async(
        self,
        content: UserContent | Sequence[Message],
        *,
        tools: AsyncTools | None = None,
        format: type[FormattableT]
        | Format[FormattableT]
        | OutputParser[FormattableT]
        | None,
    ) -> AsyncRetryResponse[None] | AsyncRetryResponse[FormattableT]: ...

    async def call_async(
        self,
        content: UserContent | Sequence[Message],
        *,
        tools: AsyncTools | None = None,
        format: type[FormattableT]
        | Format[FormattableT]
        | OutputParser[FormattableT]
        | None = None,
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
            lambda: self.wrapped_model.call_async(
                content=content, tools=tools, format=format
            ),
            self.retry_config,
        )
        # The overloads ensure type safety; cast needed due to union in implementation
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
            lambda: self.wrapped_model.resume(response=response, content=content),
            self.retry_config,
        )
        # The overloads ensure type safety; cast needed due to union in implementation
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
            lambda: self.wrapped_model.resume_async(response=response, content=content),
            self.retry_config,
        )
        # The overloads ensure type safety; cast needed due to union in implementation
        return AsyncRetryResponse(
            response=cast("AsyncResponse[FormattableT]", new_response),
            retry_config=self.retry_config,
            retry_state=retry_state,
        )
