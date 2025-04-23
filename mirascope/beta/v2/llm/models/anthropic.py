"""The Anthropic-specific implementation of the `LLM` interface."""

from typing import Literal, TypeAlias

from typing_extensions import NotRequired

from .base import LLM, Client, Params

ANTHROPIC_REGISTERED_LLMS: TypeAlias = Literal["anthropic:claude-3-5-sonnet"]


class AnthropicParams(Params):
    """The parameters for the Anthropic LLM model."""

    temperature: NotRequired[float]


class AnthropicClient(Client):
    """The client for the Anthropic LLM model."""


class Anthropic(LLM[AnthropicParams, AnthropicClient]):
    """The Anthropic-specific implementation of the `LLM` interface."""
