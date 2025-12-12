from typing import TypeAlias

from .anthropic import (
    AnthropicModelId,
)
from .google import (
    GoogleModelId,
)
from .mlx import (
    MLXModelId,
)
from .openai import (
    OpenAIModelId,
)

ModelId: TypeAlias = AnthropicModelId | GoogleModelId | OpenAIModelId | MLXModelId | str
