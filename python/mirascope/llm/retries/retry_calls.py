"""RetryCall wraps Call to return RetryResponse instead of Response."""

from dataclasses import dataclass
from typing import Generic, overload

from ..calls import AsyncCall, Call, CallT
from ..formatting import FormattableT
from ..types import P
from .retry_config import RetryConfig
from .retry_models import RetryModel
from .retry_prompts import (
    AsyncRetryPrompt,
    RetryPrompt,
)
from .retry_responses import (
    AsyncRetryResponse,
    RetryResponse,
)


@dataclass
class BaseRetryCall(Generic[CallT]):
    """Base class for all RetryCall types with shared model functionality."""

    wrapped_call: CallT
    """The underlying call that is wrapped with retry behavior."""

    config: RetryConfig
    """Configuration for retry behavior."""

    @property
    def default_model(self) -> RetryModel:
        """The default model that will be used if no model is set in context."""
        return RetryModel(self.wrapped_call.default_model, self.config)

    @property
    def model(self) -> RetryModel:
        """The model used for generating responses. May be overwritten via `with llm.model(...)`."""
        return RetryModel(self.wrapped_call.model, self.config)


@dataclass
class RetryCall(BaseRetryCall[Call[P, FormattableT]], Generic[P, FormattableT]):
    """A retry-enabled call that wraps a Call and returns RetryResponse.

    This wraps an existing Call, adding retry logic around the underlying call.
    All operations return Retry* response types instead of regular response types.

    The model can be overridden at runtime using `with llm.model(...)` context manager.
    """

    @property
    def prompt(self) -> RetryPrompt[P, FormattableT]:
        """The RetryPrompt powering the RetryCall."""
        return RetryPrompt(
            wrapped_prompt=self.wrapped_call.prompt, retry_config=self.config
        )

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


@dataclass
class AsyncRetryCall(
    BaseRetryCall[AsyncCall[P, FormattableT]], Generic[P, FormattableT]
):
    """An async retry-enabled call that wraps an AsyncCall and returns AsyncRetryResponse.

    This wraps an existing AsyncCall, adding retry logic around the underlying call.
    All operations return Retry* response types instead of regular response types.

    The model can be overridden at runtime using `with llm.model(...)` context manager.
    """

    @property
    def prompt(self) -> AsyncRetryPrompt[P, FormattableT]:
        """The AsyncRetryPrompt powering the AsyncRetryCall."""
        return AsyncRetryPrompt(
            wrapped_prompt=self.wrapped_call.prompt, retry_config=self.config
        )

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
