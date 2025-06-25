"""The OpenAI-specific implementation of the `LLM` interface."""

from openai.types.chat import ChatCompletionMessageParam

from ..messages import Message
from .base import LLM, Client, Params


class OpenAIParams(Params, total=False):
    """The parameters for the OpenAI LLM model."""


class OpenAIClient(Client):
    """The client for the OpenAI LLM model."""


class OpenAI(LLM[Message | ChatCompletionMessageParam, OpenAIParams, OpenAIClient]):
    """The OpenAI-specific implementation of the `LLM` interface."""
