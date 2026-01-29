"""OpenTelemetry GenAI instrumentation for `mirascope.llm.Model` methods."""

from __future__ import annotations

import weakref
from collections.abc import AsyncIterator, Iterator, Sequence
from contextlib import AbstractContextManager
from functools import wraps
from types import TracebackType
from typing import (
    TYPE_CHECKING,
    Any,
    cast,
    overload,
)

from opentelemetry import trace as otel_trace

from .....llm import (
    AsyncContextResponse,
    AsyncContextStreamResponse,
    AsyncContextTools,
    AsyncResponse,
    AsyncStreamResponse,
    AsyncTools,
    Context,
    ContextResponse,
    ContextStreamResponse,
    ContextTools,
    DepsT,
    FormatSpec,
    FormattableT,
    Message,
    Model,
    Response,
    RootResponse,
    StreamResponse,
    StreamResponseChunk,
    Tools,
    UserContent,
)
from .....llm.messages import promote_to_messages, user
from .common import (
    FormatParam,
    SpanContext,
    attach_response,
    attach_response_async,
    record_dropped_params,
    start_model_span,
)

if TYPE_CHECKING:
    from opentelemetry.trace import Span


# =============================================================================
# Original method references and wrapped state flags
# =============================================================================

_ORIGINAL_MODEL_CALL = Model.call
_MODEL_CALL_WRAPPED = False
_ORIGINAL_MODEL_CALL_ASYNC = Model.call_async
_MODEL_CALL_ASYNC_WRAPPED = False
_ORIGINAL_MODEL_CONTEXT_CALL = Model.context_call
_MODEL_CONTEXT_CALL_WRAPPED = False
_ORIGINAL_MODEL_CONTEXT_CALL_ASYNC = Model.context_call_async
_MODEL_CONTEXT_CALL_ASYNC_WRAPPED = False
_ORIGINAL_MODEL_STREAM = Model.stream
_MODEL_STREAM_WRAPPED = False
_ORIGINAL_MODEL_STREAM_ASYNC = Model.stream_async
_MODEL_STREAM_ASYNC_WRAPPED = False
_ORIGINAL_MODEL_CONTEXT_STREAM = Model.context_stream
_MODEL_CONTEXT_STREAM_WRAPPED = False
_ORIGINAL_MODEL_CONTEXT_STREAM_ASYNC = Model.context_stream_async
_MODEL_CONTEXT_STREAM_ASYNC_WRAPPED = False

# Resume method originals and flags
_ORIGINAL_MODEL_RESUME = Model.resume
_MODEL_RESUME_WRAPPED = False
_ORIGINAL_MODEL_RESUME_ASYNC = Model.resume_async
_MODEL_RESUME_ASYNC_WRAPPED = False
_ORIGINAL_MODEL_CONTEXT_RESUME = Model.context_resume
_MODEL_CONTEXT_RESUME_WRAPPED = False
_ORIGINAL_MODEL_CONTEXT_RESUME_ASYNC = Model.context_resume_async
_MODEL_CONTEXT_RESUME_ASYNC_WRAPPED = False
_ORIGINAL_MODEL_RESUME_STREAM = Model.resume_stream
_MODEL_RESUME_STREAM_WRAPPED = False
_ORIGINAL_MODEL_RESUME_STREAM_ASYNC = Model.resume_stream_async
_MODEL_RESUME_STREAM_ASYNC_WRAPPED = False
_ORIGINAL_MODEL_CONTEXT_RESUME_STREAM = Model.context_resume_stream
_MODEL_CONTEXT_RESUME_STREAM_WRAPPED = False
_ORIGINAL_MODEL_CONTEXT_RESUME_STREAM_ASYNC = Model.context_resume_stream_async
_MODEL_CONTEXT_RESUME_STREAM_ASYNC_WRAPPED = False


# =============================================================================
# Model.call instrumentation
# =============================================================================


@overload
def _instrumented_model_call(
    self: Model,
    content: UserContent | Sequence[Message],
    *,
    tools: Tools | None = None,
    format: None = None,
) -> Response: ...


@overload
def _instrumented_model_call(
    self: Model,
    content: UserContent | Sequence[Message],
    *,
    tools: Tools | None = None,
    format: FormatSpec[FormattableT],
) -> Response[FormattableT]: ...


@overload
def _instrumented_model_call(
    self: Model,
    content: UserContent | Sequence[Message],
    *,
    tools: Tools | None = None,
    format: FormatSpec[FormattableT] | None = None,
) -> Response | Response[FormattableT]: ...


@wraps(_ORIGINAL_MODEL_CALL)
def _instrumented_model_call(
    self: Model,
    content: UserContent | Sequence[Message],
    *,
    tools: Tools | None = None,
    format: FormatParam = None,
) -> Response | Response[FormattableT]:
    """Returns a GenAI-instrumented result of `Model.call`."""
    messages = promote_to_messages(content)
    with start_model_span(
        self,
        messages=messages,
        tools=tools,
        format=format,
    ) as span_ctx:
        response = _ORIGINAL_MODEL_CALL(
            self,
            content,
            tools=tools,
            format=format,
        )
        if span_ctx.span is not None:
            attach_response(
                span_ctx.span,
                response,
                request_messages=messages,
            )
            record_dropped_params(span_ctx.span, span_ctx.dropped_params)
        return response


def wrap_model_call() -> None:
    """Returns None. Replaces `Model.call` with the instrumented wrapper."""
    global _MODEL_CALL_WRAPPED
    if _MODEL_CALL_WRAPPED:
        return
    Model.call = _instrumented_model_call
    _MODEL_CALL_WRAPPED = True


def unwrap_model_call() -> None:
    """Returns None. Restores the original `Model.call` implementation."""
    global _MODEL_CALL_WRAPPED
    if not _MODEL_CALL_WRAPPED:
        return
    Model.call = _ORIGINAL_MODEL_CALL
    _MODEL_CALL_WRAPPED = False


# =============================================================================
# Model.call_async instrumentation
# =============================================================================


@overload
async def _instrumented_model_call_async(
    self: Model,
    content: UserContent | Sequence[Message],
    *,
    tools: AsyncTools | None = None,
    format: None = None,
) -> AsyncResponse: ...


@overload
async def _instrumented_model_call_async(
    self: Model,
    content: UserContent | Sequence[Message],
    *,
    tools: AsyncTools | None = None,
    format: FormatSpec[FormattableT],
) -> AsyncResponse[FormattableT]: ...


@overload
async def _instrumented_model_call_async(
    self: Model,
    content: UserContent | Sequence[Message],
    *,
    tools: AsyncTools | None = None,
    format: FormatSpec[FormattableT] | None = None,
) -> AsyncResponse | AsyncResponse[FormattableT]: ...


