"""RetryModel extends Model to add retry logic."""

from collections.abc import Sequence
from typing import cast, overload
from typing_extensions import Unpack

from ..formatting import FormatSpec, FormattableT
from ..messages import Message, UserContent
from ..models import Model, Params
from ..providers import ModelId
from ..responses import (
    AsyncResponse,
    Response,
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


class RetryModel(Model):
    """Extends Model with retry logic.

    This class wraps a Model (or creates one from a ModelId) and overrides call methods
    to return RetryResponse instances instead of Response instances. In the future, it
    will implement actual retry logic for handling failures, rate limits, and validation
    errors.

    Example:
        Wrapping an existing Model:

        ```python
        model = llm.Model("openai/gpt-4o", temperature=0.7)
        retry_model = llm.RetryModel(model, RetryConfig(max_attempts=3))
        ```

        Creating from a ModelId:

        ```python
        retry_model = llm.RetryModel(
            "openai/gpt-4o",
            RetryConfig(max_attempts=3),
            temperature=0.7,
        )
        ```
    """

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
        if isinstance(model, Model):
            # Wrap existing Model - copy its model_id and params
            super().__init__(model.model_id, **model.params)
        else:
            # Create from ModelId
            super().__init__(model, **params)
        self.retry_config = retry_config

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
        """
        # TODO: Wire in retry implementation
        response = super().call(content, tools=tools, format=format)
        return RetryResponse(
            response=cast(Response[FormattableT], response),
            retry_config=self.retry_config,
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
        """
        # TODO: Wire in retry implementation
        response = await super().call_async(content, tools=tools, format=format)
        return AsyncRetryResponse(
            response=cast(AsyncResponse[FormattableT], response),
            retry_config=self.retry_config,
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
        """
        # TODO: Wire in retry implementation
        new_response = super().resume(response=response, content=content)
        return RetryResponse(
            response=cast(Response[FormattableT], new_response),
            retry_config=self.retry_config,
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
        """
        # TODO: Wire in retry implementation
        new_response = await super().resume_async(response=response, content=content)
        return AsyncRetryResponse(
            response=cast(AsyncResponse[FormattableT], new_response),
            retry_config=self.retry_config,
        )
