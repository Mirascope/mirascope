"""A module for interacting with Chat APIs."""
from contextlib import suppress

from . import openai

with suppress(ImportError):
    from . import gemini