@wraps(_ORIGINAL_MODEL_CALL_ASYNC)
async def _instrumented_model_call_async(
    self: Model,
    content: UserContent | Sequence[Message],
    *,
    tools: AsyncTools | None = None,
    format: FormatParam = None,
) -> AsyncResponse | AsyncResponse[FormattableT]:
    """Returns a GenAI-instrumented result of `Model.call_async`."""
    messages = promote_to_messages(content)
    with start_model_span(
        self,
        messages=messages,
        tools=tools,
        format=format,
        activate=True,
    ) as span_ctx:
        response = await _ORIGINAL_MODEL_CALL_ASYNC(
            self,
            content,
            tools=tools,
            format=format,
        )
        if span_ctx.span is not None:
            await attach_response_async(
                span_ctx.span,
                response,
                request_messages=messages,
            )
            record_dropped_params(span_ctx.span, span_ctx.dropped_params)
        return response


def wrap_model_call_async() -> None:
    """Returns None. Replaces `Model.call_async` with the instrumented wrapper."""
    global _MODEL_CALL_ASYNC_WRAPPED
    if _MODEL_CALL_ASYNC_WRAPPED:
        return
    Model.call_async = _instrumented_model_call_async
    _MODEL_CALL_ASYNC_WRAPPED = True


def unwrap_model_call_async() -> None:
    """Returns None. Restores the original `Model.call_async` implementation."""
    global _MODEL_CALL_ASYNC_WRAPPED
    if not _MODEL_CALL_ASYNC_WRAPPED:
        return
    Model.call_async = _ORIGINAL_MODEL_CALL_ASYNC
    _MODEL_CALL_ASYNC_WRAPPED = False


# =============================================================================
# Model.context_call instrumentation
# =============================================================================


@overload
def _instrumented_model_context_call(
    self: Model,
    content: UserContent | Sequence[Message],
    *,
    ctx: Context[DepsT],
    tools: ContextTools[DepsT] | None = None,
    format: None = None,
) -> ContextResponse[DepsT, None]: ...


@overload
def _instrumented_model_context_call(
    self: Model,
    content: UserContent | Sequence[Message],
    *,
    ctx: Context[DepsT],
    tools: ContextTools[DepsT] | None = None,
    format: FormatSpec[FormattableT],
) -> ContextResponse[DepsT, FormattableT]: ...


@overload
def _instrumented_model_context_call(
    self: Model,
    content: UserContent | Sequence[Message],
    *,
    ctx: Context[DepsT],
    tools: ContextTools[DepsT] | None = None,
    format: FormatSpec[FormattableT] | None = None,
) -> ContextResponse[DepsT, None] | ContextResponse[DepsT, FormattableT]: ...


@wraps(_ORIGINAL_MODEL_CONTEXT_CALL)
def _instrumented_model_context_call(
    self: Model,
    content: UserContent | Sequence[Message],
    *,
    ctx: Context[DepsT],
    tools: ContextTools[DepsT] | None = None,
    format: FormatParam = None,
) -> ContextResponse[DepsT, None] | ContextResponse[DepsT, FormattableT]:
    """Returns a GenAI-instrumented result of `Model.context_call`."""
    messages = promote_to_messages(content)
    with start_model_span(
        self,
        messages=messages,
        tools=tools,
        format=format,
        activate=True,
    ) as span_ctx:
        response = _ORIGINAL_MODEL_CONTEXT_CALL(
            self,
            content,
            ctx=ctx,
            tools=tools,
            format=format,
        )
        if span_ctx.span is not None:
            attach_response(
                span_ctx.span,
                response,
                request_messages=messages,
            )
            record_dropped_params(span_ctx.span, span_ctx.dropped_params)
        return response


def wrap_model_context_call() -> None:
    """Returns None. Replaces `Model.context_call` with the instrumented wrapper."""
    global _MODEL_CONTEXT_CALL_WRAPPED
    if _MODEL_CONTEXT_CALL_WRAPPED:
        return
    Model.context_call = _instrumented_model_context_call
    _MODEL_CONTEXT_CALL_WRAPPED = True


def unwrap_model_context_call() -> None:
    """Returns None. Restores the original `Model.context_call` implementation."""
    global _MODEL_CONTEXT_CALL_WRAPPED
    if not _MODEL_CONTEXT_CALL_WRAPPED:
        return
    Model.context_call = _ORIGINAL_MODEL_CONTEXT_CALL
    _MODEL_CONTEXT_CALL_WRAPPED = False


# =============================================================================
# Model.context_call_async instrumentation
# =============================================================================


@overload
async def _instrumented_model_context_call_async(
    self: Model,
    content: UserContent | Sequence[Message],
    *,
    ctx: Context[DepsT],
    tools: AsyncContextTools[DepsT] | None = None,
    format: None = None,
) -> AsyncContextResponse[DepsT, None]: ...


@overload
async def _instrumented_model_context_call_async(
    self: Model,
    content: UserContent | Sequence[Message],
    *,
    ctx: Context[DepsT],
    tools: AsyncContextTools[DepsT] | None = None,
    format: FormatSpec[FormattableT],
) -> AsyncContextResponse[DepsT, FormattableT]: ...


@overload
async def _instrumented_model_context_call_async(
    self: Model,
    content: UserContent | Sequence[Message],
    *,
    ctx: Context[DepsT],
    tools: AsyncContextTools[DepsT] | None = None,
    format: FormatSpec[FormattableT] | None = None,
) -> AsyncContextResponse[DepsT, None] | AsyncContextResponse[DepsT, FormattableT]: ...


@wraps(_ORIGINAL_MODEL_CONTEXT_CALL_ASYNC)
async def _instrumented_model_context_call_async(
    self: Model,
    content: UserContent | Sequence[Message],
    *,
    ctx: Context[DepsT],
    tools: AsyncContextTools[DepsT] | None = None,
    format: FormatParam = None,
) -> AsyncContextResponse[DepsT, None] | AsyncContextResponse[DepsT, FormattableT]:
    """Returns a GenAI-instrumented result of `Model.context_call_async`."""
    messages = promote_to_messages(content)
    with start_model_span(
        self,
        messages=messages,
        tools=tools,
        format=format,
        activate=True,
    ) as span_ctx:
        response = await _ORIGINAL_MODEL_CONTEXT_CALL_ASYNC(
            self,
            content,
            ctx=ctx,
            tools=tools,
            format=format,
        )
        if span_ctx.span is not None:
            await attach_response_async(
                span_ctx.span,
                response,
                request_messages=messages,
            )
            record_dropped_params(span_ctx.span, span_ctx.dropped_params)
        return response


def wrap_model_context_call_async() -> None:
    """Returns None. Replaces `Model.context_call_async` with the instrumented wrapper."""
    global _MODEL_CONTEXT_CALL_ASYNC_WRAPPED
    if _MODEL_CONTEXT_CALL_ASYNC_WRAPPED:
        return
    Model.context_call_async = _instrumented_model_context_call_async
    _MODEL_CONTEXT_CALL_ASYNC_WRAPPED = True


