"""Utilities for retrying failed API calls."""

from contextlib import suppress

with suppress(ImportError):
    from . import tenacity as tenacity
