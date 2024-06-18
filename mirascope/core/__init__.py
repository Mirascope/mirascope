"""The Mirascope Core Functionality."""

from contextlib import suppress

from . import base
from .base import BasePrompt, tags

with suppress(ImportError):
    from . import openai

__all__ = ["base", "BasePrompt", "openai", "tags"]
