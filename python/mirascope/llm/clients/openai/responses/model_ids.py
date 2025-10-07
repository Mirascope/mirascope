"""OpenAI Responses registered LLM models."""

from typing import TypeAlias

from openai.types import ResponsesModel

OpenAIResponsesModelId: TypeAlias = ResponsesModel | str
"""The OpenAI Responses model ids registered with Mirascope."""

REASONING_MODELS = {
    "computer-use-preview-2025-03-11",
    "computer-use-preview",
    "gpt-5-mini",
    "gpt-5-nano",
    "gpt-5-pro",
    "gpt-5",
    "gpt-oss-120b",
    "gpt-oss-20b",
    "o1-pro-2025-03-19",
    "o1-pro",
    "o3-deep-research-2025-06-26",
    "o3-deep-research",
    "o3-pro-2025-06-10",
    "o3-pro",
    "o4-mini-deep-research-2025-06-26",
    "o4-mini-deep-research",
}
