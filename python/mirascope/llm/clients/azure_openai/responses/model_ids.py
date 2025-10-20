"""Azure OpenAI Responses registered LLM models."""

from typing import TypeAlias

from openai.types import ResponsesModel

AzureOpenAIResponsesModelId: TypeAlias = ResponsesModel | str
"""The Azure OpenAI Responses model ids registered with Mirascope."""
