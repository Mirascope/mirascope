"""The OpenAI-specific implementation of the `LLM` interface."""

from typing import Literal, TypeAlias

from .base import LLM, Client, Params

OPENAI_REGISTERED_LLMS: TypeAlias = Literal["openai:gpt-4o-mini"]


class OpenAIParams(Params, total=False):
    """The parameters for the OpenAI LLM model."""


class OpenAIClient(Client):
    """The client for the OpenAI LLM model."""


class OpenAI(LLM[OpenAIParams, OpenAIClient]):
    """The OpenAI-specific implementation of the `LLM` interface."""
