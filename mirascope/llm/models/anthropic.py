"""The Anthropic-specific implementation of the `LLM` interface."""

from anthropic.types import MessageParam

from ..messages import Message
from .base import LLM, Client, Params


class AnthropicParams(Params, total=False):
    """The parameters for the Anthropic LLM model."""

    temperature: float


class AnthropicClient(Client):
    """The client for the Anthropic LLM model."""


class Anthropic(LLM[Message | MessageParam, AnthropicParams, AnthropicClient]):
    """The Anthropic-specific implementation of the `LLM` interface."""
