"""Integrations with third party libraries."""

from contextlib import suppress

from .middleware_factory import middleware_decorator

with suppress(ImportError):
    from . import logfire as logfire

with suppress(ImportError):
    from . import langfuse as langfuse

with suppress(ImportError):
    from . import otel as otel

with suppress(ImportError):
    from . import tenacity as tenacity


__all__ = ["langfuse", "logfire", "middleware_decorator", "otel", "tenacity"]
