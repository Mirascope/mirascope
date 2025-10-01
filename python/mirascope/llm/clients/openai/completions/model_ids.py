"""OpenAI ChatCompletions registered LLM models."""

from typing import TypeAlias

from openai.types import ChatModel

OpenAICompletionsModelId: TypeAlias = ChatModel | str
"""The OpenAI ChatCompletions model ids registered with Mirascope."""
