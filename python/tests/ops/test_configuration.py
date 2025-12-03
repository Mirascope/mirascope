"""Tests for the configuration module."""

from opentelemetry.sdk.trace import TracerProvider

from mirascope import ops
from mirascope.ops._internal import configuration


def test_configure_with_trace_provider() -> None:
    """Configure the SDK with a custom tracer provider."""
    tracer_provider = TracerProvider()
    ops.configure(tracer_provider=tracer_provider)
    assert configuration._tracer_provider is tracer_provider  # pyright: ignore[reportPrivateUsage]
    assert configuration._tracer is not None  # pyright: ignore[reportPrivateUsage]
