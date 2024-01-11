"""mirascope package."""
import importlib.metadata

from .chat.models import OpenAIChat
from .prompts import Prompt, messages

__version__ = importlib.metadata.version("mirascope")
