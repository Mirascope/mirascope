"""Provider-specific model implementations."""

from ..clients import (
    AnthropicClient,
    AnthropicParams,
    GoogleClient,
    GoogleParams,
    OpenAIClient,
    OpenAIParams,
)
from .base import LLM


class OpenAI(LLM[OpenAIParams, OpenAIClient]):
    """The OpenAI-specific implementation of the `LLM` interface."""


class Anthropic(LLM[AnthropicParams, AnthropicClient]):
    """The Anthropic-specific implementation of the `LLM` interface."""


class Google(LLM[GoogleParams, GoogleClient]):
    """The Google-specific implementation of the `LLM` interface."""
