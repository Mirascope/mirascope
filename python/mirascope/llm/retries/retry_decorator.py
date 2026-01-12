"""The @llm.retry decorator for adding retry logic to models, prompts, and calls."""

from typing import overload
from typing_extensions import Unpack

from ..calls import AsyncCall, AsyncContextCall, Call, ContextCall
from ..context import DepsT
from ..formatting import FormattableT
from ..models import Model
from ..prompts import AsyncContextPrompt, AsyncPrompt, ContextPrompt, Prompt
from ..types import P
from .retry_calls import (
    AsyncRetryCall,
    RetryCall,
)
from .retry_config import RetryConfig
from .retry_models import RetryModel
from .retry_prompts import (
    AsyncRetryPrompt,
    RetryPrompt,
)

# Type alias for all supported target types
_RetryTarget = (
    Model
    | RetryModel
    | ContextPrompt[P, DepsT, FormattableT]
    | AsyncContextPrompt[P, DepsT, FormattableT]
    | Prompt[P, FormattableT]
    | RetryPrompt[P, FormattableT]
    | AsyncPrompt[P, FormattableT]
    | AsyncRetryPrompt[P, FormattableT]
    | ContextCall[P, DepsT, FormattableT]
    | AsyncContextCall[P, DepsT, FormattableT]
    | Call[P, FormattableT]
    | RetryCall[P, FormattableT]
    | AsyncCall[P, FormattableT]
    | AsyncRetryCall[P, FormattableT]
)

# Type alias for all return types
_RetryResult = (
    RetryModel
    | RetryPrompt[P, FormattableT]
    | AsyncRetryPrompt[P, FormattableT]
    | RetryCall[P, FormattableT]
    | AsyncRetryCall[P, FormattableT]
)


def _wrap_target(
    target: _RetryTarget[P, DepsT, FormattableT],
    retry_config: RetryConfig,
) -> _RetryResult[P, FormattableT]:
    """Internal function to wrap a target with retry logic."""
    # Wrap Model
    if isinstance(target, Model):
        return RetryModel(target, retry_config)
    if isinstance(target, RetryModel):
        return RetryModel(target.wrapped_model, retry_config)

    # Wrap Call variants (check more specific types first)
    if isinstance(target, AsyncRetryCall):
        return AsyncRetryCall(wrapped_call=target.wrapped_call, config=retry_config)
    if isinstance(target, AsyncCall):
        return AsyncRetryCall(wrapped_call=target, config=retry_config)
    if isinstance(target, RetryCall):
        return RetryCall(wrapped_call=target.wrapped_call, config=retry_config)
    if isinstance(target, Call):
        return RetryCall(wrapped_call=target, config=retry_config)

    # Wrap Prompt variants (check more specific types first)
    if isinstance(target, RetryPrompt):
        return RetryPrompt(
            wrapped_prompt=target.wrapped_prompt, retry_config=retry_config
        )
    if isinstance(target, AsyncRetryPrompt):
        return AsyncRetryPrompt(
            wrapped_prompt=target.wrapped_prompt, retry_config=retry_config
        )
    if isinstance(target, Prompt):
        return RetryPrompt(wrapped_prompt=target, retry_config=retry_config)
    if isinstance(target, AsyncPrompt):
        return AsyncRetryPrompt(wrapped_prompt=target, retry_config=retry_config)

    # This should never happen due to type checking, but just in case
    raise TypeError(f"Unsupported target type for retry: {type(target)}")


# Overloads for direct wrapping: retry(target, ...)


@overload
def retry(
    target: Model | RetryModel,
    **config: Unpack[RetryConfig],
) -> RetryModel:
    """Wrap a Model with retry logic."""
    ...


@overload
def retry(
    target: Prompt[P, FormattableT] | RetryPrompt[P, FormattableT],
    **config: Unpack[RetryConfig],
) -> RetryPrompt[P, FormattableT]:
    """Wrap a Prompt with retry logic."""
    ...


