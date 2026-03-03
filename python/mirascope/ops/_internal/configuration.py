"""Configuration utilities for Mirascope ops module initialization and setup."""

from __future__ import annotations

import logging
from collections.abc import Iterator
from contextlib import contextmanager
from typing import TYPE_CHECKING

from opentelemetry import trace as otel_trace
from opentelemetry.sdk.trace import TracerProvider

if TYPE_CHECKING:
    from opentelemetry.trace import Tracer

DEFAULT_TRACER_NAME = "mirascope.llm"

logger = logging.getLogger(__name__)

_tracer_provider: TracerProvider | None = None
_tracer_name: str = DEFAULT_TRACER_NAME
_tracer_version: str | None = None
_tracer: Tracer | None = None


def configure(
    *,
    tracer_provider: TracerProvider,
    tracer_name: str = DEFAULT_TRACER_NAME,
    tracer_version: str | None = None,
) -> None:
    """Configure the ops module for tracing.

    Args:
        tracer_provider: The TracerProvider to use for tracing.
        tracer_name: Tracer name to use when creating a tracer.
            Defaults to "mirascope.llm".
        tracer_version: Optional tracer version.

    Example:
        ```python
        from mirascope import ops
        from opentelemetry.sdk.trace import TracerProvider

        provider = TracerProvider()
        ops.configure(tracer_provider=provider)
        ```
    """
    global _tracer_provider, _tracer_name, _tracer_version, _tracer

    _tracer_provider = tracer_provider
    otel_trace.set_tracer_provider(tracer_provider)

    _tracer_name = tracer_name
    _tracer_version = tracer_version

    _tracer = tracer_provider.get_tracer(_tracer_name, _tracer_version)


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
