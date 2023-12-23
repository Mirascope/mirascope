"""Classes for interactings with LLMs through Chat APIs."""
from typing import Generator, Optional

from openai import OpenAI

from ..prompts import Prompt
from .types import OpenAIChatCompletion, OpenAIChatCompletionChunk
from .utils import get_messages


class OpenAIChat:
    """A convenience wrapper for the OpenAI Chat client."""

    def __init__(self, model: str = "gpt-3.5-turbo", api_key: Optional[str] = None):
        """Initializes an instance of `OpenAIChat."""
        self.client = OpenAI(api_key=api_key)
        self.model = model

    def create(self, prompt: Prompt, **kwargs) -> OpenAIChatCompletion:
        """Makes a call to the model using `prompt`.

        Args:
            prompt: The `Prompt` to use for the call.
            stream: Whether or not to stream the response.
            **kwargs: Additional keyword arguments to pass to the API call. You can
                find available keyword arguments here:
                https://platform.openai.com/docs/api-reference/chat/create

        Returns:
            A `OpenAIChatCompletion` instance.

        Raises:
            Re-raises any exceptions thrown by the openai chat completions create call.
        """
        try:
            return OpenAIChatCompletion(
                completion=self.client.chat.completions.create(
                    model=self.model,
                    messages=get_messages(prompt),
                    stream=False,
                    **kwargs,
                )
            )
        except:
            raise

    def stream(
        self, prompt: Prompt, **kwargs
    ) -> Generator[OpenAIChatCompletionChunk, None, None]:
        """Streams the response for a call to the model using `prompt`.

        Args:
            prompt: The `Prompt` to use for the call.
            **kwargs: Additional keyword arguments to pass to the API call. You can
                find available keyword arguments here:
                https://platform.openai.com/docs/api-reference/chat/create

        Yields:
            A `OpenAIChatCompletionChunk` for each chunk of the response.

        Raises:
            Re-raises any exceptions thrown by the openai chat completions create call.
        """
        completion_stream = self.client.chat.completions.create(
            model=self.model,
            messages=get_messages(prompt),
            stream=True,
            **kwargs,
        )
        for chunk in completion_stream:
            yield OpenAIChatCompletionChunk(chunk=chunk)
