"""mirascope package."""
import importlib.metadata

from .base import BasePrompt, Message

__version__ = importlib.metadata.version("mirascope")
