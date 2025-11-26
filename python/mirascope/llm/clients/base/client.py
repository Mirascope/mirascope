"""Base abstract interface for provider clients."""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Sequence
from contextvars import ContextVar, Token
from types import TracebackType
from typing import Any, Generic, cast, overload
from typing_extensions import Self, TypeVar, Unpack

from ...context import Context, DepsT
from ...formatting import Format, FormattableT
from ...messages import Message, UserContent, user
from ...responses import (
    AsyncContextResponse,
    AsyncContextStreamResponse,
    AsyncResponse,
    AsyncStreamResponse,
    ContextResponse,
    ContextStreamResponse,
    Response,
    StreamResponse,
)
from ...tools import (
    AsyncContextTool,
    AsyncContextToolkit,
    AsyncTool,
    AsyncToolkit,
    ContextTool,
    ContextToolkit,
    Tool,
    Toolkit,
)
from .params import Params

ModelIdT = TypeVar("ModelIdT", bound=str)
ProviderClientT = TypeVar("ProviderClientT")

ClientT = TypeVar("ClientT", bound="BaseClient[str, Any, Any]")
"""Type variable for an LLM client."""


class BaseClient(Generic[ModelIdT, ProviderClientT, ClientT], ABC):
    """Base abstract client for provider-specific implementations.

    This class defines explicit methods for each type of call, eliminating
    the need for complex overloads in provider implementations.
    """

    client: ProviderClientT
    _token: Token[ClientT] | None = None

    @property
    @abstractmethod
    def _context_var(self) -> ContextVar[ClientT]:
        """The ContextVar for this client type."""
        ...

    def __enter__(self) -> Self:
        """Sets the client context and stores the token."""
        self._token = self._context_var.set(cast(ClientT, self))
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        """Restores the client context to the token from the last setting."""
        if self._token is not None:
            self._context_var.reset(self._token)
            self._token = None

    @overload
    @abstractmethod
    def call(
        self,
        *,
        model_id: ModelIdT,
        messages: Sequence[Message],
        tools: Sequence[Tool] | Toolkit | None = None,
        format: None = None,
        **params: Unpack[Params],
    ) -> Response:
        """Generate an `llm.Response` without a response format."""
        ...

    @overload
    @abstractmethod
    def call(
        self,
        *,
        model_id: ModelIdT,
        messages: Sequence[Message],
        tools: Sequence[Tool] | Toolkit | None = None,
        format: type[FormattableT] | Format[FormattableT],
        **params: Unpack[Params],
    ) -> Response[FormattableT]:
        """Generate an `llm.Response` with a response format."""
        ...

    @overload
    @abstractmethod
    def call(
        self,
        *,
        model_id: ModelIdT,
        messages: Sequence[Message],
        tools: Sequence[Tool] | Toolkit | None = None,
        format: type[FormattableT] | Format[FormattableT] | None,
        **params: Unpack[Params],
    ) -> Response | Response[FormattableT]:
        """Generate an `llm.Response` with an optional response format."""
        ...

    @abstractmethod
    def call(
        self,
        *,
        model_id: ModelIdT,
        messages: Sequence[Message],
        tools: Sequence[Tool] | Toolkit | None = None,
        format: type[FormattableT] | Format[FormattableT] | None = None,
        **params: Unpack[Params],
    ) -> Response | Response[FormattableT]:
        """Generate an `llm.Response` by synchronously calling this client's LLM provider.

        Args:
            model_id: Model identifier to use.
            messages: Messages to send to the LLM.
            tools: Optional tools that the model may invoke.
            format: Optional response format specifier.
            **params: Additional parameters to configure output (e.g. temperature). See `llm.Params`.

        Returns:
            An `llm.Response` object containing the LLM-generated content.
        """
        ...

    @overload
    @abstractmethod
    def context_call(
        self,
        *,
        ctx: Context[DepsT],
        model_id: ModelIdT,
        messages: Sequence[Message],
        tools: Sequence[Tool | ContextTool[DepsT]]
        | ContextToolkit[DepsT]
        | None = None,
        format: None = None,
        **params: Unpack[Params],
    ) -> ContextResponse[DepsT, None]:
        """Generate an `llm.ContextResponse` without a response format."""
        ...

    @overload
    @abstractmethod
    def context_call(
        self,
        *,
        ctx: Context[DepsT],
        model_id: ModelIdT,
        messages: Sequence[Message],
        tools: Sequence[Tool | ContextTool[DepsT]]
        | ContextToolkit[DepsT]
        | None = None,
        format: type[FormattableT] | Format[FormattableT],
        **params: Unpack[Params],
    ) -> ContextResponse[DepsT, FormattableT]:
        """Generate an `llm.ContextResponse` with a response format."""
        ...

    @overload
    @abstractmethod
    def context_call(
        self,
        *,
        ctx: Context[DepsT],
        model_id: ModelIdT,
        messages: Sequence[Message],
        tools: Sequence[Tool | ContextTool[DepsT]]
        | ContextToolkit[DepsT]
        | None = None,
        format: type[FormattableT] | Format[FormattableT] | None,
        **params: Unpack[Params],
    ) -> ContextResponse[DepsT, None] | ContextResponse[DepsT, FormattableT]:
        """Generate an `llm.ContextResponse` with an optional response format."""
        ...

    @abstractmethod
    def context_call(
        self,
        *,
        ctx: Context[DepsT],
        model_id: ModelIdT,
        messages: Sequence[Message],
        tools: Sequence[Tool | ContextTool[DepsT]]
        | ContextToolkit[DepsT]
        | None = None,
        format: type[FormattableT] | Format[FormattableT] | None = None,
        **params: Unpack[Params],
    ) -> ContextResponse[DepsT, None] | ContextResponse[DepsT, FormattableT]:
        """Generate an `llm.ContextResponse` by synchronously calling this client's LLM provider.

        Args:
            ctx: Context object with dependencies for tools.
            model_id: Model identifier to use.
            messages: Messages to send to the LLM.
            tools: Optional tools that the model may invoke.
            format: Optional response format specifier.
            **params: Additional parameters to configure output (e.g. temperature). See `llm.Params`.

        Returns:
            An `llm.ContextResponse` object containing the LLM-generated content.
        """
        ...

    @overload
    @abstractmethod
    async def call_async(
        self,
        *,
        model_id: ModelIdT,
        messages: Sequence[Message],
        tools: Sequence[AsyncTool] | AsyncToolkit | None = None,
        format: None = None,
        **params: Unpack[Params],
    ) -> AsyncResponse:
        """Generate an `llm.AsyncResponse` without a response format."""
        ...

    @overload
    @abstractmethod
    async def call_async(
        self,
        *,
        model_id: ModelIdT,
        messages: Sequence[Message],
        tools: Sequence[AsyncTool] | AsyncToolkit | None = None,
        format: type[FormattableT] | Format[FormattableT],
        **params: Unpack[Params],
    ) -> AsyncResponse[FormattableT]:
        """Generate an `llm.AsyncResponse` with a response format."""
        ...

    @overload
    @abstractmethod
    async def call_async(
        self,
        *,
        model_id: ModelIdT,
        messages: Sequence[Message],
        tools: Sequence[AsyncTool] | AsyncToolkit | None = None,
        format: type[FormattableT] | Format[FormattableT] | None,
        **params: Unpack[Params],
    ) -> AsyncResponse | AsyncResponse[FormattableT]:
        """Generate an `llm.AsyncResponse` with an optional response format."""
        ...

    @abstractmethod
    async def call_async(
        self,
        *,
        model_id: ModelIdT,
        messages: Sequence[Message],
        tools: Sequence[AsyncTool] | AsyncToolkit | None = None,
        format: type[FormattableT] | Format[FormattableT] | None = None,
        **params: Unpack[Params],
    ) -> AsyncResponse | AsyncResponse[FormattableT]:
        """Generate an `llm.AsyncResponse` by asynchronously calling this client's LLM provider.

        Args:
            model_id: Model identifier to use.
            messages: Messages to send to the LLM.
            tools: Optional tools that the model may invoke.
            format: Optional response format specifier.
            **params: Additional parameters to configure output (e.g. temperature). See `llm.Params`.

        Returns:
            An `llm.AsyncResponse` object containing the LLM-generated content.
        """
        ...

    @overload
    @abstractmethod
    async def context_call_async(
        self,
        *,
        ctx: Context[DepsT],
        model_id: ModelIdT,
        messages: Sequence[Message],
        tools: Sequence[AsyncTool | AsyncContextTool[DepsT]]
        | AsyncContextToolkit[DepsT]
        | None = None,
        format: None = None,
        **params: Unpack[Params],
    ) -> AsyncContextResponse[DepsT, None]:
        """Generate an `llm.AsyncContextResponse` without a response format."""
        ...

    @overload
    @abstractmethod
    async def context_call_async(
        self,
        *,
        ctx: Context[DepsT],
        model_id: ModelIdT,
        messages: Sequence[Message],
        tools: Sequence[AsyncTool | AsyncContextTool[DepsT]]
        | AsyncContextToolkit[DepsT]
        | None = None,
        format: type[FormattableT] | Format[FormattableT],
        **params: Unpack[Params],
    ) -> AsyncContextResponse[DepsT, FormattableT]:
        """Generate an `llm.AsyncContextResponse` with a response format."""
        ...

    @overload
    @abstractmethod
    async def context_call_async(
        self,
        *,
        ctx: Context[DepsT],
        model_id: ModelIdT,
        messages: Sequence[Message],
        tools: Sequence[AsyncTool | AsyncContextTool[DepsT]]
        | AsyncContextToolkit[DepsT]
        | None = None,
        format: type[FormattableT] | Format[FormattableT] | None,
        **params: Unpack[Params],
    ) -> AsyncContextResponse[DepsT, None] | AsyncContextResponse[DepsT, FormattableT]:
        """Generate an `llm.AsyncContextResponse` with an optional response format."""
        ...

    @abstractmethod
    async def context_call_async(
        self,
        *,
        ctx: Context[DepsT],
        model_id: ModelIdT,
        messages: Sequence[Message],
        tools: Sequence[AsyncTool | AsyncContextTool[DepsT]]
        | AsyncContextToolkit[DepsT]
        | None = None,
        format: type[FormattableT] | Format[FormattableT] | None = None,
        **params: Unpack[Params],
    ) -> AsyncContextResponse[DepsT, None] | AsyncContextResponse[DepsT, FormattableT]:
        """Generate an `llm.AsyncContextResponse` by asynchronously calling this client's LLM provider.

        Args:
            ctx: Context object with dependencies for tools.
            model_id: Model identifier to use.
            messages: Messages to send to the LLM.
            tools: Optional tools that the model may invoke.
            format: Optional response format specifier.
            **params: Additional parameters to configure output (e.g. temperature). See `llm.Params`.

        Returns:
            An `llm.AsyncContextResponse` object containing the LLM-generated content.
        """
        ...

    @overload
    @abstractmethod
    def stream(
        self,
        *,
        model_id: ModelIdT,
        messages: Sequence[Message],
        tools: Sequence[Tool] | Toolkit | None = None,
        format: None = None,
        **params: Unpack[Params],
    ) -> StreamResponse:
        """Stream an `llm.StreamResponse` without a response format."""
        ...

    @overload
    @abstractmethod
    def stream(
        self,
        *,
        model_id: ModelIdT,
        messages: Sequence[Message],
        tools: Sequence[Tool] | Toolkit | None = None,
        format: type[FormattableT] | Format[FormattableT],
        **params: Unpack[Params],
    ) -> StreamResponse[FormattableT]:
        """Stream an `llm.StreamResponse` with a response format."""
        ...

    @overload
    @abstractmethod
    def stream(
        self,
        *,
        model_id: ModelIdT,
        messages: Sequence[Message],
        tools: Sequence[Tool] | Toolkit | None = None,
        format: type[FormattableT] | Format[FormattableT] | None,
        **params: Unpack[Params],
    ) -> StreamResponse | StreamResponse[FormattableT]:
        """Stream an `llm.StreamResponse` with an optional response format."""
        ...

    @abstractmethod
    def stream(
        self,
        *,
        model_id: ModelIdT,
        messages: Sequence[Message],
        tools: Sequence[Tool] | Toolkit | None = None,
        format: type[FormattableT] | Format[FormattableT] | None = None,
        **params: Unpack[Params],
    ) -> StreamResponse | StreamResponse[FormattableT]:
        """Generate an `llm.StreamResponse` by synchronously streaming from this client's LLM provider.

        Args:
            model_id: Model identifier to use.
            messages: Messages to send to the LLM.
            tools: Optional tools that the model may invoke.
            format: Optional response format specifier.
            **params: Additional parameters to configure output (e.g. temperature). See `llm.Params`.

        Returns:
            An `llm.StreamResponse` object for iterating over the LLM-generated content.
        """
        ...

    @overload
    @abstractmethod
    def context_stream(
        self,
        *,
        ctx: Context[DepsT],
        model_id: ModelIdT,
        messages: Sequence[Message],
        tools: Sequence[Tool | ContextTool[DepsT]]
        | ContextToolkit[DepsT]
        | None = None,
        format: None = None,
        **params: Unpack[Params],
    ) -> ContextStreamResponse[DepsT, None]:
        """Stream an `llm.ContextStreamResponse` without a response format."""
        ...

    @overload
    @abstractmethod
    def context_stream(
        self,
        *,
        ctx: Context[DepsT],
        model_id: ModelIdT,
        messages: Sequence[Message],
        tools: Sequence[Tool | ContextTool[DepsT]]
        | ContextToolkit[DepsT]
        | None = None,
        format: type[FormattableT] | Format[FormattableT],
        **params: Unpack[Params],
    ) -> ContextStreamResponse[DepsT, FormattableT]:
        """Stream an `llm.ContextStreamResponse` with a response format."""
        ...

    @overload
    @abstractmethod
    def context_stream(
        self,
        *,
        ctx: Context[DepsT],
        model_id: ModelIdT,
        messages: Sequence[Message],
        tools: Sequence[Tool | ContextTool[DepsT]]
        | ContextToolkit[DepsT]
        | None = None,
        format: type[FormattableT] | Format[FormattableT] | None,
        **params: Unpack[Params],
    ) -> (
        ContextStreamResponse[DepsT, None] | ContextStreamResponse[DepsT, FormattableT]
    ):
        """Stream an `llm.ContextStreamResponse` with an optional response format."""
        ...

    @abstractmethod
    def context_stream(
        self,
        *,
        ctx: Context[DepsT],
        model_id: ModelIdT,
        messages: Sequence[Message],
        tools: Sequence[Tool | ContextTool[DepsT]]
        | ContextToolkit[DepsT]
        | None = None,
        format: type[FormattableT] | Format[FormattableT] | None = None,
        **params: Unpack[Params],
    ) -> (
        ContextStreamResponse[DepsT, None] | ContextStreamResponse[DepsT, FormattableT]
    ):
        """Generate an `llm.ContextStreamResponse` by synchronously streaming from this client's LLM provider.

        Args:
            ctx: Context object with dependencies for tools.
            model_id: Model identifier to use.
            messages: Messages to send to the LLM.
            tools: Optional tools that the model may invoke.
            format: Optional response format specifier.
            **params: Additional parameters to configure output (e.g. temperature). See `llm.Params`.

        Returns:
            An `llm.ContextStreamResponse` object for iterating over the LLM-generated content.
        """
        ...

    @overload
    @abstractmethod
    async def stream_async(
        self,
        *,
        model_id: ModelIdT,
        messages: Sequence[Message],
        tools: Sequence[AsyncTool] | AsyncToolkit | None = None,
        format: None = None,
        **params: Unpack[Params],
    ) -> AsyncStreamResponse:
        """Stream an `llm.AsyncStreamResponse` without a response format."""
        ...

    @overload
    @abstractmethod
    async def stream_async(
        self,
        *,
        model_id: ModelIdT,
        messages: Sequence[Message],
        tools: Sequence[AsyncTool] | AsyncToolkit | None = None,
        format: type[FormattableT] | Format[FormattableT],
        **params: Unpack[Params],
    ) -> AsyncStreamResponse[FormattableT]:
        """Stream an `llm.AsyncStreamResponse` with a response format."""
        ...

    @overload
    @abstractmethod
    async def stream_async(
        self,
        *,
        model_id: ModelIdT,
        messages: Sequence[Message],
        tools: Sequence[AsyncTool] | AsyncToolkit | None = None,
        format: type[FormattableT] | Format[FormattableT] | None,
        **params: Unpack[Params],
    ) -> AsyncStreamResponse | AsyncStreamResponse[FormattableT]:
        """Stream an `llm.AsyncStreamResponse` with an optional response format."""
        ...

    @abstractmethod
    async def stream_async(
        self,
        *,
        model_id: ModelIdT,
        messages: Sequence[Message],
        tools: Sequence[AsyncTool] | AsyncToolkit | None = None,
        format: type[FormattableT] | Format[FormattableT] | None = None,
        **params: Unpack[Params],
    ) -> AsyncStreamResponse | AsyncStreamResponse[FormattableT]:
        """Generate an `llm.AsyncStreamResponse` by asynchronously streaming from this client's LLM provider.

        Args:
            model_id: Model identifier to use.
            messages: Messages to send to the LLM.
            tools: Optional tools that the model may invoke.
            format: Optional response format specifier.
            **params: Additional parameters to configure output (e.g. temperature). See `llm.Params`.

        Returns:
            An `llm.AsyncStreamResponse` object for asynchronously iterating over the LLM-generated content.
        """
        ...

    @overload
    @abstractmethod
    async def context_stream_async(
        self,
        *,
        ctx: Context[DepsT],
        model_id: ModelIdT,
        messages: Sequence[Message],
        tools: Sequence[AsyncTool | AsyncContextTool[DepsT]]
        | AsyncContextToolkit[DepsT]
        | None = None,
        format: None = None,
        **params: Unpack[Params],
    ) -> AsyncContextStreamResponse[DepsT, None]:
        """Stream an `llm.AsyncContextStreamResponse` without a response format."""
        ...

    @overload
    @abstractmethod
    async def context_stream_async(
        self,
        *,
        ctx: Context[DepsT],
        model_id: ModelIdT,
        messages: Sequence[Message],
        tools: Sequence[AsyncTool | AsyncContextTool[DepsT]]
        | AsyncContextToolkit[DepsT]
        | None = None,
        format: type[FormattableT] | Format[FormattableT],
        **params: Unpack[Params],
    ) -> AsyncContextStreamResponse[DepsT, FormattableT]:
        """Stream an `llm.AsyncContextStreamResponse` with a response format."""
        ...

    @overload
    @abstractmethod
    async def context_stream_async(
        self,
        *,
        ctx: Context[DepsT],
        model_id: ModelIdT,
        messages: Sequence[Message],
        tools: Sequence[AsyncTool | AsyncContextTool[DepsT]]
        | AsyncContextToolkit[DepsT]
        | None = None,
        format: type[FormattableT] | Format[FormattableT] | None,
        **params: Unpack[Params],
    ) -> (
        AsyncContextStreamResponse[DepsT, None]
        | AsyncContextStreamResponse[DepsT, FormattableT]
    ):
        """Stream an `llm.AsyncContextStreamResponse` with an optional response format."""
        ...

    @abstractmethod
    async def context_stream_async(
        self,
        *,
        ctx: Context[DepsT],
        model_id: ModelIdT,
        messages: Sequence[Message],
        tools: Sequence[AsyncTool | AsyncContextTool[DepsT]]
        | AsyncContextToolkit[DepsT]
        | None = None,
        format: type[FormattableT] | Format[FormattableT] | None = None,
        **params: Unpack[Params],
    ) -> (
        AsyncContextStreamResponse[DepsT, None]
        | AsyncContextStreamResponse[DepsT, FormattableT]
    ):
        """Generate an `llm.AsyncContextStreamResponse` by asynchronously streaming from this client's LLM provider.

        Args:
            ctx: Context object with dependencies for tools.
            model_id: Model identifier to use.
            messages: Messages to send to the LLM.
            tools: Optional tools that the model may invoke.
            format: Optional response format specifier.
            **params: Additional parameters to configure output (e.g. temperature). See `llm.Params`.

        Returns:
            An `llm.AsyncContextStreamResponse` object for asynchronously iterating over the LLM-generated content.
        """
        ...

    @overload
    def resume(
        self,
        *,
        model_id: ModelIdT,
        response: Response,
        content: UserContent,
        **params: Unpack[Params],
    ) -> Response:
        """Resume an `llm.Response` without a response format."""
        ...

    @overload
    def resume(
        self,
        *,
        model_id: ModelIdT,
        response: Response[FormattableT],
        content: UserContent,
        **params: Unpack[Params],
    ) -> Response[FormattableT]:
        """Resume an `llm.Response` with a response format."""
        ...

    @overload
    def resume(
        self,
        *,
        model_id: ModelIdT,
        response: Response | Response[FormattableT],
        content: UserContent,
        **params: Unpack[Params],
    ) -> Response | Response[FormattableT]:
        """Resume an `llm.Response` with an optional response format."""
        ...

    def resume(
        self,
        *,
        model_id: ModelIdT,
        response: Response | Response[FormattableT],
        content: UserContent,
        **params: Unpack[Params],
    ) -> Response | Response[FormattableT]:
        """Generate a new `llm.Response` by extending another response's messages with additional user content.

        Args:
            model_id: Model identifier to use.
            response: Previous response to extend.
            content: Additional user content to append.
            **params: Additional parameters to configure output (e.g. temperature). See `llm.Params`.

        Returns:
            A new `llm.Response` object containing the extended conversation.

        Note:
            Uses the previous response's tools and output format. This base method wraps
            around calling `client.call()` with a messages array derived from the response
            messages. However, clients may override this with first-class resume logic.
        """
        messages = response.messages + [user(content)]
        return self.call(
            model_id=model_id,
            messages=messages,
            tools=response.toolkit,
            format=response.format,
            **params,
        )

    @overload
    async def resume_async(
        self,
        *,
        model_id: ModelIdT,
        response: AsyncResponse,
        content: UserContent,
        **params: Unpack[Params],
    ) -> AsyncResponse:
        """Resume an `llm.AsyncResponse` without a response format."""
        ...

    @overload
    async def resume_async(
        self,
        *,
        model_id: ModelIdT,
        response: AsyncResponse[FormattableT],
        content: UserContent,
        **params: Unpack[Params],
    ) -> AsyncResponse[FormattableT]:
        """Resume an `llm.AsyncResponse` with a response format."""
        ...

    @overload
    async def resume_async(
        self,
        *,
        model_id: ModelIdT,
        response: AsyncResponse | AsyncResponse[FormattableT],
        content: UserContent,
        **params: Unpack[Params],
    ) -> AsyncResponse | AsyncResponse[FormattableT]:
        """Resume an `llm.AsyncResponse` with an optional response format."""
        ...

    async def resume_async(
        self,
        *,
        model_id: ModelIdT,
        response: AsyncResponse | AsyncResponse[FormattableT],
        content: UserContent,
        **params: Unpack[Params],
    ) -> AsyncResponse | AsyncResponse[FormattableT]:
        """Generate a new `llm.AsyncResponse` by extending another response's messages with additional user content.

        Args:
            model_id: Model identifier to use.
            response: Previous async response to extend.
            content: Additional user content to append.
            **params: Additional parameters to configure output (e.g. temperature). See `llm.Params`.

        Returns:
            A new `llm.AsyncResponse` object containing the extended conversation.

        Note:
            Uses the previous response's tools and output format. This base method wraps
            around calling `client.call_async()` with a messages array derived from the response
            messages. However, clients may override this with first-class resume logic.
        """
        messages = response.messages + [user(content)]
        return await self.call_async(
            model_id=model_id,
            messages=messages,
            tools=response.toolkit,
            format=response.format,
            **params,
        )

    @overload
    def context_resume(
        self,
        *,
        ctx: Context[DepsT],
        model_id: ModelIdT,
        response: ContextResponse[DepsT, None],
        content: UserContent,
        **params: Unpack[Params],
    ) -> ContextResponse[DepsT, None]:
        """Resume an `llm.ContextResponse` without a response format."""
        ...

    @overload
    def context_resume(
        self,
        *,
        ctx: Context[DepsT],
        model_id: ModelIdT,
        response: ContextResponse[DepsT, FormattableT],
        content: UserContent,
        **params: Unpack[Params],
    ) -> ContextResponse[DepsT, FormattableT]:
        """Resume an `llm.ContextResponse` with a response format."""
        ...

    @overload
    def context_resume(
        self,
        *,
        ctx: Context[DepsT],
        model_id: ModelIdT,
        response: ContextResponse[DepsT, None] | ContextResponse[DepsT, FormattableT],
        content: UserContent,
        **params: Unpack[Params],
    ) -> ContextResponse[DepsT, None] | ContextResponse[DepsT, FormattableT]:
        """Resume an `llm.ContextResponse` with an optional response format."""
        ...

    def context_resume(
        self,
        *,
        ctx: Context[DepsT],
        model_id: ModelIdT,
        response: ContextResponse[DepsT, None] | ContextResponse[DepsT, FormattableT],
        content: UserContent,
        **params: Unpack[Params],
    ) -> ContextResponse[DepsT, None] | ContextResponse[DepsT, FormattableT]:
        """Generate a new `llm.ContextResponse` by extending another response's messages with additional user content.

        Args:
            ctx: Context object with dependencies for tools.
            model_id: Model identifier to use.
            response: Previous context response to extend.
            content: Additional user content to append.
            **params: Additional parameters to configure output (e.g. temperature). See `llm.Params`.

        Returns:
            A new `llm.ContextResponse` object containing the extended conversation.

        Note:
            Uses the previous response's tools and output format. This base method wraps
            around calling `client.context_call()` with a messages array derived from the response
            messages. However, clients may override this with first-class resume logic.
        """
        messages = response.messages + [user(content)]
        return self.context_call(
            ctx=ctx,
            model_id=model_id,
            messages=messages,
            tools=response.toolkit,
            format=response.format,
            **params,
        )

    @overload
    async def context_resume_async(
        self,
        *,
        ctx: Context[DepsT],
        model_id: ModelIdT,
        response: AsyncContextResponse[DepsT, None],
        content: UserContent,
        **params: Unpack[Params],
    ) -> AsyncContextResponse[DepsT, None]:
        """Resume an `llm.AsyncContextResponse` without a response format."""
        ...

    @overload
    async def context_resume_async(
        self,
        *,
        ctx: Context[DepsT],
        model_id: ModelIdT,
        response: AsyncContextResponse[DepsT, FormattableT],
        content: UserContent,
        **params: Unpack[Params],
    ) -> AsyncContextResponse[DepsT, FormattableT]:
        """Resume an `llm.AsyncContextResponse` with a response format."""
        ...

    @overload
    async def context_resume_async(
        self,
        *,
        ctx: Context[DepsT],
        model_id: ModelIdT,
        response: AsyncContextResponse[DepsT, None]
        | AsyncContextResponse[DepsT, FormattableT],
        content: UserContent,
        **params: Unpack[Params],
    ) -> AsyncContextResponse[DepsT, None] | AsyncContextResponse[DepsT, FormattableT]:
        """Resume an `llm.AsyncContextResponse` with an optional response format."""
        ...

    async def context_resume_async(
        self,
        *,
        ctx: Context[DepsT],
        model_id: ModelIdT,
        response: AsyncContextResponse[DepsT, None]
        | AsyncContextResponse[DepsT, FormattableT],
        content: UserContent,
        **params: Unpack[Params],
    ) -> AsyncContextResponse[DepsT, None] | AsyncContextResponse[DepsT, FormattableT]:
        """Generate a new `llm.AsyncContextResponse` by extending another response's messages with additional user content.

        Args:
            ctx: Context object with dependencies for tools.
            model_id: Model identifier to use.
            response: Previous async context response to extend.
            content: Additional user content to append.
            **params: Additional parameters to configure output (e.g. temperature). See `llm.Params`.

        Returns:
            A new `llm.AsyncContextResponse` object containing the extended conversation.

        Note:
            Uses the previous response's tools and output format. This base method wraps
            around calling `client.context_call_async()` with a messages array derived from the response
            messages. However, clients may override this with first-class resume logic.
        """
        messages = response.messages + [user(content)]
        return await self.context_call_async(
            ctx=ctx,
            model_id=model_id,
            messages=messages,
            tools=response.toolkit,
            format=response.format,
            **params,
        )

    @overload
    def resume_stream(
        self,
        *,
        model_id: ModelIdT,
        response: StreamResponse,
        content: UserContent,
        **params: Unpack[Params],
    ) -> StreamResponse:
        """Resume an `llm.StreamResponse` without a response format."""
        ...

    @overload
    def resume_stream(
        self,
        *,
        model_id: ModelIdT,
        response: StreamResponse[FormattableT],
        content: UserContent,
        **params: Unpack[Params],
    ) -> StreamResponse[FormattableT]:
        """Resume an `llm.StreamResponse` with a response format."""
        ...

    @overload
    def resume_stream(
        self,
        *,
        model_id: ModelIdT,
        response: StreamResponse | StreamResponse[FormattableT],
        content: UserContent,
        **params: Unpack[Params],
    ) -> StreamResponse | StreamResponse[FormattableT]:
        """Resume an `llm.StreamResponse` with an optional response format."""
        ...

    def resume_stream(
        self,
        *,
        model_id: ModelIdT,
        response: StreamResponse | StreamResponse[FormattableT],
        content: UserContent,
        **params: Unpack[Params],
    ) -> StreamResponse | StreamResponse[FormattableT]:
        """Generate a new `llm.StreamResponse` by extending another response's messages with additional user content.

        Args:
            model_id: Model identifier to use.
            response: Previous stream response to extend.
            content: Additional user content to append.
            **params: Additional parameters to configure output (e.g. temperature). See `llm.Params`.

        Returns:
            A new `llm.StreamResponse` object for streaming the extended conversation.

        Note:
            Uses the previous response's tools and output format. This base method wraps
            around calling `client.stream()` with a messages array derived from the response
            messages. However, clients may override this with first-class resume logic.
        """
        messages = response.messages + [user(content)]
        return self.stream(
            model_id=model_id,
            messages=messages,
            tools=response.toolkit,
            format=response.format,
            **params,
        )

    @overload
    async def resume_stream_async(
        self,
        *,
        model_id: ModelIdT,
        response: AsyncStreamResponse,
        content: UserContent,
        **params: Unpack[Params],
    ) -> AsyncStreamResponse:
        """Resume an `llm.AsyncStreamResponse` without a response format."""
        ...

    @overload
    async def resume_stream_async(
        self,
        *,
        model_id: ModelIdT,
        response: AsyncStreamResponse[FormattableT],
        content: UserContent,
        **params: Unpack[Params],
    ) -> AsyncStreamResponse[FormattableT]:
        """Resume an `llm.AsyncStreamResponse` with a response format."""
        ...

    @overload
    async def resume_stream_async(
        self,
        *,
        model_id: ModelIdT,
        response: AsyncStreamResponse | AsyncStreamResponse[FormattableT],
        content: UserContent,
        **params: Unpack[Params],
    ) -> AsyncStreamResponse | AsyncStreamResponse[FormattableT]:
        """Resume an `llm.AsyncStreamResponse` with an optional response format."""
        ...

    async def resume_stream_async(
        self,
        *,
        model_id: ModelIdT,
        response: AsyncStreamResponse | AsyncStreamResponse[FormattableT],
        content: UserContent,
        **params: Unpack[Params],
    ) -> AsyncStreamResponse | AsyncStreamResponse[FormattableT]:
        """Generate a new `llm.AsyncStreamResponse` by extending another response's messages with additional user content.

        Args:
            model_id: Model identifier to use.
            response: Previous async stream response to extend.
            content: Additional user content to append.
            **params: Additional parameters to configure output (e.g. temperature). See `llm.Params`.

        Returns:
            A new `llm.AsyncStreamResponse` object for asynchronously streaming the extended conversation.

        Note:
            Uses the previous response's tools and output format. This base method wraps
            around calling `client.stream_async()` with a messages array derived from the response
            messages. However, clients may override this with first-class resume logic.
        """
        messages = response.messages + [user(content)]
        return await self.stream_async(
            model_id=model_id,
            messages=messages,
            tools=response.toolkit,
            format=response.format,
            **params,
        )

    @overload
    def context_resume_stream(
        self,
        *,
        ctx: Context[DepsT],
        model_id: ModelIdT,
        response: ContextStreamResponse[DepsT, None],
        content: UserContent,
        **params: Unpack[Params],
    ) -> ContextStreamResponse[DepsT, None]:
        """Resume an `llm.ContextStreamResponse` without a response format."""
        ...

    @overload
    def context_resume_stream(
        self,
        *,
        ctx: Context[DepsT],
        model_id: ModelIdT,
        response: ContextStreamResponse[DepsT, FormattableT],
        content: UserContent,
        **params: Unpack[Params],
    ) -> ContextStreamResponse[DepsT, FormattableT]:
        """Resume an `llm.ContextStreamResponse` with a response format."""
        ...

    @overload
    def context_resume_stream(
        self,
        *,
        ctx: Context[DepsT],
        model_id: ModelIdT,
        response: ContextStreamResponse[DepsT, None]
        | ContextStreamResponse[DepsT, FormattableT],
        content: UserContent,
        **params: Unpack[Params],
    ) -> (
        ContextStreamResponse[DepsT, None] | ContextStreamResponse[DepsT, FormattableT]
    ):
        """Resume an `llm.ContextStreamResponse` with an optional response format."""
        ...

    def context_resume_stream(
        self,
        *,
        ctx: Context[DepsT],
        model_id: ModelIdT,
        response: ContextStreamResponse[DepsT, None]
        | ContextStreamResponse[DepsT, FormattableT],
        content: UserContent,
        **params: Unpack[Params],
    ) -> (
        ContextStreamResponse[DepsT, None] | ContextStreamResponse[DepsT, FormattableT]
    ):
        """Generate a new `llm.ContextStreamResponse` by extending another response's messages with additional user content.

        Args:
            ctx: Context object with dependencies for tools.
            model_id: Model identifier to use.
            response: Previous context stream response to extend.
            content: Additional user content to append.
            **params: Additional parameters to configure output (e.g. temperature). See `llm.Params`.

        Returns:
            A new `llm.ContextStreamResponse` object for streaming the extended conversation.

        Note:
            Uses the previous response's tools and output format. This base method wraps
            around calling `client.context_stream()` with a messages array derived from the response
            messages. However, clients may override this with first-class resume logic.
        """
        messages = response.messages + [user(content)]
        return self.context_stream(
            ctx=ctx,
            model_id=model_id,
            messages=messages,
            tools=response.toolkit,
            format=response.format,
            **params,
        )

    @overload
    async def context_resume_stream_async(
        self,
        *,
        ctx: Context[DepsT],
        model_id: ModelIdT,
        response: AsyncContextStreamResponse[DepsT, None],
        content: UserContent,
        **params: Unpack[Params],
    ) -> AsyncContextStreamResponse[DepsT, None]:
        """Resume an `llm.AsyncContextStreamResponse` without a response format."""
        ...

    @overload
    async def context_resume_stream_async(
        self,
        *,
        ctx: Context[DepsT],
        model_id: ModelIdT,
        response: AsyncContextStreamResponse[DepsT, FormattableT],
        content: UserContent,
        **params: Unpack[Params],
    ) -> AsyncContextStreamResponse[DepsT, FormattableT]:
        """Resume an `llm.AsyncContextStreamResponse` with a response format."""
        ...

    @overload
    async def context_resume_stream_async(
        self,
        *,
        ctx: Context[DepsT],
        model_id: ModelIdT,
        response: AsyncContextStreamResponse[DepsT, None]
        | AsyncContextStreamResponse[DepsT, FormattableT],
        content: UserContent,
        **params: Unpack[Params],
    ) -> (
        AsyncContextStreamResponse[DepsT, None]
        | AsyncContextStreamResponse[DepsT, FormattableT]
    ):
        """Resume an `llm.AsyncContextStreamResponse` with an optional response format."""
        ...

    async def context_resume_stream_async(
        self,
        *,
        ctx: Context[DepsT],
        model_id: ModelIdT,
        response: AsyncContextStreamResponse[DepsT, None]
        | AsyncContextStreamResponse[DepsT, FormattableT],
        content: UserContent,
        **params: Unpack[Params],
    ) -> (
        AsyncContextStreamResponse[DepsT, None]
        | AsyncContextStreamResponse[DepsT, FormattableT]
    ):
        """Generate a new `llm.AsyncContextStreamResponse` by extending another response's messages with additional user content.

        Args:
            ctx: Context object with dependencies for tools.
            model_id: Model identifier to use.
            response: Previous async context stream response to extend.
            content: Additional user content to append.
            **params: Additional parameters to configure output (e.g. temperature). See `llm.Params`.

        Returns:
            A new `llm.AsyncContextStreamResponse` object for asynchronously streaming the extended conversation.

        Note:
            Uses the previous response's tools and output format. This base method wraps
            around calling `client.context_stream_async()` with a messages array derived from the response
            messages. However, clients may override this with first-class resume logic.
        """
        messages = response.messages + [user(content)]
        return await self.context_stream_async(
            ctx=ctx,
            model_id=model_id,
            messages=messages,
            tools=response.toolkit,
            format=response.format,
            **params,
        )
