"""mirascope package."""
import importlib.metadata
from contextlib import suppress

from .base import BasePrompt, Message

with suppress(ImportError):
    from . import openai

__version__ = importlib.metadata.version("mirascope")
