"""Classes for responses when interacting with a Chat API."""
from typing import Optional

from openai import Stream
from openai.types.chat import ChatCompletion, ChatCompletionChunk
from pydantic import BaseModel


class MirascopeChatCompletion(BaseModel):
    """Convenience wrapper around chat completions."""

    response: ChatCompletion

    @property
    def content(self) -> Optional[str]:
        """Returns the content of the chat completion response."""
        return self.response.choices[0].message.content

    def __repr__(self):
        """Returns a representation of `MirascopeChatCompletion`."""
        return str(self.__dict__)

    def __str__(self):
        """Returns the contained string content."""
        return self.content


class MirascopeChatCompletionStream(BaseModel):
    """Convenience wrapper around chat completion streaming."""

    response: Stream[ChatCompletionChunk]

    def __iter__(self):
        """Returns an iterator for the chunks."""
        raise NotImplementedError()

    def __next__(self):
        """Returns the next chunk in the iterator."""
        raise NotImplementedError()
