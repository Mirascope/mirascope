"""RetryPrompt extends Prompt to return RetryResponse instead of Response."""

from collections.abc import Callable
from typing import Any, Generic, overload

from ..formatting import FormatSpec, FormattableT
from ..models import Model
from ..prompts import (
    AsyncPrompt,
    Prompt,
)
from ..prompts.prompts import BasePrompt
from ..prompts.protocols import AsyncMessageTemplate, MessageTemplate
from ..providers import ModelId
from ..tools import AsyncToolkit, Toolkit
from ..types import P
from .retry_config import RetryConfig
from .retry_models import RetryModel
from .retry_responses import (
    AsyncRetryResponse,
    RetryResponse,
)


def _ensure_retry_model(model: Model, config: RetryConfig) -> RetryModel:
    """Ensure a model has retry capabilities, adding them if necessary."""
    if isinstance(model, RetryModel):
        return model
    return RetryModel(model=model, retry_config=config)


class BaseRetryPrompt(BasePrompt[Callable[..., Any]]):
    """Base class for retry-enabled prompts that adds retry_config."""

    retry_config: RetryConfig
    """Configuration for retry behavior."""


class RetryPrompt(BaseRetryPrompt, Prompt[P, FormattableT], Generic[P, FormattableT]):
    """A retry-enabled prompt that extends Prompt and returns RetryResponse.

    This extends Prompt and overrides call methods to return RetryResponse
    instead of Response. It handles wrapping the provided Model in a RetryModel
    if necessary.
    """

    def __init__(
        self,
        *,
        fn: MessageTemplate[P],
        toolkit: Toolkit,
        format: FormatSpec[FormattableT] | None,
        retry_config: RetryConfig,
    ) -> None:
        super().__init__(fn=fn, toolkit=toolkit, format=format)
        self.retry_config = retry_config

    @overload
    def __call__(
        self: "RetryPrompt[P, None]",
        model: Model | ModelId,
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> RetryResponse[None]: ...

    @overload
    def __call__(
        self: "RetryPrompt[P, FormattableT]",
        model: Model | ModelId,
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> RetryResponse[FormattableT]: ...

    def __call__(
        self, model: Model | ModelId, *args: P.args, **kwargs: P.kwargs
    ) -> RetryResponse[None] | RetryResponse[FormattableT]:
        """Generates a retry response using the provided model."""
        return self.call(model, *args, **kwargs)

    @overload
    def call(
        self: "RetryPrompt[P, None]",
        model: Model | ModelId,
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> RetryResponse[None]: ...

    @overload
    def call(
        self: "RetryPrompt[P, FormattableT]",
        model: Model | ModelId,
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> RetryResponse[FormattableT]: ...

    def call(
        self, model: Model | ModelId, *args: P.args, **kwargs: P.kwargs
    ) -> RetryResponse[None] | RetryResponse[FormattableT]:
        """Generates a retry response using the provided model."""
        if isinstance(model, str):
            model = Model(model)
        retry_model = _ensure_retry_model(model, self.retry_config)
        messages = self.messages(*args, **kwargs)
        return retry_model.call(
            content=messages, tools=self.toolkit, format=self.format
        )


class AsyncRetryPrompt(
    BaseRetryPrompt, AsyncPrompt[P, FormattableT], Generic[P, FormattableT]
):
    """An async retry-enabled prompt that extends AsyncPrompt and returns AsyncRetryResponse."""

    def __init__(
        self,
        *,
        fn: AsyncMessageTemplate[P],
        toolkit: AsyncToolkit,
        format: FormatSpec[FormattableT] | None,
        retry_config: RetryConfig,
    ) -> None:
        super().__init__(fn=fn, toolkit=toolkit, format=format)
        self.retry_config = retry_config

    @overload
    async def __call__(
        self: "AsyncRetryPrompt[P, None]",
        model: Model | ModelId,
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> AsyncRetryResponse[None]: ...

    @overload
    async def __call__(
        self: "AsyncRetryPrompt[P, FormattableT]",
        model: Model | ModelId,
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> AsyncRetryResponse[FormattableT]: ...

    async def __call__(
        self, model: Model | ModelId, *args: P.args, **kwargs: P.kwargs
    ) -> AsyncRetryResponse[None] | AsyncRetryResponse[FormattableT]:
        """Generates a retry response using the provided model asynchronously."""
        return await self.call(model, *args, **kwargs)

    @overload
    async def call(
        self: "AsyncRetryPrompt[P, None]",
        model: Model | ModelId,
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> AsyncRetryResponse[None]: ...

    @overload
    async def call(
        self: "AsyncRetryPrompt[P, FormattableT]",
        model: Model | ModelId,
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> AsyncRetryResponse[FormattableT]: ...

    async def call(
        self, model: Model | ModelId, *args: P.args, **kwargs: P.kwargs
    ) -> AsyncRetryResponse[None] | AsyncRetryResponse[FormattableT]:
        """Generates a retry response using the provided model asynchronously."""
        if isinstance(model, str):
            model = Model(model)
        retry_model = _ensure_retry_model(model, self.retry_config)
        messages = await self.messages(*args, **kwargs)
        return await retry_model.call_async(
            content=messages, tools=self.toolkit, format=self.format
        )
