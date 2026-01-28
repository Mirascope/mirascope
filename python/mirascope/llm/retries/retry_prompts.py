"""RetryPrompt wraps Prompt to return RetryResponse instead of Response."""

from collections.abc import Sequence
from dataclasses import dataclass
from typing import Generic, overload

from ..formatting import Format, FormattableT, OutputParser
from ..messages import Message
from ..models import Model
from ..prompts import (
    AsyncPrompt,
    Prompt,
)
from ..prompts.protocols import (
    AsyncMessageTemplate,
    MessageTemplate,
)
from ..tools import AsyncToolkit, Toolkit
from ..types import P
from .retry_config import RetryConfig
from .retry_models import RetryModel
from .retry_responses import (
    AsyncRetryResponse,
    RetryResponse,
)


def _ensure_retry_model(model: Model | RetryModel, config: RetryConfig) -> RetryModel:
    """Ensure a model has retry capabilities, adding them if necessary."""
    if isinstance(model, RetryModel):
        return model
    return RetryModel(model=model, retry_config=config)


@dataclass
class RetryPrompt(Generic[P, FormattableT]):
    """A retry-enabled prompt that wraps a Prompt and returns RetryResponse.

    This wraps an existing Prompt and ensures that when called with a Model,
    it returns a RetryResponse instead of a Response. It handles wrapping the
    provided Model in a RetryModel if necessary.
    """

    wrapped_prompt: Prompt[P, FormattableT]
    """The underlying prompt being wrapped."""

    retry_config: RetryConfig
    """Configuration for retry behavior."""

    @property
    def fn(self) -> MessageTemplate[P]:
        """The underlying prompt function that generates message content."""
        return self.wrapped_prompt.fn

    @property
    def toolkit(self) -> Toolkit:
        """The toolkit containing this prompt's tools."""
        return self.wrapped_prompt.toolkit

    @property
    def format(
        self,
    ) -> type[FormattableT] | Format[FormattableT] | OutputParser[FormattableT] | None:
        """The response format for the generated response."""
        return self.wrapped_prompt.format

    def messages(self, *args: P.args, **kwargs: P.kwargs) -> Sequence[Message]:
        """Return the `Messages` from invoking this prompt."""
        return self.wrapped_prompt.messages(*args, **kwargs)

    @overload
    def __call__(
        self: "RetryPrompt[P, None]",
        model: RetryModel | Model,
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> RetryResponse[None]: ...

    @overload
    def __call__(
        self: "RetryPrompt[P, FormattableT]",
        model: RetryModel | Model,
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> RetryResponse[FormattableT]: ...

    def __call__(
        self, model: RetryModel | Model, *args: P.args, **kwargs: P.kwargs
    ) -> RetryResponse[None] | RetryResponse[FormattableT]:
        """Generates a retry response using the provided model."""
        return self.call(model, *args, **kwargs)

    @overload
    def call(
        self: "RetryPrompt[P, None]",
        model: RetryModel | Model,
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> RetryResponse[None]: ...

    @overload
    def call(
        self: "RetryPrompt[P, FormattableT]",
        model: RetryModel | Model,
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> RetryResponse[FormattableT]: ...

    def call(
        self, model: RetryModel | Model, *args: P.args, **kwargs: P.kwargs
    ) -> RetryResponse[None] | RetryResponse[FormattableT]:
        """Generates a retry response using the provided model."""
        retry_model = _ensure_retry_model(model, self.retry_config)
        messages = self.messages(*args, **kwargs)
        return retry_model.call(
            content=messages, tools=self.toolkit, format=self.format
        )


@dataclass
class AsyncRetryPrompt(Generic[P, FormattableT]):
    """An async retry-enabled prompt that wraps an AsyncPrompt and returns AsyncRetryResponse."""

    wrapped_prompt: AsyncPrompt[P, FormattableT]
    """The underlying async prompt being wrapped."""

    retry_config: RetryConfig
    """Configuration for retry behavior."""

    @property
    def fn(self) -> AsyncMessageTemplate[P]:
        """The underlying async prompt function that generates message content."""
        return self.wrapped_prompt.fn

    @property
    def toolkit(self) -> AsyncToolkit:
        """The toolkit containing this prompt's async tools."""
        return self.wrapped_prompt.toolkit

    @property
    def format(
        self,
    ) -> type[FormattableT] | Format[FormattableT] | OutputParser[FormattableT] | None:
        """The response format for the generated response."""
        return self.wrapped_prompt.format

    async def messages(self, *args: P.args, **kwargs: P.kwargs) -> Sequence[Message]:
        """Return the `Messages` from invoking this prompt."""
        return await self.wrapped_prompt.messages(*args, **kwargs)

    @overload
    async def __call__(
        self: "AsyncRetryPrompt[P, None]",
        model: RetryModel | Model,
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> AsyncRetryResponse[None]: ...

    @overload
    async def __call__(
        self: "AsyncRetryPrompt[P, FormattableT]",
        model: RetryModel | Model,
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> AsyncRetryResponse[FormattableT]: ...

    async def __call__(
        self, model: RetryModel | Model, *args: P.args, **kwargs: P.kwargs
    ) -> AsyncRetryResponse[None] | AsyncRetryResponse[FormattableT]:
        """Generates a retry response using the provided model asynchronously."""
        return await self.call(model, *args, **kwargs)

    @overload
    async def call(
        self: "AsyncRetryPrompt[P, None]",
        model: RetryModel | Model,
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> AsyncRetryResponse[None]: ...

    @overload
    async def call(
        self: "AsyncRetryPrompt[P, FormattableT]",
        model: RetryModel | Model,
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> AsyncRetryResponse[FormattableT]: ...

    async def call(
        self, model: RetryModel | Model, *args: P.args, **kwargs: P.kwargs
    ) -> AsyncRetryResponse[None] | AsyncRetryResponse[FormattableT]:
        """Generates a retry response using the provided model asynchronously."""
        retry_model = _ensure_retry_model(model, self.retry_config)
        messages = await self.messages(*args, **kwargs)
        return await retry_model.call_async(
            content=messages, tools=self.toolkit, format=self.format
        )
