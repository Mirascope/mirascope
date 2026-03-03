"""Mirascope v2 Beta."""

from contextlib import suppress

with suppress(ImportError):
    from . import llm as llm

with suppress(ImportError):
    from . import ops as ops

__all__ = ["llm", "ops"]
