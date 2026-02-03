"""RetryModel extends Model to add retry logic."""

import asyncio
import time
from collections.abc import AsyncIterator, Awaitable, Iterator, Sequence
from typing import cast, overload
from typing_extensions import Unpack

from ..context import Context, DepsT
from ..formatting import FormatSpec, FormattableT
from ..messages import Message, UserContent
from ..models import Model, Params
from ..providers import ModelId
from ..responses import (
    AsyncContextResponse,
    AsyncContextStreamResponse,
    AsyncResponse,
    AsyncStreamResponse,
    ContextResponse,
    ContextStreamResponse,
    Response,
    StreamResponse,
)
from ..tools import (
    AsyncContextTools,
    AsyncTools,
    ContextTools,
    Tools,
)
from .retry_config import RetryArgs, RetryConfig
from .retry_responses import (
    AsyncContextRetryResponse,
    AsyncRetryResponse,
    ContextRetryResponse,
    RetryResponse,
)
from .retry_stream_responses import (
    AsyncContextRetryStreamResponse,
    AsyncRetryStreamResponse,
    ContextRetryStreamResponse,
    RetryStreamResponse,
)
from .utils import with_retry, with_retry_async


class RetryModelParams(Params, RetryArgs, total=False):
    """Combined parameters for RetryModel: model params + retry config.

    This TypedDict combines all fields from `Params` and `RetryArgs`, allowing
    users to configure both the model behavior and retry logic in a single call.
    """


_RETRY_ARG_KEYS = frozenset(RetryArgs.__annotations__.keys())


