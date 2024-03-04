"""mirascope package."""
import importlib.metadata

from . import integrations
from .partial import Partial
from .prompts import BaseCallParams, BaseTool, Prompt, messages, tags, tool_fn
from .prompts.openai import (
    AsyncOpenAIChat,
    AsyncOpenAIToolStreamParser,
    OpenAICallParams,
    OpenAIChat,
    OpenAIChatCompletion,
    OpenAIChatCompletionChunk,
    OpenAITool,
    OpenAIToolStreamParser,
)

__version__ = importlib.metadata.version("mirascope")
