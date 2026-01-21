"""Mirascope-specific instrumentation for Response.resume methods."""

from __future__ import annotations

from functools import wraps
from typing import TYPE_CHECKING, Any, cast, overload

from .....llm import (
    AsyncContextResponse,
    AsyncContextStreamResponse,
    AsyncResponse,
    AsyncStreamResponse,
    Context,
    ContextResponse,
    ContextStreamResponse,
    DepsT,
    FormattableT,
    Response,
    StreamResponse,
    UserContent,
)
from ...spans import Span as MirascopeSpan
from .serialize import attach_mirascope_response, attach_mirascope_response_async

if TYPE_CHECKING:
    pass


# =============================================================================
# Original method references and wrapped state flags
# =============================================================================

_ORIGINAL_RESPONSE_RESUME = Response.resume
_RESPONSE_RESUME_WRAPPED = False
_ORIGINAL_ASYNC_RESPONSE_RESUME = AsyncResponse.resume
_ASYNC_RESPONSE_RESUME_WRAPPED = False
_ORIGINAL_CONTEXT_RESPONSE_RESUME = ContextResponse.resume
_CONTEXT_RESPONSE_RESUME_WRAPPED = False
_ORIGINAL_ASYNC_CONTEXT_RESPONSE_RESUME = AsyncContextResponse.resume
_ASYNC_CONTEXT_RESPONSE_RESUME_WRAPPED = False
_ORIGINAL_STREAM_RESPONSE_RESUME = StreamResponse.resume
_STREAM_RESPONSE_RESUME_WRAPPED = False
_ORIGINAL_ASYNC_STREAM_RESPONSE_RESUME = AsyncStreamResponse.resume
_ASYNC_STREAM_RESPONSE_RESUME_WRAPPED = False
_ORIGINAL_CONTEXT_STREAM_RESPONSE_RESUME = ContextStreamResponse.resume
_CONTEXT_STREAM_RESPONSE_RESUME_WRAPPED = False
_ORIGINAL_ASYNC_CONTEXT_STREAM_RESPONSE_RESUME = AsyncContextStreamResponse.resume
_ASYNC_CONTEXT_STREAM_RESPONSE_RESUME_WRAPPED = False


# =============================================================================
# Response.resume instrumentation
# =============================================================================


@overload
def _instrumented_response_resume(self: Response, content: UserContent) -> Response: ...


@overload
def _instrumented_response_resume(
    self: Response[FormattableT], content: UserContent
) -> Response[FormattableT]: ...


@wraps(_ORIGINAL_RESPONSE_RESUME)
def _instrumented_response_resume(
    self: Response | Response[FormattableT], content: UserContent
) -> Response | Response[FormattableT]:
    """Returns a Mirascope-traced result of `Response.resume`."""
    with MirascopeSpan(f"Response.resume {self.model_id}") as span:
        span.set(
            **{
                "mirascope.type": "response_resume",
                "mirascope.response.model_id": self.model_id,
                "mirascope.response.provider_id": self.provider_id,
            }
        )
        result = cast(
            "Response | Response[FormattableT]",
            _ORIGINAL_RESPONSE_RESUME(cast(Any, self), content),
        )
        attach_mirascope_response(span, result)
        return result


def wrap_response_resume() -> None:
    """Returns None. Replaces `Response.resume` with the instrumented wrapper."""
    global _RESPONSE_RESUME_WRAPPED
    if _RESPONSE_RESUME_WRAPPED:
        return
    Response.resume = _instrumented_response_resume
    _RESPONSE_RESUME_WRAPPED = True


def unwrap_response_resume() -> None:
    """Returns None. Restores the original `Response.resume` implementation."""
    global _RESPONSE_RESUME_WRAPPED
    if not _RESPONSE_RESUME_WRAPPED:
        return
    Response.resume = _ORIGINAL_RESPONSE_RESUME
    _RESPONSE_RESUME_WRAPPED = False


# =============================================================================
# AsyncResponse.resume instrumentation
# =============================================================================


@overload
async def _instrumented_async_response_resume(
    self: AsyncResponse, content: UserContent
) -> AsyncResponse: ...


@overload
async def _instrumented_async_response_resume(
    self: AsyncResponse[FormattableT], content: UserContent
) -> AsyncResponse[FormattableT]: ...


