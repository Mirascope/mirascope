"""RetryModel wraps Model to add retry logic."""

from collections.abc import Sequence
from typing import overload

from ..formatting import Format, FormattableT
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
        *,
        content: UserContent | Sequence[Message],
        tools: Tools | None = None,
        format: None = None,
    ) -> RetryResponse[None]: ...

    @overload
    def call(
        self,
        *,
        content: UserContent | Sequence[Message],
        tools: Tools | None = None,
        format: type[FormattableT] | Format[FormattableT],
    ) -> RetryResponse[FormattableT]: ...

    @overload
    def call(
        self,
        *,
        content: UserContent | Sequence[Message],
        tools: Tools | None = None,
        format: type[FormattableT] | Format[FormattableT] | None,
    ) -> RetryResponse[None] | RetryResponse[FormattableT]: ...

    def call(
        self,
        *,
        content: UserContent | Sequence[Message],
        tools: Tools | None = None,
        format: type[FormattableT] | Format[FormattableT] | None = None,
    ) -> RetryResponse[None] | RetryResponse[FormattableT]:
        """Generate a RetryResponse by calling this model's LLM provider.

        Args:
            content: User content or LLM messages to send to the LLM.
            tools: Optional tools that the model may invoke.
            format: Optional response format specifier.

        Returns:
            A RetryResponse object containing the LLM-generated content and retry metadata.
        """
        # TODO: Wire in retry implementation
        response = self.wrapped_model.call(content=content, tools=tools, format=format)
        return RetryResponse(response=response, retry_config=self.retry_config)  # pyright: ignore[reportArgumentType]

    @overload
    async def call_async(
        self,
        *,
        content: UserContent | Sequence[Message],
        tools: AsyncTools | None = None,
        format: None = None,
    ) -> AsyncRetryResponse[None]: ...

    @overload
    async def call_async(
        self,
        *,
        content: UserContent | Sequence[Message],
        tools: AsyncTools | None = None,
        format: type[FormattableT] | Format[FormattableT],
    ) -> AsyncRetryResponse[FormattableT]: ...

    @overload
    async def call_async(
        self,
        *,
        content: UserContent | Sequence[Message],
        tools: AsyncTools | None = None,
        format: type[FormattableT] | Format[FormattableT] | None,
    ) -> AsyncRetryResponse[None] | AsyncRetryResponse[FormattableT]: ...

    async def call_async(
        self,
        *,
        content: UserContent | Sequence[Message],
        tools: AsyncTools | None = None,
        format: type[FormattableT] | Format[FormattableT] | None = None,
    ) -> AsyncRetryResponse[None] | AsyncRetryResponse[FormattableT]:
        """Generate an AsyncRetryResponse by asynchronously calling this model's LLM provider.

        Args:
            content: User content or LLM messages to send to the LLM.
            tools: Optional tools that the model may invoke.
            format: Optional response format specifier.

        Returns:
            An AsyncRetryResponse object containing the LLM-generated content and retry metadata.
        """
        # TODO: Wire in retry implementation
        response = await self.wrapped_model.call_async(
            content=content, tools=tools, format=format
        )
        return AsyncRetryResponse(response=response, retry_config=self.retry_config)  # pyright: ignore[reportArgumentType]

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
        """
        # TODO: Wire in retry implementation
        new_response = self.wrapped_model.resume(response=response, content=content)
        return RetryResponse(response=new_response, retry_config=self.retry_config)  # pyright: ignore[reportArgumentType]

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
        """
        # TODO: Wire in retry implementation
        new_response = await self.wrapped_model.resume_async(
            response=response, content=content
        )
        return AsyncRetryResponse(response=new_response, retry_config=self.retry_config)  # pyright: ignore[reportArgumentType]
