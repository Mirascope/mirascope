"""Mirascope package."""

import importlib.metadata
from contextlib import suppress

with suppress(ImportError):
    from . import core as core

with suppress(ImportError):
    from . import integrations as integrations

__version__ = importlib.metadata.version("mirascope")

__all__ = ["core", "integrations", "__version__"]
