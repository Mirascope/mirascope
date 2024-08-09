"""Mirascope x HyperDX Integration."""

import os

from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import (
    BatchSpanProcessor,
)

from mirascope.integrations.otel._utils import configure
from mirascope.integrations.otel._with_otel import with_otel


def with_hyperdx(fn):
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
