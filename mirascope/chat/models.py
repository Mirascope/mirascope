"""Classes for interactings with LLMs through Chat APIs."""
from typing import Generator

from openai import OpenAI

from ..prompts import MirascopePrompt
from .types import MirascopeChatCompletion, MirascopeChatCompletionChunk


class MirascopeChatOpenAI:
    """A class for interacting with the OpenAI Chat API."""

    def __init__(self, model: str = "gpt-3.5-turbo"):
        """Initializes an instance of `MirascopeChatOpenAI."""
        self.client = OpenAI()
        self.model = model

    def __call__(
        self,
        prompt: MirascopePrompt,
        **kwargs,
    ) -> MirascopeChatCompletion:
        """Makes a call to the model using `prompt`."""
        raise NotImplementedError()

    def stream(
        self,
        prompt: MirascopePrompt,
        **kwargs,
    ) -> Generator[MirascopeChatCompletionChunk, None, None]:
        """Streams the response for a call to the model using `prompt`."""
        raise NotImplementedError()
