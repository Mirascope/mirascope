"""Mirascope package."""

import importlib.metadata

from . import core

__version__ = importlib.metadata.version("mirascope")

__all__ = ["__version__", "core"]