@wraps(_ORIGINAL_ASYNC_RESPONSE_RESUME)
async def _instrumented_async_response_resume(
    self: AsyncResponse | AsyncResponse[FormattableT], content: UserContent
) -> AsyncResponse | AsyncResponse[FormattableT]:
    """Returns a Mirascope-traced result of `AsyncResponse.resume`."""
    with MirascopeSpan(f"AsyncResponse.resume {self.model_id}") as span:
        span.set(
            **{
                "mirascope.type": "response_resume",
                "mirascope.response.model_id": self.model_id,
                "mirascope.response.provider_id": self.provider_id,
            }
        )
        result = cast(
            "AsyncResponse | AsyncResponse[FormattableT]",
            await _ORIGINAL_ASYNC_RESPONSE_RESUME(cast(Any, self), content),
        )
        await attach_mirascope_response_async(span, result)
        return result


def wrap_async_response_resume() -> None:
    """Returns None. Replaces `AsyncResponse.resume` with the instrumented wrapper."""
    global _ASYNC_RESPONSE_RESUME_WRAPPED
    if _ASYNC_RESPONSE_RESUME_WRAPPED:
        return
    AsyncResponse.resume = _instrumented_async_response_resume
    _ASYNC_RESPONSE_RESUME_WRAPPED = True


def unwrap_async_response_resume() -> None:
    """Returns None. Restores the original `AsyncResponse.resume` implementation."""
    global _ASYNC_RESPONSE_RESUME_WRAPPED
    if not _ASYNC_RESPONSE_RESUME_WRAPPED:
        return
    AsyncResponse.resume = _ORIGINAL_ASYNC_RESPONSE_RESUME
    _ASYNC_RESPONSE_RESUME_WRAPPED = False


# =============================================================================
# ContextResponse.resume instrumentation
# =============================================================================


@overload
def _instrumented_context_response_resume(
    self: ContextResponse[DepsT], ctx: Context[DepsT], content: UserContent
) -> ContextResponse[DepsT]: ...


@overload
def _instrumented_context_response_resume(
    self: ContextResponse[DepsT, FormattableT],
    ctx: Context[DepsT],
    content: UserContent,
) -> ContextResponse[DepsT, FormattableT]: ...


@wraps(_ORIGINAL_CONTEXT_RESPONSE_RESUME)
def _instrumented_context_response_resume(
    self: ContextResponse[DepsT] | ContextResponse[DepsT, FormattableT],
    ctx: Context[DepsT],
    content: UserContent,
) -> ContextResponse[DepsT] | ContextResponse[DepsT, FormattableT]:
    """Returns a Mirascope-traced result of `ContextResponse.resume`."""
    with MirascopeSpan(f"ContextResponse.resume {self.model_id}") as span:
        span.set(
            **{
                "mirascope.type": "response_resume",
                "mirascope.response.model_id": self.model_id,
                "mirascope.response.provider_id": self.provider_id,
            }
        )
        result = cast(
            "ContextResponse[DepsT] | ContextResponse[DepsT, FormattableT]",
            _ORIGINAL_CONTEXT_RESPONSE_RESUME(cast(Any, self), ctx, content),
        )
        attach_mirascope_response(span, result)
        return result


def wrap_context_response_resume() -> None:
    """Returns None. Replaces `ContextResponse.resume` with the instrumented wrapper."""
    global _CONTEXT_RESPONSE_RESUME_WRAPPED
    if _CONTEXT_RESPONSE_RESUME_WRAPPED:
        return
    ContextResponse.resume = _instrumented_context_response_resume
    _CONTEXT_RESPONSE_RESUME_WRAPPED = True


def unwrap_context_response_resume() -> None:
    """Returns None. Restores the original `ContextResponse.resume` implementation."""
    global _CONTEXT_RESPONSE_RESUME_WRAPPED
    if not _CONTEXT_RESPONSE_RESUME_WRAPPED:
        return
    ContextResponse.resume = _ORIGINAL_CONTEXT_RESPONSE_RESUME
    _CONTEXT_RESPONSE_RESUME_WRAPPED = False


# =============================================================================
# AsyncContextResponse.resume instrumentation
# =============================================================================


