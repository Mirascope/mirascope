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
from .retry_config import RetryArgs, RetryConfig
from .retry_models import RetryModel
from .retry_prompts import (
    AsyncRetryPrompt,
    RetryPrompt,
)

RetryTarget = (
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
"""Union type for all targets that can be wrapped with retry logic.

Includes Models, Prompts, and Calls (both sync and async variants).
"""

RetryResult = (
    RetryModel
    | RetryPrompt[P, FormattableT]
    | AsyncRetryPrompt[P, FormattableT]
    | RetryCall[P, FormattableT]
    | AsyncRetryCall[P, FormattableT]
)
"""Union type for all retry-wrapped results.

When a target is wrapped with retry logic, it returns one of these types.
"""


# Overloads for direct wrapping: retry(target, ...)


@overload
def retry(
    target: Model | RetryModel,
    **config: Unpack[RetryArgs],
) -> RetryModel:
    """Wrap a Model with retry logic."""
    ...


@overload
def retry(
    target: Prompt[P, FormattableT] | RetryPrompt[P, FormattableT],
    **config: Unpack[RetryArgs],
) -> RetryPrompt[P, FormattableT]:
    """Wrap a Prompt with retry logic."""
    ...


@overload
def retry(
    target: AsyncPrompt[P, FormattableT] | AsyncRetryPrompt[P, FormattableT],
    **config: Unpack[RetryArgs],
) -> AsyncRetryPrompt[P, FormattableT]:
    """Wrap an AsyncPrompt with retry logic."""
    ...


@overload
def retry(
    target: Call[P, FormattableT] | RetryCall[P, FormattableT],
    **config: Unpack[RetryArgs],
) -> RetryCall[P, FormattableT]:
    """Wrap a Call with retry logic."""
    ...


@overload
def retry(
    target: AsyncCall[P, FormattableT] | AsyncRetryCall[P, FormattableT],
    **config: Unpack[RetryArgs],
) -> AsyncRetryCall[P, FormattableT]:
    """Wrap an AsyncCall with retry logic."""
    ...


# Overloads for decorator usage: @retry(...)


@overload
def retry(
    target: None = None,
    **config: Unpack[RetryArgs],
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
        target: RetryTarget[P, DepsT, FormattableT],
    ) -> RetryResult[P, FormattableT]:
        """Apply retry logic to the target."""
        return _wrap_target(target, self._config)


def _wrap_target(
    target: RetryTarget[P, DepsT, FormattableT],
    retry_config: RetryConfig,
) -> RetryResult[P, FormattableT]:
    """Internal function to wrap a target with retry logic."""
    # Wrap Model (RetryModel is a subclass of Model, so this handles both)
    if isinstance(target, Model):
        return RetryModel(target, retry_config)

    # Wrap RetryCall variants first - they inherit from BaseCall, not Call/AsyncCall
    if isinstance(target, AsyncRetryCall):
        prompt = target.prompt
        return AsyncRetryCall(
            default_model=target.default_model,
            prompt=AsyncRetryPrompt(
                fn=prompt.fn,
                toolkit=prompt.toolkit,
                format=prompt.format,
                retry_config=retry_config,
            ),
        )
    if isinstance(target, RetryCall):
        prompt = target.prompt
        return RetryCall(
            default_model=target.default_model,
            prompt=RetryPrompt(
                fn=prompt.fn,
                toolkit=prompt.toolkit,
                format=prompt.format,
                retry_config=retry_config,
            ),
        )

    # Wrap Call variants - AsyncCall check must come before Call
    if isinstance(target, AsyncCall):
        prompt = target.prompt
        return AsyncRetryCall(
            default_model=target.default_model,
            prompt=AsyncRetryPrompt(
                fn=prompt.fn,
                toolkit=prompt.toolkit,
                format=prompt.format,
                retry_config=retry_config,
            ),
        )
    if isinstance(target, Call):
        prompt = target.prompt
        return RetryCall(
            default_model=target.default_model,
            prompt=RetryPrompt(
                fn=prompt.fn,
                toolkit=prompt.toolkit,
                format=prompt.format,
                retry_config=retry_config,
            ),
        )

    # Wrap Prompt variants - AsyncPrompt check must come before Prompt
    if isinstance(target, AsyncPrompt):
        return AsyncRetryPrompt(
            fn=target.fn,
            toolkit=target.toolkit,
            format=target.format,
            retry_config=retry_config,
        )
    if isinstance(target, Prompt):
        return RetryPrompt(
            fn=target.fn,
            toolkit=target.toolkit,
            format=target.format,
            retry_config=retry_config,
        )

    raise ValueError(f"Unsupported target type for retry: {type(target)}")


def retry(
    target: RetryTarget[P, DepsT, FormattableT] | None = None,
    **config: Unpack[RetryArgs],
) -> RetryResult[P, FormattableT] | RetryDecorator:
    """Add retry logic to a Model, Prompt, or Call.

    This function can be used in two ways:

    1. Direct wrapping:
        ```python
        retry_model = llm.retry(model, max_retries=2)
        retry_call = llm.retry(my_call, max_retries=2)
        ```

    2. As a decorator:
        ```python
        @llm.retry(max_retries=2)
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
        **config: Configuration for retry behavior (see RetryArgs).

    Returns:
        A retry-wrapped version of the target that returns Retry* response types,
        or a RetryDecorator if no target is provided.
    """
    retry_config = RetryConfig.from_args(**config)

    if target is None:
        return RetryDecorator(retry_config)

    return _wrap_target(target, retry_config)
