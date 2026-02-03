"""RetryModel extends Model to add retry logic."""

from collections.abc import Awaitable, Iterator, Sequence
from typing import cast, overload
from typing_extensions import Unpack

from ..formatting import FormatSpec, FormattableT
from ..messages import Message, UserContent
from ..models import Model, Params
from ..providers import ModelId
from ..responses import (
    AsyncResponse,
    AsyncStreamResponse,
    Response,
    StreamResponse,
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
from .retry_stream_responses import (
    AsyncRetryStreamResponse,
    RetryStreamResponse,
)
from .utils import with_retry, with_retry_async


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

        Note: Streaming does not currently support fallback models. Retries will
        only be attempted with the active model.

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

        Note: Streaming does not currently support fallback models. Retries will
        only be attempted with the active model.

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

        initial_stream = await stream_fn(self._models[self._active_index])
        return AsyncRetryStreamResponse(self, stream_fn, initial_stream)

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

        initial_stream = await stream_fn(self._models[self._active_index])
        return AsyncRetryStreamResponse(self, stream_fn, initial_stream)
