"""The register of models known to Mirascope."""

from typing import TypeAlias

from ..providers.anthropic import REGISTERED_LLMS as ANTHROPIC_REGISTERED_LLMS
from ..providers.google import REGISTERED_LLMS as GOOGLE_REGISTERED_LLMS
from ..providers.openai import REGISTERED_LLMS as OPENAI_REGISTERED_LLMS

REGISTERED_LLMS: TypeAlias = (
    ANTHROPIC_REGISTERED_LLMS | GOOGLE_REGISTERED_LLMS | OPENAI_REGISTERED_LLMS
)
"""The models registered with Mirascope."""