@overload
async def _instrumented_async_context_response_resume(
    self: AsyncContextResponse[DepsT], ctx: Context[DepsT], content: UserContent
) -> AsyncContextResponse[DepsT]: ...


@overload
async def _instrumented_async_context_response_resume(
    self: AsyncContextResponse[DepsT, FormattableT],
    ctx: Context[DepsT],
    content: UserContent,
) -> AsyncContextResponse[DepsT, FormattableT]: ...


@wraps(_ORIGINAL_ASYNC_CONTEXT_RESPONSE_RESUME)
async def _instrumented_async_context_response_resume(
    self: AsyncContextResponse[DepsT] | AsyncContextResponse[DepsT, FormattableT],
    ctx: Context[DepsT],
    content: UserContent,
) -> AsyncContextResponse[DepsT] | AsyncContextResponse[DepsT, FormattableT]:
    """Returns a Mirascope-traced result of `AsyncContextResponse.resume`."""
    with MirascopeSpan(f"AsyncContextResponse.resume {self.model_id}") as span:
        span.set(
            **{
                "mirascope.type": "response_resume",
                "mirascope.response.model_id": self.model_id,
                "mirascope.response.provider_id": self.provider_id,
            }
        )
        result = cast(
            "AsyncContextResponse[DepsT] | AsyncContextResponse[DepsT, FormattableT]",
            await _ORIGINAL_ASYNC_CONTEXT_RESPONSE_RESUME(
                cast(Any, self), ctx, content
            ),
        )
        await attach_mirascope_response_async(span, result)
        return result


def wrap_async_context_response_resume() -> None:
    """Returns None. Replaces `AsyncContextResponse.resume` with the instrumented wrapper."""
    global _ASYNC_CONTEXT_RESPONSE_RESUME_WRAPPED
    if _ASYNC_CONTEXT_RESPONSE_RESUME_WRAPPED:
        return
    AsyncContextResponse.resume = _instrumented_async_context_response_resume
    _ASYNC_CONTEXT_RESPONSE_RESUME_WRAPPED = True


def unwrap_async_context_response_resume() -> None:
    """Returns None. Restores the original `AsyncContextResponse.resume` implementation."""
    global _ASYNC_CONTEXT_RESPONSE_RESUME_WRAPPED
    if not _ASYNC_CONTEXT_RESPONSE_RESUME_WRAPPED:
        return
    AsyncContextResponse.resume = _ORIGINAL_ASYNC_CONTEXT_RESPONSE_RESUME
    _ASYNC_CONTEXT_RESPONSE_RESUME_WRAPPED = False


# =============================================================================
# StreamResponse.resume instrumentation
# =============================================================================


@overload
def _instrumented_stream_response_resume(
    self: StreamResponse, content: UserContent
) -> StreamResponse: ...


@overload
def _instrumented_stream_response_resume(
    self: StreamResponse[FormattableT], content: UserContent
) -> StreamResponse[FormattableT]: ...


@wraps(_ORIGINAL_STREAM_RESPONSE_RESUME)
def _instrumented_stream_response_resume(
    self: StreamResponse | StreamResponse[FormattableT], content: UserContent
) -> StreamResponse | StreamResponse[FormattableT]:
    """Returns a Mirascope-traced result of `StreamResponse.resume`."""
    with MirascopeSpan(f"StreamResponse.resume {self.model_id}") as span:
        span.set(
            **{
                "mirascope.type": "response_resume",
                "mirascope.response.model_id": self.model_id,
                "mirascope.response.provider_id": self.provider_id,
            }
        )
        result = cast(
            "StreamResponse | StreamResponse[FormattableT]",
            _ORIGINAL_STREAM_RESPONSE_RESUME(cast(Any, self), content),
        )
        attach_mirascope_response(span, result)
        return result


def wrap_stream_response_resume() -> None:
    """Returns None. Replaces `StreamResponse.resume` with the instrumented wrapper."""
    global _STREAM_RESPONSE_RESUME_WRAPPED
    if _STREAM_RESPONSE_RESUME_WRAPPED:
        return
    StreamResponse.resume = _instrumented_stream_response_resume
    _STREAM_RESPONSE_RESUME_WRAPPED = True


