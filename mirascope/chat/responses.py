"""Classes for responses when interacting with a Chat API."""
from openai import Stream
from openai.types.chat import ChatCompletion, ChatCompletionChunk


class MirascopeChatCompletion:
    """Convenience wrapper around chat completions."""

    def __init__(self, response: ChatCompletion):
        """Initializes an instance of `MirascopeChatCompletion`."""
        self.response = response
        self.content = response.choices[0].message.content
        # We probably also want to store some level of metadata.

    def __repr__(self):
        """Returns a representation of `MirascopeChatCompletion`."""
        return str(self.__dict__)

    def __str__(self):
        """Returns the contained string content."""
        return self.content


class MirascopeChatCompletionStream:
    """Convenience wrapper around chat completion streaming."""

    def __init__(self, response: Stream[ChatCompletionChunk]):
        """Initializes and instance of `MirascopeChatCompletionStream`."""
        raise NotImplementedError()

    def __iter__(self):
        """Returns an iterator for the chunks."""
        raise NotImplementedError()

    def __next__(self):
        """Returns the next chunk in the iterator."""
        raise NotImplementedError()
