"""Mirascope package."""

import importlib.metadata
from contextlib import suppress

with suppress(ImportError):
    from . import core as core

from .core import (
    AudioPart,
    AudioURLPart,
    BaseDynamicConfig,
    BaseMessageParam,
    BaseTool,
    BaseToolKit,
    CacheControlPart,
    DocumentPart,
    ImagePart,
    ImageURLPart,
    Messages,
    TextPart,
    ToolCallPart,
    ToolResultPart,
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
    "Messages",
    "__version__",
    "AudioPart",
    "AudioURLPart",
    "CacheControlPart",
    "DocumentPart",
    "ImagePart",
    "ImageURLPart",
    "TextPart",
    "ToolCallPart",
    "ToolResultPart",
]
