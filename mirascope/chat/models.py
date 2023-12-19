"""Classes for interactings with LLMs through Chat APIs."""
from openai import OpenAI

from ..prompts import MirascopePrompt
from .responses import MirascopeChatCompletion, MirascopeChatCompletionStream


class MirascopeChatOpenAI:
    """A class for interacting with the OpenAI Chat API."""

    def __init__(self, model: str = "gpt-3.5-turbo"):
        """Initializes an instance of `MirascopeChatOpenAI."""
        self.client = OpenAI()
        self.model = model

    def __call__(
        self,
        prompt: MirascopePrompt,
        # tools=list[MirascopeChatOpenAITool],
        **kwargs,
    ) -> MirascopeChatCompletion:
        """Makes a call to the model using `prompt`."""
        raise NotImplementedError()

    def stream(
        self,
        prompt: MirascopePrompt,
        # tools=list[MirascopeChatOpenAITool],
        **kwargs,
    ) -> MirascopeChatCompletionStream:
        """Streams the response for a call to the model using `prompt`."""
        raise NotImplementedError()
