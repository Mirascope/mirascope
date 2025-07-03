"""Provider-specific model implementations."""

from ..clients import (
    AnthropicClient,
    AnthropicMessage,
    AnthropicParams,
    GoogleClient,
    GoogleMessage,
    GoogleParams,
    OpenAIClient,
    OpenAIMessage,
    OpenAIParams,
)
from .base import LLM


class OpenAI(LLM[OpenAIMessage, OpenAIParams, OpenAIClient]):
    """The OpenAI-specific implementation of the `LLM` interface."""


class Anthropic(LLM[AnthropicMessage, AnthropicParams, AnthropicClient]):
    """The Anthropic-specific implementation of the `LLM` interface."""


class Google(LLM[GoogleMessage, GoogleParams, GoogleClient]):
    """The Google-specific implementation of the `LLM` interface."""