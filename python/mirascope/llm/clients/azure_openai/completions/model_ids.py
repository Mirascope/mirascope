"""Azure OpenAI ChatCompletions registered LLM models."""

from typing import TypeAlias

from openai.types import ChatModel

AzureOpenAICompletionsModelId: TypeAlias = ChatModel | str
"""The Azure OpenAI ChatCompletions model ids registered with Mirascope."""
