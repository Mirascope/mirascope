"""Mirascope package."""

import importlib.metadata
from contextlib import suppress

with suppress(ImportError):
    from . import core as core

from .core import (
    BaseDynamicConfig,
    BaseMessageParam,
    BaseTool,
    BaseToolKit,
    Messages,
    prompt_template,
)

with suppress(ImportError):
    from . import integrations as integrations

with suppress(ImportError):
    from . import retries as retries

__version__ = importlib.metadata.version("mirascope")

__all__ = [
    "BaseDynamicConfig",
    "BaseMessageParam",
    "BaseTool",
    "BaseToolKit",
    "core",
    "integrations",
    "prompt_template",
    "retries",
    "__version__",
]
