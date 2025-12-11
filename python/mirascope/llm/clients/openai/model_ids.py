"""Combined OpenAI model IDs."""

from typing import TypeAlias

from .completions.model_ids import OpenAICompletionsModelId
from .responses.model_ids import OpenAIResponsesModelId

OpenAIModelId: TypeAlias = OpenAICompletionsModelId | OpenAIResponsesModelId
"""Union of all OpenAI model IDs (both Completions and Responses APIs)."""
