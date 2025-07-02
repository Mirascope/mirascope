"""Provider-specific model implementations."""

from anthropic.types import MessageParam
from google.genai.types import ContentDict, FunctionResponse
from openai.types.chat import ChatCompletionMessageParam

from ..clients.anthropic import AnthropicClient, AnthropicParams
from ..clients.google import GoogleClient, GoogleParams
from ..clients.openai import OpenAIClient, OpenAIParams
from ..messages import Message
from .base import LLM


class OpenAI(LLM[Message | ChatCompletionMessageParam, OpenAIParams, OpenAIClient]):
    """The OpenAI-specific implementation of the `LLM` interface."""


class Anthropic(LLM[Message | MessageParam, AnthropicParams, AnthropicClient]):
    """The Anthropic-specific implementation of the `LLM` interface."""


class Google(LLM[Message | ContentDict | FunctionResponse, GoogleParams, GoogleClient]):
    """The Google-specific implementation of the `LLM` interface."""