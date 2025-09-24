"""Base abstract interface for provider clients."""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Sequence
from contextvars import ContextVar, Token
from types import TracebackType
from typing import Generic, overload
from typing_extensions import Self, TypeVar

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
from ...tools import AsyncContextTool, AsyncTool, ContextTool, Tool
from .params import ParamsT

ModelIdT = TypeVar("ModelIdT", bound=str)
ProviderClientT = TypeVar("ProviderClientT")

ClientT = TypeVar("ClientT", bound="BaseClient")
"""Type variable for an LLM client."""


class BaseClient(Generic[ParamsT, ModelIdT, ProviderClientT], ABC):
    """Base abstract client for provider-specific implementations.

    This class defines explicit methods for each type of call, eliminating
    the need for complex overloads in provider implementations.
    """

    client: ProviderClientT
    _token: Token | None = None

    @property
    @abstractmethod
    def _context_var(self) -> ContextVar:
        """The ContextVar for this client type."""
        ...

    def __enter__(self) -> Self:
        """Sets the client context and stores the token."""
        self._token = self._context_var.set(self)
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
        tools: Sequence[Tool] | None = None,
        format: None = None,
        params: ParamsT | None = None,
    ) -> Response: ...

    @overload
    @abstractmethod
    def call(
        self,
        *,
        model_id: ModelIdT,
        messages: Sequence[Message],
        tools: Sequence[Tool] | None = None,
        format: type[FormattableT] | Format[FormattableT],
        params: ParamsT | None = None,
    ) -> Response[FormattableT]: ...

    @overload
    @abstractmethod
    def call(
        self,
        *,
        model_id: ModelIdT,
        messages: Sequence[Message],
        tools: Sequence[Tool] | None = None,
        format: type[FormattableT] | Format[FormattableT] | None,
        params: ParamsT | None = None,
    ) -> Response | Response[FormattableT]: ...

    @abstractmethod
    def call(
        self,
        *,
        model_id: ModelIdT,
        messages: Sequence[Message],
        tools: Sequence[Tool] | None = None,
        format: type[FormattableT] | Format[FormattableT] | None = None,
        params: ParamsT | None = None,
    ) -> Response | Response[FormattableT]:
        """Generate a response."""
        ...

    @overload
    @abstractmethod
    def context_call(
        self,
        *,
        ctx: Context[DepsT],
        model_id: ModelIdT,
        messages: Sequence[Message],
        tools: Sequence[Tool | ContextTool[DepsT]] | None = None,
        format: None = None,
        params: ParamsT | None = None,
    ) -> ContextResponse[DepsT, None]: ...

    @overload
    @abstractmethod
    def context_call(
        self,
        *,
        ctx: Context[DepsT],
        model_id: ModelIdT,
        messages: Sequence[Message],
        tools: Sequence[Tool | ContextTool[DepsT]] | None = None,
        format: type[FormattableT] | Format[FormattableT],
        params: ParamsT | None = None,
    ) -> ContextResponse[DepsT, FormattableT]: ...

    @overload
    @abstractmethod
    def context_call(
        self,
        *,
        ctx: Context[DepsT],
        model_id: ModelIdT,
        messages: Sequence[Message],
        tools: Sequence[Tool | ContextTool[DepsT]] | None = None,
        format: type[FormattableT] | Format[FormattableT] | None,
        params: ParamsT | None = None,
    ) -> ContextResponse[DepsT, None] | ContextResponse[DepsT, FormattableT]: ...

    @abstractmethod
    def context_call(
        self,
        *,
        ctx: Context[DepsT],
        model_id: ModelIdT,
        messages: Sequence[Message],
        tools: Sequence[Tool | ContextTool[DepsT]] | None = None,
        format: type[FormattableT] | Format[FormattableT] | None = None,
        params: ParamsT | None = None,
    ) -> ContextResponse[DepsT, None] | ContextResponse[DepsT, FormattableT]:
        """Generate a context response."""
        ...

    @overload
    @abstractmethod
    async def call_async(
        self,
        *,
        model_id: ModelIdT,
        messages: Sequence[Message],
        tools: Sequence[AsyncTool] | None = None,
        format: None = None,
        params: ParamsT | None = None,
    ) -> AsyncResponse: ...

    @overload
    @abstractmethod
    async def call_async(
        self,
        *,
        model_id: ModelIdT,
        messages: Sequence[Message],
        tools: Sequence[AsyncTool] | None = None,
        format: type[FormattableT] | Format[FormattableT],
        params: ParamsT | None = None,
    ) -> AsyncResponse[FormattableT]: ...

    @overload
    @abstractmethod
    async def call_async(
        self,
        *,
        model_id: ModelIdT,
        messages: Sequence[Message],
        tools: Sequence[AsyncTool] | None = None,
        format: type[FormattableT] | Format[FormattableT] | None,
        params: ParamsT | None = None,
    ) -> AsyncResponse | AsyncResponse[FormattableT]: ...

    @abstractmethod
    async def call_async(
        self,
        *,
        model_id: ModelIdT,
        messages: Sequence[Message],
        tools: Sequence[AsyncTool] | None = None,
        format: type[FormattableT] | Format[FormattableT] | None = None,
        params: ParamsT | None = None,
    ) -> AsyncResponse | AsyncResponse[FormattableT]:
        """Generate a response asynchronously."""
        ...

    @overload
    @abstractmethod
    async def context_call_async(
        self,
        *,
        ctx: Context[DepsT],
        model_id: ModelIdT,
        messages: Sequence[Message],
        tools: Sequence[AsyncTool | AsyncContextTool[DepsT]] | None = None,
        format: None = None,
        params: ParamsT | None = None,
    ) -> AsyncContextResponse[DepsT, None]: ...

    @overload
    @abstractmethod
    async def context_call_async(
        self,
        *,
        ctx: Context[DepsT],
        model_id: ModelIdT,
        messages: Sequence[Message],
        tools: Sequence[AsyncTool | AsyncContextTool[DepsT]] | None = None,
        format: type[FormattableT] | Format[FormattableT],
        params: ParamsT | None = None,
    ) -> AsyncContextResponse[DepsT, FormattableT]: ...

    @overload
    @abstractmethod
    async def context_call_async(
        self,
        *,
        ctx: Context[DepsT],
        model_id: ModelIdT,
        messages: Sequence[Message],
        tools: Sequence[AsyncTool | AsyncContextTool[DepsT]] | None = None,
        format: type[FormattableT] | Format[FormattableT] | None,
        params: ParamsT | None = None,
    ) -> (
        AsyncContextResponse[DepsT, None] | AsyncContextResponse[DepsT, FormattableT]
    ): ...

    @abstractmethod
    async def context_call_async(
        self,
        *,
        ctx: Context[DepsT],
        model_id: ModelIdT,
        messages: Sequence[Message],
        tools: Sequence[AsyncTool | AsyncContextTool[DepsT]] | None = None,
        format: type[FormattableT] | Format[FormattableT] | None = None,
        params: ParamsT | None = None,
    ) -> AsyncContextResponse[DepsT, None] | AsyncContextResponse[DepsT, FormattableT]:
        """Generate a context response asynchronously."""
        ...

    @overload
    @abstractmethod
    def stream(
        self,
        *,
        model_id: ModelIdT,
        messages: Sequence[Message],
        tools: Sequence[Tool] | None = None,
        format: None = None,
        params: ParamsT | None = None,
    ) -> StreamResponse: ...

    @overload
    @abstractmethod
    def stream(
        self,
        *,
        model_id: ModelIdT,
        messages: Sequence[Message],
        tools: Sequence[Tool] | None = None,
        format: type[FormattableT] | Format[FormattableT],
        params: ParamsT | None = None,
    ) -> StreamResponse[FormattableT]: ...

    @overload
    @abstractmethod
    def stream(
        self,
        *,
        model_id: ModelIdT,
        messages: Sequence[Message],
        tools: Sequence[Tool] | None = None,
        format: type[FormattableT] | Format[FormattableT] | None,
        params: ParamsT | None = None,
    ) -> StreamResponse | StreamResponse[FormattableT]: ...

    @abstractmethod
    def stream(
        self,
        *,
        model_id: ModelIdT,
        messages: Sequence[Message],
        tools: Sequence[Tool] | None = None,
        format: type[FormattableT] | Format[FormattableT] | None = None,
        params: ParamsT | None = None,
    ) -> StreamResponse | StreamResponse[FormattableT]:
        """Stream a response."""
        ...

    @overload
    @abstractmethod
    def context_stream(
        self,
        *,
        ctx: Context[DepsT],
        model_id: ModelIdT,
        messages: Sequence[Message],
        tools: Sequence[Tool | ContextTool[DepsT]] | None = None,
        format: None = None,
        params: ParamsT | None = None,
    ) -> ContextStreamResponse[DepsT, None]: ...

    @overload
    @abstractmethod
    def context_stream(
        self,
        *,
        ctx: Context[DepsT],
        model_id: ModelIdT,
        messages: Sequence[Message],
        tools: Sequence[Tool | ContextTool[DepsT]] | None = None,
        format: type[FormattableT] | Format[FormattableT],
        params: ParamsT | None = None,
    ) -> ContextStreamResponse[DepsT, FormattableT]: ...

    @overload
    @abstractmethod
    def context_stream(
        self,
        *,
        ctx: Context[DepsT],
        model_id: ModelIdT,
        messages: Sequence[Message],
        tools: Sequence[Tool | ContextTool[DepsT]] | None = None,
        format: type[FormattableT] | Format[FormattableT] | None,
        params: ParamsT | None = None,
    ) -> (
        ContextStreamResponse[DepsT, None] | ContextStreamResponse[DepsT, FormattableT]
    ): ...

    @abstractmethod
    def context_stream(
        self,
        *,
        ctx: Context[DepsT],
        model_id: ModelIdT,
        messages: Sequence[Message],
        tools: Sequence[Tool | ContextTool[DepsT]] | None = None,
        format: type[FormattableT] | Format[FormattableT] | None = None,
        params: ParamsT | None = None,
    ) -> (
        ContextStreamResponse[DepsT, None] | ContextStreamResponse[DepsT, FormattableT]
    ):
        """Stream a context response."""
        ...

    @overload
    @abstractmethod
    async def stream_async(
        self,
        *,
        model_id: ModelIdT,
        messages: Sequence[Message],
        tools: Sequence[AsyncTool] | None = None,
        format: None = None,
        params: ParamsT | None = None,
    ) -> AsyncStreamResponse: ...

    @overload
    @abstractmethod
    async def stream_async(
        self,
        *,
        model_id: ModelIdT,
        messages: Sequence[Message],
        tools: Sequence[AsyncTool] | None = None,
        format: type[FormattableT] | Format[FormattableT],
        params: ParamsT | None = None,
    ) -> AsyncStreamResponse[FormattableT]: ...

    @overload
    @abstractmethod
    async def stream_async(
        self,
        *,
        model_id: ModelIdT,
        messages: Sequence[Message],
        tools: Sequence[AsyncTool] | None = None,
        format: type[FormattableT] | Format[FormattableT] | None,
        params: ParamsT | None = None,
    ) -> AsyncStreamResponse | AsyncStreamResponse[FormattableT]: ...

    @abstractmethod
    async def stream_async(
        self,
        *,
        model_id: ModelIdT,
        messages: Sequence[Message],
        tools: Sequence[AsyncTool] | None = None,
        format: type[FormattableT] | Format[FormattableT] | None = None,
        params: ParamsT | None = None,
    ) -> AsyncStreamResponse | AsyncStreamResponse[FormattableT]:
        """Stream a response asynchronously."""
        ...

    @overload
    @abstractmethod
    async def context_stream_async(
        self,
        *,
        ctx: Context[DepsT],
        model_id: ModelIdT,
        messages: Sequence[Message],
        tools: Sequence[AsyncTool | AsyncContextTool[DepsT]] | None = None,
        format: None = None,
        params: ParamsT | None = None,
    ) -> AsyncContextStreamResponse[DepsT, None]: ...

    @overload
    @abstractmethod
    async def context_stream_async(
        self,
        *,
        ctx: Context[DepsT],
        model_id: ModelIdT,
        messages: Sequence[Message],
        tools: Sequence[AsyncTool | AsyncContextTool[DepsT]] | None = None,
        format: type[FormattableT] | Format[FormattableT],
        params: ParamsT | None = None,
    ) -> AsyncContextStreamResponse[DepsT, FormattableT]: ...

    @overload
    @abstractmethod
    async def context_stream_async(
        self,
        *,
        ctx: Context[DepsT],
        model_id: ModelIdT,
        messages: Sequence[Message],
        tools: Sequence[AsyncTool | AsyncContextTool[DepsT]] | None = None,
        format: type[FormattableT] | Format[FormattableT] | None,
        params: ParamsT | None = None,
    ) -> (
        AsyncContextStreamResponse[DepsT, None]
        | AsyncContextStreamResponse[DepsT, FormattableT]
    ): ...

    @abstractmethod
    async def context_stream_async(
        self,
        *,
        ctx: Context[DepsT],
        model_id: ModelIdT,
        messages: Sequence[Message],
        tools: Sequence[AsyncTool | AsyncContextTool[DepsT]] | None = None,
        format: type[FormattableT] | Format[FormattableT] | None = None,
        params: ParamsT | None = None,
    ) -> (
        AsyncContextStreamResponse[DepsT, None]
        | AsyncContextStreamResponse[DepsT, FormattableT]
    ):
        """Stream a context response asynchronously."""
        ...

    @overload
    def resume(
        self,
        *,
        model_id: ModelIdT,
        response: Response,
        content: UserContent,
        params: ParamsT | None = None,
    ) -> Response: ...

    @overload
    def resume(
        self,
        *,
        model_id: ModelIdT,
        response: Response[FormattableT],
        content: UserContent,
        params: ParamsT | None = None,
    ) -> Response[FormattableT]: ...

    @overload
    def resume(
        self,
        *,
        model_id: ModelIdT,
        response: Response | Response[FormattableT],
        content: UserContent,
        params: ParamsT | None = None,
    ) -> Response | Response[FormattableT]: ...

    def resume(
        self,
        *,
        model_id: ModelIdT,
        response: Response | Response[FormattableT],
        content: UserContent,
        params: ParamsT | None = None,
    ) -> Response | Response[FormattableT]:
        """Generate a new `Response` by extending another `Response`'s messages with additional user content.

        Uses the other response's tools and output format.
        This base method wraps around calling `client.call()` with a messages array
        derived from the response messages. However, clients may override this with
        first-class resume logic, if supported.
        """
        messages = response.messages + [user(content)]
        return self.call(
            model_id=model_id,
            messages=messages,
            tools=response.toolkit.tools,
            format=response.format,
            params=params,
        )

    @overload
    async def resume_async(
        self,
        *,
        model_id: ModelIdT,
        response: AsyncResponse,
        content: UserContent,
        params: ParamsT | None = None,
    ) -> AsyncResponse: ...

    @overload
    async def resume_async(
        self,
        *,
        model_id: ModelIdT,
        response: AsyncResponse[FormattableT],
        content: UserContent,
        params: ParamsT | None = None,
    ) -> AsyncResponse[FormattableT]: ...

    @overload
    async def resume_async(
        self,
        *,
        model_id: ModelIdT,
        response: AsyncResponse | AsyncResponse[FormattableT],
        content: UserContent,
        params: ParamsT | None = None,
    ) -> AsyncResponse | AsyncResponse[FormattableT]: ...

    async def resume_async(
        self,
        *,
        model_id: ModelIdT,
        response: AsyncResponse | AsyncResponse[FormattableT],
        content: UserContent,
        params: ParamsT | None = None,
    ) -> AsyncResponse | AsyncResponse[FormattableT]:
        """Generate a new `AsyncResponse` by extending another `AsyncResponse`'s messages with additional user content.

        Uses the other response's tools and output format.
        This base method wraps around calling `client.call_async()` with a messages array
        derived from the response messages. However, clients may override this with
        first-class resume logic, if supported.
        """
        messages = response.messages + [user(content)]
        return await self.call_async(
            model_id=model_id,
            messages=messages,
            tools=response.toolkit.tools,
            format=response.format,
            params=params,
        )

    @overload
    def context_resume(
        self,
        *,
        ctx: Context[DepsT],
        model_id: ModelIdT,
        response: ContextResponse[DepsT, None],
        content: UserContent,
        params: ParamsT | None = None,
    ) -> ContextResponse[DepsT, None]: ...

    @overload
    def context_resume(
        self,
        *,
        ctx: Context[DepsT],
        model_id: ModelIdT,
        response: ContextResponse[DepsT, FormattableT],
        content: UserContent,
        params: ParamsT | None = None,
    ) -> ContextResponse[DepsT, FormattableT]: ...

    @overload
    def context_resume(
        self,
        *,
        ctx: Context[DepsT],
        model_id: ModelIdT,
        response: ContextResponse[DepsT, None] | ContextResponse[DepsT, FormattableT],
        content: UserContent,
        params: ParamsT | None = None,
    ) -> ContextResponse[DepsT, None] | ContextResponse[DepsT, FormattableT]: ...

    def context_resume(
        self,
        *,
        ctx: Context[DepsT],
        model_id: ModelIdT,
        response: ContextResponse[DepsT, None] | ContextResponse[DepsT, FormattableT],
        content: UserContent,
        params: ParamsT | None = None,
    ) -> ContextResponse[DepsT, None] | ContextResponse[DepsT, FormattableT]:
        """Generate a new `ContextResponse` by extending another `ContextResponse`'s messages with additional user content.

        Uses the other response's tools and output format.
        This base method wraps around calling `client.context_call()` with a messages array
        derived from the response messages. However, clients may override this with
        first-class resume logic, if supported.
        """
        messages = response.messages + [user(content)]
        return self.context_call(
            ctx=ctx,
            model_id=model_id,
            messages=messages,
            tools=response.toolkit.tools,
            format=response.format,
            params=params,
        )

    @overload
    async def context_resume_async(
        self,
        *,
        ctx: Context[DepsT],
        model_id: ModelIdT,
        response: AsyncContextResponse[DepsT, None],
        content: UserContent,
        params: ParamsT | None = None,
    ) -> AsyncContextResponse[DepsT, None]: ...

    @overload
    async def context_resume_async(
        self,
        *,
        ctx: Context[DepsT],
        model_id: ModelIdT,
        response: AsyncContextResponse[DepsT, FormattableT],
        content: UserContent,
        params: ParamsT | None = None,
    ) -> AsyncContextResponse[DepsT, FormattableT]: ...

    @overload
    async def context_resume_async(
        self,
        *,
        ctx: Context[DepsT],
        model_id: ModelIdT,
        response: AsyncContextResponse[DepsT, None]
        | AsyncContextResponse[DepsT, FormattableT],
        content: UserContent,
        params: ParamsT | None = None,
    ) -> (
        AsyncContextResponse[DepsT, None] | AsyncContextResponse[DepsT, FormattableT]
    ): ...

    async def context_resume_async(
        self,
        *,
        ctx: Context[DepsT],
        model_id: ModelIdT,
        response: AsyncContextResponse[DepsT, None]
        | AsyncContextResponse[DepsT, FormattableT],
        content: UserContent,
        params: ParamsT | None = None,
    ) -> AsyncContextResponse[DepsT, None] | AsyncContextResponse[DepsT, FormattableT]:
        """Generate a new `AsyncContextResponse` by extending another `AsyncContextResponse`'s messages with additional user content.

        Uses the other response's tools and output format.
        This base method wraps around calling `client.context_call_async()` with a messages array
        derived from the response messages. However, clients may override this with
        first-class resume logic, if supported.
        """
        messages = response.messages + [user(content)]
        return await self.context_call_async(
            ctx=ctx,
            model_id=model_id,
            messages=messages,
            tools=response.toolkit.tools,
            format=response.format,
            params=params,
        )

    @overload
    def resume_stream(
        self,
        *,
        model_id: ModelIdT,
        response: StreamResponse,
        content: UserContent,
        params: ParamsT | None = None,
    ) -> StreamResponse: ...

    @overload
    def resume_stream(
        self,
        *,
        model_id: ModelIdT,
        response: StreamResponse[FormattableT],
        content: UserContent,
        params: ParamsT | None = None,
    ) -> StreamResponse[FormattableT]: ...

    @overload
    def resume_stream(
        self,
        *,
        model_id: ModelIdT,
        response: StreamResponse | StreamResponse[FormattableT],
        content: UserContent,
        params: ParamsT | None = None,
    ) -> StreamResponse | StreamResponse[FormattableT]: ...

    def resume_stream(
        self,
        *,
        model_id: ModelIdT,
        response: StreamResponse | StreamResponse[FormattableT],
        content: UserContent,
        params: ParamsT | None = None,
    ) -> StreamResponse | StreamResponse[FormattableT]:
        """Generate a new `StreamResponse` by extending another `StreamResponse`'s messages with additional user content.

        Uses the other response's tools and output format.
        This base method wraps around calling `client.call()` with a messages array
        derived from the response messages. However, clients may override this with
        first-class resume_stream logic, if supported.
        """
        messages = response.messages + [user(content)]
        return self.stream(
            model_id=model_id,
            messages=messages,
            tools=response.toolkit.tools,
            format=response.format,
            params=params,
        )

    @overload
    async def resume_stream_async(
        self,
        *,
        model_id: ModelIdT,
        response: AsyncStreamResponse,
        content: UserContent,
        params: ParamsT | None = None,
    ) -> AsyncStreamResponse: ...

    @overload
    async def resume_stream_async(
        self,
        *,
        model_id: ModelIdT,
        response: AsyncStreamResponse[FormattableT],
        content: UserContent,
        params: ParamsT | None = None,
    ) -> AsyncStreamResponse[FormattableT]: ...

    @overload
    async def resume_stream_async(
        self,
        *,
        model_id: ModelIdT,
        response: AsyncStreamResponse | AsyncStreamResponse[FormattableT],
        content: UserContent,
        params: ParamsT | None = None,
    ) -> AsyncStreamResponse | AsyncStreamResponse[FormattableT]: ...

    async def resume_stream_async(
        self,
        *,
        model_id: ModelIdT,
        response: AsyncStreamResponse | AsyncStreamResponse[FormattableT],
        content: UserContent,
        params: ParamsT | None = None,
    ) -> AsyncStreamResponse | AsyncStreamResponse[FormattableT]:
        """Generate a new `AsyncStreamResponse` by extending another `AsyncStreamResponse`'s messages with additional user content.

        Uses the other response's tools and output format.
        This base method wraps around calling `client.stream_async()` with a messages array
        derived from the response messages. However, clients may override this with
        first-class resume_stream logic, if supported.
        """
        messages = response.messages + [user(content)]
        return await self.stream_async(
            model_id=model_id,
            messages=messages,
            tools=response.toolkit.tools,
            format=response.format,
            params=params,
        )

    @overload
    def context_resume_stream(
        self,
        *,
        ctx: Context[DepsT],
        model_id: ModelIdT,
        response: ContextStreamResponse[DepsT, None],
        content: UserContent,
        params: ParamsT | None = None,
    ) -> ContextStreamResponse[DepsT, None]: ...

    @overload
    def context_resume_stream(
        self,
        *,
        ctx: Context[DepsT],
        model_id: ModelIdT,
        response: ContextStreamResponse[DepsT, FormattableT],
        content: UserContent,
        params: ParamsT | None = None,
    ) -> ContextStreamResponse[DepsT, FormattableT]: ...

    @overload
    def context_resume_stream(
        self,
        *,
        ctx: Context[DepsT],
        model_id: ModelIdT,
        response: ContextStreamResponse[DepsT, None]
        | ContextStreamResponse[DepsT, FormattableT],
        content: UserContent,
        params: ParamsT | None = None,
    ) -> (
        ContextStreamResponse[DepsT, None] | ContextStreamResponse[DepsT, FormattableT]
    ): ...

    def context_resume_stream(
        self,
        *,
        ctx: Context[DepsT],
        model_id: ModelIdT,
        response: ContextStreamResponse[DepsT, None]
        | ContextStreamResponse[DepsT, FormattableT],
        content: UserContent,
        params: ParamsT | None = None,
    ) -> (
        ContextStreamResponse[DepsT, None] | ContextStreamResponse[DepsT, FormattableT]
    ):
        """Generate a new `ContextStreamResponse` by extending another `ContextStreamResponse`'s messages with additional user content.

        Uses the other response's tools and output format.
        This base method wraps around calling `client.context_call()` with a messages array
        derived from the response messages. However, clients may override this with
        first-class resume_stream logic, if supported.
        """
        messages = response.messages + [user(content)]
        return self.context_stream(
            ctx=ctx,
            model_id=model_id,
            messages=messages,
            tools=response.toolkit.tools,
            format=response.format,
            params=params,
        )

    @overload
    async def context_resume_stream_async(
        self,
        *,
        ctx: Context[DepsT],
        model_id: ModelIdT,
        response: AsyncContextStreamResponse[DepsT, None],
        content: UserContent,
        params: ParamsT | None = None,
    ) -> AsyncContextStreamResponse[DepsT, None]: ...

    @overload
    async def context_resume_stream_async(
        self,
        *,
        ctx: Context[DepsT],
        model_id: ModelIdT,
        response: AsyncContextStreamResponse[DepsT, FormattableT],
        content: UserContent,
        params: ParamsT | None = None,
    ) -> AsyncContextStreamResponse[DepsT, FormattableT]: ...

    @overload
    async def context_resume_stream_async(
        self,
        *,
        ctx: Context[DepsT],
        model_id: ModelIdT,
        response: AsyncContextStreamResponse[DepsT, None]
        | AsyncContextStreamResponse[DepsT, FormattableT],
        content: UserContent,
        params: ParamsT | None = None,
    ) -> (
        AsyncContextStreamResponse[DepsT, None]
        | AsyncContextStreamResponse[DepsT, FormattableT]
    ): ...

    async def context_resume_stream_async(
        self,
        *,
        ctx: Context[DepsT],
        model_id: ModelIdT,
        response: AsyncContextStreamResponse[DepsT, None]
        | AsyncContextStreamResponse[DepsT, FormattableT],
        content: UserContent,
        params: ParamsT | None = None,
    ) -> (
        AsyncContextStreamResponse[DepsT, None]
        | AsyncContextStreamResponse[DepsT, FormattableT]
    ):
        """Generate a new `AsyncContextStreamResponse` by extending another `AsyncContextStreamResponse`'s messages with additional user content.

        Uses the other response's tools and output format.
        This base method wraps around calling `client.context_stream_async()` with a messages array
        derived from the response messages. However, clients may override this with
        first-class resume_stream logic, if supported.
        """
        messages = response.messages + [user(content)]
        return await self.context_stream_async(
            ctx=ctx,
            model_id=model_id,
            messages=messages,
            tools=response.toolkit.tools,
            format=response.format,
            params=params,
        )
