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
from .together import TogetherModelId

ModelId: TypeAlias = (
    AnthropicModelId
    | GoogleModelId
    | OpenAIModelId
    | MLXModelId
    | TogetherModelId
    | str
)
