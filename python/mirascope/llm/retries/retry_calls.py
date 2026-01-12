"""RetryCall extends Call to return RetryResponse instead of Response."""

from typing import Generic, TypeVar, overload

from ..calls.calls import BaseCall
from ..formatting import FormattableT
from ..types import P
from .retry_config import RetryConfig
from .retry_models import RetryModel
from .retry_prompts import (
    AsyncRetryPrompt,
    BaseRetryPrompt,
    RetryPrompt,
)
from .retry_responses import (
    AsyncRetryResponse,
    RetryResponse,
)

RetryPromptT = TypeVar("RetryPromptT", bound=BaseRetryPrompt)


class BaseRetryCall(BaseCall[RetryPromptT], Generic[RetryPromptT]):
    """Base class for retry-enabled calls with shared model wrapping."""

    @property
    def retry_config(self) -> RetryConfig:
        """The retry configuration from the prompt."""
        return self.prompt.retry_config

    @property
    def model(self) -> RetryModel:
        """The model used for generating responses. May be overwritten via `with llm.model(...)`."""
        model = super().model
        if isinstance(model, RetryModel):
            return model
        return RetryModel(model, self.retry_config)


class RetryCall(BaseRetryCall[RetryPrompt[P, FormattableT]], Generic[P, FormattableT]):
    """A retry-enabled call that extends BaseRetryCall and returns RetryResponse.

    This extends BaseRetryCall with a RetryPrompt and returns RetryResponse
    instead of Response. The prompt contains the retry configuration.

    The model can be overridden at runtime using `with llm.model(...)` context manager.
    """

    @overload
    def __call__(
        self: "RetryCall[P, None]", *args: P.args, **kwargs: P.kwargs
    ) -> RetryResponse[None]: ...

    @overload
    def __call__(
        self: "RetryCall[P, FormattableT]", *args: P.args, **kwargs: P.kwargs
    ) -> RetryResponse[FormattableT]: ...

    def __call__(
        self, *args: P.args, **kwargs: P.kwargs
    ) -> RetryResponse[None] | RetryResponse[FormattableT]:
        """Generates a retry response using the LLM."""
        return self.call(*args, **kwargs)

    @overload
    def call(
        self: "RetryCall[P, None]", *args: P.args, **kwargs: P.kwargs
    ) -> RetryResponse[None]: ...

    @overload
    def call(
        self: "RetryCall[P, FormattableT]", *args: P.args, **kwargs: P.kwargs
    ) -> RetryResponse[FormattableT]: ...

    def call(
        self, *args: P.args, **kwargs: P.kwargs
    ) -> RetryResponse[None] | RetryResponse[FormattableT]:
        """Generates a retry response using the LLM."""
        return self.prompt.call(self.model, *args, **kwargs)


class AsyncRetryCall(
    BaseRetryCall[AsyncRetryPrompt[P, FormattableT]], Generic[P, FormattableT]
):
    """An async retry-enabled call that extends BaseRetryCall and returns AsyncRetryResponse.

    This extends BaseRetryCall with an AsyncRetryPrompt and returns AsyncRetryResponse
    instead of AsyncResponse. The prompt contains the retry configuration.

    The model can be overridden at runtime using `with llm.model(...)` context manager.
    """

    @overload
    async def __call__(
        self: "AsyncRetryCall[P, None]", *args: P.args, **kwargs: P.kwargs
    ) -> AsyncRetryResponse[None]: ...

    @overload
    async def __call__(
        self: "AsyncRetryCall[P, FormattableT]", *args: P.args, **kwargs: P.kwargs
    ) -> AsyncRetryResponse[FormattableT]: ...

    async def __call__(
        self, *args: P.args, **kwargs: P.kwargs
    ) -> AsyncRetryResponse[None] | AsyncRetryResponse[FormattableT]:
        """Generates a retry response using the LLM asynchronously."""
        return await self.call(*args, **kwargs)

    @overload
    async def call(
        self: "AsyncRetryCall[P, None]", *args: P.args, **kwargs: P.kwargs
    ) -> AsyncRetryResponse[None]: ...

    @overload
    async def call(
        self: "AsyncRetryCall[P, FormattableT]", *args: P.args, **kwargs: P.kwargs
    ) -> AsyncRetryResponse[FormattableT]: ...

    async def call(
        self, *args: P.args, **kwargs: P.kwargs
    ) -> AsyncRetryResponse[None] | AsyncRetryResponse[FormattableT]:
        """Generates a retry response using the LLM asynchronously."""
        return await self.prompt.call(self.model, *args, **kwargs)