@overload
def retry(
    target: AsyncPrompt[P, FormattableT] | AsyncRetryPrompt[P, FormattableT],
    **config: Unpack[RetryConfig],
) -> AsyncRetryPrompt[P, FormattableT]:
    """Wrap an AsyncPrompt with retry logic."""
    ...


@overload
def retry(
    target: Call[P, FormattableT] | RetryCall[P, FormattableT],
    **config: Unpack[RetryConfig],
) -> RetryCall[P, FormattableT]:
    """Wrap a Call with retry logic."""
    ...


@overload
def retry(
    target: AsyncCall[P, FormattableT] | AsyncRetryCall[P, FormattableT],
    **config: Unpack[RetryConfig],
) -> AsyncRetryCall[P, FormattableT]:
    """Wrap an AsyncCall with retry logic."""
    ...


# Overloads for decorator usage: @retry(...)


@overload
def retry(
    target: None = None,
    **config: Unpack[RetryConfig],
) -> "RetryDecorator":
    """Return a decorator that adds retry logic."""
    ...


class RetryDecorator:
    """A decorator class that wraps targets with retry logic.

    This class is returned when `retry()` is called without a target,
    allowing it to be used as a parameterized decorator.
    """

    def __init__(self, config: RetryConfig) -> None:
        self._config = config

    @overload
    def __call__(self, target: Model | RetryModel) -> RetryModel: ...

    @overload
    def __call__(
        self, target: Prompt[P, FormattableT] | RetryPrompt[P, FormattableT]
    ) -> RetryPrompt[P, FormattableT]: ...

    @overload
    def __call__(
        self, target: AsyncPrompt[P, FormattableT] | AsyncRetryPrompt[P, FormattableT]
    ) -> AsyncRetryPrompt[P, FormattableT]: ...

    @overload
    def __call__(
        self, target: Call[P, FormattableT] | RetryCall[P, FormattableT]
    ) -> RetryCall[P, FormattableT]: ...

    @overload
    def __call__(
        self, target: AsyncCall[P, FormattableT] | AsyncRetryCall[P, FormattableT]
    ) -> AsyncRetryCall[P, FormattableT]: ...

    def __call__(
        self,
        target: _RetryTarget[P, DepsT, FormattableT],
    ) -> _RetryResult[P, FormattableT]:
        """Apply retry logic to the target."""
        return _wrap_target(target, self._config)


def retry(
    target: _RetryTarget[P, DepsT, FormattableT] | None = None,
    **config: Unpack[RetryConfig],
) -> _RetryResult[P, FormattableT] | RetryDecorator:
    """Add retry logic to a Model, Prompt, or Call.

    This function can be used in two ways:

    1. Direct wrapping:
        ```python
        retry_model = llm.retry(model, max_attempts=3)
        retry_call = llm.retry(my_call, max_attempts=3)
        ```

    2. As a decorator:
        ```python
        @llm.retry(max_attempts=3)
        @llm.call("openai/gpt-4")
        def my_call() -> str:
            return "Hello"
        ```

    This function wraps the provided target with retry capabilities, allowing it to
    automatically retry on failures, handle rate limits, and use fallback models.
    The retry configuration can be provided as keyword arguments.

    If a RetryModel, RetryPrompt, or RetryCall is passed, then this will return a new
    RetryModel, RetryPrompt, or RetryCall using the retry_config passed to the function.

    Args:
        target: The Model, Prompt, or Call to wrap with retry logic. If None,
            returns a decorator that can be applied to a target.
        **config: Configuration for retry behavior (see RetryConfig).

    Returns:
        A retry-wrapped version of the target that returns Retry* response types,
        or a RetryDecorator if no target is provided.
    """
    retry_config = RetryConfig(**config)

    if target is None:
        return RetryDecorator(retry_config)

    return _wrap_target(target, retry_config)
