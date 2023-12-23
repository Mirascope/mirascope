"""Classes for responses when interacting with a Chat API."""
from typing import Optional

from openai.types.chat import ChatCompletion, ChatCompletionChunk
from openai.types.chat.chat_completion import Choice
from openai.types.chat.chat_completion_chunk import Choice as ChunkChoice
from openai.types.chat.chat_completion_chunk import ChoiceDelta
from openai.types.chat.chat_completion_message import ChatCompletionMessage
from pydantic import BaseModel


class OpenAIChatCompletion(BaseModel):
    """Convenience wrapper around chat completions."""

    completion: ChatCompletion

    @property
    def choices(self) -> list[Choice]:
        """Returns the array of chat completion choices."""
        return self.completion.choices

    @property
    def choice(self) -> Choice:
        """Returns the 0th choice."""
        return self.completion.choices[0]

    @property
    def message(self) -> ChatCompletionMessage:
        """Returns the message of the chat completion for the 0th choice."""
        return self.completion.choices[0].message

    @property
    def content(self) -> Optional[str]:
        """Returns the content of the chat completion for the 0th choice."""
        return self.completion.choices[0].message.content

    def __str__(self):
        """Returns the contained string content for the 0th choice."""
        return self.content


class OpenAIChatCompletionChunk(BaseModel):
    """Convenience wrapper around chat completion streaming chunks."""

    chunk: ChatCompletionChunk

    @property
    def choices(self) -> list[ChunkChoice]:
        """Returns the array of chat completion choices."""
        return self.chunk.choices

    @property
    def choice(self) -> ChunkChoice:
        """Returns the 0th choice."""
        return self.chunk.choices[0]

    @property
    def delta(self) -> ChoiceDelta:
        """Returns the delta for the 0th choice."""
        return self.choices[0].delta

    @property
    def content(self) -> Optional[str]:
        """Returns the content for the 0th choice delta."""
        return self.delta.content

    def __str__(self) -> str:
        """Returns the chunk content for the 0th choice."""
        return self.content if self.content is not None else ""
