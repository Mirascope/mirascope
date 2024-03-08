"""mirascope package."""
import importlib.metadata
from contextlib import suppress

with suppress(ImportError):
    from . import gemini

with suppress(ImportError):
    from . import wandb

from .base import BaseCallParams, BasePrompt, BaseTool, tags, tool_fn
from .openai import (
    AsyncOpenAIChat,
    AsyncOpenAIToolStreamParser,
    OpenAICallParams,
    OpenAIChat,
    OpenAIChatCompletion,
    OpenAIChatCompletionChunk,
    OpenAITool,
    OpenAIToolStreamParser,
)
from .partial import Partial
from .prompts import Prompt, messages

__version__ = importlib.metadata.version("mirascope")
