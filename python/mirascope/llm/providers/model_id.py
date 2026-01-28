from typing import TypeAlias

from .anthropic import (
    AnthropicModelId,
)
from .azure import (
    AzureModelId,
)
from .bedrock import (
    BedrockModelId,
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
    AnthropicModelId
    | AzureModelId
    | BedrockModelId
    | GoogleModelId
    | OpenAIModelId
    | MLXModelId
    | str
)
