"""Utilities for retrying failed API calls."""

from contextlib import suppress

from .fallback import FallbackError, fallback

with suppress(ImportError):
    from . import tenacity as tenacity


__all__ = ["fallback", "FallbackError", "tenacity"]
