"""Retry response classes that extend base responses with retry metadata."""

from typing import TYPE_CHECKING, Generic, overload

from ..context import Context, DepsT
from ..formatting import FormattableT
from ..messages import UserContent
from ..responses import (
    AsyncContextResponse,
    AsyncResponse,
    ContextResponse,
    Response,
)
from .utils import RetryFailure

if TYPE_CHECKING:
    from .retry_models import RetryModel


class RetryResponse(Response[FormattableT]):
    """Response that includes retry metadata.

    Extends `Response` directly, copying all attributes from a wrapped response
    and adding retry configuration. The `model` property returns a `RetryModel`
    with the successful model as the active model.
    """

    _retry_model: "RetryModel"
    """The RetryModel with the successful model as active."""

    retry_failures: list[RetryFailure]
    """Failed attempts before the successful one (empty if first attempt succeeded)."""

    def __init__(
        self,
        response: Response[FormattableT],
        retry_model: "RetryModel",
        retry_failures: list[RetryFailure],
    ) -> None:
        """Initialize a RetryResponse.

        Args:
            response: The successful response from the LLM.
            retry_model: RetryModel with the successful model as active.
            retry_failures: List of failed attempts before success.
        """
        # Copy all attributes from the wrapped response
        for key, value in response.__dict__.items():
            object.__setattr__(self, key, value)
        self._retry_model = retry_model
        self.retry_failures = retry_failures

    @property
    def model(self) -> "RetryModel":
        """A RetryModel with the successful model as active.

        This RetryModel has the same pool of available models, but with the
        model that succeeded set as the active model. This means:
        - `response.model.model_id` equals `response.model_id`
        - `response.resume()` will try the successful model first
        """
        return self._retry_model

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
    and adding retry configuration. The `model` property returns a `RetryModel`
    with the successful model as the active model.
    """

    _retry_model: "RetryModel"
    """The RetryModel with the successful model as active."""

    retry_failures: list[RetryFailure]
    """Failed attempts before the successful one (empty if first attempt succeeded)."""

    def __init__(
        self,
        response: AsyncResponse[FormattableT],
        retry_model: "RetryModel",
        retry_failures: list[RetryFailure],
    ) -> None:
        """Initialize an AsyncRetryResponse.

        Args:
            response: The successful async response from the LLM.
            retry_model: RetryModel with the successful model as active.
            retry_failures: List of failed attempts before success.
        """
        # Copy all attributes from the wrapped response
        for key, value in response.__dict__.items():
            object.__setattr__(self, key, value)
        self._retry_model = retry_model
        self.retry_failures = retry_failures

    @property
    def model(self) -> "RetryModel":
        """A RetryModel with the successful model as active.

        This RetryModel has the same pool of available models, but with the
        model that succeeded set as the active model. This means:
        - `response.model.model_id` equals `response.model_id`
        - `response.resume()` will try the successful model first
        """
        return self._retry_model

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


class ContextRetryResponse(
    ContextResponse[DepsT, FormattableT], Generic[DepsT, FormattableT]
):
    """Context response that includes retry metadata.

    Extends `ContextResponse` directly, copying all attributes from a wrapped response
    and adding retry configuration. The `model` property returns a `RetryModel`
    with the successful model as the active model.
    """

    _retry_model: "RetryModel"
    """The RetryModel with the successful model as active."""

    retry_failures: list[RetryFailure]
    """Failed attempts before the successful one (empty if first attempt succeeded)."""

    def __init__(
        self,
        response: ContextResponse[DepsT, FormattableT],
        retry_model: "RetryModel",
        retry_failures: list[RetryFailure],
    ) -> None:
        """Initialize a ContextRetryResponse.

        Args:
            response: The successful context response from the LLM.
            retry_model: RetryModel with the successful model as active.
            retry_failures: List of failed attempts before success.
        """
        # Copy all attributes from the wrapped response
        for key, value in response.__dict__.items():
            object.__setattr__(self, key, value)
        self._retry_model = retry_model
        self.retry_failures = retry_failures

    @property
    def model(self) -> "RetryModel":
        """A RetryModel with the successful model as active.

        This RetryModel has the same pool of available models, but with the
        model that succeeded set as the active model. This means:
        - `response.model.model_id` equals `response.model_id`
        - `response.resume()` will try the successful model first
        """
        return self._retry_model

    @overload
    def resume(
        self: "ContextRetryResponse[DepsT, None]",
        ctx: Context[DepsT],
        content: UserContent,
    ) -> "ContextRetryResponse[DepsT, None]": ...

    @overload
    def resume(
        self: "ContextRetryResponse[DepsT, FormattableT]",
        ctx: Context[DepsT],
        content: UserContent,
    ) -> "ContextRetryResponse[DepsT, FormattableT]": ...

    def resume(
        self, ctx: Context[DepsT], content: UserContent
    ) -> (
        "ContextRetryResponse[DepsT, None] | ContextRetryResponse[DepsT, FormattableT]"
    ):
        """Generate a new ContextRetryResponse using this response's messages with additional user content.

        Args:
            ctx: A `Context` with the required deps type.
            content: The new user message content to append to the message history.

        Returns:
            A new ContextRetryResponse instance generated from the extended message history.
        """
        return self.model.context_resume(ctx=ctx, response=self, content=content)


class AsyncContextRetryResponse(
    AsyncContextResponse[DepsT, FormattableT], Generic[DepsT, FormattableT]
):
    """Async context response that includes retry metadata.

    Extends `AsyncContextResponse` directly, copying all attributes from a wrapped response
    and adding retry configuration. The `model` property returns a `RetryModel`
    with the successful model as the active model.
    """

    _retry_model: "RetryModel"
    """The RetryModel with the successful model as active."""

    retry_failures: list[RetryFailure]
    """Failed attempts before the successful one (empty if first attempt succeeded)."""

    def __init__(
        self,
        response: AsyncContextResponse[DepsT, FormattableT],
        retry_model: "RetryModel",
        retry_failures: list[RetryFailure],
    ) -> None:
        """Initialize an AsyncContextRetryResponse.

        Args:
            response: The successful async context response from the LLM.
            retry_model: RetryModel with the successful model as active.
            retry_failures: List of failed attempts before success.
        """
        # Copy all attributes from the wrapped response
        for key, value in response.__dict__.items():
            object.__setattr__(self, key, value)
        self._retry_model = retry_model
        self.retry_failures = retry_failures

    @property
    def model(self) -> "RetryModel":
        """A RetryModel with the successful model as active.

        This RetryModel has the same pool of available models, but with the
        model that succeeded set as the active model. This means:
        - `response.model.model_id` equals `response.model_id`
        - `response.resume()` will try the successful model first
        """
        return self._retry_model

    @overload
    async def resume(
        self: "AsyncContextRetryResponse[DepsT, None]",
        ctx: Context[DepsT],
        content: UserContent,
    ) -> "AsyncContextRetryResponse[DepsT, None]": ...

    @overload
    async def resume(
        self: "AsyncContextRetryResponse[DepsT, FormattableT]",
        ctx: Context[DepsT],
        content: UserContent,
    ) -> "AsyncContextRetryResponse[DepsT, FormattableT]": ...

    async def resume(
        self, ctx: Context[DepsT], content: UserContent
    ) -> "AsyncContextRetryResponse[DepsT, None] | AsyncContextRetryResponse[DepsT, FormattableT]":
        """Generate a new AsyncContextRetryResponse using this response's messages with additional user content.

        Args:
            ctx: A `Context` with the required deps type.
            content: The new user message content to append to the message history.

        Returns:
            A new AsyncContextRetryResponse instance generated from the extended message history.
        """
        return await self.model.context_resume_async(
            ctx=ctx, response=self, content=content
        )
