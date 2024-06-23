"""Integrations with third party libraries."""

from contextlib import suppress

with suppress(ImportError):
    from . import tenacity as tenacity

__all__ = ["tenacity"]
