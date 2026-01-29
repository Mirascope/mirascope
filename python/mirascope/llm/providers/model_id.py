from typing import TypeAlias

from .anthropic import (
    AnthropicModelId,
)
from .azure import (
    AzureModelId,
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

ModelId: TypeAlias = (
    AnthropicModelId | AzureModelId | GoogleModelId | OpenAIModelId | MLXModelId | str
)
