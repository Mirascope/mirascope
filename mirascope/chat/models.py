"""Classes for interactings with LLMs through Chat APIs."""
from typing import Generator, Optional

from openai import OpenAI

from ..prompts import MirascopePrompt
from .types import MirascopeChatCompletionChunkOpenAI, MirascopeChatCompletionOpenAI
from .utils import get_messages


class MirascopeChatOpenAI:
    """A convenience wrapper for the OpenAI Chat client."""

    def __init__(self, model: str = "gpt-3.5-turbo", api_key: Optional[str] = None):
        """Initializes an instance of `MirascopeChatOpenAI."""
        self.client = OpenAI(api_key=api_key)
        self.model = model

    def create(
        self, prompt: MirascopePrompt, **kwargs
    ) -> MirascopeChatCompletionOpenAI:
        """Makes a call to the model using `prompt`.

        Args:
            prompt: The `MirascopePrompt` to use for the call.
            stream: Whether or not to stream the response.
            **kwargs: Additional keyword arguments to pass to the API call. You can
                find available keyword arguments here:
                https://platform.openai.com/docs/api-reference/chat/create

        Returns:
            A `MirascopeChatCompletionOpenAI` instance.

        Raises:
            Re-raises any exceptions thrown by the openai chat completions create call.
        """
        try:
            return MirascopeChatCompletionOpenAI(
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
        self, prompt: MirascopePrompt, **kwargs
    ) -> Generator[MirascopeChatCompletionChunkOpenAI, None, None]:
        """Streams the response for a call to the model using `prompt`.

        Args:
            prompt: The `MirascopePrompt` to use for the call.
            **kwargs: Additional keyword arguments to pass to the API call. You can
                find available keyword arguments here:
                https://platform.openai.com/docs/api-reference/chat/create

        Yields:
            A `MirascopeChatCompletionChunkOpenAI` for each chunk of the response.

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
            yield MirascopeChatCompletionChunkOpenAI(chunk=chunk)
