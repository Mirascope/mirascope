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
    from . import logfire

with suppress(ImportError):
    from . import langfuse

with suppress(ImportError):
    from . import mistral

with suppress(ImportError):
    from . import openai

with suppress(ImportError):
    from . import pinecone

with suppress(ImportError):
    from . import wandb


__version__ = importlib.metadata.version("mirascope")

__all__ = [
    "__version__",
    "anthropic",
    "BaseCallParams",
    "BasePrompt",
    "chroma",
    "cohere",
    "gemini",
    "groq",
    "langfuse",
    "logfire",
    "Message",
    "mistral",
    "openai",
    "pinecone",
    "tags",
    "wandb",
]