def unwrap_model_context_call_async() -> None:
    """Returns None. Restores the original `Model.context_call_async` implementation."""
    global _MODEL_CONTEXT_CALL_ASYNC_WRAPPED
    if not _MODEL_CONTEXT_CALL_ASYNC_WRAPPED:
        return
    Model.context_call_async = _ORIGINAL_MODEL_CONTEXT_CALL_ASYNC
    _MODEL_CONTEXT_CALL_ASYNC_WRAPPED = False


# =============================================================================
# Stream span handler helpers
# =============================================================================


def _attach_stream_span_handlers(
    *,
    response: ContextStreamResponse[DepsT, FormattableT | None]
    | StreamResponse[FormattableT | None],
    span_cm: AbstractContextManager[SpanContext],
    span: Span,
    request_messages: Sequence[Message],
) -> None:
    """Returns None. Closes the span when streaming completes."""
    chunk_iterator: Iterator[StreamResponseChunk] = response._chunk_iterator

    response_ref = weakref.ref(response)
    closed = False

    def _close_span(
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        nonlocal closed
        if closed:
            return
        closed = True
        response_obj = response_ref()
        if response_obj is not None:
            attach_response(
                span,
                response_obj,
                request_messages=request_messages,
            )
        span_cm.__exit__(exc_type, exc, tb)

    def _wrapped_iterator() -> Iterator[StreamResponseChunk]:
        with otel_trace.use_span(span, end_on_exit=False):
            try:
                yield from chunk_iterator
            except Exception as exc:  # noqa: BLE001
                _close_span(type(exc), exc, exc.__traceback__)
                raise
            else:
                _close_span(None, None, None)
            finally:
                _close_span(None, None, None)

    response._chunk_iterator = _wrapped_iterator()


def _attach_async_stream_span_handlers(
    *,
    response: AsyncContextStreamResponse[DepsT, FormattableT | None],
    span_cm: AbstractContextManager[SpanContext],
    span: Span,
    request_messages: Sequence[Message],
) -> None:
    """Returns None. Closes the span when async streaming completes."""
    chunk_iterator: AsyncIterator[StreamResponseChunk] = response._chunk_iterator

    response_ref = weakref.ref(response)
    closed = False

    def _close_span(
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        nonlocal closed
        if closed:
            return
        closed = True
        response_obj = response_ref()
        if response_obj is not None:
            attach_response(
                span,
                response_obj,
                request_messages=request_messages,
            )
        span_cm.__exit__(exc_type, exc, tb)

    async def _wrapped_iterator() -> AsyncIterator[StreamResponseChunk]:
        try:
            async for chunk in chunk_iterator:
                yield chunk
        except Exception as exc:  # noqa: BLE001
            _close_span(type(exc), exc, exc.__traceback__)
            raise
        else:
            _close_span(None, None, None)
        finally:
            _close_span(None, None, None)

    response._chunk_iterator = _wrapped_iterator()


# =============================================================================
# Model.stream instrumentation
# =============================================================================


@overload
def _instrumented_model_stream(
    self: Model,
    content: UserContent | Sequence[Message],
    *,
    tools: Tools | None = None,
    format: None = None,
) -> StreamResponse: ...


@overload
def _instrumented_model_stream(
    self: Model,
    content: UserContent | Sequence[Message],
    *,
    tools: Tools | None = None,
    format: FormatSpec[FormattableT],
) -> StreamResponse[FormattableT]: ...


@overload
def _instrumented_model_stream(
    self: Model,
    content: UserContent | Sequence[Message],
    *,
    tools: Tools | None = None,
    format: FormatSpec[FormattableT] | None = None,
) -> StreamResponse | StreamResponse[FormattableT]: ...


@wraps(_ORIGINAL_MODEL_STREAM)
def _instrumented_model_stream(
    self: Model,
    content: UserContent | Sequence[Message],
    *,
    tools: Tools | None = None,
    format: FormatParam = None,
) -> StreamResponse | StreamResponse[FormattableT]:
    """Returns a GenAI-instrumented result of `Model.stream`."""
    messages = promote_to_messages(content)
    span_cm = start_model_span(
        self,
        messages=messages,
        tools=tools,
        format=format,
        activate=False,
    )
    span_ctx = span_cm.__enter__()
    if span_ctx.span is None:
        response = _ORIGINAL_MODEL_STREAM(
            self,
            content,
            tools=tools,
            format=format,
        )
        span_cm.__exit__(None, None, None)
        return response

    try:
        with otel_trace.use_span(span_ctx.span, end_on_exit=False):
            response = _ORIGINAL_MODEL_STREAM(
                self,
                content,
                tools=tools,
                format=format,
            )
    except Exception as exc:
        span_cm.__exit__(type(exc), exc, exc.__traceback__)
        raise

    record_dropped_params(span_ctx.span, span_ctx.dropped_params)

    try:
        _attach_stream_span_handlers(
            response=response,
            span_cm=span_cm,
            span=span_ctx.span,
            request_messages=messages,
        )
    except Exception as exc:  # pragma: no cover
        span_cm.__exit__(type(exc), exc, exc.__traceback__)
        raise

    return response


def wrap_model_stream() -> None:
    """Returns None. Replaces `Model.stream` with the instrumented wrapper."""
    global _MODEL_STREAM_WRAPPED
    if _MODEL_STREAM_WRAPPED:
        return
    Model.stream = _instrumented_model_stream
    _MODEL_STREAM_WRAPPED = True


def unwrap_model_stream() -> None:
    """Returns None. Restores the original `Model.stream` implementation."""
    global _MODEL_STREAM_WRAPPED
    if not _MODEL_STREAM_WRAPPED:
        return
    Model.stream = _ORIGINAL_MODEL_STREAM
    _MODEL_STREAM_WRAPPED = False


# =============================================================================
# Model.stream_async instrumentation
# =============================================================================


@overload
async def _instrumented_model_stream_async(
    self: Model,
    content: UserContent | Sequence[Message],
    *,
    tools: AsyncTools | None = None,
    format: None = None,
) -> AsyncStreamResponse: ...


@overload
async def _instrumented_model_stream_async(
    self: Model,
    content: UserContent | Sequence[Message],
    *,
    tools: AsyncTools | None = None,
    format: FormatSpec[FormattableT],
) -> AsyncStreamResponse[FormattableT]: ...


@overload
async def _instrumented_model_stream_async(
    self: Model,
    content: UserContent | Sequence[Message],
    *,
    tools: AsyncTools | None = None,
    format: FormatSpec[FormattableT] | None = None,
) -> AsyncStreamResponse | AsyncStreamResponse[FormattableT]: ...


@wraps(_ORIGINAL_MODEL_STREAM_ASYNC)
async def _instrumented_model_stream_async(
    self: Model,
    content: UserContent | Sequence[Message],
    *,
    tools: AsyncTools | None = None,
    format: FormatParam = None,
) -> AsyncStreamResponse | AsyncStreamResponse[FormattableT]:
    """Returns a GenAI-instrumented result of `Model.stream_async`."""
    messages = promote_to_messages(content)
    span_cm = start_model_span(
        self,
        messages=messages,
        tools=tools,
        format=format,
        activate=False,
    )
    span_ctx = span_cm.__enter__()
    if span_ctx.span is None:
        response = await _ORIGINAL_MODEL_STREAM_ASYNC(
            self,
            content,
            tools=tools,
            format=format,
        )
        span_cm.__exit__(None, None, None)
        return response

    try:
        with otel_trace.use_span(span_ctx.span, end_on_exit=False):
            response = await _ORIGINAL_MODEL_STREAM_ASYNC(
                self,
                content,
                tools=tools,
                format=format,
            )
    except Exception as exc:
        span_cm.__exit__(type(exc), exc, exc.__traceback__)
        raise

    record_dropped_params(span_ctx.span, span_ctx.dropped_params)

    try:
        _attach_async_stream_span_handlers(
            response=cast(
                "AsyncContextStreamResponse[Any, FormattableT | None]", response
            ),
            span_cm=span_cm,
            span=span_ctx.span,
            request_messages=messages,
        )
    except Exception as exc:  # pragma: no cover
        span_cm.__exit__(type(exc), exc, exc.__traceback__)
        raise

    return response


def wrap_model_stream_async() -> None:
    """Returns None. Replaces `Model.stream_async` with the instrumented wrapper."""
    global _MODEL_STREAM_ASYNC_WRAPPED
    if _MODEL_STREAM_ASYNC_WRAPPED:
        return
    Model.stream_async = _instrumented_model_stream_async
    _MODEL_STREAM_ASYNC_WRAPPED = True


def unwrap_model_stream_async() -> None:
    """Returns None. Restores the original `Model.stream_async` implementation."""
    global _MODEL_STREAM_ASYNC_WRAPPED
    if not _MODEL_STREAM_ASYNC_WRAPPED:
        return
    Model.stream_async = _ORIGINAL_MODEL_STREAM_ASYNC
    _MODEL_STREAM_ASYNC_WRAPPED = False


# =============================================================================
# Model.context_stream instrumentation
# =============================================================================


@overload
def _instrumented_model_context_stream(
    self: Model,
    content: UserContent | Sequence[Message],
    *,
    ctx: Context[DepsT],
    tools: ContextTools[DepsT] | None = None,
    format: None = None,
) -> ContextStreamResponse[DepsT, None]: ...


@overload
def _instrumented_model_context_stream(
    self: Model,
    content: UserContent | Sequence[Message],
    *,
    ctx: Context[DepsT],
    tools: ContextTools[DepsT] | None = None,
    format: FormatSpec[FormattableT],
) -> ContextStreamResponse[DepsT, FormattableT]: ...


@overload
def _instrumented_model_context_stream(
    self: Model,
    content: UserContent | Sequence[Message],
    *,
    ctx: Context[DepsT],
    tools: ContextTools[DepsT] | None = None,
    format: FormatSpec[FormattableT] | None = None,
) -> (
    ContextStreamResponse[DepsT, None] | ContextStreamResponse[DepsT, FormattableT]
): ...


@wraps(_ORIGINAL_MODEL_CONTEXT_STREAM)
def _instrumented_model_context_stream(
    self: Model,
    content: UserContent | Sequence[Message],
    *,
    ctx: Context[DepsT],
    tools: ContextTools[DepsT] | None = None,
    format: FormatParam = None,
) -> ContextStreamResponse[DepsT, None] | ContextStreamResponse[DepsT, FormattableT]:
    """Returns a GenAI-instrumented result of `Model.context_stream`."""
    messages = promote_to_messages(content)
    span_cm = start_model_span(
        self,
        messages=messages,
        tools=tools,
        format=format,
        activate=False,
    )
    span_ctx = span_cm.__enter__()
    if span_ctx.span is None:
        response = _ORIGINAL_MODEL_CONTEXT_STREAM(
            self,
            content,
            ctx=ctx,
            tools=tools,
            format=format,
        )
        span_cm.__exit__(None, None, None)
        return response

    try:
        with otel_trace.use_span(span_ctx.span, end_on_exit=False):
            response = _ORIGINAL_MODEL_CONTEXT_STREAM(
                self,
                content,
                ctx=ctx,
                tools=tools,
                format=format,
            )
    except Exception as exc:
        span_cm.__exit__(type(exc), exc, exc.__traceback__)
        raise

    record_dropped_params(span_ctx.span, span_ctx.dropped_params)

    try:
        _attach_stream_span_handlers(
            response=response,
            span_cm=span_cm,
            span=span_ctx.span,
            request_messages=messages,
        )
    except Exception as exc:  # pragma: no cover
        span_cm.__exit__(type(exc), exc, exc.__traceback__)
        raise

    return response


def wrap_model_context_stream() -> None:
    """Returns None. Replaces `Model.context_stream` with the instrumented wrapper."""
    global _MODEL_CONTEXT_STREAM_WRAPPED
    if _MODEL_CONTEXT_STREAM_WRAPPED:
        return
    Model.context_stream = _instrumented_model_context_stream
    _MODEL_CONTEXT_STREAM_WRAPPED = True


def unwrap_model_context_stream() -> None:
    """Returns None. Restores the original `Model.context_stream` implementation."""
    global _MODEL_CONTEXT_STREAM_WRAPPED
    if not _MODEL_CONTEXT_STREAM_WRAPPED:
        return
    Model.context_stream = _ORIGINAL_MODEL_CONTEXT_STREAM
    _MODEL_CONTEXT_STREAM_WRAPPED = False


# =============================================================================
# Model.context_stream_async instrumentation
# =============================================================================


@overload
async def _instrumented_model_context_stream_async(
    self: Model,
    content: UserContent | Sequence[Message],
    *,
    ctx: Context[DepsT],
    tools: AsyncContextTools[DepsT] | None = None,
    format: None = None,
) -> AsyncContextStreamResponse[DepsT, None]: ...


@overload
async def _instrumented_model_context_stream_async(
    self: Model,
    content: UserContent | Sequence[Message],
    *,
    ctx: Context[DepsT],
    tools: AsyncContextTools[DepsT] | None = None,
    format: FormatSpec[FormattableT],
) -> AsyncContextStreamResponse[DepsT, FormattableT]: ...


@overload
async def _instrumented_model_context_stream_async(
    self: Model,
    content: UserContent | Sequence[Message],
    *,
    ctx: Context[DepsT],
    tools: AsyncContextTools[DepsT] | None = None,
    format: FormatSpec[FormattableT] | None = None,
) -> (
    AsyncContextStreamResponse[DepsT, None]
    | AsyncContextStreamResponse[DepsT, FormattableT]
): ...


@wraps(_ORIGINAL_MODEL_CONTEXT_STREAM_ASYNC)
async def _instrumented_model_context_stream_async(
    self: Model,
    content: UserContent | Sequence[Message],
    *,
    ctx: Context[DepsT],
    tools: AsyncContextTools[DepsT] | None = None,
    format: FormatParam = None,
) -> (
    AsyncContextStreamResponse[DepsT, None]
    | AsyncContextStreamResponse[DepsT, FormattableT]
):
    """Returns a GenAI-instrumented result of `Model.context_stream_async`."""
    messages = promote_to_messages(content)
    span_cm = start_model_span(
        self,
        messages=messages,
        tools=tools,
        format=format,
        activate=False,
    )
    span_ctx = span_cm.__enter__()
    if span_ctx.span is None:
        response = await _ORIGINAL_MODEL_CONTEXT_STREAM_ASYNC(
            self,
            content,
            ctx=ctx,
            tools=tools,
            format=format,
        )
        span_cm.__exit__(None, None, None)
        return response

    try:
        with otel_trace.use_span(span_ctx.span, end_on_exit=False):
            response = await _ORIGINAL_MODEL_CONTEXT_STREAM_ASYNC(
                self,
                content,
                ctx=ctx,
                tools=tools,
                format=format,
            )
    except Exception as exc:
        span_cm.__exit__(type(exc), exc, exc.__traceback__)
        raise

    record_dropped_params(span_ctx.span, span_ctx.dropped_params)

    try:
        _attach_async_stream_span_handlers(
            response=response,
            span_cm=span_cm,
            span=span_ctx.span,
            request_messages=messages,
        )
    except Exception as exc:  # pragma: no cover
        span_cm.__exit__(type(exc), exc, exc.__traceback__)
        raise

    return response


def wrap_model_context_stream_async() -> None:
    """Returns None. Replaces `Model.context_stream_async` with the instrumented wrapper."""
    global _MODEL_CONTEXT_STREAM_ASYNC_WRAPPED
    if _MODEL_CONTEXT_STREAM_ASYNC_WRAPPED:
        return
    Model.context_stream_async = _instrumented_model_context_stream_async
    _MODEL_CONTEXT_STREAM_ASYNC_WRAPPED = True


def unwrap_model_context_stream_async() -> None:
    """Returns None. Restores the original `Model.context_stream_async` implementation."""
    global _MODEL_CONTEXT_STREAM_ASYNC_WRAPPED
    if not _MODEL_CONTEXT_STREAM_ASYNC_WRAPPED:
        return
    Model.context_stream_async = _ORIGINAL_MODEL_CONTEXT_STREAM_ASYNC
    _MODEL_CONTEXT_STREAM_ASYNC_WRAPPED = False


# =============================================================================
# Model.resume instrumentation
# =============================================================================


@overload
def _instrumented_model_resume(
    self: Model,
    *,
    response: Response,
    content: UserContent,
) -> Response: ...


@overload
def _instrumented_model_resume(
    self: Model,
    *,
    response: Response[FormattableT],
    content: UserContent,
) -> Response[FormattableT]: ...


@overload
def _instrumented_model_resume(
    self: Model,
    *,
    response: Response | Response[FormattableT],
    content: UserContent,
) -> Response | Response[FormattableT]: ...


@wraps(_ORIGINAL_MODEL_RESUME)
def _instrumented_model_resume(
    self: Model,
    *,
    response: Response | Response[FormattableT],
    content: UserContent,
) -> Response | Response[FormattableT]:
    """Returns a GenAI-instrumented result of `Model.resume`."""
    messages = list(response.messages) + [user(content)]
    with start_model_span(
        self,
        messages=messages,
        tools=response.toolkit,
        format=cast(FormatParam, response.format),
    ) as span_ctx:
        result = _ORIGINAL_MODEL_RESUME(
            self,
            response=response,
            content=content,
        )
        if span_ctx.span is not None:
            attach_response(
                span_ctx.span,
                cast("RootResponse[Any, FormattableT | None]", result),
                request_messages=messages,
            )
            record_dropped_params(span_ctx.span, span_ctx.dropped_params)
        return result


def wrap_model_resume() -> None:
    """Returns None. Replaces `Model.resume` with the instrumented wrapper."""
    global _MODEL_RESUME_WRAPPED
    if _MODEL_RESUME_WRAPPED:
        return
    Model.resume = _instrumented_model_resume
    _MODEL_RESUME_WRAPPED = True


def unwrap_model_resume() -> None:
    """Returns None. Restores the original `Model.resume` implementation."""
    global _MODEL_RESUME_WRAPPED
    if not _MODEL_RESUME_WRAPPED:
        return
    Model.resume = _ORIGINAL_MODEL_RESUME
    _MODEL_RESUME_WRAPPED = False


# =============================================================================
# Model.resume_async instrumentation
# =============================================================================


@overload
async def _instrumented_model_resume_async(
    self: Model,
    *,
    response: AsyncResponse,
    content: UserContent,
) -> AsyncResponse: ...


@overload
async def _instrumented_model_resume_async(
    self: Model,
    *,
    response: AsyncResponse[FormattableT],
    content: UserContent,
) -> AsyncResponse[FormattableT]: ...


@overload
async def _instrumented_model_resume_async(
    self: Model,
    *,
    response: AsyncResponse | AsyncResponse[FormattableT],
    content: UserContent,
) -> AsyncResponse | AsyncResponse[FormattableT]: ...


@wraps(_ORIGINAL_MODEL_RESUME_ASYNC)
async def _instrumented_model_resume_async(
    self: Model,
    *,
    response: AsyncResponse | AsyncResponse[FormattableT],
    content: UserContent,
) -> AsyncResponse | AsyncResponse[FormattableT]:
    """Returns a GenAI-instrumented result of `Model.resume_async`."""
    messages = list(response.messages) + [user(content)]
    with start_model_span(
        self,
        messages=messages,
        tools=response.toolkit,
        format=cast(FormatParam, response.format),
        activate=True,
    ) as span_ctx:
        result = await _ORIGINAL_MODEL_RESUME_ASYNC(
            self,
            response=response,
            content=content,
        )
        if span_ctx.span is not None:
            await attach_response_async(
                span_ctx.span,
                cast("RootResponse[Any, FormattableT | None]", result),
                request_messages=messages,
            )
            record_dropped_params(span_ctx.span, span_ctx.dropped_params)
        return result


def wrap_model_resume_async() -> None:
    """Returns None. Replaces `Model.resume_async` with the instrumented wrapper."""
    global _MODEL_RESUME_ASYNC_WRAPPED
    if _MODEL_RESUME_ASYNC_WRAPPED:
        return
    Model.resume_async = _instrumented_model_resume_async
    _MODEL_RESUME_ASYNC_WRAPPED = True


def unwrap_model_resume_async() -> None:
    """Returns None. Restores the original `Model.resume_async` implementation."""
    global _MODEL_RESUME_ASYNC_WRAPPED
    if not _MODEL_RESUME_ASYNC_WRAPPED:
        return
    Model.resume_async = _ORIGINAL_MODEL_RESUME_ASYNC
    _MODEL_RESUME_ASYNC_WRAPPED = False


# =============================================================================
# Model.context_resume instrumentation
# =============================================================================


@overload
def _instrumented_model_context_resume(
    self: Model,
    *,
    ctx: Context[DepsT],
    response: ContextResponse[DepsT, None],
    content: UserContent,
) -> ContextResponse[DepsT, None]: ...


@overload
def _instrumented_model_context_resume(
    self: Model,
    *,
    ctx: Context[DepsT],
    response: ContextResponse[DepsT, FormattableT],
    content: UserContent,
) -> ContextResponse[DepsT, FormattableT]: ...


@overload
def _instrumented_model_context_resume(
    self: Model,
    *,
    ctx: Context[DepsT],
    response: ContextResponse[DepsT, None] | ContextResponse[DepsT, FormattableT],
    content: UserContent,
) -> ContextResponse[DepsT, None] | ContextResponse[DepsT, FormattableT]: ...


@wraps(_ORIGINAL_MODEL_CONTEXT_RESUME)
def _instrumented_model_context_resume(
    self: Model,
    *,
    ctx: Context[DepsT],
    response: ContextResponse[DepsT, None] | ContextResponse[DepsT, FormattableT],
    content: UserContent,
) -> ContextResponse[DepsT, None] | ContextResponse[DepsT, FormattableT]:
    """Returns a GenAI-instrumented result of `Model.context_resume`."""
    messages = list(response.messages) + [user(content)]
    with start_model_span(
        self,
        messages=messages,
        tools=response.toolkit,
        format=cast(FormatParam, response.format),
        activate=True,
    ) as span_ctx:
        result = _ORIGINAL_MODEL_CONTEXT_RESUME(
            self,
            ctx=ctx,
            response=response,
            content=content,
        )
        if span_ctx.span is not None:
            attach_response(
                span_ctx.span,
                cast("RootResponse[Any, FormattableT | None]", result),
                request_messages=messages,
            )
            record_dropped_params(span_ctx.span, span_ctx.dropped_params)
        return result


def wrap_model_context_resume() -> None:
    """Returns None. Replaces `Model.context_resume` with the instrumented wrapper."""
    global _MODEL_CONTEXT_RESUME_WRAPPED
    if _MODEL_CONTEXT_RESUME_WRAPPED:
        return
    Model.context_resume = _instrumented_model_context_resume
    _MODEL_CONTEXT_RESUME_WRAPPED = True


def unwrap_model_context_resume() -> None:
    """Returns None. Restores the original `Model.context_resume` implementation."""
    global _MODEL_CONTEXT_RESUME_WRAPPED
    if not _MODEL_CONTEXT_RESUME_WRAPPED:
        return
    Model.context_resume = _ORIGINAL_MODEL_CONTEXT_RESUME
    _MODEL_CONTEXT_RESUME_WRAPPED = False


# =============================================================================
# Model.context_resume_async instrumentation
# =============================================================================


@overload
async def _instrumented_model_context_resume_async(
    self: Model,
    *,
    ctx: Context[DepsT],
    response: AsyncContextResponse[DepsT, None],
    content: UserContent,
) -> AsyncContextResponse[DepsT, None]: ...


@overload
async def _instrumented_model_context_resume_async(
    self: Model,
    *,
    ctx: Context[DepsT],
    response: AsyncContextResponse[DepsT, FormattableT],
    content: UserContent,
) -> AsyncContextResponse[DepsT, FormattableT]: ...


@overload
async def _instrumented_model_context_resume_async(
    self: Model,
    *,
    ctx: Context[DepsT],
    response: AsyncContextResponse[DepsT, None]
    | AsyncContextResponse[DepsT, FormattableT],
    content: UserContent,
) -> AsyncContextResponse[DepsT, None] | AsyncContextResponse[DepsT, FormattableT]: ...


@wraps(_ORIGINAL_MODEL_CONTEXT_RESUME_ASYNC)
async def _instrumented_model_context_resume_async(
    self: Model,
    *,
    ctx: Context[DepsT],
    response: AsyncContextResponse[DepsT, None]
    | AsyncContextResponse[DepsT, FormattableT],
    content: UserContent,
) -> AsyncContextResponse[DepsT, None] | AsyncContextResponse[DepsT, FormattableT]:
    """Returns a GenAI-instrumented result of `Model.context_resume_async`."""
    messages = list(response.messages) + [user(content)]
    with start_model_span(
        self,
        messages=messages,
        tools=response.toolkit,
        format=cast(FormatParam, response.format),
        activate=True,
    ) as span_ctx:
        result = await _ORIGINAL_MODEL_CONTEXT_RESUME_ASYNC(
            self,
            ctx=ctx,
            response=response,
            content=content,
        )
        if span_ctx.span is not None:
            await attach_response_async(
                span_ctx.span,
                cast("RootResponse[Any, FormattableT | None]", result),
                request_messages=messages,
            )
            record_dropped_params(span_ctx.span, span_ctx.dropped_params)
        return result


def wrap_model_context_resume_async() -> None:
    """Returns None. Replaces `Model.context_resume_async` with the instrumented wrapper."""
    global _MODEL_CONTEXT_RESUME_ASYNC_WRAPPED
    if _MODEL_CONTEXT_RESUME_ASYNC_WRAPPED:
        return
    Model.context_resume_async = _instrumented_model_context_resume_async
    _MODEL_CONTEXT_RESUME_ASYNC_WRAPPED = True


def unwrap_model_context_resume_async() -> None:
    """Returns None. Restores the original `Model.context_resume_async` implementation."""
    global _MODEL_CONTEXT_RESUME_ASYNC_WRAPPED
    if not _MODEL_CONTEXT_RESUME_ASYNC_WRAPPED:
        return
    Model.context_resume_async = _ORIGINAL_MODEL_CONTEXT_RESUME_ASYNC
    _MODEL_CONTEXT_RESUME_ASYNC_WRAPPED = False


# =============================================================================
# Model.resume_stream instrumentation
# =============================================================================


@overload
def _instrumented_model_resume_stream(
    self: Model,
    *,
    response: StreamResponse,
    content: UserContent,
) -> StreamResponse: ...


@overload
def _instrumented_model_resume_stream(
    self: Model,
    *,
    response: StreamResponse[FormattableT],
    content: UserContent,
) -> StreamResponse[FormattableT]: ...


@overload
def _instrumented_model_resume_stream(
    self: Model,
    *,
    response: StreamResponse | StreamResponse[FormattableT],
    content: UserContent,
) -> StreamResponse | StreamResponse[FormattableT]: ...


@wraps(_ORIGINAL_MODEL_RESUME_STREAM)
def _instrumented_model_resume_stream(
    self: Model,
    *,
    response: StreamResponse | StreamResponse[FormattableT],
    content: UserContent,
) -> StreamResponse | StreamResponse[FormattableT]:
    """Returns a GenAI-instrumented result of `Model.resume_stream`."""
    messages = list(response.messages) + [user(content)]
    span_cm = start_model_span(
        self,
        messages=messages,
        tools=response.toolkit,
        format=cast(FormatParam, response.format),
        activate=False,
    )
    span_ctx = span_cm.__enter__()
    if span_ctx.span is None:
        result = _ORIGINAL_MODEL_RESUME_STREAM(
            self,
            response=response,
            content=content,
        )
        span_cm.__exit__(None, None, None)
        return result

    try:
        with otel_trace.use_span(span_ctx.span, end_on_exit=False):
            result = _ORIGINAL_MODEL_RESUME_STREAM(
                self,
                response=response,
                content=content,
            )
    except Exception as exc:
        span_cm.__exit__(type(exc), exc, exc.__traceback__)
        raise

    record_dropped_params(span_ctx.span, span_ctx.dropped_params)

    try:
        _attach_stream_span_handlers(
            response=cast(StreamResponse[FormattableT | None], result),
            span_cm=span_cm,
            span=span_ctx.span,
            request_messages=messages,
        )
    except Exception as exc:  # pragma: no cover
        span_cm.__exit__(type(exc), exc, exc.__traceback__)
        raise

    return result


def wrap_model_resume_stream() -> None:
    """Returns None. Replaces `Model.resume_stream` with the instrumented wrapper."""
    global _MODEL_RESUME_STREAM_WRAPPED
    if _MODEL_RESUME_STREAM_WRAPPED:
        return
    Model.resume_stream = _instrumented_model_resume_stream
    _MODEL_RESUME_STREAM_WRAPPED = True


def unwrap_model_resume_stream() -> None:
    """Returns None. Restores the original `Model.resume_stream` implementation."""
    global _MODEL_RESUME_STREAM_WRAPPED
    if not _MODEL_RESUME_STREAM_WRAPPED:
        return
    Model.resume_stream = _ORIGINAL_MODEL_RESUME_STREAM
    _MODEL_RESUME_STREAM_WRAPPED = False


# =============================================================================
# Model.resume_stream_async instrumentation
# =============================================================================


@overload
async def _instrumented_model_resume_stream_async(
    self: Model,
    *,
    response: AsyncStreamResponse,
    content: UserContent,
) -> AsyncStreamResponse: ...


@overload
async def _instrumented_model_resume_stream_async(
    self: Model,
    *,
    response: AsyncStreamResponse[FormattableT],
    content: UserContent,
) -> AsyncStreamResponse[FormattableT]: ...


@overload
async def _instrumented_model_resume_stream_async(
    self: Model,
    *,
    response: AsyncStreamResponse | AsyncStreamResponse[FormattableT],
    content: UserContent,
) -> AsyncStreamResponse | AsyncStreamResponse[FormattableT]: ...


@wraps(_ORIGINAL_MODEL_RESUME_STREAM_ASYNC)
async def _instrumented_model_resume_stream_async(
    self: Model,
    *,
    response: AsyncStreamResponse | AsyncStreamResponse[FormattableT],
    content: UserContent,
) -> AsyncStreamResponse | AsyncStreamResponse[FormattableT]:
    """Returns a GenAI-instrumented result of `Model.resume_stream_async`."""
    messages = list(response.messages) + [user(content)]
    span_cm = start_model_span(
        self,
        messages=messages,
        tools=response.toolkit,
        format=cast(FormatParam, response.format),
        activate=False,
    )
    span_ctx = span_cm.__enter__()
    if span_ctx.span is None:
        result = await _ORIGINAL_MODEL_RESUME_STREAM_ASYNC(
            self,
            response=response,
            content=content,
        )
        span_cm.__exit__(None, None, None)
        return result

    try:
        with otel_trace.use_span(span_ctx.span, end_on_exit=False):
            result = await _ORIGINAL_MODEL_RESUME_STREAM_ASYNC(
                self,
                response=response,
                content=content,
            )
    except Exception as exc:
        span_cm.__exit__(type(exc), exc, exc.__traceback__)
        raise

    record_dropped_params(span_ctx.span, span_ctx.dropped_params)

    try:
        _attach_async_stream_span_handlers(
            response=cast(
                "AsyncContextStreamResponse[Any, FormattableT | None]", result
            ),
            span_cm=span_cm,
            span=span_ctx.span,
            request_messages=messages,
        )
    except Exception as exc:  # pragma: no cover
        span_cm.__exit__(type(exc), exc, exc.__traceback__)
        raise

    return result


def wrap_model_resume_stream_async() -> None:
    """Returns None. Replaces `Model.resume_stream_async` with the instrumented wrapper."""
    global _MODEL_RESUME_STREAM_ASYNC_WRAPPED
    if _MODEL_RESUME_STREAM_ASYNC_WRAPPED:
        return
    Model.resume_stream_async = _instrumented_model_resume_stream_async
    _MODEL_RESUME_STREAM_ASYNC_WRAPPED = True


def unwrap_model_resume_stream_async() -> None:
    """Returns None. Restores the original `Model.resume_stream_async` implementation."""
    global _MODEL_RESUME_STREAM_ASYNC_WRAPPED
    if not _MODEL_RESUME_STREAM_ASYNC_WRAPPED:
        return
    Model.resume_stream_async = _ORIGINAL_MODEL_RESUME_STREAM_ASYNC
    _MODEL_RESUME_STREAM_ASYNC_WRAPPED = False


# =============================================================================
# Model.context_resume_stream instrumentation
# =============================================================================


@overload
def _instrumented_model_context_resume_stream(
    self: Model,
    *,
    ctx: Context[DepsT],
    response: ContextStreamResponse[DepsT, None],
    content: UserContent,
) -> ContextStreamResponse[DepsT, None]: ...


@overload
def _instrumented_model_context_resume_stream(
    self: Model,
    *,
    ctx: Context[DepsT],
    response: ContextStreamResponse[DepsT, FormattableT],
    content: UserContent,
) -> ContextStreamResponse[DepsT, FormattableT]: ...


@overload
def _instrumented_model_context_resume_stream(
    self: Model,
    *,
    ctx: Context[DepsT],
    response: ContextStreamResponse[DepsT, None]
    | ContextStreamResponse[DepsT, FormattableT],
    content: UserContent,
) -> (
    ContextStreamResponse[DepsT, None] | ContextStreamResponse[DepsT, FormattableT]
): ...


@wraps(_ORIGINAL_MODEL_CONTEXT_RESUME_STREAM)
def _instrumented_model_context_resume_stream(
    self: Model,
    *,
    ctx: Context[DepsT],
    response: ContextStreamResponse[DepsT, None]
    | ContextStreamResponse[DepsT, FormattableT],
    content: UserContent,
) -> ContextStreamResponse[DepsT, None] | ContextStreamResponse[DepsT, FormattableT]:
    """Returns a GenAI-instrumented result of `Model.context_resume_stream`."""
    messages = list(response.messages) + [user(content)]
    span_cm = start_model_span(
        self,
        messages=messages,
        tools=response.toolkit,
        format=cast(FormatParam, response.format),
        activate=False,
    )
    span_ctx = span_cm.__enter__()
    if span_ctx.span is None:
        result = _ORIGINAL_MODEL_CONTEXT_RESUME_STREAM(
            self,
            ctx=ctx,
            response=response,
            content=content,
        )
        span_cm.__exit__(None, None, None)
        return result

    try:
        with otel_trace.use_span(span_ctx.span, end_on_exit=False):
            result = _ORIGINAL_MODEL_CONTEXT_RESUME_STREAM(
                self,
                ctx=ctx,
                response=response,
                content=content,
            )
    except Exception as exc:
        span_cm.__exit__(type(exc), exc, exc.__traceback__)
        raise

    record_dropped_params(span_ctx.span, span_ctx.dropped_params)

    try:
        _attach_stream_span_handlers(
            response=cast("ContextStreamResponse[Any, FormattableT | None]", result),
            span_cm=span_cm,
            span=span_ctx.span,
            request_messages=messages,
        )
    except Exception as exc:  # pragma: no cover
        span_cm.__exit__(type(exc), exc, exc.__traceback__)
        raise

    return result


def wrap_model_context_resume_stream() -> None:
    """Returns None. Replaces `Model.context_resume_stream` with the instrumented wrapper."""
    global _MODEL_CONTEXT_RESUME_STREAM_WRAPPED
    if _MODEL_CONTEXT_RESUME_STREAM_WRAPPED:
        return
    Model.context_resume_stream = _instrumented_model_context_resume_stream
    _MODEL_CONTEXT_RESUME_STREAM_WRAPPED = True


def unwrap_model_context_resume_stream() -> None:
    """Returns None. Restores the original `Model.context_resume_stream` implementation."""
    global _MODEL_CONTEXT_RESUME_STREAM_WRAPPED
    if not _MODEL_CONTEXT_RESUME_STREAM_WRAPPED:
        return
    Model.context_resume_stream = _ORIGINAL_MODEL_CONTEXT_RESUME_STREAM
    _MODEL_CONTEXT_RESUME_STREAM_WRAPPED = False


# =============================================================================
# Model.context_resume_stream_async instrumentation
# =============================================================================


@overload
async def _instrumented_model_context_resume_stream_async(
    self: Model,
    *,
    ctx: Context[DepsT],
    response: AsyncContextStreamResponse[DepsT, None],
    content: UserContent,
) -> AsyncContextStreamResponse[DepsT, None]: ...


@overload
async def _instrumented_model_context_resume_stream_async(
    self: Model,
    *,
    ctx: Context[DepsT],
    response: AsyncContextStreamResponse[DepsT, FormattableT],
    content: UserContent,
) -> AsyncContextStreamResponse[DepsT, FormattableT]: ...


@overload
async def _instrumented_model_context_resume_stream_async(
    self: Model,
    *,
    ctx: Context[DepsT],
    response: AsyncContextStreamResponse[DepsT, None]
    | AsyncContextStreamResponse[DepsT, FormattableT],
    content: UserContent,
) -> (
    AsyncContextStreamResponse[DepsT, None]
    | AsyncContextStreamResponse[DepsT, FormattableT]
): ...


@wraps(_ORIGINAL_MODEL_CONTEXT_RESUME_STREAM_ASYNC)
async def _instrumented_model_context_resume_stream_async(
    self: Model,
    *,
    ctx: Context[DepsT],
    response: AsyncContextStreamResponse[DepsT, None]
    | AsyncContextStreamResponse[DepsT, FormattableT],
    content: UserContent,
) -> (
    AsyncContextStreamResponse[DepsT, None]
    | AsyncContextStreamResponse[DepsT, FormattableT]
):
    """Returns a GenAI-instrumented result of `Model.context_resume_stream_async`."""
    messages = list(response.messages) + [user(content)]
    span_cm = start_model_span(
        self,
        messages=messages,
        tools=response.toolkit,
        format=cast(FormatParam, response.format),
        activate=False,
    )
    span_ctx = span_cm.__enter__()
    if span_ctx.span is None:
        result = await _ORIGINAL_MODEL_CONTEXT_RESUME_STREAM_ASYNC(
            self,
            ctx=ctx,
            response=response,
            content=content,
        )
        span_cm.__exit__(None, None, None)
        return result

    try:
        with otel_trace.use_span(span_ctx.span, end_on_exit=False):
            result = await _ORIGINAL_MODEL_CONTEXT_RESUME_STREAM_ASYNC(
                self,
                ctx=ctx,
                response=response,
                content=content,
            )
    except Exception as exc:
        span_cm.__exit__(type(exc), exc, exc.__traceback__)
        raise

    record_dropped_params(span_ctx.span, span_ctx.dropped_params)

    try:
        _attach_async_stream_span_handlers(
            response=cast(
                "AsyncContextStreamResponse[Any, FormattableT | None]", result
            ),
            span_cm=span_cm,
            span=span_ctx.span,
            request_messages=messages,
        )
    except Exception as exc:  # pragma: no cover
        span_cm.__exit__(type(exc), exc, exc.__traceback__)
        raise

    return result


def wrap_model_context_resume_stream_async() -> None:
    """Returns None. Replaces `Model.context_resume_stream_async` with the instrumented wrapper."""
    global _MODEL_CONTEXT_RESUME_STREAM_ASYNC_WRAPPED
    if _MODEL_CONTEXT_RESUME_STREAM_ASYNC_WRAPPED:
        return
    Model.context_resume_stream_async = _instrumented_model_context_resume_stream_async
    _MODEL_CONTEXT_RESUME_STREAM_ASYNC_WRAPPED = True


def unwrap_model_context_resume_stream_async() -> None:
    """Returns None. Restores the original `Model.context_resume_stream_async` implementation."""
    global _MODEL_CONTEXT_RESUME_STREAM_ASYNC_WRAPPED
    if not _MODEL_CONTEXT_RESUME_STREAM_ASYNC_WRAPPED:
        return
    Model.context_resume_stream_async = _ORIGINAL_MODEL_CONTEXT_RESUME_STREAM_ASYNC
    _MODEL_CONTEXT_RESUME_STREAM_ASYNC_WRAPPED = False
