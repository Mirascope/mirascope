"""The OpenAI-specific implementation of the `LLM` interface."""

from typing import Literal, TypeAlias

from typing_extensions import NotRequired

from .base import LLM, Client, Params

OPENAI_REGISTERED_LLMS: TypeAlias = Literal["openai:gpt-4o-mini"]


class OpenAIParams(Params):
    """The parameters for the OpenAI LLM model."""

    temperature: NotRequired[float]


class OpenAIClient(Client):
    """The client for the OpenAI LLM model."""


class OpenAI(LLM[OpenAIParams, OpenAIClient]):
    """The OpenAI-specific implementation of the `LLM` interface."""
