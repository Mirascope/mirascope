"""Mock Provider for testing retry logic."""

from collections.abc import Sequence
from typing import Any, ClassVar
from typing_extensions import Unpack

from mirascope import llm
from mirascope.llm import (
    AsyncContextResponse,
    AsyncContextStreamResponse,
    AsyncContextToolkit,
    AsyncResponse,
    AsyncStreamResponse,
    AsyncToolkit,
    Context,
    ContextResponse,
    ContextStreamResponse,
    ContextToolkit,
    DepsT,
    Format,
    FormattableT,
    OutputParser,
    Params,
    Response,
    StreamResponse,
    Toolkit,
)
from mirascope.llm.providers import BaseProvider
from mirascope.llm.providers.base import ProviderErrorMap


class MockProvider(BaseProvider[None]):
    """A mock Provider for testing that returns configurable responses.

    The provider can be configured with a sequence of exceptions to raise before
    eventually returning a successful response. This allows testing retry logic
    with predictable failure patterns.
    """

    # TODO Consider unifying with test provider.
    # cf #2101 (https://github.com/Mirascope/mirascope/issues/2120)

    id: ClassVar[llm.ProviderId] = "mock"
    default_scope: ClassVar[str | list[str]] = "mock/"
    error_map: ClassVar[ProviderErrorMap] = {}

    def __init__(self) -> None:
        """Initialize the MockProvider."""
        self.client = None
        self._exceptions: list[BaseException] = []
        self._call_count = 0

    @property
    def call_count(self) -> int:
        """The number of times _call() has been invoked."""
        return self._call_count

    def set_exceptions(self, exceptions: Sequence[BaseException]) -> None:
        """Set exceptions to raise before returning a successful response.

        Args:
            exceptions: A list of exceptions to raise in order. Once exhausted,
                subsequent calls will return the mock response.
        """
        self._exceptions = list(exceptions)

    def _make_response(
        self, model_id: str, messages: Sequence[llm.messages.Message]
    ) -> Response[Any]:
        """Create a minimal valid Response for testing."""
        return Response(
            raw={"mock": True},
            usage=None,
            provider_id="mock",
            model_id=model_id,
            provider_model_name="test-model",
            params={},
            tools=None,
            input_messages=list(messages),
            assistant_message=llm.messages.assistant(
                [llm.Text(text="mock response")],
                model_id=model_id,
                provider_id="mock",
            ),
            finish_reason=None,
        )

    def _make_async_response(
        self, model_id: str, messages: Sequence[llm.messages.Message]
    ) -> AsyncResponse[Any]:
        """Create a minimal valid AsyncResponse for testing."""
        return AsyncResponse(
            raw={"mock": True},
            usage=None,
            provider_id="mock",
            model_id=model_id,
            provider_model_name="test-model",
            params={},
            tools=None,
            input_messages=list(messages),
            assistant_message=llm.messages.assistant(
                [llm.Text(text="mock response")],
                model_id=model_id,
                provider_id="mock",
            ),
            finish_reason=None,
        )

    def _call(
        self,
        *,
        model_id: str,
        messages: Sequence[llm.messages.Message],
        toolkit: Toolkit,
        format: type[FormattableT]
        | Format[FormattableT]
        | OutputParser[FormattableT]
        | None = None,
        **params: Unpack[Params],
    ) -> Response[Any]:
        """Return the configured response or raise the next configured exception."""
        self._call_count += 1
        if self._exceptions:
            raise self._exceptions.pop(0)
        return self._make_response(model_id, messages)

    async def _call_async(
        self,
        *,
        model_id: str,
        messages: Sequence[llm.messages.Message],
        toolkit: AsyncToolkit,
        format: type[FormattableT]
        | Format[FormattableT]
        | OutputParser[FormattableT]
        | None = None,
        **params: Unpack[Params],
    ) -> AsyncResponse[Any]:
        """Return the configured response or raise the next configured exception."""
        self._call_count += 1
        if self._exceptions:
            raise self._exceptions.pop(0)
        return self._make_async_response(model_id, messages)

    def _context_call(
        self,
        *,
        ctx: Context[DepsT],
        model_id: str,
        messages: Sequence[llm.messages.Message],
        toolkit: ContextToolkit[DepsT],
        format: type[FormattableT]
        | Format[FormattableT]
        | OutputParser[FormattableT]
        | None = None,
        **params: Unpack[Params],
    ) -> ContextResponse[DepsT, None] | ContextResponse[DepsT, FormattableT]:
        """Not implemented for mock."""
        raise NotImplementedError

    async def _context_call_async(
        self,
        *,
        ctx: Context[DepsT],
        model_id: str,
        messages: Sequence[llm.messages.Message],
        toolkit: AsyncContextToolkit[DepsT],
        format: type[FormattableT]
        | Format[FormattableT]
        | OutputParser[FormattableT]
        | None = None,
        **params: Unpack[Params],
    ) -> AsyncContextResponse[DepsT, None] | AsyncContextResponse[DepsT, FormattableT]:
        """Not implemented for mock."""
        raise NotImplementedError

    def _stream(
        self,
        *,
        model_id: str,
        messages: Sequence[llm.messages.Message],
        toolkit: Toolkit,
        format: type[FormattableT]
        | Format[FormattableT]
        | OutputParser[FormattableT]
        | None = None,
        **params: Unpack[Params],
    ) -> StreamResponse[Any]:
        """Not implemented for mock."""
        raise NotImplementedError

    async def _stream_async(
        self,
        *,
        model_id: str,
        messages: Sequence[llm.messages.Message],
        toolkit: AsyncToolkit,
        format: type[FormattableT]
        | Format[FormattableT]
        | OutputParser[FormattableT]
        | None = None,
        **params: Unpack[Params],
    ) -> AsyncStreamResponse[Any]:
        """Not implemented for mock."""
        raise NotImplementedError

    def _context_stream(
        self,
        *,
        ctx: Context[DepsT],
        model_id: str,
        messages: Sequence[llm.messages.Message],
        toolkit: ContextToolkit[DepsT],
        format: type[FormattableT]
        | Format[FormattableT]
        | OutputParser[FormattableT]
        | None = None,
        **params: Unpack[Params],
    ) -> (
        ContextStreamResponse[DepsT, None] | ContextStreamResponse[DepsT, FormattableT]
    ):
        """Not implemented for mock."""
        raise NotImplementedError

    async def _context_stream_async(
        self,
        *,
        ctx: Context[DepsT],
        model_id: str,
        messages: Sequence[llm.messages.Message],
        toolkit: AsyncContextToolkit[DepsT],
        format: type[FormattableT]
        | Format[FormattableT]
        | OutputParser[FormattableT]
        | None = None,
        **params: Unpack[Params],
    ) -> (
        AsyncContextStreamResponse[DepsT, None]
        | AsyncContextStreamResponse[DepsT, FormattableT]
    ):
        """Not implemented for mock."""
        raise NotImplementedError

    def get_error_status(self, e: Exception) -> int | None:
        """Return None for mock provider."""
        return None
