"""Classes for interactings with LLMs through Chat APIs."""
from typing import Generator

from openai import OpenAI
from openai.types.chat import ChatCompletionMessageParam

from ..prompts import MirascopePrompt
from .types import MirascopeChatCompletion, MirascopeChatCompletionChunk


def _get_messages(
    prompt: MirascopePrompt,
) -> list[ChatCompletionMessageParam]:
    """Returns a list of messages parsed from the prompt."""
    if hasattr(prompt, "messages"):
        return [message.__dict__ for message in prompt.messages]
    return [{"role": "user", "content": str(prompt)}]


class MirascopeChatOpenAI:
    """A convenience wrapper for the OpenAI Chat client."""

    def __init__(self, model: str = "gpt-3.5-turbo"):
        """Initializes an instance of `MirascopeChatOpenAI."""
        self.client = OpenAI()
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
                messages=_get_messages(prompt),
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
            messages=[{"role": "user", "content": str(prompt)}],
            **kwargs,
        )
        for chunk in stream:
            yield MirascopeChatCompletionChunk(chunk=chunk)