def unwrap_stream_response_resume() -> None:
    """Returns None. Restores the original `StreamResponse.resume` implementation."""
    global _STREAM_RESPONSE_RESUME_WRAPPED
    if not _STREAM_RESPONSE_RESUME_WRAPPED:
        return
    StreamResponse.resume = _ORIGINAL_STREAM_RESPONSE_RESUME
    _STREAM_RESPONSE_RESUME_WRAPPED = False


# =============================================================================
# AsyncStreamResponse.resume instrumentation
# =============================================================================


@overload
async def _instrumented_async_stream_response_resume(
    self: AsyncStreamResponse, content: UserContent
) -> AsyncStreamResponse: ...


@overload
async def _instrumented_async_stream_response_resume(
    self: AsyncStreamResponse[FormattableT], content: UserContent
) -> AsyncStreamResponse[FormattableT]: ...


@wraps(_ORIGINAL_ASYNC_STREAM_RESPONSE_RESUME)
async def _instrumented_async_stream_response_resume(
    self: AsyncStreamResponse | AsyncStreamResponse[FormattableT], content: UserContent
) -> AsyncStreamResponse | AsyncStreamResponse[FormattableT]:
    """Returns a Mirascope-traced result of `AsyncStreamResponse.resume`."""
    with MirascopeSpan(f"AsyncStreamResponse.resume {self.model_id}") as span:
        span.set(
            **{
                "mirascope.type": "response_resume",
                "mirascope.response.model_id": self.model_id,
                "mirascope.response.provider_id": self.provider_id,
            }
        )
        result = cast(
            "AsyncStreamResponse | AsyncStreamResponse[FormattableT]",
            await _ORIGINAL_ASYNC_STREAM_RESPONSE_RESUME(cast(Any, self), content),
        )
        await attach_mirascope_response_async(span, result)
        return result


def wrap_async_stream_response_resume() -> None:
    """Returns None. Replaces `AsyncStreamResponse.resume` with the instrumented wrapper."""
    global _ASYNC_STREAM_RESPONSE_RESUME_WRAPPED
    if _ASYNC_STREAM_RESPONSE_RESUME_WRAPPED:
        return
    AsyncStreamResponse.resume = _instrumented_async_stream_response_resume
    _ASYNC_STREAM_RESPONSE_RESUME_WRAPPED = True


def unwrap_async_stream_response_resume() -> None:
    """Returns None. Restores the original `AsyncStreamResponse.resume` implementation."""
    global _ASYNC_STREAM_RESPONSE_RESUME_WRAPPED
    if not _ASYNC_STREAM_RESPONSE_RESUME_WRAPPED:
        return
    AsyncStreamResponse.resume = _ORIGINAL_ASYNC_STREAM_RESPONSE_RESUME
    _ASYNC_STREAM_RESPONSE_RESUME_WRAPPED = False


# =============================================================================
# ContextStreamResponse.resume instrumentation
# =============================================================================


@overload
def _instrumented_context_stream_response_resume(
    self: ContextStreamResponse[DepsT], ctx: Context[DepsT], content: UserContent
) -> ContextStreamResponse[DepsT]: ...


@overload
def _instrumented_context_stream_response_resume(
    self: ContextStreamResponse[DepsT, FormattableT],
    ctx: Context[DepsT],
    content: UserContent,
) -> ContextStreamResponse[DepsT, FormattableT]: ...


@wraps(_ORIGINAL_CONTEXT_STREAM_RESPONSE_RESUME)
def _instrumented_context_stream_response_resume(
    self: ContextStreamResponse[DepsT] | ContextStreamResponse[DepsT, FormattableT],
    ctx: Context[DepsT],
    content: UserContent,
) -> ContextStreamResponse[DepsT] | ContextStreamResponse[DepsT, FormattableT]:
    """Returns a Mirascope-traced result of `ContextStreamResponse.resume`."""
    with MirascopeSpan(f"ContextStreamResponse.resume {self.model_id}") as span:
        span.set(
            **{
                "mirascope.type": "response_resume",
                "mirascope.response.model_id": self.model_id,
                "mirascope.response.provider_id": self.provider_id,
            }
        )
        result = cast(
            "ContextStreamResponse[DepsT] | ContextStreamResponse[DepsT, FormattableT]",
            _ORIGINAL_CONTEXT_STREAM_RESPONSE_RESUME(cast(Any, self), ctx, content),
        )
        attach_mirascope_response(span, result)
        return result


