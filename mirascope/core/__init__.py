"""The Mirascope Core Functionality."""

from contextlib import suppress

from . import base
from .base import BasePrompt, prompt_template, tags

with suppress(ImportError):
    from . import openai as openai

__all__ = ["base", "BasePrompt", "openai", "prompt_template", "tags"]
