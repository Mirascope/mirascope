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
    "anthropic",  # AnthropicClient
    "google",  # GoogleClient
    "openai:responses",  # OpenAIResponsesClient
    "openai",  # OpenAICompletionsClient
]
PROVIDERS = get_args(Provider)

ModelId: TypeAlias = (
    AnthropicModelId
    | GoogleModelId
    | OpenAIResponsesModelId
    | OpenAICompletionsModelId
    | str
)
