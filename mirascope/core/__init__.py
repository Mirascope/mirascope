"""The Mirascope Core Functionality."""

from contextlib import suppress

from . import base
from .base import (
    AudioPart,
    AudioURLPart,
    BaseCallResponse,
    BaseDynamicConfig,
    BaseMessageParam,
    BasePrompt,
    BaseStream,
    BaseTool,
    BaseToolKit,
    CacheControlPart,
    DocumentPart,
    FromCallArgs,
    ImagePart,
    ImageURLPart,
    Messages,
    ResponseModelConfigDict,
    TextPart,
    ToolCallPart,
    ToolResultPart,
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
    from . import google as google

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
    "AudioPart",
    "AudioURLPart",
    "BaseCallResponse",
    "BaseCallResponse",
    "BaseDynamicConfig",
    "BaseMessageParam",
    "BasePrompt",
    "BaseStream",
    "BaseTool",
    "BaseToolKit",
    "CacheControlPart",
    "DocumentPart",
    "FromCallArgs",
    "ImagePart",
    "ImageURLPart",
    "Messages",
    "ResponseModelConfigDict",
    "TextPart",
    "ToolCallPart",
    "ToolResultPart",
    "anthropic",
    "azure",
    "base",
    "cohere",
    "gemini",
    "google",
    "groq",
    "litellm",
    "merge_decorators",
    "metadata",
    "mistral",
    "openai",
    "prompt_template",
    "toolkit_tool",
    "vertex",
]
