"""Classes for interactings with LLMs through Chat APIs."""
from typing import Generator, Optional

from openai import OpenAI

from ..prompts import MirascopePrompt
from .types import MirascopeChatCompletion, MirascopeChatCompletionChunk
from .utils import get_messages


class MirascopeChatOpenAI:
    """A convenience wrapper for the OpenAI Chat client."""

    def __init__(self, model: str = "gpt-3.5-turbo", api_key: Optional[str] = None):
        """Initializes an instance of `MirascopeChatOpenAI."""
        self.client = OpenAI(api_key=api_key)
        self.model = model

    def __call__(
        self,
        prompt: MirascopePrompt,
        **kwargs,
    ) -> MirascopeChatCompletion:
        """Makes a call to the model using `prompt`.

        Args:
            prompt: The `MirascopePrompt` to use for the call.
            **kwargs: Additional keyword arguments to pass to the API call. You can
                find available keyword arguments here:
                https://platform.openai.com/docs/api-reference/chat/create
        """
        return MirascopeChatCompletion(
            completion=self.client.chat.completions.create(
                model=self.model,
                messages=get_messages(prompt),
                **kwargs,
            )
        )

    def stream(
        self,
        prompt: MirascopePrompt,
        **kwargs,
    ) -> Generator[MirascopeChatCompletionChunk, None, None]:
        """Streams the response for a call to the model using `prompt`.

        Args:
            prompt: The `MirascopePrompt` to use for the call.
            **kwargs: Additional keyword arguments to pass to the API call. You can
                find available keyword arguments here:
                https://platform.openai.com/docs/api-reference/chat/create

        Yields:
            A `MirascopeChatCompletionChunk` for each chunk of the response.
        """
        stream = self.client.chat.completions.create(
            model=self.model,
            messages=get_messages(prompt),
            stream=True,
            **kwargs,
        )
        for chunk in stream:
            yield MirascopeChatCompletionChunk(chunk=chunk)
