"""Utilities for retrying failed API calls."""

from contextlib import suppress

from .fallback import fallback

with suppress(ImportError):
    from . import tenacity as tenacity


__all__ = ["fallback", "tenacity"]
