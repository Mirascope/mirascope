"""OpenAI registered LLM models."""

from typing import TypeAlias

from openai.types import ChatModel

OpenAIModelId: TypeAlias = ChatModel | str
"""The OpenAI model ids registered with Mirascope."""
