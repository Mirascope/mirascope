from typing import Literal, TypeAlias, get_args

from .anthropic import (
    AnthropicModelId,
)
from .google import (
    GoogleModelId,
)
from .openai import (
    OpenAICompletionsModelId,
    OpenAIResponsesModelId,
)

Provider: TypeAlias = Literal[
    "anthropic",
    "google",
    "openai:completions",  # OpenAICompletionsClient
    "openai:responses",  # OpenAIResponsesClient
    "openai",  # Alias for "openai:responses"
]
PROVIDERS = get_args(Provider)

ModelId: TypeAlias = (
    AnthropicModelId
    | GoogleModelId
    | OpenAIResponsesModelId
    | OpenAICompletionsModelId
    | str
)
