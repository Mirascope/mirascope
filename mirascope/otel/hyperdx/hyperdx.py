import os

from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import (
    BatchSpanProcessor,
)

import mirascope.otel.otel as motel  # pytest weirdness


def with_hyperdx(cls):
    """Decorator to wrap a function with hyperdx."""
    provider = trace.get_tracer_provider()
    if not isinstance(provider, TracerProvider):
        motel.configure(
            processors=[
                BatchSpanProcessor(
                    OTLPSpanExporter(
                        endpoint="https://in-otel.hyperdx.io/v1/traces",
                        headers={"authorization": os.getenv("HYPERDX_API_KEY")},
                    )
                )
            ]
        )
    return motel.with_otel(cls)
