"""OpenTelemetry GenAI instrumentation for `mirascope.llm`.

This module provides the public instrument_llm() and uninstrument_llm() functions
that enable/disable instrumentation for Model calls and Response.resume methods.
"""

from __future__ import annotations

import os

from opentelemetry import trace as otel_trace

from ...configuration import get_tracer
from .model import (
    unwrap_model_call,
    unwrap_model_call_async,
    unwrap_model_context_call,
    unwrap_model_context_call_async,
    unwrap_model_context_resume,
    unwrap_model_context_resume_async,
    unwrap_model_context_resume_stream,
    unwrap_model_context_resume_stream_async,
    unwrap_model_context_stream,
    unwrap_model_context_stream_async,
    unwrap_model_resume,
    unwrap_model_resume_async,
    unwrap_model_resume_stream,
    unwrap_model_resume_stream_async,
    unwrap_model_stream,
    unwrap_model_stream_async,
    wrap_model_call,
    wrap_model_call_async,
    wrap_model_context_call,
    wrap_model_context_call_async,
    wrap_model_context_resume,
    wrap_model_context_resume_async,
    wrap_model_context_resume_stream,
    wrap_model_context_resume_stream_async,
    wrap_model_context_stream,
    wrap_model_context_stream_async,
    wrap_model_resume,
    wrap_model_resume_async,
    wrap_model_resume_stream,
    wrap_model_resume_stream_async,
    wrap_model_stream,
    wrap_model_stream_async,
)
from .response import (
    unwrap_async_context_response_resume,
    unwrap_async_context_stream_response_resume,
    unwrap_async_response_resume,
    unwrap_async_stream_response_resume,
    unwrap_context_response_resume,
    unwrap_context_stream_response_resume,
    unwrap_response_resume,
    unwrap_stream_response_resume,
    wrap_async_context_response_resume,
    wrap_async_context_stream_response_resume,
    wrap_async_response_resume,
    wrap_async_stream_response_resume,
    wrap_context_response_resume,
    wrap_context_stream_response_resume,
    wrap_response_resume,
    wrap_stream_response_resume,
)


def instrument_llm() -> None:
    """Enable GenAI 1.38 span emission for future `llm.Model` calls and streams.

    Uses the tracer provider configured via `ops.configure()`. If no provider
    was configured, uses the global OpenTelemetry tracer provider.

    Example:

        Enable instrumentation with a custom provider:
        ```python
        from mirascope import ops
        from opentelemetry.sdk.trace import TracerProvider

        provider = TracerProvider()
        ops.configure(tracer_provider=provider)
        ops.instrument_llm()
        ```
    """
    if otel_trace is None:  # pragma: no cover
        raise ImportError(
            "OpenTelemetry is not installed. Run `pip install mirascope[otel]` "
            "and ensure `opentelemetry-api` is available before calling "
            "`instrument_llm`."
        )

    os.environ.setdefault("OTEL_SEMCONV_STABILITY_OPT_IN", "gen_ai_latest_experimental")

    if get_tracer() is None:  # pragma: no cover
        raise RuntimeError(
            "You must call `configure()` before calling `instrument_llm()`."
        )

    # Model call methods
    wrap_model_call()
    wrap_model_call_async()
    wrap_model_context_call()
    wrap_model_context_call_async()
    wrap_model_stream()
    wrap_model_stream_async()
    wrap_model_context_stream()
    wrap_model_context_stream_async()

    # Model resume methods
    wrap_model_resume()
    wrap_model_resume_async()
    wrap_model_context_resume()
    wrap_model_context_resume_async()
    wrap_model_resume_stream()
    wrap_model_resume_stream_async()
    wrap_model_context_resume_stream()
    wrap_model_context_resume_stream_async()

    # Response resume methods (Mirascope-specific spans)
    wrap_response_resume()
    wrap_async_response_resume()
    wrap_context_response_resume()
    wrap_async_context_response_resume()
    wrap_stream_response_resume()
    wrap_async_stream_response_resume()
    wrap_context_stream_response_resume()
    wrap_async_context_stream_response_resume()


def uninstrument_llm() -> None:
    """Disable previously configured instrumentation."""
    # Model call methods
    unwrap_model_call()
    unwrap_model_call_async()
    unwrap_model_context_call()
    unwrap_model_context_call_async()
    unwrap_model_stream()
    unwrap_model_stream_async()
    unwrap_model_context_stream()
    unwrap_model_context_stream_async()

    # Model resume methods
    unwrap_model_resume()
    unwrap_model_resume_async()
    unwrap_model_context_resume()
    unwrap_model_context_resume_async()
    unwrap_model_resume_stream()
    unwrap_model_resume_stream_async()
    unwrap_model_context_resume_stream()
    unwrap_model_context_resume_stream_async()

    # Response resume methods (Mirascope-specific spans)
    unwrap_response_resume()
    unwrap_async_response_resume()
    unwrap_context_response_resume()
    unwrap_async_context_response_resume()
    unwrap_stream_response_resume()
    unwrap_async_stream_response_resume()
    unwrap_context_stream_response_resume()
    unwrap_async_context_stream_response_resume()
