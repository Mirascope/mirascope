"""Retry response classes that extend base responses with retry metadata."""

from typing import TYPE_CHECKING, overload

from ..formatting import FormattableT
from ..messages import UserContent
from ..responses import (
    AsyncResponse,
    Response,
)
from .retry_config import RetryConfig
from .utils import RetryState

if TYPE_CHECKING:
    from .retry_models import RetryModel


class RetryResponse(Response[FormattableT]):
    """Response that includes retry metadata.

    Extends `Response` directly, copying all attributes from a wrapped response
    and adding retry configuration.
    """

    retry_config: RetryConfig
    """Configuration for retry behavior."""

    retry_state: RetryState
    """State tracking retry attempts and any exceptions caught."""

    def __init__(
        self,
        response: Response[FormattableT],
        retry_config: RetryConfig,
        retry_state: RetryState,
    ) -> None:
        """Initialize a RetryResponse.

        Args:
            response: The successful response from the LLM.
            retry_config: Configuration for retry behavior.
            retry_state: State tracking retry attempts and exceptions.
        """
        # Copy all attributes from the wrapped response
        for key, value in response.__dict__.items():
            object.__setattr__(self, key, value)
        self.retry_config = retry_config
        self.retry_state = retry_state

    @property
    def model(self) -> "RetryModel":
        """A RetryModel with parameters matching this response."""
        from .retry_models import RetryModel

        base_model = super().model
        return RetryModel(base_model, retry_config=self.retry_config)

    @overload
    def resume(
        self: "RetryResponse[None]", content: UserContent
    ) -> "RetryResponse[None]": ...

    @overload
    def resume(
        self: "RetryResponse[FormattableT]", content: UserContent
    ) -> "RetryResponse[FormattableT]": ...

    def resume(
        self, content: UserContent
    ) -> "RetryResponse[None] | RetryResponse[FormattableT]":
        """Generate a new RetryResponse using this response's messages with additional user content.

        Args:
            content: The new user message content to append to the message history.

        Returns:
            A new RetryResponse instance generated from the extended message history.
        """
        return self.model.resume(response=self, content=content)


class AsyncRetryResponse(AsyncResponse[FormattableT]):
    """Async response that includes retry metadata.

    Extends `AsyncResponse` directly, copying all attributes from a wrapped response
    and adding retry configuration.
    """

    retry_config: RetryConfig
    """Configuration for retry behavior."""

    retry_state: RetryState
    """State tracking retry attempts and any exceptions caught."""

    def __init__(
        self,
        response: AsyncResponse[FormattableT],
        retry_config: RetryConfig,
        retry_state: RetryState,
    ) -> None:
        """Initialize an AsyncRetryResponse.

        Args:
            response: The successful async response from the LLM.
            retry_config: Configuration for retry behavior.
            retry_state: State tracking retry attempts and exceptions.
        """
        # Copy all attributes from the wrapped response
        for key, value in response.__dict__.items():
            object.__setattr__(self, key, value)
        self.retry_config = retry_config
        self.retry_state = retry_state

    @property
    def model(self) -> "RetryModel":
        """A RetryModel with parameters matching this response."""
        from .retry_models import RetryModel

        base_model = super().model
        return RetryModel(base_model, retry_config=self.retry_config)

    @overload
    async def resume(
        self: "AsyncRetryResponse[None]", content: UserContent
    ) -> "AsyncRetryResponse[None]": ...

    @overload
    async def resume(
        self: "AsyncRetryResponse[FormattableT]", content: UserContent
    ) -> "AsyncRetryResponse[FormattableT]": ...

    async def resume(
        self, content: UserContent
    ) -> "AsyncRetryResponse[None] | AsyncRetryResponse[FormattableT]":
        """Generate a new AsyncRetryResponse using this response's messages with additional user content.

        Args:
            content: The new user message content to append to the message history.

        Returns:
            A new AsyncRetryResponse instance generated from the extended message history.
        """
        return await self.model.resume_async(response=self, content=content)
