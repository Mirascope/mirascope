"""mirascope package."""
import importlib.metadata

from . import prompts
from .chat.models import OpenAIChat
from .prompts import Prompt, messages

__version__ = importlib.metadata.version("mirascope")
