"""Base abstract interface for provider clients."""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Sequence
from typing import TYPE_CHECKING, Any, ClassVar, Generic, TypeAlias, overload
from typing_extensions import TypeVar, Unpack

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

if TYPE_CHECKING:
    from ..provider_id import ProviderId

ProviderClientT = TypeVar("ProviderClientT")

Provider: TypeAlias = "BaseProvider[Any]"
"""Type alias for `BaseProvider` with any client type."""


class BaseProvider(Generic[ProviderClientT], ABC):
    """Base abstract provider for LLM interactions.

    This class defines explicit methods for each type of call, eliminating
    the need for complex overloads in provider implementations.
    """

    id: ClassVar[ProviderId]
    """Provider identifier (e.g., "anthropic", "openai")."""

    default_scope: ClassVar[str | list[str]]
    """Default scope(s) for this provider when explicitly registered.

    Can be a single scope string or a list of scopes. For example:
    - "anthropic/" - Single scope
    - ["anthropic/", "openai/"] - Multiple scopes (e.g., for AWS Bedrock)
    """

    client: ProviderClientT

    @overload
    def call(
        self,
        *,
        model_id: str,
        messages: Sequence[Message],
        tools: Sequence[Tool] | Toolkit | None = None,
        format: None = None,
        **params: Unpack[Params],
    ) -> Response:
        """Generate an `llm.Response` without a response format."""
        ...

    @overload
    def call(
        self,
        *,
        model_id: str,
        messages: Sequence[Message],
        tools: Sequence[Tool] | Toolkit | None = None,
        format: type[FormattableT] | Format[FormattableT],
        **params: Unpack[Params],
    ) -> Response[FormattableT]:
        """Generate an `llm.Response` with a response format."""
        ...

    @overload
    def call(
        self,
        *,
        model_id: str,
        messages: Sequence[Message],
        tools: Sequence[Tool] | Toolkit | None = None,
        format: type[FormattableT] | Format[FormattableT] | None,
        **params: Unpack[Params],
    ) -> Response | Response[FormattableT]:
        """Generate an `llm.Response` with an optional response format."""
        ...

    def call(
        self,
        *,
        model_id: str,
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
        return self._call(
            model_id=model_id,
            messages=messages,
            tools=tools,
            format=format,
            **params,
        )

    @abstractmethod
    def _call(
        self,
        *,
        model_id: str,
        messages: Sequence[Message],
        tools: Sequence[Tool] | Toolkit | None = None,
        format: type[FormattableT] | Format[FormattableT] | None = None,
        **params: Unpack[Params],
    ) -> Response | Response[FormattableT]:
        """Implementation for call(). Subclasses override this method."""
        ...

    @overload
    def context_call(
        self,
        *,
        ctx: Context[DepsT],
        model_id: str,
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
    def context_call(
        self,
        *,
        ctx: Context[DepsT],
        model_id: str,
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
    def context_call(
        self,
        *,
        ctx: Context[DepsT],
        model_id: str,
        messages: Sequence[Message],
        tools: Sequence[Tool | ContextTool[DepsT]]
        | ContextToolkit[DepsT]
        | None = None,
        format: type[FormattableT] | Format[FormattableT] | None,
        **params: Unpack[Params],
    ) -> ContextResponse[DepsT, None] | ContextResponse[DepsT, FormattableT]:
        """Generate an `llm.ContextResponse` with an optional response format."""
        ...

    def context_call(
        self,
        *,
        ctx: Context[DepsT],
        model_id: str,
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
        return self._context_call(
            ctx=ctx,
            model_id=model_id,
            messages=messages,
            tools=tools,
            format=format,
            **params,
        )

    @abstractmethod
    def _context_call(
        self,
        *,
        ctx: Context[DepsT],
        model_id: str,
        messages: Sequence[Message],
        tools: Sequence[Tool | ContextTool[DepsT]]
        | ContextToolkit[DepsT]
        | None = None,
        format: type[FormattableT] | Format[FormattableT] | None = None,
        **params: Unpack[Params],
    ) -> ContextResponse[DepsT, None] | ContextResponse[DepsT, FormattableT]:
        """Implementation for context_call(). Subclasses override this method."""
        ...

    @overload
    async def call_async(
        self,
        *,
        model_id: str,
        messages: Sequence[Message],
        tools: Sequence[AsyncTool] | AsyncToolkit | None = None,
        format: None = None,
        **params: Unpack[Params],
    ) -> AsyncResponse:
        """Generate an `llm.AsyncResponse` without a response format."""
        ...

    @overload
    async def call_async(
        self,
        *,
        model_id: str,
        messages: Sequence[Message],
        tools: Sequence[AsyncTool] | AsyncToolkit | None = None,
        format: type[FormattableT] | Format[FormattableT],
        **params: Unpack[Params],
    ) -> AsyncResponse[FormattableT]:
        """Generate an `llm.AsyncResponse` with a response format."""
        ...

    @overload
    async def call_async(
        self,
        *,
        model_id: str,
        messages: Sequence[Message],
        tools: Sequence[AsyncTool] | AsyncToolkit | None = None,
        format: type[FormattableT] | Format[FormattableT] | None,
        **params: Unpack[Params],
    ) -> AsyncResponse | AsyncResponse[FormattableT]:
        """Generate an `llm.AsyncResponse` with an optional response format."""
        ...

    async def call_async(
        self,
        *,
        model_id: str,
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
        return await self._call_async(
            model_id=model_id,
            messages=messages,
            tools=tools,
            format=format,
            **params,
        )

    @abstractmethod
    async def _call_async(
        self,
        *,
        model_id: str,
        messages: Sequence[Message],
        tools: Sequence[AsyncTool] | AsyncToolkit | None = None,
        format: type[FormattableT] | Format[FormattableT] | None = None,
        **params: Unpack[Params],
    ) -> AsyncResponse | AsyncResponse[FormattableT]:
        """Implementation for call_async(). Subclasses override this method."""
        ...

    @overload
    async def context_call_async(
        self,
        *,
        ctx: Context[DepsT],
        model_id: str,
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
    async def context_call_async(
        self,
        *,
        ctx: Context[DepsT],
        model_id: str,
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
    async def context_call_async(
        self,
        *,
        ctx: Context[DepsT],
        model_id: str,
        messages: Sequence[Message],
        tools: Sequence[AsyncTool | AsyncContextTool[DepsT]]
        | AsyncContextToolkit[DepsT]
        | None = None,
        format: type[FormattableT] | Format[FormattableT] | None,
        **params: Unpack[Params],
    ) -> AsyncContextResponse[DepsT, None] | AsyncContextResponse[DepsT, FormattableT]:
        """Generate an `llm.AsyncContextResponse` with an optional response format."""
        ...

    async def context_call_async(
        self,
        *,
        ctx: Context[DepsT],
        model_id: str,
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
        return await self._context_call_async(
            ctx=ctx,
            model_id=model_id,
            messages=messages,
            tools=tools,
            format=format,
            **params,
        )

    @abstractmethod
    async def _context_call_async(
        self,
        *,
        ctx: Context[DepsT],
        model_id: str,
        messages: Sequence[Message],
        tools: Sequence[AsyncTool | AsyncContextTool[DepsT]]
        | AsyncContextToolkit[DepsT]
        | None = None,
        format: type[FormattableT] | Format[FormattableT] | None = None,
        **params: Unpack[Params],
    ) -> AsyncContextResponse[DepsT, None] | AsyncContextResponse[DepsT, FormattableT]:
        """Implementation for context_call_async(). Subclasses override this method."""
        ...

    @overload
    def stream(
        self,
        *,
        model_id: str,
        messages: Sequence[Message],
        tools: Sequence[Tool] | Toolkit | None = None,
        format: None = None,
        **params: Unpack[Params],
    ) -> StreamResponse:
        """Stream an `llm.StreamResponse` without a response format."""
        ...

    @overload
    def stream(
        self,
        *,
        model_id: str,
        messages: Sequence[Message],
        tools: Sequence[Tool] | Toolkit | None = None,
        format: type[FormattableT] | Format[FormattableT],
        **params: Unpack[Params],
    ) -> StreamResponse[FormattableT]:
        """Stream an `llm.StreamResponse` with a response format."""
        ...

    @overload
    def stream(
        self,
        *,
        model_id: str,
        messages: Sequence[Message],
        tools: Sequence[Tool] | Toolkit | None = None,
        format: type[FormattableT] | Format[FormattableT] | None,
        **params: Unpack[Params],
    ) -> StreamResponse | StreamResponse[FormattableT]:
        """Stream an `llm.StreamResponse` with an optional response format."""
        ...

    def stream(
        self,
        *,
        model_id: str,
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
        return self._stream(
            model_id=model_id,
            messages=messages,
            tools=tools,
            format=format,
            **params,
        )

    @abstractmethod
    def _stream(
        self,
        *,
        model_id: str,
        messages: Sequence[Message],
        tools: Sequence[Tool] | Toolkit | None = None,
        format: type[FormattableT] | Format[FormattableT] | None = None,
        **params: Unpack[Params],
    ) -> StreamResponse | StreamResponse[FormattableT]:
        """Implementation for stream(). Subclasses override this method."""
        ...

    @overload
    def context_stream(
        self,
        *,
        ctx: Context[DepsT],
        model_id: str,
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
    def context_stream(
        self,
        *,
        ctx: Context[DepsT],
        model_id: str,
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
    def context_stream(
        self,
        *,
        ctx: Context[DepsT],
        model_id: str,
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

    def context_stream(
        self,
        *,
        ctx: Context[DepsT],
        model_id: str,
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
        return self._context_stream(
            ctx=ctx,
            model_id=model_id,
            messages=messages,
            tools=tools,
            format=format,
            **params,
        )

    @abstractmethod
    def _context_stream(
        self,
        *,
        ctx: Context[DepsT],
        model_id: str,
        messages: Sequence[Message],
        tools: Sequence[Tool | ContextTool[DepsT]]
        | ContextToolkit[DepsT]
        | None = None,
        format: type[FormattableT] | Format[FormattableT] | None = None,
        **params: Unpack[Params],
    ) -> (
        ContextStreamResponse[DepsT, None] | ContextStreamResponse[DepsT, FormattableT]
    ):
        """Implementation for context_stream(). Subclasses override this method."""
        ...

    @overload
    async def stream_async(
        self,
        *,
        model_id: str,
        messages: Sequence[Message],
        tools: Sequence[AsyncTool] | AsyncToolkit | None = None,
        format: None = None,
        **params: Unpack[Params],
    ) -> AsyncStreamResponse:
        """Stream an `llm.AsyncStreamResponse` without a response format."""
        ...

    @overload
    async def stream_async(
        self,
        *,
        model_id: str,
        messages: Sequence[Message],
        tools: Sequence[AsyncTool] | AsyncToolkit | None = None,
        format: type[FormattableT] | Format[FormattableT],
        **params: Unpack[Params],
    ) -> AsyncStreamResponse[FormattableT]:
        """Stream an `llm.AsyncStreamResponse` with a response format."""
        ...

    @overload
    async def stream_async(
        self,
        *,
        model_id: str,
        messages: Sequence[Message],
        tools: Sequence[AsyncTool] | AsyncToolkit | None = None,
        format: type[FormattableT] | Format[FormattableT] | None,
        **params: Unpack[Params],
    ) -> AsyncStreamResponse | AsyncStreamResponse[FormattableT]:
        """Stream an `llm.AsyncStreamResponse` with an optional response format."""
        ...

    async def stream_async(
        self,
        *,
        model_id: str,
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
        return await self._stream_async(
            model_id=model_id,
            messages=messages,
            tools=tools,
            format=format,
            **params,
        )

    @abstractmethod
    async def _stream_async(
        self,
        *,
        model_id: str,
        messages: Sequence[Message],
        tools: Sequence[AsyncTool] | AsyncToolkit | None = None,
        format: type[FormattableT] | Format[FormattableT] | None = None,
        **params: Unpack[Params],
    ) -> AsyncStreamResponse | AsyncStreamResponse[FormattableT]:
        """Implementation for stream_async(). Subclasses override this method."""
        ...

    @overload
    async def context_stream_async(
        self,
        *,
        ctx: Context[DepsT],
        model_id: str,
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
    async def context_stream_async(
        self,
        *,
        ctx: Context[DepsT],
        model_id: str,
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
    async def context_stream_async(
        self,
        *,
        ctx: Context[DepsT],
        model_id: str,
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

    async def context_stream_async(
        self,
        *,
        ctx: Context[DepsT],
        model_id: str,
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
        return await self._context_stream_async(
            ctx=ctx,
            model_id=model_id,
            messages=messages,
            tools=tools,
            format=format,
            **params,
        )

    @abstractmethod
    async def _context_stream_async(
        self,
        *,
        ctx: Context[DepsT],
        model_id: str,
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
        """Implementation for context_stream_async(). Subclasses override this method."""
        ...

    @overload
    def resume(
        self,
        *,
        model_id: str,
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
        model_id: str,
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
        model_id: str,
        response: Response | Response[FormattableT],
        content: UserContent,
        **params: Unpack[Params],
    ) -> Response | Response[FormattableT]:
        """Resume an `llm.Response` with an optional response format."""
        ...

    def resume(
        self,
        *,
        model_id: str,
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
        model_id: str,
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
        model_id: str,
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
        model_id: str,
        response: AsyncResponse | AsyncResponse[FormattableT],
        content: UserContent,
        **params: Unpack[Params],
    ) -> AsyncResponse | AsyncResponse[FormattableT]:
        """Resume an `llm.AsyncResponse` with an optional response format."""
        ...

    async def resume_async(
        self,
        *,
        model_id: str,
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
        model_id: str,
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
        model_id: str,
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
        model_id: str,
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
        model_id: str,
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
        model_id: str,
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
        model_id: str,
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
        model_id: str,
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
        model_id: str,
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
        model_id: str,
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
        model_id: str,
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
        model_id: str,
        response: StreamResponse | StreamResponse[FormattableT],
        content: UserContent,
        **params: Unpack[Params],
    ) -> StreamResponse | StreamResponse[FormattableT]:
        """Resume an `llm.StreamResponse` with an optional response format."""
        ...

    def resume_stream(
        self,
        *,
        model_id: str,
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
        model_id: str,
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
        model_id: str,
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
        model_id: str,
        response: AsyncStreamResponse | AsyncStreamResponse[FormattableT],
        content: UserContent,
        **params: Unpack[Params],
    ) -> AsyncStreamResponse | AsyncStreamResponse[FormattableT]:
        """Resume an `llm.AsyncStreamResponse` with an optional response format."""
        ...

    async def resume_stream_async(
        self,
        *,
        model_id: str,
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
        model_id: str,
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
        model_id: str,
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
        model_id: str,
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
        model_id: str,
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
        model_id: str,
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
        model_id: str,
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
        model_id: str,
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
        model_id: str,
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
