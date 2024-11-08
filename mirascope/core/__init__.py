"""The Mirascope Core Functionality."""

from contextlib import suppress

from . import base
from .base import (
    BaseDynamicConfig,
    BaseMessageParam,
    BasePrompt,
    BaseTool,
    BaseToolKit,
    FromCallArgs,
    Messages,
    ResponseModelConfigDict,
    merge_decorators,
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

with suppress(ImportError):
    from . import vertex as vertex

with suppress(ImportError):
    from . import azure as azure

__all__ = [
    "anthropic",
    "azure",
    "base",
    "BaseDynamicConfig",
    "BaseMessageParam",
    "BasePrompt",
    "BaseTool",
    "BaseToolKit",
    "cohere",
    "FromCallArgs",
    "gemini",
    "groq",
    "litellm",
    "merge_decorators",
    "Messages",
    "metadata",
    "mistral",
    "openai",
    "prompt_template",
    "ResponseModelConfigDict",
    "toolkit_tool",
    "vertex",
]
