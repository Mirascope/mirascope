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
    LocalProvider,
    Messages,
    Provider,
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
    "AudioPart",
    "AudioURLPart",
    "BaseDynamicConfig",
    "BaseMessageParam",
    "BaseTool",
    "BaseToolKit",
    "CacheControlPart",
    "DocumentPart",
    "ImagePart",
    "ImageURLPart",
    "LocalProvider",
    "Messages",
    "Provider",
    "TextPart",
    "ToolCallPart",
    "ToolResultPart",
    "__version__",
    "core",
    "integrations",
    "prompt_template",
    "retries",
]
