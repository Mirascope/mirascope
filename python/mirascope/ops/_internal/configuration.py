"""Configuration utilities for Mirascope ops module initialization and setup."""

from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.trace import Tracer
else:
    Tracer = None

DEFAULT_TRACER_NAME = "mirascope.llm"

try:
    from opentelemetry import trace as otel_trace
except ImportError:  # pragma: no cover
    otel_trace = None

_tracer_provider: TracerProvider | None = None
_tracer_name: str = DEFAULT_TRACER_NAME
_tracer_version: str | None = None
_tracer: Tracer | None = None


def configure(
    *,
    tracer_provider: TracerProvider | None = None,
    tracer_name: str = DEFAULT_TRACER_NAME,
    tracer_version: str | None = None,
) -> None:
    """Configure the ops module defaults for tracing.

    Sets up default tracer settings for the ops module. If a tracer_provider
    is supplied, it will be installed as the global OpenTelemetry tracer provider.

    Args:
        tracer_provider: Optional OpenTelemetry TracerProvider to use as default
            and to install globally.
        tracer_name: Tracer name to use when creating a tracer.
            Defaults to "mirascope.llm".
        tracer_version: Optional tracer version.

    Example:

        Configure custom tracer settings:
        ```python
        from mirascope import ops
        from opentelemetry.sdk.trace import TracerProvider

        provider = TracerProvider()
        ops.configure(tracer_provider=provider)
        ops.instrument_llm()
        ```
    """
    # TODO: refactor alongside other import error handling improvements
    if otel_trace is None:  # pragma: no cover
        raise ImportError(
            "OpenTelemetry is not installed. Run `pip install mirascope[otel]` "
            "before calling `ops.configure(tracer_provider=...)`."
        )

    global _tracer_provider, _tracer_name, _tracer_version, _tracer

    if tracer_provider is not None:
        _tracer_provider = tracer_provider
        otel_trace.set_tracer_provider(tracer_provider)

    _tracer_name = tracer_name
    _tracer_version = tracer_version

    if otel_trace is not None:
        provider = (
            otel_trace.get_tracer_provider()
            if _tracer_provider is None
            else _tracer_provider
        )
        _tracer = provider.get_tracer(_tracer_name, _tracer_version)


def set_tracer(tracer: Tracer | None) -> None:
    """Set the configured tracer instance."""
    global _tracer
    _tracer = tracer


def get_tracer() -> Tracer | None:
    """Return the configured tracer instance."""
    return _tracer


@contextmanager
def tracer_context(tracer: Tracer | None) -> Iterator[Tracer | None]:
    """Context manager for temporarily setting a tracer.

    Temporarily sets the tracer for the duration of the context and restores
    the previous tracer when the context exits.

    Args:
        tracer: The tracer to use within the context.

    Yields:
        The tracer that was set.

    Example:
        ```python
        from mirascope import ops
        from opentelemetry.sdk.trace import TracerProvider

        provider = TracerProvider()
        tracer = provider.get_tracer("my-tracer")

        with ops.tracer_context(tracer):
            # Use the tracer within this context
            ...
        # Previous tracer is restored here
        ```
    """
    previous_tracer = get_tracer()
    set_tracer(tracer)
    try:
        yield tracer
    finally:
        set_tracer(previous_tracer)
