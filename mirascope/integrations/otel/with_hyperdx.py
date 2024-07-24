"""Mirascope x HyperDX Integration."""

import os
from typing import (
    Awaitable,
    Callable,
    ParamSpec,
    TypeVar,
)

from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import (
    BatchSpanProcessor,
)
from pydantic import BaseModel

from mirascope.integrations.otel import configure, with_otel

from ...core.base import BaseCallResponse
from ...core.base._stream import BaseStream
from ...core.base._structured_stream import BaseStructuredStream

_BaseCallResponseT = TypeVar("_BaseCallResponseT", bound=BaseCallResponse)
_BaseStreamT = TypeVar("_BaseStreamT", bound=BaseStream)
_BaseModelT = TypeVar("_BaseModelT", bound=BaseModel)
_BaseStructuredStreamT = TypeVar("_BaseStructuredStreamT", bound=BaseStructuredStream)
_P = ParamSpec("_P")
SyncFunc = Callable[
    _P, _BaseCallResponseT | _BaseStreamT | _BaseModelT | _BaseStructuredStreamT
]
AsyncFunc = Callable[
    _P,
    Awaitable[_BaseCallResponseT | _BaseStreamT | _BaseModelT | _BaseStructuredStreamT],
]


def with_hyperdx(
    fn: SyncFunc | AsyncFunc,
) -> SyncFunc | AsyncFunc:
    """Decorator to wrap a function with hyperdx."""
    provider = trace.get_tracer_provider()
    if not isinstance(provider, TracerProvider):
        configure(
            processors=[
                BatchSpanProcessor(
                    OTLPSpanExporter(
                        endpoint="https://in-otel.hyperdx.io/v1/traces",
                        headers={"authorization": os.getenv("HYPERDX_API_KEY", "")},
                    )
                )
            ]
        )
    return with_otel(fn)
