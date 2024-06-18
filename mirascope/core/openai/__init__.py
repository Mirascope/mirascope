"""The Mirascope OpenAI Module."""

from .openai_call import openai_call
from .types import OpenAICallResponse

__all__ = ["OpenAICallResponse", "openai_call"]