def wrap_context_stream_response_resume() -> None:
    """Returns None. Replaces `ContextStreamResponse.resume` with the instrumented wrapper."""
    global _CONTEXT_STREAM_RESPONSE_RESUME_WRAPPED
    if _CONTEXT_STREAM_RESPONSE_RESUME_WRAPPED:
        return
    ContextStreamResponse.resume = _instrumented_context_stream_response_resume
    _CONTEXT_STREAM_RESPONSE_RESUME_WRAPPED = True


def unwrap_context_stream_response_resume() -> None:
    """Returns None. Restores the original `ContextStreamResponse.resume` implementation."""
    global _CONTEXT_STREAM_RESPONSE_RESUME_WRAPPED
    if not _CONTEXT_STREAM_RESPONSE_RESUME_WRAPPED:
        return
    ContextStreamResponse.resume = _ORIGINAL_CONTEXT_STREAM_RESPONSE_RESUME
    _CONTEXT_STREAM_RESPONSE_RESUME_WRAPPED = False


# =============================================================================
# AsyncContextStreamResponse.resume instrumentation
# =============================================================================


@overload
async def _instrumented_async_context_stream_response_resume(
    self: AsyncContextStreamResponse[DepsT],
    ctx: Context[DepsT],
    content: UserContent,
) -> AsyncContextStreamResponse[DepsT]: ...


@overload
async def _instrumented_async_context_stream_response_resume(
    self: AsyncContextStreamResponse[DepsT, FormattableT],
    ctx: Context[DepsT],
    content: UserContent,
) -> AsyncContextStreamResponse[DepsT, FormattableT]: ...


@wraps(_ORIGINAL_ASYNC_CONTEXT_STREAM_RESPONSE_RESUME)
async def _instrumented_async_context_stream_response_resume(
    self: AsyncContextStreamResponse[DepsT]
    | AsyncContextStreamResponse[DepsT, FormattableT],
    ctx: Context[DepsT],
    content: UserContent,
) -> (
    AsyncContextStreamResponse[DepsT] | AsyncContextStreamResponse[DepsT, FormattableT]
):
    """Returns a Mirascope-traced result of `AsyncContextStreamResponse.resume`."""
    with MirascopeSpan(f"AsyncContextStreamResponse.resume {self.model_id}") as span:
        span.set(
            **{
                "mirascope.type": "response_resume",
                "mirascope.response.model_id": self.model_id,
                "mirascope.response.provider_id": self.provider_id,
            }
        )
        result = cast(
            "AsyncContextStreamResponse[DepsT] | AsyncContextStreamResponse[DepsT, FormattableT]",
            await _ORIGINAL_ASYNC_CONTEXT_STREAM_RESPONSE_RESUME(
                cast(Any, self), ctx, content
            ),
        )
        await attach_mirascope_response_async(span, result)
        return result


def wrap_async_context_stream_response_resume() -> None:
    """Returns None. Replaces `AsyncContextStreamResponse.resume` with the instrumented wrapper."""
    global _ASYNC_CONTEXT_STREAM_RESPONSE_RESUME_WRAPPED
    if _ASYNC_CONTEXT_STREAM_RESPONSE_RESUME_WRAPPED:
        return
    AsyncContextStreamResponse.resume = (
        _instrumented_async_context_stream_response_resume
    )
    _ASYNC_CONTEXT_STREAM_RESPONSE_RESUME_WRAPPED = True


def unwrap_async_context_stream_response_resume() -> None:
    """Returns None. Restores the original `AsyncContextStreamResponse.resume` implementation."""
    global _ASYNC_CONTEXT_STREAM_RESPONSE_RESUME_WRAPPED
    if not _ASYNC_CONTEXT_STREAM_RESPONSE_RESUME_WRAPPED:
        return
    AsyncContextStreamResponse.resume = _ORIGINAL_ASYNC_CONTEXT_STREAM_RESPONSE_RESUME
    _ASYNC_CONTEXT_STREAM_RESPONSE_RESUME_WRAPPED = False
