"""OpenAI Responses registered LLM models."""

from typing import TypeAlias

from openai.types import ResponsesModel

OpenAIResponsesModelId: TypeAlias = ResponsesModel | str
"""The OpenAI Responses model ids registered with Mirascope."""
