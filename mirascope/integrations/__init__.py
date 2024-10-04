"""Integrations with third party libraries."""

from contextlib import suppress

from ._middleware_factory import middleware_factory

with suppress(ImportError):
    from . import logfire as logfire

with suppress(ImportError):
    from . import langfuse as langfuse

with suppress(ImportError):
    from . import otel as otel

__all__ = ["langfuse", "logfire", "middleware_factory", "otel"]
