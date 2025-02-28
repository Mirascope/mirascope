"""The Mirascope Core Functionality."""

from contextlib import suppress

from . import base, costs
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
    CostMetadata,
    DocumentPart,
    FromCallArgs,
    ImagePart,
    ImageURLPart,
    LocalProvider,
    Messages,
    Provider,
    ResponseModelConfigDict,
    TextPart,
    ToolCallPart,
    ToolResultPart,
    merge_decorators,
    metadata,
    prompt_template,
    toolkit_tool,
)
from .costs import calculate_cost

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
    "CostMetadata",
    "DocumentPart",
    "FromCallArgs",
    "ImagePart",
    "ImageURLPart",
    "LocalProvider",
    "Messages",
    "Provider",
    "ResponseModelConfigDict",
    "TextPart",
    "ToolCallPart",
    "ToolResultPart",
    "anthropic",
    "azure",
    "base",
    "calculate_cost",
    "cohere",
    "costs",
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
