"""mirascope package."""
import importlib.metadata
from contextlib import suppress

from .base import BaseCallParams, BasePrompt, Message, tags

with suppress(ImportError):
    from . import anthropic

with suppress(ImportError):
    from . import gemini

with suppress(ImportError):
    from . import openai

with suppress(ImportError):
    from . import mistral

with suppress(ImportError):
    from . import wandb

__version__ = importlib.metadata.version("mirascope")
