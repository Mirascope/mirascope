"""mirascope package."""
import importlib.metadata
from contextlib import suppress

from .base import BaseCallParams, BasePrompt, Message, tags

with suppress(ImportError):
    from . import anthropic

with suppress(ImportError):
    from . import chroma

with suppress(ImportError):
    from . import cohere

with suppress(ImportError):
    from . import gemini

with suppress(ImportError):
    from . import groq

with suppress(ImportError):
    from . import mistral

with suppress(ImportError):
    from . import openai

with suppress(ImportError):
    from . import wandb

with suppress(ImportError):
    from . import logfire

with suppress(ImportError):
    from . import pinecone


__version__ = importlib.metadata.version("mirascope")

__all__ = [
    "__version__",
    "anthropic",
    "chroma",
    "cohere",
    "gemini",
    "groq",
    "mistral",
    "openai",
    "pinecone",
    "logfire",
    "wandb",
    "BaseCallParams",
    "BasePrompt",
    "Message",
    "tags",
]
