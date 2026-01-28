"""Operational helpers (tracing, sessions, future ops.* utilities)."""

from __future__ import annotations

from .._stubs import stub_module_if_missing

# Stub modules for missing optional dependencies BEFORE importing
# This must happen before any imports from these modules
stub_module_if_missing("mirascope.ops", "ops")

# Now imports work regardless of which packages are installed
# ruff: noqa: E402
from ._internal.configuration import configure, tracer_context
from ._internal.context import propagated_context
from ._internal.instrumentation import (
    instrument_anthropic,
    instrument_google_genai,
    instrument_llm,
    instrument_openai,
    is_anthropic_instrumented,
    is_google_genai_instrumented,
    is_openai_instrumented,
    uninstrument_anthropic,
    uninstrument_google_genai,
    uninstrument_llm,
    uninstrument_openai,
)
from ._internal.propagation import (
    ContextPropagator,
    PropagatorFormat,
    extract_context,
    get_propagator,
    inject_context,
    reset_propagator,
)
from ._internal.session import (
    SESSION_HEADER_NAME,
    SessionContext,
    current_session,
    extract_session_id,
    session,
)
from ._internal.spans import Span, span
from ._internal.traced_calls import (
    TracedAsyncCall,
    TracedAsyncContextCall,
    TracedCall,
    TracedContextCall,
)
from ._internal.traced_functions import (
    AsyncTrace,
    AsyncTracedFunction,
    AsyncTracedSpanFunction,
    Trace,
    TracedFunction,
    TracedSpanFunction,
)
from ._internal.tracing import (
    TraceDecorator,
    trace,
)
from ._internal.versioned_calls import (
    VersionedAsyncCall,
    VersionedAsyncContextCall,
    VersionedCall,
    VersionedContextCall,
)
from ._internal.versioned_functions import (
    AsyncVersionedFunction,
    VersionedFunction,
    VersionInfo,
)
from ._internal.versioning import (
    VersionDecorator,
    version,
)
from .exceptions import ClosureComputationError

__all__ = [
    "SESSION_HEADER_NAME",
    "AsyncTrace",
    "AsyncTracedFunction",
    "AsyncTracedSpanFunction",
    "AsyncVersionedFunction",
    "ClosureComputationError",
    "ContextPropagator",
    "PropagatorFormat",
    "SessionContext",
    "Span",
    "Trace",
    "TraceDecorator",
    "TracedAsyncCall",
    "TracedAsyncContextCall",
    "TracedCall",
    "TracedContextCall",
    "TracedFunction",
    "TracedSpanFunction",
    "VersionDecorator",
    "VersionInfo",
    "VersionedAsyncCall",
    "VersionedAsyncContextCall",
    "VersionedCall",
    "VersionedContextCall",
    "VersionedFunction",
    "configure",
    "current_session",
    "extract_context",
    "extract_session_id",
    "get_propagator",
    "inject_context",
    "instrument_anthropic",
    "instrument_google_genai",
    "instrument_llm",
    "instrument_openai",
    "is_anthropic_instrumented",
    "is_google_genai_instrumented",
    "is_openai_instrumented",
    "propagated_context",
    "reset_propagator",
    "session",
    "span",
    "trace",
    "tracer_context",
    "uninstrument_anthropic",
    "uninstrument_google_genai",
    "uninstrument_llm",
    "uninstrument_openai",
    "version",
]
