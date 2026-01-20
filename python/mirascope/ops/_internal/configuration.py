"""Configuration utilities for Mirascope ops module initialization and setup."""

from __future__ import annotations

import logging
from collections.abc import Iterator
from contextlib import contextmanager
from typing import TYPE_CHECKING

from opentelemetry import trace as otel_trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

from ...api.client import Mirascope
from ...api.settings import update_settings
from .exporters import MirascopeOTLPExporter

if TYPE_CHECKING:
    from opentelemetry.trace import Tracer

DEFAULT_TRACER_NAME = "mirascope.llm"

logger = logging.getLogger(__name__)

_tracer_provider: TracerProvider | None = None
_tracer_name: str = DEFAULT_TRACER_NAME
_tracer_version: str | None = None
_tracer: Tracer | None = None


def _create_mirascope_cloud_provider(
    api_key: str | None = None, base_url: str | None = None
) -> TracerProvider:
    """Create a TracerProvider configured for Mirascope Cloud.

    Args:
        api_key: Optional API key. If not provided, uses MIRASCOPE_API_KEY env var.

    Returns:
        Configured TracerProvider with MirascopeOTLPExporter.

    Raises:
        RuntimeError: If API key is not available.
    """
    try:
        client = Mirascope(api_key=api_key, base_url=base_url)
    except (ValueError, RuntimeError) as e:
        raise RuntimeError(
            "Failed to create Mirascope Cloud client. "
            "Set MIRASCOPE_API_KEY environment variable or pass api_key parameter."
        ) from e

    exporter = MirascopeOTLPExporter(client=client)
    provider = TracerProvider()
    provider.add_span_processor(BatchSpanProcessor(exporter))

    return provider


def configure(
    *,
    api_key: str | None = None,
    base_url: str | None = None,
    tracer_provider: TracerProvider | None = None,
    tracer_name: str = DEFAULT_TRACER_NAME,
    tracer_version: str | None = None,
) -> None:
    """Configure the ops module for tracing.

    When called without arguments, automatically configures Mirascope Cloud
    using the MIRASCOPE_API_KEY environment variable.

    Args:
        tracer_provider: Optional custom TracerProvider. If provided, this takes
            precedence over automatic Mirascope Cloud configuration.
        api_key: Optional Mirascope Cloud API key. If not provided, uses
            MIRASCOPE_API_KEY environment variable.
        tracer_name: Tracer name to use when creating a tracer.
            Defaults to "mirascope.llm".
        tracer_version: Optional tracer version.

    Raises:
        RuntimeError: If no tracer_provider is given and Mirascope Cloud
            cannot be configured (missing API key).

    Example:
        Simple Mirascope Cloud configuration (recommended):
        ```python
        import os
        os.environ["MIRASCOPE_API_KEY"] = "your-api-key"

        from mirascope import ops

        ops.configure()  # Automatically uses Mirascope Cloud
        ```

        With explicit API key:
        ```python
        from mirascope import ops

        ops.configure(api_key="your-api-key")
        ```

        With custom tracer provider:
        ```python
        from mirascope import ops
        from opentelemetry.sdk.trace import TracerProvider

        provider = TracerProvider()
        ops.configure(tracer_provider=provider)
        ```
    """
    global _tracer_provider, _tracer_name, _tracer_version, _tracer

    # Update settings so get_sync_client/get_async_client can use these values
    if api_key is not None or base_url is not None:
        update_settings(api_key=api_key, base_url=base_url)

    # If no tracer_provider given, auto-configure Mirascope Cloud
    if tracer_provider is None:
        tracer_provider = _create_mirascope_cloud_provider(
            api_key=api_key, base_url=base_url
        )

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
