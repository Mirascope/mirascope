"""Client interfaces for LLM providers."""

from typing import Literal, TypeAlias

from .anthropic import (
    AnthropicClient,
    AnthropicModel,
    AnthropicParams,
)
from .base import (
    BaseClient,
    BaseParams,
    ClientT,
    ParamsT,
)
from .google import GoogleClient, GoogleModel, GoogleParams
from .openai import OpenAIClient, OpenAIModel, OpenAIParams

Provider: TypeAlias = Literal["openai", "anthropic", "google"]
Model: TypeAlias = OpenAIModel | AnthropicModel | GoogleModel | str

__all__ = [
    "AnthropicClient",
    "AnthropicModel",
    "AnthropicParams",
    "BaseClient",
    "BaseParams",
    "ClientT",
    "GoogleClient",
    "GoogleModel",
    "GoogleParams",
    "Model",
    "OpenAIClient",
    "OpenAIModel",
    "OpenAIParams",
    "ParamsT",
    "Provider",
]
