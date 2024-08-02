"""The Mirascope Core Functionality."""

from contextlib import suppress

from . import base
from .base import (
    BasePrompt,
    BaseTool,
    BaseToolKit,
    metadata,
    prompt_template,
    toolkit_tool,
)

with suppress(ImportError):
    from . import anthropic as anthropic

with suppress(ImportError):
    from . import cohere as cohere

with suppress(ImportError):
    from . import gemini as gemini

with suppress(ImportError):
    from . import groq as groq


with suppress(ImportError):
    from . import litellm as litellm


with suppress(ImportError):
    from . import mistral as mistral

with suppress(ImportError):
    from . import openai as openai

__all__ = [
    "anthropic",
    "base",
    "BasePrompt",
    "BaseTool",
    "BaseToolKit",
    "cohere",
    "gemini",
    "groq",
    "litellm",
    "metadata",
    "mistral",
    "openai",
    "prompt_template",
    "toolkit_tool",
]
