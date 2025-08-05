"""The register of models known to Mirascope."""

from typing import TypeAlias, TypeVar

from .anthropic import ANTHROPIC_REGISTERED_LLMS
from .google import GOOGLE_REGISTERED_LLMS
from .openai import OPENAI_REGISTERED_LLMS

REGISTERED_LLMS: TypeAlias = (
    ANTHROPIC_REGISTERED_LLMS | GOOGLE_REGISTERED_LLMS | OPENAI_REGISTERED_LLMS
)
"""The models registered with Mirascope."""

LLMT = TypeVar("LLMT", bound=REGISTERED_LLMS)
"""Type variable for a registered LLM model. Will be a string of form provider:model_name."""
