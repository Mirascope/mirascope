"""The Anthropic-specific implementation of the `LLM` interface."""

from typing import Literal, TypeAlias

from .base import LLM, Client, Params

ANTHROPIC_REGISTERED_LLMS: TypeAlias = Literal["anthropic:claude-3-5-sonnet-latest"]


class AnthropicParams(Params, total=False):
    """The parameters for the Anthropic LLM model."""

    temperature: float


class AnthropicClient(Client):
    """The client for the Anthropic LLM model."""


class Anthropic(LLM[AnthropicParams, AnthropicClient]):
    """The Anthropic-specific implementation of the `LLM` interface."""
