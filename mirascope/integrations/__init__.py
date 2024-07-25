"""Integrations with third party libraries."""

from contextlib import suppress

from .middleware_factory import middleware_decorator

with suppress(ImportError):
    from . import tenacity as tenacity

with suppress(ImportError):
    from . import logfire as logfire

__all__ = ["tenacity", "logfire", "middleware_decorator"]
