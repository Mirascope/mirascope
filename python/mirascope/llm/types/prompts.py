from typing_extensions import TypeVar

from ..prompts import AsyncPrompt, Prompt

PromptT = TypeVar("PromptT", bound=Prompt | AsyncPrompt)
"""Type variable for prompt types.

This TypeVar represents either synchronous Prompt or asynchronous AsyncPrompt
function types. It's used in generic classes and functions that work with
both prompt variants.
"""
