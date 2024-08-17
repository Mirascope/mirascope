"""This module contains the `GeminiCallResponseChunk` class.

usage docs: learn/streams.md#handling-streamed-responses
"""

from google.ai.generativelanguage import Candidate
from google.generativeai.types import (  # type: ignore
    GenerateContentResponse,
)

from ..base import BaseCallResponseChunk


class GeminiCallResponseChunk(
    BaseCallResponseChunk[GenerateContentResponse, Candidate.FinishReason]
):
    """Convenience wrapper around chat completion streaming chunks.

    When using Mirascope's convenience wrappers to interact with Gemini models via
    `GeminiCall`, responses using `GeminiCall.stream()` will return a
    `GeminiCallResponseChunk`, whereby the implemented properties allow for simpler
    syntax and a convenient developer experience.

    Example:

    ```python
    from mirascope.core import prompt_template
    from mirascope.core.gemini import gemini_call


    @gemini_call("gemini-1.5-flash", stream=True)
    @prompt_template("Recommend a {genre} book")
    def recommend_book(genre: str):
        ...


    stream = recommend_book("fantasy")  # response is an `GeminiStream`
    for chunk, _ in stream:
        print(chunk.content, end="", flush=True)
    ```
    """

    @property
    def content(self) -> str:
        """Returns the chunk content for the 0th choice."""
        return self.chunk.candidates[0].content.parts[0].text

    @property
    def finish_reasons(self) -> list[Candidate.FinishReason]:
        """Returns the finish reasons of the response."""
        return [candidate.finish_reason for candidate in self.chunk.candidates]

    @property
    def model(self) -> None:
        """Returns the model name.

        google.generativeai does not return model, so we return None
        """
        return None

    @property
    def id(self) -> str | None:
        """Returns the id of the response.

        google.generativeai does not return an id
        """
        return None

    @property
    def usage(self) -> None:
        """Returns the usage of the chat completion.

        google.generativeai does not have Usage, so we return None
        """
        return None

    @property
    def input_tokens(self) -> None:
        """Returns the number of input tokens."""
        return None

    @property
    def output_tokens(self) -> None:
        """Returns the number of output tokens."""
        return None
