"""A module for calling OpenAI's Chat Completion models."""
from typing import AsyncGenerator, ClassVar, Generator, Optional

from ..base import BaseCall, BaseCallParams, BasePrompt
from .tools import OpenAITool
from .types import OpenAICallResponse, OpenAICallResponseChunk


class OpenAICall(BaseCall, BasePrompt):
    """A base class for calling OpenAI's Chat Completion models.

    Example:

    ```python
    from mirascope.openai import OpenAICall


    class BookRecommender(OpenAICall):
        template = "Please recommend a {genre} book"

        genre: str

    book = BookRecommender(genre="fantasy").call()
    print(book)
    #> There are many great books to read, it ultimately depends...
    ```
    """

    class CallParams(BaseCallParams[OpenAITool]):
        """The parameters with which to make a call."""

    call_params: ClassVar[CallParams] = CallParams(model="gpt-3.5-turbo-0125")

    def call(self, params: Optional[CallParams] = None) -> OpenAICallResponse:
        """Makes a call to the model using this `OpenAICall` instance.

        Args:
            params: Additional call parameters to pass to the `create` call.

        Returns:
            A `OpenAICallResponse` instance.

        Raises:
            OpenAIError: raises any OpenAI errors, see:
                https://platform.openai.com/docs/guides/error-codes/api-errors
        """
        raise NotImplementedError()

    def call_async(self, params: Optional[CallParams] = None) -> OpenAICallResponse:
        """Makes an asynchronous call to the model using this `OpenAICall`.

        Args:
            params: Additional call parameters to pass to the `create` call.

        Returns:
            An `OpenAICallResponse` instance.

        Raises:
            OpenAIError: raises any OpenAI errors, see:
                https://platform.openai.com/docs/guides/error-codes/api-errors
        """
        raise NotImplementedError()

    def stream(
        self, params: Optional[CallParams] = None
    ) -> Generator[OpenAICallResponseChunk, None, None]:
        """Streams the response for a call using this `OpenAICall`.

        Args:
            params: Additional call parameters to pass to the `create` call.

        Yields:
            A `OpenAICallResponseChunk` for each chunk of the response.

        Raises:
            OpenAIError: raises any OpenAI errors, see:
                https://platform.openai.com/docs/guides/error-codes/api-errors
        """
        raise NotImplementedError()

    def stream_async(
        self, params: Optional[CallParams] = None
    ) -> AsyncGenerator[OpenAICallResponseChunk, None]:
        """Streams the response for an asynchronous call using this `OpenAICall`.

        Args:
            params: Additional call parameters to pass to the `create` call.

        Yields:
            A `OpenAICallResponseChunk` for each chunk of the response.

        Raises:
            OpenAIError: raises any OpenAI errors, see:
                https://platform.openai.com/docs/guides/error-codes/api-errors
        """
        raise NotImplementedError()
