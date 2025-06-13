"""The register of models known to Mirascope."""

from typing import Literal, TypeAlias

ANTHROPIC_REGISTERED_LLMS: TypeAlias = Literal["anthropic:claude-3-5-sonnet-latest"]
"""The Anthropic models registered with Mirascope."""


GOOGLE_REGISTERED_LLMS: TypeAlias = Literal["google:gemini-2.5-flash"]
"""The Google models registered with Mirascope."""


OPENAI_REGISTERED_LLMS: TypeAlias = Literal["openai:gpt-4o-mini"]
"""The OpenAI models registered with Mirascope."""


REGISTERED_LLMS: TypeAlias = (
    ANTHROPIC_REGISTERED_LLMS | GOOGLE_REGISTERED_LLMS | OPENAI_REGISTERED_LLMS
)
"""The models registered with Mirascope."""
