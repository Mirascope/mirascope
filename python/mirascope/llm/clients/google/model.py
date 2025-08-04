"""Google registered LLM models."""

from typing import Literal, TypeAlias

GoogleModel: TypeAlias = Literal["google:gemini-2.5-flash"] | str
"""The Google models registered with Mirascope."""
