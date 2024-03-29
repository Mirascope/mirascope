"""mirascope package."""
import importlib.metadata
from contextlib import suppress

with suppress(ImportError):
    from . import anthropic

with suppress(ImportError):
    from . import gemini

with suppress(ImportError):
    from . import openai

with suppress(ImportError):
    from . import mistral

with suppress(ImportError):
    from .wandb import wandb

__version__ = importlib.metadata.version("mirascope")
