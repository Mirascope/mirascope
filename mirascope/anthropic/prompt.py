"""A module for prompting Anthropics's Chat API."""
import datetime
import os
import re
from typing import Annotated, ClassVar, Generator, Iterable

from anthropic import Anthropic
from anthropic.types import MessageParam
from pydantic import BeforeValidator, InstanceOf

from ..base.prompt import BasePrompt, format_template
from .types import AnthropicCallParams, AnthropicCompletion, AnthropicCompletionChunk


def _set_api_key(api_key: str) -> None:
    """Sets the Anthropic API key in the environment."""
    if api_key:
        os.environ["ANTHROPIC_API_KEY"] = api_key
    return None


class AnthropicPrompt(BasePrompt):
    '''A class for prompting Anthropics's Chat API.

    This prompt supports the message types: USER, ASSISTANT

    Example:

    ```python
    import os

    from mirascope.anthropic import AnthropicPrompt

    os.environ["ANTHROPIC_API_KEY"] = "YOUR_API_KEY"


    class BookRecommendation(AnthropicPrompt):
        """
        USER:
        You're the world's greatest librarian.

        ASSISTANT:
        Ok, I understand that I'm the world's greatest librarian. How can I help you?

        USER:
        Please recommend some {genre} books.
        """

        genre: str


    prompt = BookRecommendation(genre="fantasy")
    print(prompt.create())
    #> As the world's greatest librarian, I am delighted to recommend...
    ```
    '''

    api_key: Annotated[
        InstanceOf[None],
        BeforeValidator(lambda key: _set_api_key(key)),
    ] = None

    call_params: ClassVar[AnthropicCallParams] = AnthropicCallParams()

    @property
    def messages(self) -> Iterable[MessageParam]:
        """Returns the `ContentsType` messages for Gemini `generate_content`."""
        messages: list[MessageParam] = []
        for match in re.finditer(
            r"(USER|ASSISTANT): " r"((.|\n)+?)(?=\n(USER|ASSISTANT):|\Z)",
            self.template(),
        ):
            role: str = match.group(1).lower()
            content = format_template(self, match.group(2))
            messages.append({"role": role, "content": content})
        if len(messages) == 0:
            messages.append({"role": "user", "content": str(self)})
        return messages

    def create(self) -> AnthropicCompletion:
        """Makes a call to the model using this `AnthropicPrompt`.

        Returns:
            A `AnthropicCompletion` instance.
        """
        client = Anthropic(base_url=self.call_params.base_url)
        if self.call_params.wrapper is not None:
            client = self.call_params.wrapper(client)
        completion_start_time = datetime.datetime.now().timestamp() * 1000
        message = client.messages.create(
            messages=self.messages,
            stream=False,
            **self.call_params.kwargs,
        )
        return AnthropicCompletion(
            completion=message,
            start_time=completion_start_time,
            end_time=datetime.datetime.now().timestamp() * 1000,
        )

    def stream(self) -> Generator[AnthropicCompletionChunk, None, None]:
        """Streams the response for a call to the model using this prompt.

        Yields:
            A `AnthropicCompletionChunk` for each chunk of the response.
        """
        client = Anthropic(base_url=self.call_params.base_url)
        if self.call_params.wrapper is not None:
            client = self.call_params.wrapper(client)
        with client.messages.stream(
            messages=self.messages, **self.call_params.kwargs
        ) as stream:
            for chunk in stream:
                yield AnthropicCompletionChunk(chunk=chunk)