class RetryModel(Model):
    """Extends Model with retry logic and optional fallback models.

    RetryModel "is-a" Model - it has a primary model_id and params determined by
    the active model. It also supports fallback models that will be tried if the
    active model exhausts its retries.

    The `_models` tuple contains all available models (primary + resolved fallbacks).
    The `_active_index` indicates which model is currently "primary". When a call
    succeeds on a fallback model, the returned response's `.model` property will
    be a new RetryModel with that successful model as the active model.
    """

    _models: tuple[Model, ...]
    """All available models: primary at index 0, then fallbacks."""

    _active_index: int
    """Index into _models for the currently active model."""

    retry_config: RetryConfig
    """The RetryConfig specifying retry behavior."""

    @overload
    def __init__(
        self,
        model: Model,
        retry_config: RetryConfig,
    ) -> None:
        """Wrap an existing Model with retry logic."""
        ...

    @overload
    def __init__(
        self,
        model: ModelId,
        retry_config: RetryConfig,
        **params: Unpack[Params],
    ) -> None:
        """Create a RetryModel from a ModelId with optional params."""
        ...

    def __init__(
        self,
        model: Model | ModelId,
        retry_config: RetryConfig,
        **params: Unpack[Params],
    ) -> None:
        """Initialize a RetryModel.

        Args:
            model: Either a Model instance to wrap, or a ModelId string to create
                a new Model from.
            retry_config: Configuration for retry behavior.
            **params: Additional parameters for the model. Only used when `model`
                is a ModelId string; ignored when wrapping an existing Model.
        """
        # Resolve the primary model (strip to plain Model if needed)
        if isinstance(model, Model):
            primary = (
                model if type(model) is Model else Model(model.model_id, **model.params)
            )
        else:
            primary = Model(model, **params)

        # Resolve fallback models
        resolved_fallbacks: list[Model] = []
        for fb in retry_config.fallback_models:
            if isinstance(fb, Model):
                # Strip any RetryModel wrapping, just take model_id and params
                resolved_fallbacks.append(
                    fb if type(fb) is Model else Model(fb.model_id, **fb.params)
                )
            else:
                # ModelId string - inherit params from primary
                resolved_fallbacks.append(Model(fb, **primary.params))

        self._models = (primary, *resolved_fallbacks)
        self._active_index = 0
        self.retry_config = retry_config

        # Initialize _token_stack for context manager support
        object.__setattr__(self, "_token_stack", [])

    @classmethod
    def _create_with_active(
        cls,
        models: tuple[Model, ...],
        active_index: int,
        retry_config: RetryConfig,
    ) -> "RetryModel":
        """Internal constructor for creating a RetryModel with pre-resolved models."""
        instance = object.__new__(cls)
        instance._models = models
        instance._active_index = active_index
        instance.retry_config = retry_config
        object.__setattr__(instance, "_token_stack", [])
        return instance

    def get_active_model(self) -> Model:
        """Get the currently active model."""
        return self._models[self._active_index]

    @property
    def model_id(self) -> ModelId:  # pyright: ignore[reportIncompatibleVariableOverride]
        """The model_id of the currently active model."""
        return self._models[self._active_index].model_id

    @property
    def params(self) -> Params:  # pyright: ignore[reportIncompatibleVariableOverride]
        """The params of the currently active model."""
        return self._models[self._active_index].params

    def _with_active(self, index: int) -> "RetryModel":
        """Return a new RetryModel with a different active model."""
        return self._create_with_active(
            models=self._models,
            active_index=index,
            retry_config=self.retry_config,
        )

    def _attempt_variants(self) -> Iterator["RetryModel"]:
        """Yield RetryModels in attempt order: active model first, then others."""
        yield self
        for i in range(len(self._models)):
            if i != self._active_index:
                yield self._with_active(i)

    def variants(self) -> Iterator["RetryModel"]:
        """Yield model variants with backoff delays between retries.

        Yields the active model variant first. After each yield, if the caller
        encountered an error and iterates again, this applies the appropriate
        backoff delay before yielding the next attempt. Each model gets
        max_retries additional attempts before moving to the next fallback model.

        Yields:
            RetryModel variants to attempt, with backoff delays applied between yields.
        """
        from .utils import calculate_delay

        config = self.retry_config
        for variant in self._attempt_variants():
            for attempt in range(config.max_retries + 1):
                yield variant
                # If caller iterates again, they hit an error - apply backoff
                if attempt < config.max_retries:
                    delay = calculate_delay(config, attempt + 1)
                    time.sleep(delay)

    async def variants_async(self) -> AsyncIterator["RetryModel"]:
        """Async version of variants().

        Yields the active model variant first. After each yield, if the caller
        encountered an error and iterates again, this applies the appropriate
        backoff delay before yielding the next attempt. Each model gets
        max_retries additional attempts before moving to the next fallback model.

        Yields:
            RetryModel variants to attempt, with backoff delays applied between yields.
        """
        from .utils import calculate_delay

        config = self.retry_config
        for variant in self._attempt_variants():
            for attempt in range(config.max_retries + 1):
                yield variant
                # If caller iterates again, they hit an error - apply backoff
                if attempt < config.max_retries:
                    delay = calculate_delay(config, attempt + 1)
                    await asyncio.sleep(delay)

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
        format: FormatSpec[FormattableT],
    ) -> RetryResponse[FormattableT]: ...

    @overload
    def call(
        self,
        content: UserContent | Sequence[Message],
        *,
        tools: Tools | None = None,
        format: FormatSpec[FormattableT] | None,
    ) -> RetryResponse[None] | RetryResponse[FormattableT]: ...

    def call(
        self,
        content: UserContent | Sequence[Message],
        *,
        tools: Tools | None = None,
        format: FormatSpec[FormattableT] | None = None,
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
        response, failures, updated_model = with_retry(
            fn=lambda m: m.call(content, tools=tools, format=format),
            retry_model=self,
        )
        return RetryResponse(
            response=cast("Response[FormattableT]", response),
            retry_model=updated_model,
            retry_failures=failures,
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
        format: FormatSpec[FormattableT],
    ) -> AsyncRetryResponse[FormattableT]: ...

    @overload
    async def call_async(
        self,
        content: UserContent | Sequence[Message],
        *,
        tools: AsyncTools | None = None,
        format: FormatSpec[FormattableT] | None,
    ) -> AsyncRetryResponse[None] | AsyncRetryResponse[FormattableT]: ...

    async def call_async(
        self,
        content: UserContent | Sequence[Message],
        *,
        tools: AsyncTools | None = None,
        format: FormatSpec[FormattableT] | None = None,
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
        response, failures, updated_model = await with_retry_async(
            fn=lambda m: m.call_async(content, tools=tools, format=format),
            retry_model=self,
        )
        return AsyncRetryResponse(
            response=cast("AsyncResponse[FormattableT]", response),
            retry_model=updated_model,
            retry_failures=failures,
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
        new_response, failures, updated_model = with_retry(
            fn=lambda m: m.resume(response=response, content=content),
            retry_model=self,
        )
        return RetryResponse(
            response=cast("Response[FormattableT]", new_response),
            retry_model=updated_model,
            retry_failures=failures,
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
        new_response, failures, updated_model = await with_retry_async(
            fn=lambda m: m.resume_async(response=response, content=content),
            retry_model=self,
        )
        return AsyncRetryResponse(
            response=cast("AsyncResponse[FormattableT]", new_response),
            retry_model=updated_model,
            retry_failures=failures,
        )

    # Context call methods

    @overload
    def context_call(
        self,
        content: UserContent | Sequence[Message],
        *,
        ctx: Context[DepsT],
        tools: ContextTools[DepsT] | None = None,
        format: None = None,
    ) -> ContextRetryResponse[DepsT, None]: ...

    @overload
    def context_call(
        self,
        content: UserContent | Sequence[Message],
        *,
        ctx: Context[DepsT],
        tools: ContextTools[DepsT] | None = None,
        format: FormatSpec[FormattableT],
    ) -> ContextRetryResponse[DepsT, FormattableT]: ...

    @overload
    def context_call(
        self,
        content: UserContent | Sequence[Message],
        *,
        ctx: Context[DepsT],
        tools: ContextTools[DepsT] | None = None,
        format: FormatSpec[FormattableT] | None,
    ) -> (
        ContextRetryResponse[DepsT, None] | ContextRetryResponse[DepsT, FormattableT]
    ): ...

    def context_call(
        self,
        content: UserContent | Sequence[Message],
        *,
        ctx: Context[DepsT],
        tools: ContextTools[DepsT] | None = None,
        format: FormatSpec[FormattableT] | None = None,
    ) -> ContextRetryResponse[DepsT, None] | ContextRetryResponse[DepsT, FormattableT]:
        """Generate a ContextRetryResponse by calling this model's LLM provider with context.

        Args:
            content: User content or LLM messages to send to the LLM.
            ctx: A `Context` with the required deps type.
            tools: Optional context-aware tools that the model may invoke.
            format: Optional response format specifier.

        Returns:
            A ContextRetryResponse object containing the LLM-generated content and retry metadata.

        Raises:
            Exception: The last exception encountered if all retry attempts fail.
        """
        response, failures, updated_model = with_retry(
            fn=lambda m: m.context_call(content, ctx=ctx, tools=tools, format=format),
            retry_model=self,
        )
        return ContextRetryResponse(
            response=cast("ContextResponse[DepsT, FormattableT]", response),
            retry_model=updated_model,
            retry_failures=failures,
        )

    @overload
    async def context_call_async(
        self,
        content: UserContent | Sequence[Message],
        *,
        ctx: Context[DepsT],
        tools: AsyncContextTools[DepsT] | None = None,
        format: None = None,
    ) -> AsyncContextRetryResponse[DepsT, None]: ...

    @overload
    async def context_call_async(
        self,
        content: UserContent | Sequence[Message],
        *,
        ctx: Context[DepsT],
        tools: AsyncContextTools[DepsT] | None = None,
        format: FormatSpec[FormattableT],
    ) -> AsyncContextRetryResponse[DepsT, FormattableT]: ...

    @overload
    async def context_call_async(
        self,
        content: UserContent | Sequence[Message],
        *,
        ctx: Context[DepsT],
        tools: AsyncContextTools[DepsT] | None = None,
        format: FormatSpec[FormattableT] | None,
    ) -> (
        AsyncContextRetryResponse[DepsT, None]
        | AsyncContextRetryResponse[DepsT, FormattableT]
    ): ...

    async def context_call_async(
        self,
        content: UserContent | Sequence[Message],
        *,
        ctx: Context[DepsT],
        tools: AsyncContextTools[DepsT] | None = None,
        format: FormatSpec[FormattableT] | None = None,
    ) -> (
        AsyncContextRetryResponse[DepsT, None]
        | AsyncContextRetryResponse[DepsT, FormattableT]
    ):
        """Generate an AsyncContextRetryResponse by asynchronously calling this model's LLM provider with context.

        Args:
            content: User content or LLM messages to send to the LLM.
            ctx: A `Context` with the required deps type.
            tools: Optional context-aware tools that the model may invoke.
            format: Optional response format specifier.

        Returns:
            An AsyncContextRetryResponse object containing the LLM-generated content and retry metadata.

        Raises:
            Exception: The last exception encountered if all retry attempts fail.
        """
        response, failures, updated_model = await with_retry_async(
            fn=lambda m: m.context_call_async(
                content, ctx=ctx, tools=tools, format=format
            ),
            retry_model=self,
        )
        return AsyncContextRetryResponse(
            response=cast("AsyncContextResponse[DepsT, FormattableT]", response),
            retry_model=updated_model,
            retry_failures=failures,
        )

    # Context resume methods

    @overload
    def context_resume(
        self,
        *,
        ctx: Context[DepsT],
        response: ContextResponse[DepsT, None],
        content: UserContent,
    ) -> ContextRetryResponse[DepsT, None]: ...

    @overload
    def context_resume(
        self,
        *,
        ctx: Context[DepsT],
        response: ContextResponse[DepsT, FormattableT],
        content: UserContent,
    ) -> ContextRetryResponse[DepsT, FormattableT]: ...

    @overload
    def context_resume(
        self,
        *,
        ctx: Context[DepsT],
        response: ContextResponse[DepsT, None] | ContextResponse[DepsT, FormattableT],
        content: UserContent,
    ) -> (
        ContextRetryResponse[DepsT, None] | ContextRetryResponse[DepsT, FormattableT]
    ): ...

    def context_resume(  # pyright: ignore[reportIncompatibleMethodOverride]
        self,
        *,
        ctx: Context[DepsT],
        response: ContextResponse[DepsT, None] | ContextResponse[DepsT, FormattableT],
        content: UserContent,
    ) -> ContextRetryResponse[DepsT, None] | ContextRetryResponse[DepsT, FormattableT]:
        """Generate a new ContextRetryResponse by extending another response's messages.

        Args:
            ctx: A `Context` with the required deps type.
            response: Previous context response to extend.
            content: Additional user content to append.

        Returns:
            A new ContextRetryResponse containing the extended conversation.

        Raises:
            Exception: The last exception encountered if all retry attempts fail.
        """
        new_response, failures, updated_model = with_retry(
            fn=lambda m: m.context_resume(ctx=ctx, response=response, content=content),
            retry_model=self,
        )
        return ContextRetryResponse(
            response=cast("ContextResponse[DepsT, FormattableT]", new_response),
            retry_model=updated_model,
            retry_failures=failures,
        )

    @overload
    async def context_resume_async(
        self,
        *,
        ctx: Context[DepsT],
        response: AsyncContextResponse[DepsT, None],
        content: UserContent,
    ) -> AsyncContextRetryResponse[DepsT, None]: ...

    @overload
    async def context_resume_async(
        self,
        *,
        ctx: Context[DepsT],
        response: AsyncContextResponse[DepsT, FormattableT],
        content: UserContent,
    ) -> AsyncContextRetryResponse[DepsT, FormattableT]: ...

    @overload
    async def context_resume_async(
        self,
        *,
        ctx: Context[DepsT],
        response: (
            AsyncContextResponse[DepsT, None]
            | AsyncContextResponse[DepsT, FormattableT]
        ),
        content: UserContent,
    ) -> (
        AsyncContextRetryResponse[DepsT, None]
        | AsyncContextRetryResponse[DepsT, FormattableT]
    ): ...

    async def context_resume_async(  # pyright: ignore[reportIncompatibleMethodOverride]
        self,
        *,
        ctx: Context[DepsT],
        response: (
            AsyncContextResponse[DepsT, None]
            | AsyncContextResponse[DepsT, FormattableT]
        ),
        content: UserContent,
    ) -> (
        AsyncContextRetryResponse[DepsT, None]
        | AsyncContextRetryResponse[DepsT, FormattableT]
    ):
        """Generate a new AsyncContextRetryResponse by extending another response's messages.

        Args:
            ctx: A `Context` with the required deps type.
            response: Previous async context response to extend.
            content: Additional user content to append.

        Returns:
            A new AsyncContextRetryResponse containing the extended conversation.

        Raises:
            Exception: The last exception encountered if all retry attempts fail.
        """
        new_response, failures, updated_model = await with_retry_async(
            fn=lambda m: m.context_resume_async(
                ctx=ctx, response=response, content=content
            ),
            retry_model=self,
        )
        return AsyncContextRetryResponse(
            response=cast("AsyncContextResponse[DepsT, FormattableT]", new_response),
            retry_model=updated_model,
            retry_failures=failures,
        )

    # Stream methods

    @overload
    def stream(
        self,
        content: UserContent | Sequence[Message],
        *,
        tools: Tools | None = None,
        format: None = None,
    ) -> RetryStreamResponse[None]: ...

    @overload
    def stream(
        self,
        content: UserContent | Sequence[Message],
        *,
        tools: Tools | None = None,
        format: FormatSpec[FormattableT],
    ) -> RetryStreamResponse[FormattableT]: ...

    @overload
    def stream(
        self,
        content: UserContent | Sequence[Message],
        *,
        tools: Tools | None = None,
        format: FormatSpec[FormattableT] | None,
    ) -> RetryStreamResponse[None] | RetryStreamResponse[FormattableT]: ...

    def stream(
        self,
        content: UserContent | Sequence[Message],
        *,
        tools: Tools | None = None,
        format: FormatSpec[FormattableT] | None = None,
    ) -> RetryStreamResponse[None] | RetryStreamResponse[FormattableT]:
        """Generate a RetryStreamResponse by streaming from this model's LLM provider.

        The returned response supports automatic retry on failure. If a retryable
        error occurs during iteration, a `StreamRestarted` exception is raised
        and the user can re-iterate to continue from the new attempt.

        Supports fallback models - when the active model exhausts its retries,
        the next fallback model is tried.

        Args:
            content: User content or LLM messages to send to the LLM.
            tools: Optional tools that the model may invoke.
            format: Optional response format specifier.

        Returns:
            A RetryStreamResponse for iterating over the LLM-generated content.
        """
        return RetryStreamResponse(
            self,
            lambda m: cast(
                "StreamResponse[FormattableT]",
                m.stream(content=content, tools=tools, format=format),
            ),
        )

    @overload
    async def stream_async(
        self,
        content: UserContent | Sequence[Message],
        *,
        tools: AsyncTools | None = None,
        format: None = None,
    ) -> AsyncRetryStreamResponse[None]: ...

    @overload
    async def stream_async(
        self,
        content: UserContent | Sequence[Message],
        *,
        tools: AsyncTools | None = None,
        format: FormatSpec[FormattableT],
    ) -> AsyncRetryStreamResponse[FormattableT]: ...

    @overload
    async def stream_async(
        self,
        content: UserContent | Sequence[Message],
        *,
        tools: AsyncTools | None = None,
        format: FormatSpec[FormattableT] | None,
    ) -> AsyncRetryStreamResponse[None] | AsyncRetryStreamResponse[FormattableT]: ...

    async def stream_async(
        self,
        content: UserContent | Sequence[Message],
        *,
        tools: AsyncTools | None = None,
        format: FormatSpec[FormattableT] | None = None,
    ) -> AsyncRetryStreamResponse[None] | AsyncRetryStreamResponse[FormattableT]:
        """Generate an AsyncRetryStreamResponse by streaming from this model's LLM provider.

        The returned response supports automatic retry on failure. If a retryable
        error occurs during iteration, a `StreamRestarted` exception is raised
        and the user can re-iterate to continue from the new attempt.

        Supports fallback models - when the active model exhausts its retries,
        the next fallback model is tried.

        Args:
            content: User content or LLM messages to send to the LLM.
            tools: Optional tools that the model may invoke.
            format: Optional response format specifier.

        Returns:
            An AsyncRetryStreamResponse for asynchronously iterating over the LLM-generated content.
        """

        def stream_fn(m: Model) -> Awaitable[AsyncStreamResponse[FormattableT]]:
            return cast(
                "Awaitable[AsyncStreamResponse[FormattableT]]",
                m.stream_async(content=content, tools=tools, format=format),
            )

        variants_iter = self.variants_async()
        initial_variant = await anext(variants_iter)
        initial_stream = await stream_fn(initial_variant.get_active_model())
        return AsyncRetryStreamResponse(
            stream_fn, initial_stream, initial_variant, variants_iter
        )

    # Resume stream methods

    @overload
    def resume_stream(
        self,
        *,
        response: StreamResponse,
        content: UserContent,
    ) -> RetryStreamResponse[None]: ...

    @overload
    def resume_stream(
        self,
        *,
        response: StreamResponse[FormattableT],
        content: UserContent,
    ) -> RetryStreamResponse[FormattableT]: ...

    @overload
    def resume_stream(
        self,
        *,
        response: StreamResponse | StreamResponse[FormattableT],
        content: UserContent,
    ) -> RetryStreamResponse[None] | RetryStreamResponse[FormattableT]: ...

    def resume_stream(
        self,
        *,
        response: StreamResponse | StreamResponse[FormattableT],
        content: UserContent,
    ) -> RetryStreamResponse[None] | RetryStreamResponse[FormattableT]:
        """Generate a new RetryStreamResponse by extending another response's messages.

        Args:
            response: Previous stream response to extend.
            content: Additional user content to append.

        Returns:
            A new RetryStreamResponse for streaming the extended conversation.
        """
        return RetryStreamResponse(
            self,
            lambda m: cast(
                "StreamResponse[FormattableT]",
                m.resume_stream(response=response, content=content),
            ),
        )

    @overload
    async def resume_stream_async(
        self,
        *,
        response: AsyncStreamResponse,
        content: UserContent,
    ) -> AsyncRetryStreamResponse[None]: ...

    @overload
    async def resume_stream_async(
        self,
        *,
        response: AsyncStreamResponse[FormattableT],
        content: UserContent,
    ) -> AsyncRetryStreamResponse[FormattableT]: ...

    @overload
    async def resume_stream_async(
        self,
        *,
        response: AsyncStreamResponse | AsyncStreamResponse[FormattableT],
        content: UserContent,
    ) -> AsyncRetryStreamResponse[None] | AsyncRetryStreamResponse[FormattableT]: ...

    async def resume_stream_async(
        self,
        *,
        response: AsyncStreamResponse | AsyncStreamResponse[FormattableT],
        content: UserContent,
    ) -> AsyncRetryStreamResponse[None] | AsyncRetryStreamResponse[FormattableT]:
        """Generate a new AsyncRetryStreamResponse by extending another response's messages.

        Args:
            response: Previous async stream response to extend.
            content: Additional user content to append.

        Returns:
            A new AsyncRetryStreamResponse for asynchronously streaming the extended conversation.
        """

        def stream_fn(m: Model) -> Awaitable[AsyncStreamResponse[FormattableT]]:
            return cast(
                "Awaitable[AsyncStreamResponse[FormattableT]]",
                m.resume_stream_async(response=response, content=content),
            )

        variants_iter = self.variants_async()
        initial_variant = await anext(variants_iter)
        initial_stream = await stream_fn(initial_variant.get_active_model())
        return AsyncRetryStreamResponse(
            stream_fn, initial_stream, initial_variant, variants_iter
        )

    # Context stream methods

    @overload
    def context_stream(
        self,
        content: UserContent | Sequence[Message],
        *,
        ctx: Context[DepsT],
        tools: ContextTools[DepsT] | None = None,
        format: None = None,
    ) -> ContextRetryStreamResponse[DepsT, None]: ...

    @overload
    def context_stream(
        self,
        content: UserContent | Sequence[Message],
        *,
        ctx: Context[DepsT],
        tools: ContextTools[DepsT] | None = None,
        format: FormatSpec[FormattableT],
    ) -> ContextRetryStreamResponse[DepsT, FormattableT]: ...

    @overload
    def context_stream(
        self,
        content: UserContent | Sequence[Message],
        *,
        ctx: Context[DepsT],
        tools: ContextTools[DepsT] | None = None,
        format: FormatSpec[FormattableT] | None,
    ) -> (
        ContextRetryStreamResponse[DepsT, None]
        | ContextRetryStreamResponse[DepsT, FormattableT]
    ): ...

    def context_stream(
        self,
        content: UserContent | Sequence[Message],
        *,
        ctx: Context[DepsT],
        tools: ContextTools[DepsT] | None = None,
        format: FormatSpec[FormattableT] | None = None,
    ) -> (
        ContextRetryStreamResponse[DepsT, None]
        | ContextRetryStreamResponse[DepsT, FormattableT]
    ):
        """Generate a ContextRetryStreamResponse by streaming from this model's LLM provider with context.

        The returned response supports automatic retry on failure. If a retryable
        error occurs during iteration, a `StreamRestarted` exception is raised
        and the user can re-iterate to continue from the new attempt.

        Supports fallback models - when the active model exhausts its retries,
        the next fallback model is tried.

        Args:
            content: User content or LLM messages to send to the LLM.
            ctx: A `Context` with the required deps type.
            tools: Optional context-aware tools that the model may invoke.
            format: Optional response format specifier.

        Returns:
            A ContextRetryStreamResponse for iterating over the LLM-generated content.
        """
        return ContextRetryStreamResponse(
            self,
            lambda m: cast(
                "ContextStreamResponse[DepsT, FormattableT]",
                m.context_stream(content=content, ctx=ctx, tools=tools, format=format),
            ),
        )

    @overload
    async def context_stream_async(
        self,
        content: UserContent | Sequence[Message],
        *,
        ctx: Context[DepsT],
        tools: AsyncContextTools[DepsT] | None = None,
        format: None = None,
    ) -> AsyncContextRetryStreamResponse[DepsT, None]: ...

    @overload
    async def context_stream_async(
        self,
        content: UserContent | Sequence[Message],
        *,
        ctx: Context[DepsT],
        tools: AsyncContextTools[DepsT] | None = None,
        format: FormatSpec[FormattableT],
    ) -> AsyncContextRetryStreamResponse[DepsT, FormattableT]: ...

    @overload
    async def context_stream_async(
        self,
        content: UserContent | Sequence[Message],
        *,
        ctx: Context[DepsT],
        tools: AsyncContextTools[DepsT] | None = None,
        format: FormatSpec[FormattableT] | None,
    ) -> (
        AsyncContextRetryStreamResponse[DepsT, None]
        | AsyncContextRetryStreamResponse[DepsT, FormattableT]
    ): ...

    async def context_stream_async(
        self,
        content: UserContent | Sequence[Message],
        *,
        ctx: Context[DepsT],
        tools: AsyncContextTools[DepsT] | None = None,
        format: FormatSpec[FormattableT] | None = None,
    ) -> (
        AsyncContextRetryStreamResponse[DepsT, None]
        | AsyncContextRetryStreamResponse[DepsT, FormattableT]
    ):
        """Generate an AsyncContextRetryStreamResponse by streaming from this model's LLM provider with context.

        The returned response supports automatic retry on failure. If a retryable
        error occurs during iteration, a `StreamRestarted` exception is raised
        and the user can re-iterate to continue from the new attempt.

        Supports fallback models - when the active model exhausts its retries,
        the next fallback model is tried.

        Args:
            content: User content or LLM messages to send to the LLM.
            ctx: A `Context` with the required deps type.
            tools: Optional context-aware tools that the model may invoke.
            format: Optional response format specifier.

        Returns:
            An AsyncContextRetryStreamResponse for asynchronously iterating over the LLM-generated content.
        """

        def stream_fn(
            m: Model,
        ) -> Awaitable[AsyncContextStreamResponse[DepsT, FormattableT]]:
            return cast(
                "Awaitable[AsyncContextStreamResponse[DepsT, FormattableT]]",
                m.context_stream_async(
                    content=content, ctx=ctx, tools=tools, format=format
                ),
            )

        variants_iter = self.variants_async()
        initial_variant = await anext(variants_iter)
        initial_stream = await stream_fn(initial_variant.get_active_model())
        return AsyncContextRetryStreamResponse(
            stream_fn, initial_stream, initial_variant, variants_iter
        )

    # Context resume stream methods

    @overload
    def context_resume_stream(
        self,
        *,
        ctx: Context[DepsT],
        response: ContextStreamResponse[DepsT, None],
        content: UserContent,
    ) -> ContextRetryStreamResponse[DepsT, None]: ...

    @overload
    def context_resume_stream(
        self,
        *,
        ctx: Context[DepsT],
        response: ContextStreamResponse[DepsT, FormattableT],
        content: UserContent,
    ) -> ContextRetryStreamResponse[DepsT, FormattableT]: ...

    @overload
    def context_resume_stream(
        self,
        *,
        ctx: Context[DepsT],
        response: (
            ContextStreamResponse[DepsT, None]
            | ContextStreamResponse[DepsT, FormattableT]
        ),
        content: UserContent,
    ) -> (
        ContextRetryStreamResponse[DepsT, None]
        | ContextRetryStreamResponse[DepsT, FormattableT]
    ): ...

    def context_resume_stream(  # pyright: ignore[reportIncompatibleMethodOverride]
        self,
        *,
        ctx: Context[DepsT],
        response: (
            ContextStreamResponse[DepsT, None]
            | ContextStreamResponse[DepsT, FormattableT]
        ),
        content: UserContent,
    ) -> (
        ContextRetryStreamResponse[DepsT, None]
        | ContextRetryStreamResponse[DepsT, FormattableT]
    ):
        """Generate a new ContextRetryStreamResponse by extending another response's messages.

        Args:
            ctx: A `Context` with the required deps type.
            response: Previous context stream response to extend.
            content: Additional user content to append.

        Returns:
            A new ContextRetryStreamResponse for streaming the extended conversation.
        """
        return ContextRetryStreamResponse(
            self,
            lambda m: cast(
                "ContextStreamResponse[DepsT, FormattableT]",
                m.context_resume_stream(ctx=ctx, response=response, content=content),
            ),
        )

    @overload
    async def context_resume_stream_async(
        self,
        *,
        ctx: Context[DepsT],
        response: AsyncContextStreamResponse[DepsT, None],
        content: UserContent,
    ) -> AsyncContextRetryStreamResponse[DepsT, None]: ...

    @overload
    async def context_resume_stream_async(
        self,
        *,
        ctx: Context[DepsT],
        response: AsyncContextStreamResponse[DepsT, FormattableT],
        content: UserContent,
    ) -> AsyncContextRetryStreamResponse[DepsT, FormattableT]: ...

    @overload
    async def context_resume_stream_async(
        self,
        *,
        ctx: Context[DepsT],
        response: (
            AsyncContextStreamResponse[DepsT, None]
            | AsyncContextStreamResponse[DepsT, FormattableT]
        ),
        content: UserContent,
    ) -> (
        AsyncContextRetryStreamResponse[DepsT, None]
        | AsyncContextRetryStreamResponse[DepsT, FormattableT]
    ): ...

    async def context_resume_stream_async(  # pyright: ignore[reportIncompatibleMethodOverride]
        self,
        *,
        ctx: Context[DepsT],
        response: (
            AsyncContextStreamResponse[DepsT, None]
            | AsyncContextStreamResponse[DepsT, FormattableT]
        ),
        content: UserContent,
    ) -> (
        AsyncContextRetryStreamResponse[DepsT, None]
        | AsyncContextRetryStreamResponse[DepsT, FormattableT]
    ):
        """Generate a new AsyncContextRetryStreamResponse by extending another response's messages.

        Args:
            ctx: A `Context` with the required deps type.
            response: Previous async context stream response to extend.
            content: Additional user content to append.

        Returns:
            A new AsyncContextRetryStreamResponse for asynchronously streaming the extended conversation.
        """

        def stream_fn(
            m: Model,
        ) -> Awaitable[AsyncContextStreamResponse[DepsT, FormattableT]]:
            return cast(
                "Awaitable[AsyncContextStreamResponse[DepsT, FormattableT]]",
                m.context_resume_stream_async(
                    ctx=ctx, response=response, content=content
                ),
            )

        variants_iter = self.variants_async()
        initial_variant = await anext(variants_iter)
        initial_stream = await stream_fn(initial_variant.get_active_model())
        return AsyncContextRetryStreamResponse(
            stream_fn, initial_stream, initial_variant, variants_iter
        )


def retry_model(
    model_id: ModelId,
    **kwargs: Unpack[RetryModelParams],
) -> RetryModel:
    """Helper for creating a `RetryModel` instance with retry logic.

    This function creates a RetryModel that wraps the specified model with automatic
    retry functionality. It accepts both model parameters (temperature, max_tokens, etc.)
    and retry configuration (max_retries, initial_delay, etc.) in a single call.

    Args:
        model_id: A model ID string (e.g., "openai/gpt-4").
        **kwargs: Combined model parameters and retry configuration. Model parameters
            (temperature, max_tokens, top_p, top_k, seed, stop_sequences, thinking)
            are passed to the underlying Model. Retry parameters (max_retries, retry_on,
            initial_delay, max_delay, backoff_multiplier, jitter, fallback_models)
            configure the retry behavior.

    Returns:
        A RetryModel instance configured with the specified model and retry settings.

    Raises:
        ValueError: If the model_id format is invalid.

    Example:
        Basic usage with retry defaults:

        ```python
        import mirascope.llm as llm

        model = llm.retry_model("openai/gpt-4o")
        response = model.call("Hello!")
        ```

    Example:
        With model parameters and retry configuration:

        ```python
        import mirascope.llm as llm

        model = llm.retry_model(
            "openai/gpt-4o",
            temperature=0.7,
            max_tokens=1000,
            max_retries=5,
            initial_delay=1.0,
            backoff_multiplier=2.0,
        )
        response = model.call("Write a story.")
        ```

    Example:
        With fallback models:

        ```python
        import mirascope.llm as llm

        model = llm.retry_model(
            "openai/gpt-4o",
            max_retries=3,
            fallback_models=["anthropic/claude-sonnet-4-5", "google/gemini-2.0-flash"],
        )
        response = model.call("Complex task...")
        ```
    """
    # Separate retry args from model params
    retry_args: RetryArgs = {}
    model_params: Params = {}

    for key, value in kwargs.items():
        if key in _RETRY_ARG_KEYS:
            retry_args[key] = value
        else:
            model_params[key] = value

    retry_config = RetryConfig.from_args(**retry_args)
    return RetryModel(model_id, retry_config, **model_params)
